import os
os.environ["QT_API"] = "pyside6" # Força o uso do PySide6

# Configura plataforma Qt para offscreen se não houver display
if not os.environ.get('DISPLAY'):
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'

import sys
# Desativa a integração do GUI do IPython se estiver rodando no VS Code/Jupyter
try:
    from IPython import get_ipython
    shell = get_ipython()
    if shell:
        shell.run_line_magic('gui', 'off')
except:
    pass

from CoolProp.CoolProp import PropsSI

class Node:
    def __init__(self):
        self.p = 0.0; self.t = 0.0; self.m = 0.0; self.h = 0.0
        self.fluid = "Water"

class Component:
    def __init__(self, name):
        self.name = name
        self.inputs = {}
        self.outputs = {}

class HRSG(Component): # Caldeira de Recuperação
    def calculate(self, gas_inlet, water_inlet, p_steam, t_steam):
        # Simplificação do balanço térmico da caldeira
        h_steam = PropsSI('H', 'P', p_steam*1e5, 'T', t_steam+273.15, 'Water')
        self.heat_duty = water_inlet.m * (h_steam - water_inlet.h)
        return h_steam

class Deaerator(Component): # Desaerador
    def solve(self, water_in, steam_ext, p_target):
        # Balanço de Massa e Energia para mistura
        p_pa = p_target * 1e5
        h_sat = PropsSI('H', 'P', p_pa, 'Q', 0, 'Water')
        # m1*h1 + m2*h2 = (m1+m2)*h_sat
        return h_sat

from PySide6.QtWidgets import (QApplication, QMainWindow, QGraphicsScene, 
                             QGraphicsView, QGraphicsItem, QGraphicsRectItem, 
                             QToolBar, QDialog, QFormLayout, QLineEdit, 
                             QPushButton, QGraphicsLineItem)
from PySide6.QtCore import Qt, QPointF, QLineF
from PySide6.QtGui import QPen, QBrush, QColor, QAction

# --- CLASSE DE CONEXÃO COM DADOS ---
class ConnectionLine(QGraphicsLineItem):
    def __init__(self, source, target):
        super().__init__()
        self.source = source
        self.target = target
        self.setPen(QPen(QColor("#38bdf8"), 3))
        self.update_pos()

    def update_pos(self):
        line = QLineF(self.source.scenePos() + QPointF(80, 30), 
                     self.target.scenePos() + QPointF(0, 30))
        self.setLine(line)

# --- COMPONENTE COM LÓGICA DE CÁLCULO ---
class ComponentItem(QGraphicsRectItem):
    def __init__(self, name, x, y, type="turbine"):
        super().__init__(0, 0, 80, 60)
        self.setPos(x, y)
        self.setBrush(QBrush(QColor("#1e293b")))
        self.setPen(QPen(QColor("#38bdf8"), 2))
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable | 
                      QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.name = name
        self.type = type
        print(f"Componente '{name}' criado do tipo '{type}'.")
        
        # Cenários automatizados para teste
        self.scenarios = [
            {"P (bar)": "60.0", "T (°C)": "500.0", "Vazão (kg/h)": "200000", "Eficiência (%)": "85"},
            {"P (bar)": "70.0", "T (°C)": "520.0", "Vazão (kg/h)": "214000", "Eficiência (%)": "88"},
            {"P (bar)": "80.0", "T (°C)": "540.0", "Vazão (kg/h)": "230000", "Eficiência (%)": "90"},
        ]
        
        # Atributos default baseados na sua Ficha Mestre
        self.props = {
            "P (bar)": "66.0",
            "T (°C)": "520.0",
            "Vazão (kg/h)": "214000",
            "Eficiência (%)": "88"
        }
        
        # Para teste em modo offscreen, executar 1 cenário do usuário via terminal
        if not os.environ.get('DISPLAY'):
            print(f"\nDigite os parâmetros para o cenário de '{self.name}':")
            p = input("P (bar): ").strip()
            if not p:
                print("Nenhum parâmetro inserido. Finalizando.")
                sys.exit(0)
            t = input("T (°C): ").strip()
            if not t:
                print("Parâmetro T não inserido. Finalizando.")
                sys.exit(0)
            vazao = input("Vazão (kg/h): ").strip()
            if not vazao:
                print("Parâmetro Vazão não inserido. Finalizando.")
                sys.exit(0)
            eff = input("Eficiência (%): ").strip()
            if not eff:
                print("Parâmetro Eficiência não inserido. Finalizando.")
                sys.exit(0)
            
            self.props = {
                "P (bar)": p,
                "T (°C)": t,
                "Vazão (kg/h)": vazao,
                "Eficiência (%)": eff
            }
            print(f"Parâmetros: {self.props}")
            self.run_local_balance()
            print(f"\nCenário concluído para '{self.name}'. Finalizando programa.")
            sys.exit(0)

    def mouseDoubleClickEvent(self, event):
        dialog = QDialog()
        dialog.setWindowTitle(f"Configurar {self.name}")
        layout = QFormLayout(dialog)
        
        inputs = {}
        for k, v in self.props.items():
            inputs[k] = QLineEdit(v)
            layout.addRow(k, inputs[k])
            
        btn = QPushButton("Salvar e Calcular")
        btn.clicked.connect(lambda: self.apply(inputs, dialog))
        layout.addRow(btn)
        dialog.exec()

    def apply(self, inputs, dialog):
        for k in inputs:
            self.props[k] = inputs[k].text()
        dialog.accept()
        print(f"Propriedades do componente '{self.name}' atualizadas: {self.props}")
        self.run_local_balance()

    def run_local_balance(self):
        print(f"Iniciando cálculo para '{self.name}'.")
        # Exemplo de cálculo de Entalpia usando CoolProp
        try:
            P = float(self.props["P (bar)"]) * 1e5
            T = float(self.props["T (°C)"]) + 273.15
            h = PropsSI('H', 'P', P, 'T', T, 'Water')
            m = float(self.props["Vazão (kg/h)"])
            eff = float(self.props["Eficiência (%)"]) / 100
            
            # Cálculo simplificado de potência (kW) - assumindo turbina
            # Potência = vazão * delta_h * eficiência (simplificado, sem delta_h real)
            power = (m * h * eff) / 3600000  # kW (aproximado)
            
            # Heat rate simplificado (MJ/kWh) - assumindo entrada térmica
            # Heat rate = energia térmica entrada / potência
            # Aqui, assumindo entrada térmica baseada em h
            heat_input = m * h / 3600 / 1000000  # MW térmico (simplificado)
            if power > 0:
                heat_rate = heat_input / (power / 1000)  # MJ/kWh
            else:
                heat_rate = 0
            
            print(f"[{self.name}] Cálculo concluído: Pressão={self.props['P (bar)']} bar, Temperatura={self.props['T (°C)']} °C, Entalpia={h/1000:.2f} kJ/kg")
            print(f"[{self.name}] Potência estimada do ciclo: {power:.2f} kW")
            print(f"[{self.name}] Heat rate estimado: {heat_rate:.2f} MJ/kWh")
        except Exception as e:
            print(f"Erro no cálculo para '{self.name}': {e}")

# --- INTERFACE PRINCIPAL ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        print("Simulador de Balanço Térmico iniciado.")
        self.setWindowTitle("Engine de Balanço Térmico - BTEE40")
        self.resize(1000, 700)

        self.scene = QGraphicsScene(0, 0, 2000, 2000)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(self.view.renderHints().Antialiasing)
        self.setCentralWidget(self.view)

        self.create_toolbar()
        
        # Para teste em modo offscreen, adicionar componente automaticamente
        if not os.environ.get('DISPLAY'):
            self.add_component("Turbina", 100, 100)

    def add_component(self, name, x, y):
        item = ComponentItem(name, x, y)
        self.scene.addItem(item)

    def create_toolbar(self):
        print("Criando toolbar com botões.")
        tb = self.addToolBar("Componentes")
        
        def add_comp(name, x, y):
            item = ComponentItem(name, x, y)
            self.scene.addItem(item)
            print(f"Componente '{name}' adicionado à cena em ({x}, {y}).")

        act_turb = QAction("Add Turbina", self)
        act_turb.triggered.connect(lambda: add_comp("Turbina", 100, 100))
        tb.addAction(act_turb)

        act_calc = QAction("Conectar e Calcular", self)
        act_calc.triggered.connect(self.connect_logic)
        tb.addAction(act_calc)

    def connect_logic(self):
        items = self.scene.selectedItems()
        if len(items) == 2:
            line = ConnectionLine(items[0], items[1])
            self.scene.addItem(line)
            # Aqui inicia o fluxo de dados entre componentes
            print(f"Fluxo estabelecido entre {items[0].name} e {items[1].name}")
        else:
            print("Selecione exatamente 2 componentes para conectar.")

if __name__ == "__main__":
    print("Iniciando aplicação...")
    app = QApplication.instance() or QApplication(sys.argv)
    win = MainWindow()
    if not os.environ.get('DISPLAY'):
        print("\nCálculos concluídos. Finalizando programa.")
        sys.exit(0)
    win.show()
    print("Aplicação pronta. Aguardando interações.")
    sys.exit(app.exec())