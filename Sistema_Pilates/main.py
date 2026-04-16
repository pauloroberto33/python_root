from pathlib import Path
from datetime import datetime
import sqlite3

from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "pilates_studio.db"

app = FastAPI(title="Sistema Pilates Studio Web")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def setup_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            data_nascimento TEXT,
            cpf TEXT UNIQUE,
            telefone TEXT,
            email TEXT UNIQUE,
            data_cadastro TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS avaliacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            data_avaliacao TEXT NOT NULL,
            postura_observacoes TEXT,
            forca_flexibilidade TEXT,
            objetivos TEXT,
            plano_aula_sugerido TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS planos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_plano TEXT NOT NULL,
            valor REAL NOT NULL,
            duracao_meses INTEGER,
            descricao TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pagamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            plano_id INTEGER,
            data_pagamento TEXT NOT NULL,
            valor_pago REAL NOT NULL,
            metodo_pagamento TEXT,
            observacoes TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id),
            FOREIGN KEY (plano_id) REFERENCES planos(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS despesas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            data_despesa TEXT NOT NULL,
            categoria TEXT
        )
    ''')

    conn.commit()
    conn.close()
    seed_database()


def seed_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT OR IGNORE INTO planos (id, nome_plano, valor, duracao_meses, descricao) VALUES (?, ?, ?, ?, ?)",
                   (1, 'Mensal - 4 Aulas / Mês', 290.00, 1, 'Plano básico ideal para rotinas leves.'))
    cursor.execute("INSERT OR IGNORE INTO planos (id, nome_plano, valor, duracao_meses, descricao) VALUES (?, ?, ?, ?, ?)",
                   (2, 'Trimestral - 8 Aulas / Mês', 720.00, 3, 'Plano ideal para clientes com objetivos de fortalecimento.'))
    cursor.execute("INSERT OR IGNORE INTO planos (id, nome_plano, valor, duracao_meses, descricao) VALUES (?, ?, ?, ?, ?)",
                   (3, 'Semestral - 12 Aulas / Mês', 1380.00, 6, 'Plano premium com acompanhamento mensal personalizado.'))

    cursor.execute("INSERT OR IGNORE INTO clientes (id, nome, data_nascimento, cpf, telefone, email, data_cadastro) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (1, 'Ana Beatriz Silva', '1989-05-20', '11122233344', '(11) 98765-4321', 'ana.silva@email.com', '2025-11-01'))
    cursor.execute("INSERT OR IGNORE INTO clientes (id, nome, data_nascimento, cpf, telefone, email, data_cadastro) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (2, 'Bruno Oliveira', '1992-08-14', '22233344455', '(21) 99876-5432', 'bruno.oliveira@email.com', '2025-11-10'))
    cursor.execute("INSERT OR IGNORE INTO clientes (id, nome, data_nascimento, cpf, telefone, email, data_cadastro) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (3, 'Camila Sousa', '1979-01-30', '33344455566', '(31) 99654-3210', 'camila.sousa@email.com', '2025-12-03'))

    cursor.execute("INSERT OR IGNORE INTO avaliacoes (id, cliente_id, data_avaliacao, postura_observacoes, forca_flexibilidade, objetivos, plano_aula_sugerido) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (1, 1, '2025-12-05', 'Alinhamento de ombros e coluna', 'Flexibilidade média, força abaixo da média', 'Melhorar postura e reduzir dores lombares', 'Exercícios de core e alongamento leve'))
    cursor.execute("INSERT OR IGNORE INTO avaliacoes (id, cliente_id, data_avaliacao, postura_observacoes, forca_flexibilidade, objetivos, plano_aula_sugerido) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (2, 2, '2025-12-08', 'Boa postura geral', 'Força e flexibilidade equilibradas', 'Aumentar resistência e mobilidade', 'Sequência de reformer e estabilidade'))

    cursor.execute("INSERT OR IGNORE INTO pagamentos (id, cliente_id, plano_id, data_pagamento, valor_pago, metodo_pagamento, observacoes) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (1, 1, 1, '2025-12-10', 290.00, 'Pix', 'Primeiro pagamento do plano mensal'))
    cursor.execute("INSERT OR IGNORE INTO pagamentos (id, cliente_id, plano_id, data_pagamento, valor_pago, metodo_pagamento, observacoes) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (2, 2, 2, '2025-12-10', 720.00, 'Cartão', 'Entrada do plano trimestral'))
    cursor.execute("INSERT OR IGNORE INTO pagamentos (id, cliente_id, plano_id, data_pagamento, valor_pago, metodo_pagamento, observacoes) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (3, 3, 3, '2025-12-11', 1380.00, 'Transferência', 'Plano semestral com desconto promocional'))

    cursor.execute("INSERT OR IGNORE INTO despesas (id, descricao, valor, data_despesa, categoria) VALUES (?, ?, ?, ?, ?)",
                   (1, 'Aluguel do estúdio', 2200.00, '2025-12-01', 'Aluguel'))
    cursor.execute("INSERT OR IGNORE INTO despesas (id, descricao, valor, data_despesa, categoria) VALUES (?, ?, ?, ?, ?)",
                   (2, 'Pagamento de instrutor', 3200.00, '2025-12-05', 'Salários'))
    cursor.execute("INSERT OR IGNORE INTO despesas (id, descricao, valor, data_despesa, categoria) VALUES (?, ?, ?, ?, ?)",
                   (3, 'Materiais de pilates', 450.00, '2025-12-08', 'Material'))
    cursor.execute("INSERT OR IGNORE INTO despesas (id, descricao, valor, data_despesa, categoria) VALUES (?, ?, ?, ?, ?)",
                   (4, 'Campanha de divulgação', 780.00, '2025-12-09', 'Marketing'))

    conn.commit()
    conn.close()


def fetch_all(query, params=()):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows


def execute_query(query, params=()):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()


def get_summary():
    total_clientes = fetch_all("SELECT COUNT(*) AS total FROM clientes")[0][0]
    total_avaliacoes = fetch_all("SELECT COUNT(*) AS total FROM avaliacoes")[0][0]
    total_pagamentos = fetch_all("SELECT COUNT(*) AS total FROM pagamentos")[0][0]
    total_despesas = fetch_all("SELECT COUNT(*) AS total FROM despesas")[0][0]
    receita = fetch_all("SELECT IFNULL(SUM(valor_pago), 0) AS total FROM pagamentos")[0][0]
    despesas = fetch_all("SELECT IFNULL(SUM(valor), 0) AS total FROM despesas")[0][0]
    saldo = receita - despesas
    return {
        "total_clientes": total_clientes,
        "total_avaliacoes": total_avaliacoes,
        "total_pagamentos": total_pagamentos,
        "total_despesas": total_despesas,
        "receita": receita,
        "despesas": despesas,
        "saldo": saldo,
    }


@app.on_event("startup")
def startup_event():
    setup_database()


@app.get("/")
async def home(request: Request):
    summary = get_summary()
    return templates.TemplateResponse(request, "index.html", {"request": request, **summary})


@app.get("/dashboard")
async def dashboard(request: Request):
    pagamentos = fetch_all("SELECT data_pagamento, valor_pago FROM pagamentos ORDER BY data_pagamento")
    despesas = fetch_all("SELECT data_despesa, valor FROM despesas ORDER BY data_despesa")

    monthly = {}
    for data, valor in pagamentos:
        date_key = datetime.fromisoformat(data).strftime("%Y-%m")
        monthly.setdefault(date_key, {"receita": 0.0, "despesa": 0.0})
        monthly[date_key]["receita"] += valor
    for data, valor in despesas:
        date_key = datetime.fromisoformat(data).strftime("%Y-%m")
        monthly.setdefault(date_key, {"receita": 0.0, "despesa": 0.0})
        monthly[date_key]["despesa"] += valor

    months = sorted(monthly.keys())
    receita = [monthly[month]["receita"] for month in months]
    despesa = [monthly[month]["despesa"] for month in months]
    saldo = [monthly[month]["receita"] - monthly[month]["despesa"] for month in months]

    return templates.TemplateResponse(request, "dashboard.html", {
        "request": request,
        "months": months,
        "receita": receita,
        "despesa": despesa,
        "saldo": saldo,
    })


@app.get("/clientes")
async def clientes(request: Request):
    clientes = fetch_all("SELECT * FROM clientes ORDER BY nome")
    return templates.TemplateResponse(request, "clientes.html", {"request": request, "clientes": clientes})


@app.post("/clientes/novo")
async def criar_cliente(
    nome: str = Form(...),
    data_nascimento: str = Form(""),
    cpf: str = Form(""),
    telefone: str = Form(""),
    email: str = Form(""),
):
    execute_query(
        "INSERT INTO clientes (nome, data_nascimento, cpf, telefone, email, data_cadastro) VALUES (?, ?, ?, ?, ?, ?)",
        (nome, data_nascimento or None, cpf or None, telefone or None, email or None, datetime.now().strftime("%Y-%m-%d")),
    )
    return RedirectResponse(url="/clientes", status_code=303)


@app.get("/avaliacoes")
async def avaliacoes(request: Request):
    avaliacoes = fetch_all(
        "SELECT a.id, a.data_avaliacao, c.nome AS cliente, a.postura_observacoes, a.forca_flexibilidade, a.objetivos, a.plano_aula_sugerido FROM avaliacoes a JOIN clientes c ON a.cliente_id = c.id ORDER BY a.data_avaliacao DESC"
    )
    clientes = fetch_all("SELECT id, nome FROM clientes ORDER BY nome")
    return templates.TemplateResponse(request, "avaliacoes.html", {"request": request, "avaliacoes": avaliacoes, "clientes": clientes})


@app.post("/avaliacoes/novo")
async def criar_avaliacao(
    cliente_id: int = Form(...),
    data_avaliacao: str = Form(""),
    postura_observacoes: str = Form(""),
    forca_flexibilidade: str = Form(""),
    objetivos: str = Form(""),
    plano_aula_sugerido: str = Form(""),
):
    execute_query(
        "INSERT INTO avaliacoes (cliente_id, data_avaliacao, postura_observacoes, forca_flexibilidade, objetivos, plano_aula_sugerido) VALUES (?, ?, ?, ?, ?, ?)",
        (cliente_id, data_avaliacao or datetime.now().strftime("%Y-%m-%d"), postura_observacoes, forca_flexibilidade, objetivos, plano_aula_sugerido),
    )
    return RedirectResponse(url="/avaliacoes", status_code=303)


@app.get("/pagamentos")
async def pagamentos(request: Request):
    pagamentos = fetch_all(
        "SELECT p.id, c.nome AS cliente, pl.nome_plano, p.data_pagamento, p.valor_pago, p.metodo_pagamento, p.observacoes FROM pagamentos p JOIN clientes c ON p.cliente_id = c.id LEFT JOIN planos pl ON p.plano_id = pl.id ORDER BY p.data_pagamento DESC"
    )
    clientes = fetch_all("SELECT id, nome FROM clientes ORDER BY nome")
    planos = fetch_all("SELECT id, nome_plano FROM planos ORDER BY valor")
    return templates.TemplateResponse(request, "pagamentos.html", {"request": request, "pagamentos": pagamentos, "clientes": clientes, "planos": planos})


@app.post("/pagamentos/novo")
async def criar_pagamento(
    cliente_id: int = Form(...),
    plano_id: int = Form(0),
    valor_pago: float = Form(...),
    metodo_pagamento: str = Form(""),
    observacoes: str = Form(""),
):
    execute_query(
        "INSERT INTO pagamentos (cliente_id, plano_id, data_pagamento, valor_pago, metodo_pagamento, observacoes) VALUES (?, ?, ?, ?, ?, ?)",
        (cliente_id, plano_id if plano_id != 0 else None, datetime.now().strftime("%Y-%m-%d"), valor_pago, metodo_pagamento, observacoes),
    )
    return RedirectResponse(url="/pagamentos", status_code=303)


@app.get("/despesas")
async def despesas(request: Request):
    despesas = fetch_all("SELECT * FROM despesas ORDER BY data_despesa DESC")
    return templates.TemplateResponse(request, "despesas.html", {"request": request, "despesas": despesas})


@app.post("/despesas/novo")
async def criar_despesa(
    descricao: str = Form(...),
    valor: float = Form(...),
    data_despesa: str = Form(""),
    categoria: str = Form(""),
):
    execute_query(
        "INSERT INTO despesas (descricao, valor, data_despesa, categoria) VALUES (?, ?, ?, ?)",
        (descricao, valor, data_despesa or datetime.now().strftime("%Y-%m-%d"), categoria),
    )
    return RedirectResponse(url="/despesas", status_code=303)
