class Dados:
    def __init__(self):
        print("---------------Dados de controle de senha--------------\n")
        print("Esse programa registra os dados e controla senhas\n")
    
    def DefinicaoAcao(self):
        print("Registro de endereço: 1\n"
              "Alteração de registro: 2\n"
              "Verificar o registro selecionado: 3\n"
              "Mostra todos os dados: 4")
        self.opcao = input("Opção de escolha: ")
        print('\n')
        if self.opcao == '1':
            dados1.ControleDedados()
            dados1.AdicionarDados()
        if self.opcao == '3':
            # dados1.Imprimir()
            dados1.Requesitar()
        if self.opcao == '2':
            dados1.AlterarSenha1()
        if self.opcao == '4':
            dados1.MostarDados()


    def ControleDedados(self):
        self.nome = input("Nome do endereço: ")
        self.senha = input("Senha: ")
        print()

    def Imprimir(self):
        print("-----Dados solcitados-----")
        print(self.nome)
        print(self.senha)

    def AdicionarDados(self):
        arquivo = open('C:/Users/admin\OneDrive/Área de Trabalho/PYTHON/python_root/python_root/DadosDeSenha.txt', 'r+')
        while True:
            linha = arquivo.readline()
            if linha == '' and linha != 'Dados e senhas':
                arquivo.writelines(str(self.nome + ' | ' + self.senha + '\n'))
                break
        arquivo.close()
    
    def MostarDados(self):
        arquivo = open('C:/Users/admin/OneDrive/Área de Trabalho/PYTHON/python_root/python_root/DadosDeSenha.txt', 'r')
        arquivo.readline()
        for linha in arquivo:
            valores = linha.split()
            print('Requerente: ', valores[0], 'Senha: ', valores[2])
        arquivo.close()

    def Requesitar(self):
        self.nome = input("Digite o requerente: ")
        arquivo = open('C:/Users/admin/OneDrive/Área de Trabalho/PYTHON/python_root/python_root/DadosDeSenha.txt', 'r')
        for linha in arquivo:
            requesito = linha.split()
            requerente = requesito[0]
            senha = requesito[2]
            if self.nome == requesito[0]:
                print('Senha: ', senha)
        arquivo.close()

    def AlterarSenha1(self):
        nome = input("Digite o requerente: ")
        nova_senha = input("Digite a nova senha: ")
        arquivo = open('C:/Users/admin/OneDrive/Área de Trabalho/PYTHON/python_root/python_root/DadosDeSenha.txt', 'r+')
        lista_dados = []
        for linhas in arquivo:
            x = linhas.split()
            y = x[0]
            z = x[2]
            if nome == x[0]:
                linhas = linhas.replace(y + ' | ' + z, nome + ' | ' + nova_senha)
            lista_dados.append(linhas)
        arquivo.seek(0)
        arquivo.writelines(lista_dados)
        arquivo.close()

dados1 = Dados()
dados1.DefinicaoAcao()
    