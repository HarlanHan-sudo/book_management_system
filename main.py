from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table, or_
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session
import math
import os

# ==================== 数据库配置 ====================
DATABASE_URL = "sqlite:///./library.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==================== 数据模型 ====================
# 多对多关联表：图书与作者
book_author_table = Table(
    'book_author', Base.metadata,
    Column('book_id', Integer, ForeignKey('books.id', ondelete="CASCADE"), primary_key=True),
    Column('author_id', Integer, ForeignKey('authors.id', ondelete="CASCADE"), primary_key=True)
)


class Publisher(Base):
    __tablename__ = "publishers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    books = relationship("Book", back_populates="publisher", cascade="all, delete-orphan")


class Author(Base):
    __tablename__ = "authors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    books = relationship("Book", secondary=book_author_table, back_populates="authors")


class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    publisher_id = Column(Integer, ForeignKey("publishers.id"))

    publisher = relationship("Publisher", back_populates="books")
    authors = relationship("Author", secondary=book_author_table, back_populates="books")


# 创建表
Base.metadata.create_all(bind=engine)

# ==================== FastAPI 初始化 ====================
app = FastAPI(title="图书管理系统")
templates = Jinja2Templates(directory="templates")


# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 根路由重定向到图书页
@app.get("/", response_class=RedirectResponse)
async def read_root():
    return RedirectResponse(url="/books")


# ==================== 通用分页助手 ====================
def get_pagination(query, page: int, per_page: int = 5):
    total = query.count()
    total_pages = math.ceil(total / per_page) if total > 0 else 1
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, total, total_pages


# ==================== 出版社路由 ====================
@app.get("/publishers", response_class=HTMLResponse)
async def list_publishers(request: Request, q: str = "", page: int = 1, db: Session = Depends(get_db)):
    query = db.query(Publisher)
    if q:
        query = query.filter(Publisher.name.contains(q))
    items, total, total_pages = get_pagination(query, page)
    return templates.TemplateResponse("publishers.html", {"request": request, "items": items, "q": q, "page": page,
                                                          "total_pages": total_pages, "active": "publishers"})


@app.post("/publishers/add")
async def add_publisher(name: str = Form(...), db: Session = Depends(get_db)):
    db.add(Publisher(name=name))
    db.commit()
    return RedirectResponse(url="/publishers", status_code=303)


@app.post("/publishers/edit/{id}")
async def edit_publisher(id: int, name: str = Form(...), db: Session = Depends(get_db)):
    pub = db.query(Publisher).filter(Publisher.id == id).first()
    if pub:
        pub.name = name
        db.commit()
    return RedirectResponse(url="/publishers", status_code=303)


@app.post("/publishers/delete/{id}")
async def delete_publisher(id: int, db: Session = Depends(get_db)):
    pub = db.query(Publisher).filter(Publisher.id == id).first()
    if pub:
        db.delete(pub)
        db.commit()
    return RedirectResponse(url="/publishers", status_code=303)


# ==================== 作者路由 ====================
@app.get("/authors", response_class=HTMLResponse)
async def list_authors(request: Request, q: str = "", page: int = 1, db: Session = Depends(get_db)):
    query = db.query(Author)
    if q:
        query = query.filter(Author.name.contains(q))
    items, total, total_pages = get_pagination(query, page)
    return templates.TemplateResponse("authors.html", {"request": request, "items": items, "q": q, "page": page,
                                                       "total_pages": total_pages, "active": "authors"})


@app.post("/authors/add")
async def add_author(name: str = Form(...), db: Session = Depends(get_db)):
    db.add(Author(name=name))
    db.commit()
    return RedirectResponse(url="/authors", status_code=303)


@app.post("/authors/edit/{id}")
async def edit_author(id: int, name: str = Form(...), db: Session = Depends(get_db)):
    author = db.query(Author).filter(Author.id == id).first()
    if author:
        author.name = name
        db.commit()
    return RedirectResponse(url="/authors", status_code=303)


@app.post("/authors/delete/{id}")
async def delete_author(id: int, db: Session = Depends(get_db)):
    author = db.query(Author).filter(Author.id == id).first()
    if author:
        db.delete(author)
        db.commit()
    return RedirectResponse(url="/authors", status_code=303)


# ==================== 图书路由 ====================
@app.get("/books", response_class=HTMLResponse)
async def list_books(request: Request, q: str = "", page: int = 1, db: Session = Depends(get_db)):
    query = db.query(Book)
    if q:
        query = query.filter(Book.name.contains(q))

    items, total, total_pages = get_pagination(query, page)
    all_publishers = db.query(Publisher).all()
    all_authors = db.query(Author).all()

    return templates.TemplateResponse("books.html", {
        "request": request, "items": items, "q": q, "page": page,
        "total_pages": total_pages, "active": "books",
        "publishers": all_publishers, "authors": all_authors
    })


@app.post("/books/add")
async def add_book(request: Request, name: str = Form(...), publisher_id: int = Form(...),
                   db: Session = Depends(get_db)):
    form_data = await request.form()
    author_ids = form_data.getlist("author_ids")  # 获取多选作者

    new_book = Book(name=name, publisher_id=publisher_id)
    if author_ids:
        authors = db.query(Author).filter(Author.id.in_([int(aid) for aid in author_ids])).all()
        new_book.authors = authors

    db.add(new_book)
    db.commit()
    return RedirectResponse(url="/books", status_code=303)


@app.post("/books/edit/{id}")
async def edit_book(request: Request, id: int, name: str = Form(...), publisher_id: int = Form(...),
                    db: Session = Depends(get_db)):
    form_data = await request.form()
    author_ids = form_data.getlist("author_ids")

    book = db.query(Book).filter(Book.id == id).first()
    if book:
        book.name = name
        book.publisher_id = publisher_id
        book.authors = []  # 先清空，再重新赋值
        if author_ids:
            authors = db.query(Author).filter(Author.id.in_([int(aid) for aid in author_ids])).all()
            book.authors = authors
        db.commit()
    return RedirectResponse(url="/books", status_code=303)


@app.post("/books/delete/{id}")
async def delete_book(id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == id).first()
    if book:
        db.delete(book)
        db.commit()
    return RedirectResponse(url="/books", status_code=303)