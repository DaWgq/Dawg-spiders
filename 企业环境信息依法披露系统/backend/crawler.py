import asyncio
import random
import uuid
import json
from datetime import datetime, timedelta
from typing import Callable, Optional

import database as db

# 模拟数据池
PROVINCES = ["河北省", "山东省", "江苏省", "浙江省", "广东省", "四川省", "湖北省", "辽宁省", "河南省", "安徽省"]
CITIES = {
    "河北省": ["石家庄市", "保定市", "邢台市", "唐山市", "廊坊市"],
    "山东省": ["济南市", "青岛市", "烟台市", "潍坊市", "临沂市"],
    "江苏省": ["南京市", "苏州市", "无锡市", "常州市", "南通市"],
    "浙江省": ["杭州市", "宁波市", "温州市", "嘉兴市", "绍兴市"],
    "广东省": ["广州市", "深圳市", "东莞市", "佛山市", "惠州市"],
    "四川省": ["成都市", "绵阳市", "德阳市", "宜宾市", "泸州市"],
    "湖北省": ["武汉市", "宜昌市", "襄阳市", "荆州市", "黄石市"],
    "辽宁省": ["沈阳市", "大连市", "鞍山市", "抚顺市", "锦州市"],
    "河南省": ["郑州市", "洛阳市", "南阳市", "许昌市", "新乡市"],
    "安徽省": ["合肥市", "芜湖市", "蚌埠市", "阜阳市", "安庆市"],
}
COUNTIES = ["高新区", "经济开发区", "正定县", "元氏县", "赞皇县", "晋州市", "新华区", "桥西区", "长安区", "裕华区"]
INDUSTRY_CATEGORIES = [
    ("C2614", "有机化学原料制造"),
    ("C2661", "化学试剂和助剂制造"),
    ("C2631", "化学农药制造"),
    ("C3612", "新能源车整车制造"),
    ("C3770", "助动车制造"),
    ("C2221", "机制纸及纸板制造"),
    ("C1352", "禽类屠宰"),
    ("C4210", "金属废料和碎屑加工处理"),
    ("C3071", "建筑陶瓷制品制造"),
    ("C3216", "铝冶炼"),
    ("C1512", "白酒制造"),
    ("D4620", "污水处理及其再生利用"),
    ("N7724", "危险废物治理"),
    ("C3012", "石灰和石膏制造"),
    ("C2929", "塑料零件及其他塑料制品制造"),
]
COMPANY_PREFIXES = [
    "恒达", "鑫源", "华信", "中博", "畅泽", "永通", "新宇宙", "鸿业", "金鹏", "海特",
    "顺境", "润德", "揽悦", "程阳", "福星", "华星", "旭阳", "兴冀", "三益", "长征",
    "邢酒", "麒盛", "诚质", "益民", "宝丰", "绿洲", "清源", "东方", "天瑞", "盛达",
]
COMPANY_SUFFIXES = [
    "环保科技有限公司", "化工有限公司", "制造有限公司", "纸业有限责任公司",
    "食品有限公司", "建材有限公司", "陶瓷制造有限公司", "再生资源利用有限公司",
    "能源科技有限公司", "汽车有限公司", "塑胶制品有限公司", "酒业股份有限公司",
]


def generate_mock_record(page_num: int, index: int) -> dict:
    """生成一条模拟企业记录"""
    province = random.choice(PROVINCES)
    city = random.choice(CITIES[province])
    county = random.choice(COUNTIES)
    industry = random.choice(INDUSTRY_CATEGORIES)
    company_name = f"{city[:2]}{random.choice(COMPANY_PREFIXES)}{random.choice(COMPANY_SUFFIXES)}"

    now = datetime.now()
    report_time = (now - timedelta(days=random.randint(1, 180))).strftime("%Y-%m-%d %H:%M:%S")

    return {
        "id": str(uuid.uuid4()).upper(),
        "province": province,
        "city": city,
        "county": county,
        "towns": f"{random.choice(['东', '西', '南', '北'])}街道办事处",
        "contactPerson": f"{'赵钱孙李周吴郑王'[random.randint(0, 7)]}"
                         f"{'明华强伟芳敏静丽'[random.randint(0, 7)]}"
                         f"{'国建民志文学杰龙'[random.randint(0, 7)]}",
        "contactNumber": f"1{random.choice(['38', '39', '58', '59', '85', '86', '37', '36'])}"
                         f"{random.randint(10000000, 99999999)}",
        "registeredAddress": f"{province}{city}{county}工业园区{random.randint(1, 99)}号",
        "productionAddress": f"{province}{city}{county}工业园区{random.randint(1, 99)}号",
        "name": company_name,
        "creditCode": f"91{random.randint(100000, 999999)}MA{random.randint(10000000, 99999999)}",
        "unifiedId": str(random.choice(["2023", "2024", "2025", ""])),
        "isKeyDischargeEnp": str(random.choice([0, 1])),
        "isCcpaEnp": str(random.choice([0, 1])),
        "industryCategoryCode": industry[0],
        "industryCategoryName": industry[1],
        "enpNatureCode": str(random.choice([1, 2, 3])),
        "enpNatureName": "",
        "year": "2025",
        "reportTime": report_time,
        "status": "已完成",
        "longitude": round(random.uniform(113.0, 120.0), 6),
        "latitude": round(random.uniform(30.0, 40.0), 6),
        "reportId": str(uuid.uuid4()),
        "createTime": report_time,
    }


class CrawlerEngine:
    """爬虫引擎 (模拟模式)"""

    def __init__(self):
        self._task: Optional[asyncio.Task] = None
        self._broadcast: Optional[Callable] = None

    def set_broadcast(self, broadcast_fn: Callable):
        """设置 WebSocket 广播函数"""
        self._broadcast = broadcast_fn

    async def _send(self, msg_type: str, data: dict):
        """发送消息到前端"""
        if self._broadcast:
            await self._broadcast(json.dumps({"type": msg_type, "data": data}, ensure_ascii=False))

    async def _run(self):
        """核心爬虫循环"""
        try:
            state = db.get_all_state()
            total_pages = int(state.get("total_pages", 300))
            page_size = int(state.get("page_size", 20))
            delay = float(state.get("delay", 2))
            current_page = int(state.get("current_page", 0))

            if current_page > 0:
                log = db.add_log(f"检测到断点，从第 {current_page + 1} 页继续执行增量爬取...")
            else:
                log = db.add_log("启动全新爬取任务...")
            await self._send("log", log)

            while current_page < total_pages:
                # 检查状态
                status = db.get_state("status")
                if status != "running":
                    break

                current_page += 1
                is_error = random.random() < 0.05  # 5% 概率模拟错误

                if is_error:
                    failed = int(db.get_state("failed_pages")) + 1
                    db.set_state("failed_pages", str(failed))
                    log = db.add_log(
                        f"[错误] 抓取第 {current_page} 页时发生网络波动，准备重试...",
                        "error",
                    )
                    await self._send("log", log)
                    await self._send("stats", {
                        "currentPage": current_page - 1,  # 不递进
                        "successPages": int(db.get_state("success_pages")),
                        "failedPages": failed,
                        "totalRecords": int(db.get_state("total_records")),
                    })
                    await asyncio.sleep(delay * 0.5)
                    current_page -= 1  # 重试当前页
                    continue

                # 生成模拟数据并存入数据库
                records = []
                for i in range(page_size):
                    record = generate_mock_record(current_page, i)
                    db.insert_record(record)
                    records.append(record)

                # 更新统计
                success = int(db.get_state("success_pages")) + 1
                total_records = int(db.get_state("total_records")) + page_size
                db.set_state("current_page", str(current_page))
                db.set_state("success_pages", str(success))
                db.set_state("total_records", str(total_records))

                checkpoint_file = db.get_state("checkpoint_file") or "checkpoint.json"
                log = db.add_log(
                    f"成功抓取第 {current_page} 页数据，解析到 {page_size} 条记录。已自动保存进度到 {checkpoint_file}"
                )
                await self._send("log", log)

                # 发送统计和最新记录
                await self._send("stats", {
                    "currentPage": current_page,
                    "successPages": success,
                    "failedPages": int(db.get_state("failed_pages")),
                    "totalRecords": total_records,
                })

                # 发送最新记录到预览
                preview_records = []
                for r in records[:5]:
                    preview_records.append({
                        "id": r["id"][:8] + "...",
                        "name": r["name"],
                        "creditCode": r["creditCode"],
                        "province": r["province"],
                        "city": r["city"],
                        "year": r["year"],
                        "status": r["status"],
                    })
                await self._send("records", preview_records)

                await asyncio.sleep(delay * 0.5)  # 加快模拟速度

            # 完成
            status = db.get_state("status")
            if status == "running":
                db.set_state("status", "completed")
                log = db.add_log("爬取任务全部完成！", "success")
                await self._send("log", log)
                await self._send("status_change", {"status": "completed"})

        except asyncio.CancelledError:
            db.add_log("任务被取消", "warning")
        except Exception as e:
            db.set_state("status", "error")
            log = db.add_log(f"爬虫发生异常: {str(e)}", "error")
            await self._send("log", log)
            await self._send("status_change", {"status": "error"})

    def start(self):
        """启动爬虫"""
        status = db.get_state("status")
        cookie = db.get_state("cookie")

        if status == "idle" and not cookie:
            log = db.add_log("警告: 未配置 Cookie/JSESSIONID，可能会遇到 405 或 401 错误。", "warning")

        db.set_state("status", "running")
        self._task = asyncio.create_task(self._run())
        return {"status": "running"}

    def pause(self):
        """暂停爬虫"""
        db.set_state("status", "paused")
        if self._task and not self._task.done():
            self._task.cancel()
        db.add_log("任务已暂停，进度已安全保存。", "warning")
        return {"status": "paused"}

    def reset(self):
        """重置爬虫"""
        if self._task and not self._task.done():
            self._task.cancel()
        db.reset_state()
        db.clear_records()
        db.clear_logs()
        db.add_log("已清除断点，下次将从第 1 页重新开始。")
        return {"status": "idle"}


# 全局爬虫实例
crawler_engine = CrawlerEngine()
