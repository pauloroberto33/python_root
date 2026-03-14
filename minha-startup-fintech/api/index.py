from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DadosFinanceiros(BaseModel):
    renda: float
    divida: float

@app.get("/api/healthcheck")
def health():
    return {"status": "IA Financeira Online"}

@app.post("/api/analisar")
def analisar(dados: DadosFinanceiros):
    # Lógica simplificada da IA
    score = (dados.renda / (dados.divida + 1)) * 20
    score = min(score, 1000) # Limita a 1000
    
    status = "APROVADO" if score > 600 else "REVISÃO"
    
    return {
        "score": round(score, 0),
        "recomendacao": status
    }

app.mount("/", StaticFiles(directory="public", html=True), name="static")