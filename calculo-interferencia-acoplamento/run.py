import numpy as np

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
        """
        Calcula a interferência diametral necessária (mm).
        FS: Fator de Segurança contra deslizamento.
        mu: Coeficiente de atrito.
        """
        L = comprimento_cubo_mm / 1000
        
        # 1. Torque de operação
        torque = self.potencia / self.omega
        
        # 2. Pressão mínima necessária para transmitir o torque (Dinâmica)
        # T = P * (2 * pi * r * L) * r * mu
        p_min_dinamica = (torque * FS) / (2 * np.pi * (self.r_contato**2) * L * mu)
        
        # 3. Perda de interferência devido à rotação (Efeito Centrífugo)
        # O cubo expande para fora, o eixo (sólido) expande menos.
        # u_perda = u_cubo - u_eixo
        u_cubo = (self.rho * self.omega**2 * self.r_contato / (8 * self.E)) * \
                 ((3 + self.nu) * (self.r_contato**2 + self.re**2) + (1 - self.nu) * self.r_contato**2 + (1 + self.nu) * self.re**2)
        
        u_eixo = (self.rho * self.omega**2 * self.r_contato**3 * (1 - self.nu)) / (4 * self.E)
        u_perda_radial = u_cubo - u_eixo
        
        # 4. Cálculo da interferência radial necessária
        # Delta_total = Delta_pressao + Delta_centrifugo
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

# --- Exemplo de Uso ---
if __name__ == "__main__":
    print("=== Dimensionamento de Interferência de Acoplamento ===")
    d_eixo = float(input("Diâmetro nominal do eixo (mm): "))
    d_externo = float(input("Diâmetro externo do cubo (mm): "))
    pot = float(input("Potência da Turbina (kW): "))
    rotacao = float(input("Rotação de Operação (RPM): "))
    largura = float(input("Comprimento de contato do cubo (mm): "))

    calc = DimensionamentoAcoplamento(d_eixo, d_externo, pot, rotacao)
    res = calc.calcular_interferencia_projeto(largura)

    print("-" * 40)
    print(f"Torque Nominal: {res['torque']:.2f} Nm")
    print(f"Pressão de Contato Requerida (com FS={res['FS']:.1f}): {res['pressao_min_mpa']:.2f} MPa")
    print(f"Perda por Efeito Centrífugo (no diâmetro): {res['expansao_centrifuga_mm']:.4f} mm")
    print(f"\n>>> INTERFERÊNCIA DIAMETRAL DE PROJETO: {res['interf_projeto_mm']:.3f} mm")
    print("-" * 40)