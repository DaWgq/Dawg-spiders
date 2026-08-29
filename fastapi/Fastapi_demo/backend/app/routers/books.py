from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Book, Category
from ..schemas import BookCreate, BookOut, BookUpdate, CategoryOut

router = APIRouter()


@router.get("/categories", response_model=list[CategoryOut], summary="图书分类列表")
def list_categories(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Category).order_by(Category.id).all()


@router.get("/query", summary="按关键字查询图书(供借书台使用)")
def query_books(keyword: str = "", limit: int = 20, db: Session = Depends(get_db), _=Depends(get_current_user)):
    query = db.query(Book)
    if keyword:
        like = f"%{keyword}%"
        query = query.filter(
            or_(Book.title.like(like), Book.author.like(like), Book.isbn.like(like))
        )
    books = query.order_by(Book.id.desc()).limit(limit).all()
    return [
        {
            "id": b.id,
            "isbn": b.isbn,
            "title": b.title,
            "author": b.author,
            "available_copies": b.available_copies,
            "total_copies": b.total_copies,
        }
        for b in books
    ]


@router.get("", summary="图书分页列表")
def list_books(
    keyword: str = "",
    category_id: int | None = None,
    status: str = "",
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    query = db.query(Book)
    if keyword:
        like = f"%{keyword}%"
        query = query.filter(
            or_(
                Book.title.like(like),
                Book.author.like(like),
                Book.isbn.like(like),
                Book.publisher.like(like),
            )
        )
    if category_id is not None:
        query = query.filter(Book.category_id == category_id)
    if status == "在馆可借":
        query = query.filter(Book.available_copies > 0)
    elif status == "全部借出":
        query = query.filter(Book.available_copies == 0)

    total = query.count()
    books = (
        query.order_by(Book.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "items": [BookOut.model_validate(b) for b in books],
        "total": total,
    }


@router.post("", response_model=BookOut, summary="新增图书")
def create_book(payload: BookCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    exists = db.query(Book).filter(Book.isbn == payload.isbn).first()
    if exists:
        raise HTTPException(status_code=400, detail=f"ISBN {payload.isbn} 已存在")
    book = Book(
        isbn=payload.isbn,
        title=payload.title,
        author=payload.author,
        publisher=payload.publisher,
        category_id=payload.category_id,
        location=payload.location,
        total_copies=payload.total_copies,
        available_copies=payload.total_copies,
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


@router.put("/{book_id}", response_model=BookOut, summary="更新图书")
def update_book(
    book_id: int, payload: BookUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)
):
    book = db.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="图书不存在")
    exists = db.query(Book).filter(Book.isbn == payload.isbn, Book.id != book_id).first()
    if exists:
        raise HTTPException(status_code=400, detail=f"ISBN {payload.isbn} 已被其他图书使用")

    diff = payload.total_copies - book.total_copies
    book.isbn = payload.isbn
    book.title = payload.title
    book.author = payload.author
    book.publisher = payload.publisher
    book.category_id = payload.category_id
    book.location = payload.location
    book.total_copies = payload.total_copies
    book.available_copies = max(0, book.available_copies + diff)
    db.commit()
    db.refresh(book)
    return book


@router.delete("/{book_id}", summary="删除图书")
def delete_book(book_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    book = db.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="图书不存在")
    if book.available_copies < book.total_copies:
        raise HTTPException(status_code=400, detail="该图书存在未归还的借阅记录, 无法删除")
    db.delete(book)
    db.commit()
    return {"message": "删除成功"}
