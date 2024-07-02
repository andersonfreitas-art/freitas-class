from fastapi import FastAPI, Request, Depends, HTTPException, Form
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette.responses import HTMLResponse

from .db import get_db, init_db
from .models import Student

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")


@app.on_event("startup")
async def on_startup():
    await init_db()


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/{name}", response_class=HTMLResponse)
async def search_name(request: Request, name: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Student).filter_by(name=name))
    student = result.scalars().first()

    if student:
        return templates.TemplateResponse(
            "history.html",
            {"request": request, "name": student.name, "history": student.history},
        )
    else:
        return templates.TemplateResponse(
            "not_found.html", {"request": request, "name": name}
        )


@app.get("/adm/add_student", response_class=HTMLResponse)
async def add_student_form(request: Request):
    return templates.TemplateResponse("add_student.html", {"request": request})


@app.post("/adm/add_student", response_class=HTMLResponse)
async def add_student(
    request: Request,
    name: str = Form(...),
    history: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    student = Student(name=name, history=history)
    db.add(student)
    try:
        await db.commit()
        return templates.TemplateResponse(
            "add_student_success.html", {"request": request, "name": name}
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Could not add student")


@app.get("/adm/students", response_class=HTMLResponse)
async def get_students(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Student))
    students = result.scalars().all()
    return templates.TemplateResponse(
        "students.html", {"request": request, "students": students}
    )
