from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ---------- 认证 ----------
class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, description="用户名")
    password: str = Field(..., min_length=1, description="密码")


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    real_name: str
    role: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- 分类 ----------
class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


# ---------- 图书 ----------
class BookCreate(BaseModel):
    isbn: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)
    publisher: str = ""
    category_id: int | None = None
    location: str = ""
    total_copies: int = Field(1, ge=1)


class BookUpdate(BaseModel):
    isbn: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)
    publisher: str = ""
    category_id: int | None = None
    location: str = ""
    total_copies: int = Field(1, ge=1)


class BookOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    isbn: str
    title: str
    author: str
    publisher: str
    category_id: int | None
    category_name: str | None
    location: str
    total_copies: int
    available_copies: int


# ---------- 读者 ----------
class ReaderCreate(BaseModel):
    reader_no: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    gender: str = "其他"
    phone: str = ""
    email: str = ""
    status: str = "正常"


class ReaderUpdate(BaseModel):
    reader_no: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    gender: str = "其他"
    phone: str = ""
    email: str = ""
    status: str = "正常"


class ReaderStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(正常|冻结)$")


class ReaderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reader_no: str
    name: str
    gender: str
    phone: str
    email: str
    status: str


# ---------- 借阅 ----------
class BorrowCreate(BaseModel):
    reader_id: int
    book_id: int
    days: int = Field(30, ge=1, le=365)


class ReturnCreate(BaseModel):
    book_id: int


class RenewCreate(BaseModel):
    record_id: int
    days: int = Field(30, ge=1, le=365)


class BorrowRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reader_id: int
    reader_name: str
    reader_no: str
    book_id: int
    book_title: str
    book_isbn: str
    borrow_date: datetime
    due_date: datetime
    return_date: datetime | None
    status: str
