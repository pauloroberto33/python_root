from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from CoolProp.CoolProp import PropsSI
import os
from typing import Optional

app = FastAPI()

class DadosTurbina(BaseModel):
    p_entrada: float  # bar
    t_entrada: float  # °C
    vazao: float      # kg/h
    p_escape: float   # bar
    eficiencia: float # %
    p_extracao: Optional[float] = None  # bar, opcional
    vazao_extracao: Optional[float] = None  # kg/h, opcional

@app.post("/api/calcular")
def calcular_turbina(d: DadosTurbina):
    try:
        # Conversão de unidades para o SI (Pascal, Kelvin, kg/s)
        P1 = d.p_entrada * 1e5
        T1 = d.t_entrada + 273.15
        P2 = d.p_escape * 1e5
        m_dot_total = d.vazao / 3600
        eta = d.eficiencia / 100
        P_extr = d.p_extracao * 1e5 if d.p_extracao is not None else None
        m_dot_extr = d.vazao_extracao / 3600 if d.vazao_extracao is not None else 0

        # 1. Entalpia e Entropia na Entrada
        h1 = PropsSI('H', 'P', P1, 'T', T1, 'Water')
        s1 = PropsSI('S', 'P', P1, 'T', T1, 'Water')

        if d.p_extracao is not None and d.vazao_extracao is not None and d.vazao_extracao > 0:
            # Turbina com extração
            h_extr_s = PropsSI('H', 'P', P_extr, 'S', s1, 'Water')
            dh_extr_real = (h1 - h_extr_s) * eta
            h_extr_real = h1 - dh_extr_real

            h2_s = PropsSI('H', 'P', P2, 'S', s1, 'Water')
            dh2_real = (h1 - h2_s) * eta
            h2_real = h1 - dh2_real

            m_dot_saida = m_dot_total - m_dot_extr
            potencia_kw = m_dot_saida * (h1 - h2_real) / 1000 + m_dot_extr * (h1 - h_extr_real) / 1000
        else:
            # Turbina simples
            h2_s = PropsSI('H', 'P', P2, 'S', s1, 'Water')
            dh_real = (h1 - h2_s) * eta
            potencia_kw = m_dot_total * dh_real / 1000

        return {
            "entalpia_entrada_kJkg": round(h1/1000, 2),
            "potencia_estimada_kW": round(potencia_kw, 2),
            "potencia_estimada_MW": round(potencia_kw/1000, 3)
        }
    except Exception as e:
        return {"erro": f"Erro no cálculo: {str(e)}"}

@app.get("/", response_class=HTMLResponse)
def get_index():
    # Caminho para o index.html
    html_path = os.path.join(os.path.dirname(__file__), 'public', 'index.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        return f.read()

if __name__ == "__main__":
    import subprocess
    import webbrowser
    import time

    # Comando para iniciar o servidor
    command = [
        'uvicorn',
        'run:app',
        '--host', '0.0.0.0',
        '--port', '8000'
    ]

    # Iniciar o servidor em background
    process = subprocess.Popen(command, cwd=os.path.dirname(__file__))

    # Aguardar um pouco para o servidor iniciar
    time.sleep(2)

    # Abrir o navegador
    webbrowser.open('http://localhost:8000')

    # Manter o script rodando
    try:
        process.wait()
    except KeyboardInterrupt:
        process.terminate()