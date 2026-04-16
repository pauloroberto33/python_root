# -*- coding: utf-8 -*-
"""
Created on Mon Jul 14 10:15:16 2025

@author: paulo
"""

import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime, date

# --- 1. Configuração do Banco de Dados SQLite ---
DB_NAME = 'pilates_studio.db'

def setup_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Tabela Clientes
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

    # Tabela Avaliacoes
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

    # Tabela Planos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS planos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_plano TEXT NOT NULL,
            valor REAL NOT NULL,
            duracao_meses INTEGER,
            descricao TEXT
        )
    ''')
    # Inserir alguns planos padrão se não existirem
    cursor.execute("INSERT OR IGNORE INTO planos (id, nome_plano, valor, duracao_meses) VALUES (?, ?, ?, ?)", (1, 'Mensal - 4 Aulas/Mês', 300.00, 1))
    cursor.execute("INSERT OR IGNORE INTO planos (id, nome_plano, valor, duracao_meses) VALUES (?, ?, ?, ?)", (2, 'Trimestral - 8 Aulas/Mês', 750.00, 3))
    cursor.execute("INSERT OR IGNORE INTO planos (id, nome_plano, valor, duracao_meses) VALUES (?, ?, ?, ?)", (3, 'Semestral - 12 Aulas/Mês', 1200.00, 6))


    # Tabela Pagamentos
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

    # Tabela Despesas
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

# --- 2. Funções de Gerenciamento de Clientes ---

def adicionar_cliente():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    print("\n--- Adicionar Novo Cliente ---")
    nome = input("Nome Completo: ")
    data_nascimento = input("Data de Nascimento (YYYY-MM-DD): ")
    cpf = input("CPF (opcional): ")
    telefone = input("Telefone (opcional): ")
    email = input("E-mail (opcional): ")
    data_cadastro = datetime.now().strftime('%Y-%m-%d')

    try:
        cursor.execute("INSERT INTO clientes (nome, data_nascimento, cpf, telefone, email, data_cadastro) VALUES (?, ?, ?, ?, ?, ?)",
                       (nome, data_nascimento, cpf if cpf else None, telefone if telefone else None, email if email else None, data_cadastro))
        conn.commit()
        print(f"Cliente '{nome}' adicionado com sucesso! ID: {cursor.lastrowid}")
    except sqlite3.IntegrityError as e:
        print(f"Erro ao adicionar cliente: {e}. CPF ou E-mail já podem existir.")
    finally:
        conn.close()

def listar_clientes():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, telefone, email FROM clientes ORDER BY nome")
    clientes = cursor.fetchall()
    conn.close()

    print("\n--- Lista de Clientes ---")
    if not clientes:
        print("Nenhum cliente cadastrado.")
        return

    for cli in clientes:
        print(f"ID: {cli[0]}, Nome: {cli[1]}, Tel: {cli[2] or 'N/A'}, Email: {cli[3] or 'N/A'}")
    return clientes # Retorna para uso interno, se necessário

def buscar_cliente_por_id(cliente_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,))
    cliente = cursor.fetchone()
    conn.close()
    return cliente

def atualizar_cliente():
    listar_clientes()
    cliente_id = input("Digite o ID do cliente para atualizar: ")
    cliente = buscar_cliente_por_id(cliente_id)

    if not cliente:
        print("Cliente não encontrado.")
        return

    print(f"\n--- Atualizar Cliente: {cliente[1]} ---")
    print("Deixe em branco para manter o valor atual.")
    nome = input(f"Nome Completo ({cliente[1]}): ") or cliente[1]
    data_nascimento = input(f"Data de Nascimento ({cliente[2]}): ") or cliente[2]
    cpf = input(f"CPF ({cliente[3]}): ") or cliente[3]
    telefone = input(f"Telefone ({cliente[4]}): ") or cliente[4]
    email = input(f"E-mail ({cliente[5]}): ") or cliente[5]

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE clientes SET nome=?, data_nascimento=?, cpf=?, telefone=?, email=? WHERE id=?",
                       (nome, data_nascimento, cpf, telefone, email, cliente_id))
        conn.commit()
        print(f"Cliente '{nome}' atualizado com sucesso!")
    except sqlite3.IntegrityError as e:
        print(f"Erro ao atualizar cliente: {e}. CPF ou E-mail já podem existir.")
    finally:
        conn.close()

def remover_cliente():
    listar_clientes()
    cliente_id = input("Digite o ID do cliente para remover: ")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Cliente ID {cliente_id} removido com sucesso.")
        else:
            print("Cliente não encontrado.")
    except Exception as e:
        print(f"Erro ao remover cliente: {e}")
    finally:
        conn.close()

# --- 3. Funções de Avaliação de Clientes ---

def adicionar_avaliacao():
    listar_clientes()
    cliente_id = input("Digite o ID do cliente para a avaliação: ")
    cliente = buscar_cliente_por_id(cliente_id)

    if not cliente:
        print("Cliente não encontrado.")
        return

    print(f"\n--- Nova Avaliação para {cliente[1]} ---")
    data_avaliacao = input("Data da Avaliação (YYYY-MM-DD, ou deixe em branco para hoje): ") or datetime.now().strftime('%Y-%m-%d')
    postura = input("Observações Posturais: ")
    forca_flex = input("Avaliação de Força e Flexibilidade: ")
    objetivos = input("Objetivos do Cliente: ")
    plano_aula = input("Plano de Aula Sugerido: ")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO avaliacoes (cliente_id, data_avaliacao, postura_observacoes, forca_flexibilidade, objetivos, plano_aula_sugerido) VALUES (?, ?, ?, ?, ?, ?)",
                   (cliente_id, data_avaliacao, postura, forca_flex, objetivos, plano_aula))
    conn.commit()
    conn.close()
    print(f"Avaliação para '{cliente[1]}' adicionada com sucesso!")

def visualizar_avaliacoes_cliente():
    listar_clientes()
    cliente_id = input("Digite o ID do cliente para visualizar as avaliações: ")
    cliente = buscar_cliente_por_id(cliente_id)

    if not cliente:
        print("Cliente não encontrado.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT data_avaliacao, postura_observacoes, forca_flexibilidade, objetivos, plano_aula_sugerido FROM avaliacoes WHERE cliente_id = ? ORDER BY data_avaliacao DESC", (cliente_id,))
    avaliacoes = cursor.fetchall()
    conn.close()

    print(f"\n--- Avaliações de {cliente[1]} ---")
    if not avaliacoes:
        print("Nenhuma avaliação encontrada para este cliente.")
        return

    for i, aval in enumerate(avaliacoes):
        print(f"\n--- Avaliação {i+1} em {aval[0]} ---")
        print(f"Postura: {aval[1]}")
        print(f"Força/Flexibilidade: {aval[2]}")
        print(f"Objetivos: {aval[3]}")
        print(f"Plano de Aula Sugerido: {aval[4]}")

# --- 4. Funções de Finanças ---

def listar_planos():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome_plano, valor, duracao_meses FROM planos ORDER BY valor")
    planos = cursor.fetchall()
    conn.close()

    print("\n--- Planos Disponíveis ---")
    if not planos:
        print("Nenhum plano cadastrado.")
        return None
    for plano in planos:
        print(f"ID: {plano[0]}, Nome: {plano[1]}, Valor: R${plano[2]:.2f}, Duração: {plano[3]} meses")
    return planos

def registrar_pagamento():
    listar_clientes()
    cliente_id = input("Digite o ID do cliente pagador: ")
    cliente = buscar_cliente_por_id(cliente_id)
    if not cliente:
        print("Cliente não encontrado.")
        return

    planos_disponiveis = listar_planos()
    if not planos_disponiveis:
        return

    plano_id = input("Digite o ID do plano pago (ou '0' se não for um plano específico): ")
    valor_pago = float(input("Valor pago (R$): "))
    metodo = input("Método de Pagamento (Cartao/Dinheiro/Pix/Transferencia): ")
    observacoes = input("Observações sobre o pagamento (opcional): ")
    data_pagamento = datetime.now().strftime('%Y-%m-%d')

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO pagamentos (cliente_id, plano_id, data_pagamento, valor_pago, metodo_pagamento, observacoes) VALUES (?, ?, ?, ?, ?, ?)",
                       (cliente_id, plano_id if plano_id != '0' else None, data_pagamento, valor_pago, metodo, observacoes))
        conn.commit()
        print(f"Pagamento de R${valor_pago:.2f} registrado para '{cliente[1]}' com sucesso!")
    except Exception as e:
        print(f"Erro ao registrar pagamento: {e}")
    finally:
        conn.close()

def registrar_despesa():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    print("\n--- Registrar Nova Despesa ---")
    descricao = input("Descrição da Despesa: ")
    valor = float(input("Valor da Despesa (R$): "))
    data_despesa = input("Data da Despesa (YYYY-MM-DD, ou deixe em branco para hoje): ") or datetime.now().strftime('%Y-%m-%d')
    categoria = input("Categoria (Aluguel/Salarios/Material/Marketing/Outros): ")

    try:
        cursor.execute("INSERT INTO despesas (descricao, valor, data_despesa, categoria) VALUES (?, ?, ?, ?)",
                       (descricao, valor, data_despesa, categoria))
        conn.commit()
        print(f"Despesa de R${valor:.2f} ('{descricao}') registrada com sucesso!")
    except Exception as e:
        print(f"Erro ao registrar despesa: {e}")
    finally:
        conn.close()

def visualizar_transacoes_financeiras():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    print("\n--- Transações Financeiras ---")
    print("\n--- Pagamentos ---")
    cursor.execute("SELECT c.nome, p.data_pagamento, p.valor_pago, pl.nome_plano FROM pagamentos p JOIN clientes c ON p.cliente_id = c.id LEFT JOIN planos pl ON p.plano_id = pl.id ORDER BY p.data_pagamento DESC")
    pagamentos = cursor.fetchall()
    if not pagamentos:
        print("Nenhum pagamento registrado.")
    else:
        for pag in pagamentos:
            print(f"Cliente: {pag[0]}, Data: {pag[1]}, Valor: R${pag[2]:.2f}, Plano: {pag[3] or 'N/A'}")

    print("\n--- Despesas ---")
    cursor.execute("SELECT descricao, data_despesa, valor, categoria FROM despesas ORDER BY data_despesa DESC")
    despesas = cursor.fetchall()
    if not despesas:
        print("Nenhuma despesa registrada.")
    else:
        for desp in despesas:
            print(f"Desc: {desp[0]}, Data: {desp[1]}, Valor: R${desp[2]:.2f}, Cat: {desp[3]}")
    conn.close()

# --- 5. Funções de Dashboard ---

def gerar_dashboard_financeiro():
    conn = sqlite3.connect(DB_NAME)
    
    # Carregar dados de pagamentos
    df_pagamentos = pd.read_sql_query("SELECT data_pagamento, valor_pago FROM pagamentos", conn)
    df_pagamentos['data'] = pd.to_datetime(df_pagamentos['data_pagamento'])
    df_pagamentos_mes = df_pagamentos.set_index('data').resample('ME')['valor_pago'].sum().reset_index()
    df_pagamentos_mes.rename(columns={'valor_pago': 'Valor', 'data': 'Mês'}, inplace=True)
    df_pagamentos_mes['Tipo'] = 'Receita'

    # Carregar dados de despesas
    df_despesas = pd.read_sql_query("SELECT data_despesa, valor FROM despesas", conn)
    df_despesas['data'] = pd.to_datetime(df_despesas['data_despesa'])
    df_despesas_mes = df_despesas.set_index('data').resample('ME')['valor'].sum().reset_index()
    df_despesas_mes.rename(columns={'valor': 'Valor', 'data': 'Mês'}, inplace=True)
    df_despesas_mes['Tipo'] = 'Despesa'
    
    conn.close()

    # Combinar dados para o gráfico de fluxo de caixa
    df_fluxo = pd.concat([df_pagamentos_mes, df_despesas_mes])
    df_fluxo['Mês'] = df_fluxo['Mês'].dt.strftime('%Y-%m') # Formato para o eixo x

    if df_fluxo.empty:
        print("\nDados insuficientes para gerar o dashboard financeiro.")
        return

    # Gerar gráfico de barras com Plotly
    fig = px.bar(df_fluxo, x='Mês', y='Valor', color='Tipo',
                 title='Fluxo de Caixa Mensal do Pilates Studio', barmode='group',
                 labels={'Valor': 'Valor (R$)', 'Mês': 'Mês/Ano'},
                 color_discrete_map={'Receita': 'green', 'Despesa': 'red'})
    
    fig.update_layout(xaxis_title="Mês/Ano", yaxis_title="Valor (R$)",
                      hovermode="x unified") # Mostra detalhes ao passar o mouse

    # Salvar o gráfico como um arquivo HTML interativo
    dashboard_file = 'dashboard_financeiro.html'
    fig.write_html(dashboard_file, auto_open=True) # auto_open abre no navegador
    print(f"\nDashboard financeiro gerado e salvo como '{dashboard_file}'. Abrindo no navegador...")

# --- 6. Menu Principal ---

def menu_principal():
    while True:
        print("\n--- Sistema de Gestão Pilates Studio ---")
        print("1. Gerenciar Clientes")
        print("2. Gerenciar Avaliações")
        print("3. Gerenciar Finanças")
        print("4. Gerar Dashboard Financeiro")
        print("5. Sair")

        escolha = input("Escolha uma opção: ")

        if escolha == '1':
            menu_clientes()
        elif escolha == '2':
            menu_avaliacoes()
        elif escolha == '3':
            menu_financas()
        elif escolha == '4':
            gerar_dashboard_financeiro()
        elif escolha == '5':
            print("Saindo do sistema. Até mais!")
            break
        else:
            print("Opção inválida. Tente novamente.")

def menu_clientes():
    while True:
        print("\n--- Gerenciar Clientes ---")
        print("1. Adicionar Cliente")
        print("2. Listar Clientes")
        print("3. Atualizar Cliente")
        print("4. Remover Cliente")
        print("5. Voltar ao Menu Principal")
        
        escolha = input("Escolha uma opção: ")
        if escolha == '1':
            adicionar_cliente()
        elif escolha == '2':
            listar_clientes()
        elif escolha == '3':
            atualizar_cliente()
        elif escolha == '4':
            remover_cliente()
        elif escolha == '5':
            break
        else:
            print("Opção inválida. Tente novamente.")

def menu_avaliacoes():
    while True:
        print("\n--- Gerenciar Avaliações ---")
        print("1. Adicionar Avaliação")
        print("2. Visualizar Avaliações de Cliente")
        print("3. Voltar ao Menu Principal")
        
        escolha = input("Escolha uma opção: ")
        if escolha == '1':
            adicionar_avaliacao()
        elif escolha == '2':
            visualizar_avaliacoes_cliente()
        elif escolha == '3':
            break
        else:
            print("Opção inválida. Tente novamente.")

def menu_financas():
    while True:
        print("\n--- Gerenciar Finanças ---")
        print("1. Listar Planos")
        print("2. Registrar Pagamento")
        print("3. Registrar Despesa")
        print("4. Visualizar Transações Financeiras")
        print("5. Voltar ao Menu Principal")
        
        escolha = input("Escolha uma opção: ")
        if escolha == '1':
            listar_planos()
        elif escolha == '2':
            registrar_pagamento()
        elif escolha == '3':
            registrar_despesa()
        elif escolha == '4':
            visualizar_transacoes_financeiras()
        elif escolha == '5':
            break
        else:
            print("Opção inválida. Tente novamente.")

# --- Execução Principal ---
if __name__ == "__main__":
    setup_database()
    menu_principal()