from fastapi import FastAPI
from pydantic import BaseModel
from CoolProp.CoolProp import PropsSI

app = FastAPI()

class DadosTurbina(BaseModel):
    p_entrada: float  # bar
    t_entrada: float  # °C
    vazao: float      # kg/h
    p_escape: float   # bar
    eficiencia: float # %

@app.post("/api/calcular")
def calcular_turbina(d: DadosTurbina):
    # Conversão de unidades para o SI (Pascal, Kelvin, kg/s)
    P1 = d.p_entrada * 1e5
    T1 = d.t_entrada + 273.15
    P2 = d.p_escape * 1e5
    m_dot = d.vazao / 3600
    eta = d.eficiencia / 100

    # 1. Entalpia e Entropia na Entrada
    h1 = PropsSI('H', 'P', P1, 'T', T1, 'Water')
    s1 = PropsSI('S', 'P', P1, 'T', T1, 'Water')

    # 2. Entalpia Isentrópica na Saída (Ideal)
    h2_s = PropsSI('H', 'P', P2, 'S', s1, 'Water')

    # 3. Queda de Entalpia Real considerando Eficiência
    dh_real = (h1 - h2_s) * eta
    
    # 4. Potência (P = m_dot * delta_h) em kW
    potencia_kw = m_dot * dh_real / 1000

    return {
        "entalpia_entrada_kJkg": round(h1/1000, 2),
        "potencia_estimada_kW": round(potencia_kw, 2),
        "potencia_estimada_MW": round(potencia_kw/1000, 3)
    }