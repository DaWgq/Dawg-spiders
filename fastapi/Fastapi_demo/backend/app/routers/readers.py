from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import BorrowRecord, Reader
from ..schemas import ReaderCreate, ReaderOut, ReaderStatusUpdate, ReaderUpdate

router = APIRouter()


@router.get("/query", summary="按关键字查询读者(供借书台使用)")
def query_readers(keyword: str = "", limit: int = 20, db: Session = Depends(get_db), _=Depends(get_current_user)):
    query = db.query(Reader)
    if keyword:
        like = f"%{keyword}%"
        query = query.filter(
            or_(Reader.name.like(like), Reader.reader_no.like(like), Reader.phone.like(like))
        )
    readers = query.order_by(Reader.id.desc()).limit(limit).all()
    return [
        {"id": r.id, "reader_no": r.reader_no, "name": r.name, "phone": r.phone, "status": r.status}
        for r in readers
    ]


@router.get("", summary="读者分页列表")
def list_readers(
    keyword: str = "",
    status: str = "",
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    query = db.query(Reader)
    if keyword:
        like = f"%{keyword}%"
        query = query.filter(
            or_(Reader.name.like(like), Reader.reader_no.like(like), Reader.phone.like(like), Reader.email.like(like))
        )
    if status in ("正常", "冻结"):
        query = query.filter(Reader.status == status)

    total = query.count()
    readers = (
        query.order_by(Reader.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    # 附加每个读者的当前在借数量
    items = []
    for r in readers:
        borrowed = (
            db.query(BorrowRecord)
            .filter(BorrowRecord.reader_id == r.id, BorrowRecord.status == "借出中")
            .count()
        )
        data = ReaderOut.model_validate(r).model_dump()
        data["borrowed_count"] = borrowed
        items.append(data)
    return {"items": items, "total": total}


@router.post("", response_model=ReaderOut, summary="新增读者")
def create_reader(payload: ReaderCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    exists = db.query(Reader).filter(Reader.reader_no == payload.reader_no).first()
    if exists:
        raise HTTPException(status_code=400, detail=f"读者编号 {payload.reader_no} 已存在")
    reader = Reader(**payload.model_dump())
    db.add(reader)
    db.commit()
    db.refresh(reader)
    return reader


@router.put("/{reader_id}", response_model=ReaderOut, summary="更新读者")
def update_reader(
    reader_id: int, payload: ReaderUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)
):
    reader = db.get(Reader, reader_id)
    if reader is None:
        raise HTTPException(status_code=404, detail="读者不存在")
    exists = (
        db.query(Reader).filter(Reader.reader_no == payload.reader_no, Reader.id != reader_id).first()
    )
    if exists:
        raise HTTPException(status_code=400, detail=f"读者编号 {payload.reader_no} 已被其他读者使用")
    for field, value in payload.model_dump().items():
        setattr(reader, field, value)
    db.commit()
    db.refresh(reader)
    return reader


@router.put("/{reader_id}/status", response_model=ReaderOut, summary="修改读者状态(正常/冻结)")
def change_reader_status(
    reader_id: int, payload: ReaderStatusUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)
):
    reader = db.get(Reader, reader_id)
    if reader is None:
        raise HTTPException(status_code=404, detail="读者不存在")
    reader.status = payload.status
    db.commit()
    db.refresh(reader)
    return reader


@router.delete("/{reader_id}", summary="删除读者")
def delete_reader(reader_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    reader = db.get(Reader, reader_id)
    if reader is None:
        raise HTTPException(status_code=404, detail="读者不存在")
    active = (
        db.query(BorrowRecord)
        .filter(BorrowRecord.reader_id == reader_id, BorrowRecord.status == "借出中")
        .first()
    )
    if active:
        raise HTTPException(status_code=400, detail="该读者存在未归还的图书, 无法删除")
    db.delete(reader)
    db.commit()
    return {"message": "删除成功"}


@router.get("/{reader_id}/borrows", summary="读者借阅历史")
def reader_borrows(reader_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    reader = db.get(Reader, reader_id)
    if reader is None:
        raise HTTPException(status_code=404, detail="读者不存在")
    records = (
        db.query(BorrowRecord)
        .filter(BorrowRecord.reader_id == reader_id)
        .order_by(BorrowRecord.borrow_date.desc())
        .all()
    )
    result = []
    for r in records:
        # 计算实际状态: 未归还且已过应还日期 -> 逾期
        status = r.status
        if r.status != "已归还" and r.due_date < datetime.now():
            status = "逾期"
        result.append(
            {
                "id": r.id,
                "book_id": r.book_id,
                "book_title": r.book_title,
                "book_isbn": r.book_isbn,
                "borrow_date": r.borrow_date,
                "due_date": r.due_date,
                "return_date": r.return_date,
                "status": status,
            }
        )
    return result
