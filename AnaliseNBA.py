#Analise estatistica de dados da NBA
import numpy as np

class EstatitiscaNBA:
    def __init__(self):
        self.nome = input('Digite o nome do jogador: ')
        self.pontos = float(input('Digite a média de pontos: '))
        self.rebotes = float(input('Digite a média de rebotes: '))
        self.assistencias = float(input('Digite a média de assistências: '))
        self.tocos = float(input('Digite a média de tocos: '))
        self.roubos = float(input('Digite a média de roubos: '))

    def Dados(self):
        #def Dados(self, pontos, rebotes, assistencias, tocos, roubos):
        curva_pontos = 0.02*self.pontos
        curva_rebotes = (0.000006*np.power(self.rebotes,3)) - (0.003*np.power(self.rebotes,2)) + (0.0605*self.rebotes) + 0.0032
        curva_assistencia = (0.000006*np.power(self.assistencias,3)) - (0.003*np.power(self.assistencias,2)) + (0.0605*self.assistencias) + 0.0032
        curva_tocos = 0.036*self.tocos + 0.03
        curva_roubos = 0.036*self.roubos + 0.03
        self.rendimento_final = round((curva_pontos + curva_rebotes + curva_assistencia + curva_tocos + curva_roubos)/5,3)
        self.rendimento_final = self.rendimento_final + 0.15

    def DefineCurva(self):
        a = (0.7-0)/(35-0)
        y = a*self.pontos
        print('Curva de pontos: ' + str(y))

    def Resultado(self):
        print("------------------Resultado------------------------------------")
        print('Nome do jogador: ' + self.nome)
        print('Rendimento: ' + str(self.rendimento_final))

obj1 = EstatitiscaNBA()
obj1.Dados()
obj1.Resultado()
obj1.DefineCurva()
