from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import numpy as np
import os

app = FastAPI()

class DimensionamentoAcoplamento:
    def __init__(self, d_eixo_mm, d_externo_cubo_mm, potencia_kw, rpm, material_e=205e9, material_nu=0.3, material_rho=7850):
        self.r_contato = (d_eixo_mm / 2) / 1000  # m
        self.re = (d_externo_cubo_mm / 2) / 1000  # m
        self.potencia = potencia_kw * 1000        # W
        self.omega = rpm * (2 * np.pi / 60)       # rad/s
        self.E = material_e
        self.nu = material_nu
        self.rho = material_rho

    def calcular_interferencia_projeto(self, comprimento_cubo_mm, FS=1.2, mu=0.15):
        L = comprimento_cubo_mm / 1000
        torque = self.potencia / self.omega
        p_min_dinamica = (torque * FS) / (2 * np.pi * (self.r_contato**2) * L * mu)
        
        u_cubo = (self.rho * self.omega**2 * self.r_contato / (8 * self.E)) * \
                 ((3 + self.nu) * (self.r_contato**2 + self.re**2) + (1 - self.nu) * self.r_contato**2 + (1 + self.nu) * self.re**2)
        
        u_eixo = (self.rho * self.omega**2 * self.r_contato**3 * (1 - self.nu)) / (4 * self.E)
        u_perda_radial = u_cubo - u_eixo
        
        K_cubo = (1 / self.E) * ((self.re**2 + self.r_contato**2) / (self.re**2 - self.r_contato**2) + self.nu)
        K_eixo = (1 / self.E) * (1 - self.nu)
        
        delta_r_pressao = p_min_dinamica * self.r_contato * (K_cubo + K_eixo)
        delta_r_total = delta_r_pressao + u_perda_radial
        interferencia_diametral_mm = (delta_r_total * 2) * 1000
        
        return {
            "torque": torque,
            "FS": FS,
            "pressao_min_mpa": p_min_dinamica / 1e6,
            "expansao_centrifuga_mm": (u_perda_radial * 2) * 1000,
            "interf_projeto_mm": interferencia_diametral_mm
        }

class DadosAcoplamento(BaseModel):
    d_eixo_mm: float
    d_externo_cubo_mm: float
    potencia_kw: float
    rpm: float
    comprimento_cubo_mm: float
    fator_seguranca: float = 1.2
    coef_atrito: float = 0.15

@app.get("/", response_class=HTMLResponse)
def get_index():
    html_path = os.path.join(os.path.dirname(__file__), '..', 'public', 'index.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        return f.read()

@app.post("/api/calcular")
def calcular_acoplamento(dados: DadosAcoplamento):
    try:
        calc = DimensionamentoAcoplamento(
            dados.d_eixo_mm,
            dados.d_externo_cubo_mm,
            dados.potencia_kw,
            dados.rpm
        )
        
        resultado = calc.calcular_interferencia_projeto(
            dados.comprimento_cubo_mm,
            FS=dados.fator_seguranca,
            mu=dados.coef_atrito
        )
        
        return {
            "torque_nm": round(resultado['torque'], 2),
            "pressao_min_mpa": round(resultado['pressao_min_mpa'], 3),
            "expansao_centrifuga_mm": round(resultado['expansao_centrifuga_mm'], 4),
            "interferencia_projeto_mm": round(resultado['interf_projeto_mm'], 3),
            "fator_seguranca": resultado['FS']
        }
    except Exception as e:
        return {"erro": f"Erro no cálculo: {str(e)}"}