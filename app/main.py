from fastapi import FastAPI, Request, Depends, HTTPException, Form
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette.responses import HTMLResponse
import os

from .db import get_db, init_db
from .models import Student

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# Configuração da URL do banco de dados a partir das variáveis de ambiente
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/mydatabase.db")


@app.on_event("startup")
async def on_startup():
    await init_db()


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/{apelido}", response_class=HTMLResponse)
async def search_student_by_apelido(
    request: Request, apelido: str, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Student).filter_by(apelido=apelido))
    student = result.scalars().first()

    if student:
        return templates.TemplateResponse(
            "history.html",
            {"request": request, "name": student.nome, "history": student.history},
        )
    else:
        return templates.TemplateResponse(
            "not_found.html", {"request": request, "name": apelido}
        )


@app.get("/adm/add_student", response_class=HTMLResponse)
async def add_student_form(request: Request):
    return templates.TemplateResponse("add_student.html", {"request": request})


@app.post("/adm/add_student", response_class=HTMLResponse)
async def add_student(
    request: Request,
    nome: str = Form(...),
    sobrenome: str = Form(...),
    telefone: str = Form(...),
    email: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    apelido = (nome + sobrenome).lower().replace(" ", "")
    history = f"Início do curso."

    student = Student(
        nome=nome,
        sobrenome=sobrenome,
        telefone=telefone,
        email=email,
        apelido=apelido,
        history=history,
    )
    db.add(student)
    try:
        await db.commit()
        return templates.TemplateResponse(
            "add_student_success.html", {"request": request, "name": nome}
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=400, detail="Não foi possível adicionar o aluno."
        )


@app.get("/adm/students", response_class=HTMLResponse)
async def get_students(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Student))
    students = result.scalars().all()
    return templates.TemplateResponse(
        "students.html", {"request": request, "students": students}
    )
