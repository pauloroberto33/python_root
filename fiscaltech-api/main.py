import os
import datetime
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- Configuração da Base de Dados (Pronto para Nuvem) ---
# Em produção, a plataforma web (ex: Vercel) injetará a URL do PostgreSQL aqui.
# Localmente, ele continuará criando o arquivo SQLite.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fiscal_tech.db")

# Ajuste para compatibilidade de threads se for SQLite
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Modelos ---
class TransactionRecord(Base):
    __tablename__ = "audit_ledger"
    id = Column(Integer, primary_key=True, index=True)
    tx_id = Column(String, unique=True)
    gross_value = Column(Float)
    cbs_value = Column(Float)
    ibs_value = Column(Float)
    net_value = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(bind=engine)

# --- Instância da Aplicação ---
app = FastAPI(title="FiscalTech API 2026", version="1.0.0")

# --- Motor de Cálculo ---
def calculate_split(value: float):
    cbs = round(value * 0.009, 2)
    ibs = round(value * 0.001, 2)
    net_value = round(value - cbs - ibs, 2)
    return cbs, ibs, net_value

# --- Endpoints ---
@app.get("/")
def home():
    return {"status": "FiscalTech API Online", "sistema": "IVA Dual 2026"}

@app.post("/v2/process-payment")
def process_payment(tx_id: str, amount: float):
    db = SessionLocal()
    try:
        cbs, ibs, net = calculate_split(amount)
        record = TransactionRecord(
            tx_id=tx_id, gross_value=amount,
            cbs_value=cbs, ibs_value=ibs, net_value=net
        )
        db.add(record)
        db.commit()
        return {
            "status": "success",
            "split": {"fisco": cbs + ibs, "vendedor": net},
            "audit_trail_id": record.id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Erro ao processar transação")
    finally:
        db.close()