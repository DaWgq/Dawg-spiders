import json
import csv
import io
from typing import List, Set
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

import database as db
from crawler import crawler_engine


# --- WebSocket 连接管理 ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.append(connection)
        for conn in disconnected:
            self.disconnect(conn)


manager = ConnectionManager()


# --- App Lifecycle ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时设置广播函数
    crawler_engine.set_broadcast(manager.broadcast)
    db.init_db()
    # 若之前是 running 状态则重置为 paused
    if db.get_state("status") == "running":
        db.set_state("status", "paused")
    yield


app = FastAPI(title="企业环境信息依法披露系统 - 爬虫控制台", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- REST API ---
@app.get("/api/status")
async def get_status():
    state = db.get_all_state()
    total_pages = int(state.get("total_pages", 300))
    current_page = int(state.get("current_page", 0))
    progress = min(100, round((current_page / total_pages) * 100)) if total_pages > 0 else 0
    return {
        "status": state.get("status", "idle"),
        "stats": {
            "currentPage": current_page,
            "successPages": int(state.get("success_pages", 0)),
            "failedPages": int(state.get("failed_pages", 0)),
            "totalRecords": int(state.get("total_records", 0)),
        },
        "progress": progress,
        "config": {
            "totalPages": int(state.get("total_pages", 300)),
            "pageSize": int(state.get("page_size", 20)),
            "csvFile": state.get("csv_file", "data.csv"),
            "checkpointFile": state.get("checkpoint_file", "checkpoint.json"),
            "cookie": state.get("cookie", ""),
            "retryLimit": int(state.get("retry_limit", 5)),
            "delay": float(state.get("delay", 2)),
        },
    }


@app.post("/api/start")
async def start_crawler():
    crawler_engine.start()
    return {"message": "爬虫已启动", "status": "running"}


@app.post("/api/pause")
async def pause_crawler():
    crawler_engine.pause()
    return {"message": "爬虫已暂停", "status": "paused"}


@app.post("/api/reset")
async def reset_crawler():
    crawler_engine.reset()
    return {"message": "已重置", "status": "idle"}


@app.put("/api/config")
async def update_config(config: dict):
    field_map = {
        "totalPages": "total_pages",
        "pageSize": "page_size",
        "csvFile": "csv_file",
        "checkpointFile": "checkpoint_file",
        "cookie": "cookie",
        "retryLimit": "retry_limit",
        "delay": "delay",
    }
    for key, value in config.items():
        if key in field_map:
            db.set_state(field_map[key], str(value))
    return {"message": "配置已更新"}


@app.get("/api/records")
async def get_records(limit: int = 100, offset: int = 0):
    records = db.get_records(limit, offset)
    total = db.get_record_count()
    return {"records": records, "total": total}


@app.get("/api/logs")
async def get_logs():
    logs = db.get_logs(200)
    return {"logs": logs}


@app.get("/api/export")
async def export_csv():
    records = db.get_all_records_for_export()
    if not records:
        return {"message": "暂无数据可导出"}

    output = io.StringIO()
    # Write BOM for Excel compatibility
    output.write('\ufeff')
    if records:
        writer = csv.DictWriter(output, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=enterprise_data.csv"},
    )


# --- WebSocket ---
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # 发送当前状态
        state = db.get_all_state()
        total_pages = int(state.get("total_pages", 300))
        current_page = int(state.get("current_page", 0))
        await websocket.send_text(json.dumps({
            "type": "init",
            "data": {
                "status": state.get("status", "idle"),
                "stats": {
                    "currentPage": current_page,
                    "successPages": int(state.get("success_pages", 0)),
                    "failedPages": int(state.get("failed_pages", 0)),
                    "totalRecords": int(state.get("total_records", 0)),
                },
                "logs": db.get_logs(200),
            }
        }, ensure_ascii=False))

        while True:
            data = await websocket.receive_text()
            # 处理前端发来的命令
            try:
                cmd = json.loads(data)
                action = cmd.get("action")
                if action == "start":
                    crawler_engine.start()
                    await manager.broadcast(json.dumps({
                        "type": "status_change",
                        "data": {"status": "running"}
                    }))
                elif action == "pause":
                    crawler_engine.pause()
                    await manager.broadcast(json.dumps({
                        "type": "status_change",
                        "data": {"status": "paused"}
                    }))
                elif action == "reset":
                    crawler_engine.reset()
                    await manager.broadcast(json.dumps({
                        "type": "status_change",
                        "data": {"status": "idle"}
                    }))
                    await manager.broadcast(json.dumps({
                        "type": "stats",
                        "data": {
                            "currentPage": 0,
                            "successPages": 0,
                            "failedPages": 0,
                            "totalRecords": 0,
                        }
                    }))
                    await manager.broadcast(json.dumps({
                        "type": "clear_data",
                        "data": {}
                    }))
                elif action == "config":
                    config_data = cmd.get("data", {})
                    field_map = {
                        "totalPages": "total_pages",
                        "pageSize": "page_size",
                        "cookie": "cookie",
                        "delay": "delay",
                    }
                    for key, value in config_data.items():
                        if key in field_map:
                            db.set_state(field_map[key], str(value))
            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
