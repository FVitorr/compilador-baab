# ---------------------------------------------------
# Tradutor para a linguagem CALC
#
# versao 1a (mar-2024)
# ---------------------------------------------------
from ttoken import TOKEN


class Lexico:
    def __init__(self, arqFonte):
        self.arqFonte = arqFonte
        self.fonte = self.readF()
        self.indiceFimFile = len(self.fonte)
        self.indiceLeitura = 0
        self.tokenLido = None  # (token, lexema, linha, coluna)
        self.linha = 1  # linha atual no fonte
        self.coluna = 0  # coluna atual no fonte
        self.prebuild = '' #<r>

    def readF(self):
        return open(self.arqFonte, "r").read()

    def fimDoArquivo(self):
        return self.indiceLeitura >= self.indiceFimFile
    
    def testarGetchar(self):
        print(' <-----------------> Testando Getchar <-----------------> ')
        while not self.fimDoArquivo():
            print(self.obterChar())

    def obterChar(self):
        if self.fimDoArquivo():
            return '\0'
        car = self.fonte[self.indiceLeitura]
        self.indiceLeitura += 1
        if car == '\n':
            self.linha += 1
            self.coluna = 0
        else:
            self.coluna += 1
        return car
    
    def unGetChar(self, simbolo):
        if simbolo == '\n':
            self.linha -= 1

        if self.indiceLeitura > 0:
            self.indiceLeitura -= 1

        self.coluna -= 1

    def verDados(self):
        print(f'Fonte: {self.fonte}')
        print(f'Indice de Leitura: {self.indiceLeitura}')
        print(f'Indice de Fim do Arquivo: {self.indiceFimFile}')
        print(f'Caracter Lido: {self.tokenLido}')
        print(f'Linha: {self.linha}')
        print(f'Coluna: {self.coluna}')
    

    def estadoErro(self, token, linha, coluna):
        print(f'Erro -> {token} linha: {linha}, coluna: {coluna}')
        exit(1)

    
    def getToken(self):
        estado = 1
        simbolo = self.obterChar()
        lexema = ''
        while simbolo in ['#', ' ', '\t', '\n']: # ignora comentários e espaços
            if simbolo == '#':
                while simbolo != '\n':
                    simbolo = self.obterChar()
            while simbolo in [' ', '\t', '\n']:
                simbolo = self.obterChar()
        # Aqui vai começar a pegar um token...
        lin = self.linha  # onde inicia o token, para msgs
        col = self.coluna  # onde inicia o token, para msgs
        while (True):
            #Inicio Automato
            if estado == 1: 
                if simbolo.isalpha():
                    estado = 2 #Buscar Palavra Reservada
                elif simbolo.isdigit():
                    estado = 3 #Buscar Numeros
                elif simbolo == TOKEN.msg(TOKEN.ASPAS_SIMPLES) or simbolo == TOKEN.msg(TOKEN.ASPAS_DUPLA):
                    estado = 4 #Buscar String
                elif simbolo == "(":
                    return (TOKEN.abrePar, "(", lin, col)
                elif simbolo == ")":
                    return (TOKEN.fechaPar, ")", lin, col)
                elif simbolo == ",":
                    return (TOKEN.virg, ",", lin, col)
                elif simbolo == ";":
                    return (TOKEN.ptoVirg, ";", lin, col)
                elif simbolo == ".":
                    estado = 10
                elif simbolo == "+":
                    return (TOKEN.mais, "-", lin, col)
                elif simbolo == "-":
                    return (TOKEN.menos, "-", lin, col)
                elif simbolo == "*":
                    return (TOKEN.multiplica, "*", lin, col)
                elif simbolo == "/":
                    return (TOKEN.divide, "/", lin, col)
                elif simbolo == "{":
                    return (TOKEN.abreChave, "{", lin, col)
                elif simbolo == "}":
                    return (TOKEN.fechaChave, "}", lin, col)
                elif simbolo == "<":
                    estado = 5  # < ou <=
                elif simbolo == ">":
                    estado = 6  # > ou >=
                elif simbolo == "=":
                    estado = 7  # = ou ==
                elif simbolo == "!":  # !=
                    estado = 8
                elif simbolo == '\0':
                    return (TOKEN.eof, '<eof>', lin, col)
                else:
                    #lexema += simbolo
                    #return (TOKEN.erro, lexema, lin, col)
                    estado = 10
            elif estado == 2:
                if simbolo.isalnum():
                    estado = 2
                else:
                    self.unGetChar(simbolo)
                    token = TOKEN.reservada(lexema)
                    return (token, lexema, lin, col)
            elif estado == 3:
                if simbolo.isdigit():
                    estado = 3
                elif simbolo == '.':
                    estado = 3.1
                elif simbolo.isalpha():
                    #lexema += simbolo
                    #return (TOKEN.erro, lexema, lin, col)
                    estado = 10
                else:
                    self.unGetChar(simbolo)
                    return (TOKEN.num, lexema, lin, col)

            elif estado == 3.1:
                #parte real do numero
                if simbolo.isdigit(): #verifica se apos o . é um numero
                    estado = 3.2
                else:
                    estado = 10
            elif estado == 3.2:
                if simbolo.isdigit():
                    estado = 3.2
                elif simbolo.isalpha():
                    estado = 10
                else:
                    self.unGetChar(simbolo)
                    return (TOKEN.num, lexema, lin, col)
            elif estado == 4: #String
                while True:
                    if simbolo == TOKEN.msg(TOKEN.ASPAS_SIMPLES) or simbolo == TOKEN.msg(TOKEN.ASPAS_DUPLA):
                        lexema += simbolo
                        return (TOKEN.string, lexema, lin, col)
                    elif simbolo in ['\0', '\n', ';']:
                        return (TOKEN.erro, lexema, lin, col)
                    else:
                        lexema += simbolo
                        simbolo = self.obterChar()
            elif estado == 5:
                if simbolo == '=':
                    lexema = lexema + simbolo
                    return (TOKEN.oprel, lexema, lin, col)
                else:
                    self.unGetChar(simbolo)
                    return (TOKEN.oprel, lexema, lin, col)
            elif estado == 6:
                if simbolo == '=':
                    lexema = lexema + simbolo
                    return (TOKEN.oprel, lexema, lin, col)
                else:
                    self.unGetChar(simbolo)
                    return (TOKEN.oprel, lexema, lin, col)
            elif estado == 7:
                if simbolo == '=':
                    lexema += simbolo
                    return (TOKEN.igual, lexema, lin, col)
                else:
                    self.unGetChar(simbolo)
                    return (TOKEN.atrib, lexema, lin, col)
            elif estado == 8:
                if simbolo == '=':
                    lexema += simbolo
                    return (TOKEN.diferente, lexema, lin, col)
                else:  # se o proximo simbolo nao for = , quer dizer que tem um ! solto no código
                    self.unGetChar(simbolo)  # eu volto o "ponteiro" pra posicao que eu encontrei a !
                    #return (TOKEN.erro, lexema, lin, col)
                    estado = 10  # retorno o ! dizendo que ele é um erro
            elif estado == 10:
                while True:
                    lexema += simbolo
                    simbolo = self.obterChar()
                    if simbolo in [' ', '\t', '\n', ';', '\0', ')', '(']:
                        break
                   
                self.unGetChar(simbolo)
                estado = 1
                return (TOKEN.erro, lexema, lin, col)
            else:
                print('BUG!!!')
                
            lexema = lexema + simbolo
            simbolo = self.obterChar()
        
    
    def testaLexico(self):
        self.tokenLido = self.getToken()
        (token, lexema, linha, coluna) = self.tokenLido
        while token != TOKEN.eof or lexema == 'end':
            self.imprimeToken(self.tokenLido)
            self.tokenLido = self.getToken()
            (token, lexema, linha, coluna) = self.tokenLido
    
    def imprimeToken(self, tokenCorrente):
        (token, lexema, linha, coluna) = tokenCorrente
        msg = TOKEN.msg(token)

        # Definindo a largura total desejada para a linha, incluindo os pontos
        largura_total = 50

        # Formata o token e o lexema com um espaço entre eles
        saida_inicial = f'< {TOKEN.msg(token)} ,  "{lexema}" >'

        # Calcula o número de pontos necessário para preencher até a largura total
        num_pontos = largura_total - len(saida_inicial) - len(f'[{linha},{coluna}]')
        pontos = '.' * max(num_pontos, 0)  # Garante que não será negativo

        # Formata a saída final com os colchetes e as coordenadas de linha e coluna
        print(f'{saida_inicial}{pontos} [{linha},{coluna}]')


                
        

if __name__ == "__main__":
    x = Lexico('codigoFonte.txt')
    x.testaLexico()
   # x.verDados()
    