from sklearn import tree

class machineLearning:

    def exe_1(self):

        lisa = 1
        irregular = 0
        maca = 1     
        laranja = 0
        pomar = [[150, lisa], [120, lisa], [170, irregular], [180, irregular], [100, lisa], [200, irregular]]
        resultado = [maca, maca, laranja, laranja, maca, laranja]

        clf = tree.DecisionTreeClassifier()
        clf = clf.fit(pomar, resultado)

        peso = input('Entre com o peso: ')
        superficie = input('Entre com a superficie (lisa=1 | irregular=0): ')
        resultadoUsuario = clf.predict([[peso, superficie]])
        if resultadoUsuario == 1:               
            print('É uma maça')
        else:
            print('É uma laranja')

    def exe_2(self):
        print('Tudo certo')

obj1 = machineLearning()
obj1.exe_1()
obj1.exe_2()