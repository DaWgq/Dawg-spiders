from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from database import get_wallpapers, get_wallpaper_detail, get_categories

app = FastAPI(title="道格壁纸 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/wallpapers")
def list_wallpapers(
    page: int = Query(1, ge=1),
    pageSize: int = Query(24, ge=1, le=100),
    type: int | None = Query(None, alias="type"),
    keyword: str | None = Query(None),
):
    return get_wallpapers(page=page, page_size=pageSize, wp_type=type, keyword=keyword)


@app.get("/api/wallpapers/{wt_id}")
def wallpaper_detail(wt_id: str):
    data = get_wallpaper_detail(wt_id)
    if not data:
        return {"error": "not found"}, 404
    return data


@app.get("/api/categories")
def categories():
    return get_categories()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
