from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Obtém a URL do banco de dados a partir das variáveis de ambiente
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/mydatabase.db")

# Configuração do SQLAlchemy para o banco de dados SQLite
engine = create_async_engine(
    DATABASE_URL, echo=True, future=True, connect_args={"check_same_thread": False}
)

# Cria a fábrica de sessões assíncronas
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

# Classe base para a definição de modelos
Base = declarative_base()


# Definição do modelo de Student (exemplo)
class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    sobrenome = Column(String, index=True)
    telefone = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    apelido = Column(String, unique=True, index=True)
    history = Column(String)


# Função para inicializar o banco de dados
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


# Função para obter uma sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
