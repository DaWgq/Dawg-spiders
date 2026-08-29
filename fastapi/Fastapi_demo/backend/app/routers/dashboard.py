from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Book, BorrowRecord, Reader

router = APIRouter()


@router.get("/stats", summary="仪表盘统计")
def stats(db: Session = Depends(get_db), _=Depends(get_current_user)):
    now = datetime.now()

    total_books = db.query(func.coalesce(func.sum(Book.total_copies), 0)).scalar() or 0
    total_readers = db.query(func.count(Reader.id)).scalar() or 0
    borrowed_now = (
        db.query(func.count(BorrowRecord.id)).filter(BorrowRecord.status == "借出中").scalar() or 0
    )
    overdue = (
        db.query(func.count(BorrowRecord.id))
        .filter(BorrowRecord.status == "借出中", BorrowRecord.due_date < now)
        .scalar()
        or 0
    )

    # 本月新增图书
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    new_books_month = (
        db.query(func.count(Book.id)).filter(Book.created_at >= month_start).scalar() or 0
    )
    # 本周新增读者
    week_start = now - timedelta(days=now.weekday())
    new_readers_week = (
        db.query(func.count(Reader.id)).filter(Reader.created_at >= week_start).scalar() or 0
    )
    # 在馆可借图书种数
    available_books = db.query(func.count(Book.id)).filter(Book.available_copies > 0).scalar() or 0

    return {
        "total_books": total_books,
        "total_readers": total_readers,
        "borrowed_now": borrowed_now,
        "overdue": overdue,
        "new_books_month": new_books_month,
        "new_readers_week": new_readers_week,
        "available_books": available_books,
    }


@router.get("/recent-activities", summary="最新借还动态")
def recent_activities(limit: int = 12, db: Session = Depends(get_db), _=Depends(get_current_user)):
    records = (
        db.query(BorrowRecord)
        .order_by(BorrowRecord.id.desc())
        .limit(60)
        .all()
    )
    now = datetime.now()
    events = []
    for r in records:
        reader = r.reader
        book = r.book
        reader_label = f"{reader.name} ({reader.reader_no})" if reader else "-"
        book_label = book.title if book else "-"
        events.append(
            {
                "type": "borrow",
                "reader_label": reader_label,
                "book_title": book_label,
                "isbn": book.isbn if book else "",
                "time": r.borrow_date,
            }
        )
        if r.return_date:
            events.append(
                {
                    "type": "return",
                    "reader_label": reader_label,
                    "book_title": book_label,
                    "isbn": book.isbn if book else "",
                    "time": r.return_date,
                }
            )
        if r.status == "借出中" and r.due_date < now:
            events.append(
                {
                    "type": "overdue",
                    "reader_label": reader_label,
                    "book_title": book_label,
                    "overdue_days": (now - r.due_date).days,
                    "time": r.due_date,
                }
            )

    events.sort(key=lambda e: e["time"], reverse=True)
    return events[:limit]


@router.get("/popular-books", summary="热门借阅图书")
def popular_books(limit: int = 5, db: Session = Depends(get_db), _=Depends(get_current_user)):
    rows = (
        db.query(Book, func.count(BorrowRecord.id).label("cnt"))
        .join(BorrowRecord, BorrowRecord.book_id == Book.id)
        .group_by(Book.id)
        .order_by(func.count(BorrowRecord.id).desc(), Book.id.asc())
        .limit(limit)
        .all()
    )
    return [
        {"title": book.title, "author": book.author, "count": cnt, "isbn": book.isbn}
        for book, cnt in rows
    ]
