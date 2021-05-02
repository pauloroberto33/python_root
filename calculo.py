import numpy as np
import matplotlib.pylab as plt


class Calculos:

    def __init__(self):
        print('####################Programa de calculos#######################\n')

    def Definicao(self):
        print("Gerar o polinônimo através de informações de x e y: 1\n"
              "Calcular ressultado através da informação do polinônimo: 2\n")
        self.opcao = input("Opção de escolha: ")
        print('\n')
        if self.opcao == '1':
            calculo1.CalculoPolininomo()
        if self.opcao == '2':
            calculo1.CalculoResulatdo()

    def CalculoPolininomo(self):
        dx = list(input("Digite valores de x (x1 x2 ... xn): ").split(" "))
        dy = list(input("Digite valores de y (y1 y2 ... yn): ").split(" "))

        px = np.array(dx, dtype=float)
        py = np.array(dy, dtype=float)
        pz = np.polyfit(px, py, 1)
        print('polinonimo -> x[0] + ... x[n]: ', pz)
        print(' ')
        ppp = len(px)
        for i in range(ppp):
            tx = px[i]
            ty = np.poly1d(pz)
            ty1 = ty(tx)

        plt.plot(px, py, label='x1')
        plt.plot(tx, ty1, '--', label='x2', color='g')
        plt.xlabel('valores de x')
        plt.ylabel('valores de y')
        plt.title('Curva característtica')
        plt.axis('tight')
        plt.legend()
        plt.show()

    def CalculoResulatdo(self):
        polix = list(input("Digite o polinonimo -> x² + x + k: ").split(" "))
        x = float(input("Digite o valor de x: "))
        poli_array = np.array(polix, dtype=float)
        poli_resultado = np.poly1d(poli_array)
        poli_final = poli_resultado(x)
        print('Valor de y: ', poli_final)
        print(' ')

calculo1 = Calculos()
calculo1.Definicao()


##############################################################################
#Calcula o polinonimo através de informação de dados de x e y

""" dx = list(input("Digite valores de x: ").split(" "))
dy = list(input("Digite valores de y: ").split(" "))

px = np.array(dx, dtype=float)
py = np.array(dy, dtype=float)
pz = np.polyfit(px, py, 1)

print(px)
print(py)
print('polinonimo -> x[0] + ... x[n]: ', pz) """

# validação do cálculo do polinonimo
# xx = float(input("Digite valor: "))
# yy = 10*xx + 0.00000011269856*xx
# print(yy)

""" plt.plot(px, py)
plt.xlabel('valores de x')
plt.ylabel('valores de y')
plt.title('Curva característtica')
plt.axis('tight')
plt.show()
 """
##############################################################################
# calcula resultado atráves da informação de um polinonimo

""" polix = list(input("Digite valores de x: ").split(" "))

poli_array = np.array(polix, dtype=float)
print(poli_array)
poli_resultado = np.poly1d(poli_array)
poli_final = poli_resultado(2.0)
print('Valor de y: ', poli_final) """