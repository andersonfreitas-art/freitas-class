from fastapi import FastAPI, Request, Depends, HTTPException, Form
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette.responses import HTMLResponse
import unidecode

from .db import get_db, SessionLocal
from .models import Student, Base, engine

# Criar as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")


@app.on_event("startup")
async def on_startup():
    pass


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
    # Remover acentos e converter para minúsculas
    nome_sem_acentos = unidecode.unidecode(nome).lower()
    sobrenome_sem_acentos = unidecode.unidecode(sobrenome).lower()

    # Concatenar nome e sobrenome sem espaços para gerar o apelido
    apelido = nome_sem_acentos + sobrenome_sem_acentos

    # Criar novo aluno no banco de dados
    student = Student(
        nome=nome,
        sobrenome=sobrenome,
        telefone=telefone,
        email=email,
        apelido=apelido,
        history=f"Nome: {nome} Sobrenome: {sobrenome} Telefone: {telefone} Email: {email}",
    )
    db.add(student)
    try:
        await db.commit()
        return templates.TemplateResponse(
            "add_student_success.html", {"request": request, "name": nome}
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
