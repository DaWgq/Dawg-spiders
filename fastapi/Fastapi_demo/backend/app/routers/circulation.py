from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Book, BorrowRecord, Reader
from ..schemas import BorrowCreate, BorrowRecordOut, RenewCreate, ReturnCreate

router = APIRouter()


def effective_status(record: BorrowRecord) -> str:
    """计算记录实际状态: 未归还且已过应还日期 -> 逾期"""
    if record.status == "已归还":
        return "已归还"
    if record.due_date < datetime.now():
        return "逾期"
    return "借出中"


@router.get("/records", summary="借阅记录分页列表")
def list_records(
    status: str = "",
    keyword: str = "",
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    query = db.query(BorrowRecord)
    if keyword:
        like = f"%{keyword}%"
        query = query.join(Reader).join(Book).filter(
            or_(
                Reader.name.like(like),
                Reader.reader_no.like(like),
                Book.title.like(like),
                Book.isbn.like(like),
            )
        )
    if status == "已归还":
        query = query.filter(BorrowRecord.status == "已归还")
    elif status == "借出中":
        query = query.filter(BorrowRecord.status == "借出中", BorrowRecord.due_date >= datetime.now())
    elif status == "逾期":
        query = query.filter(BorrowRecord.status == "借出中", BorrowRecord.due_date < datetime.now())

    total = query.count()
    records = (
        query.order_by(BorrowRecord.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    items = []
    for r in records:
        data = BorrowRecordOut.model_validate(r).model_dump()
        data["status"] = effective_status(r)
        items.append(data)
    return {"items": items, "total": total}


@router.post("/borrow", summary="借书")
def borrow_book(payload: BorrowCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    reader = db.get(Reader, payload.reader_id)
    if reader is None:
        raise HTTPException(status_code=404, detail="读者不存在")
    if reader.status == "冻结":
        raise HTTPException(status_code=400, detail="该读者已被冻结, 无法借书")

    book = db.get(Book, payload.book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="图书不存在")
    if book.available_copies <= 0:
        raise HTTPException(status_code=400, detail="该图书已全部借出")

    active = (
        db.query(BorrowRecord)
        .filter(
            BorrowRecord.reader_id == reader.id,
            BorrowRecord.book_id == book.id,
            BorrowRecord.status == "借出中",
        )
        .first()
    )
    if active:
        raise HTTPException(status_code=400, detail="该读者已借阅此书且尚未归还")

    now = datetime.now()
    record = BorrowRecord(
        reader_id=reader.id,
        book_id=book.id,
        borrow_date=now,
        due_date=now + timedelta(days=payload.days),
        status="借出中",
    )
    db.add(record)
    book.available_copies -= 1
    db.commit()
    db.refresh(record)
    return {
        "message": "借书成功",
        "record_id": record.id,
        "reader_name": reader.name,
        "book_title": book.title,
        "due_date": record.due_date,
    }


@router.post("/return", summary="还书")
def return_book(payload: ReturnCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    book = db.get(Book, payload.book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="图书不存在")

    record = (
        db.query(BorrowRecord)
        .filter(BorrowRecord.book_id == book.id, BorrowRecord.status == "借出中")
        .order_by(BorrowRecord.borrow_date.asc())
        .first()
    )
    if record is None:
        raise HTTPException(status_code=400, detail="该图书当前没有借出记录")

    record.status = "已归还"
    record.return_date = datetime.now()
    book.available_copies = min(book.total_copies, book.available_copies + 1)
    db.commit()
    return {
        "message": "还书成功",
        "record_id": record.id,
        "reader_name": record.reader.name if record.reader else "",
        "book_title": book.title,
    }


@router.post("/renew", summary="续借")
def renew_record(payload: RenewCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    record = db.get(BorrowRecord, payload.record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="借阅记录不存在")
    if record.status != "借出中":
        raise HTTPException(status_code=400, detail="该记录已归还, 无法续借")
    record.due_date = record.due_date + timedelta(days=payload.days)
    db.commit()
    return {
        "message": "续借成功",
        "record_id": record.id,
        "due_date": record.due_date,
        "reader_name": record.reader.name if record.reader else "",
        "book_title": record.book.title if record.book else "",
    }
