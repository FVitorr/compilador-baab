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
    
    def getErroPos(self, line, col):
        try:
            lines = open(self.arqFonte, "r").readlines()
            if line < 1 or line > len(lines):
                raise ValueError("Número da linha está fora do intervalo do arquivo.")
            line_ = lines[line - 1].strip()

            if col == -1: col = len(line_)
            r_line = " " * (col - 1) + "^"
            return line_ + "\n" + r_line
        except ValueError as ve:
            raise ve
        except Exception as e:
            raise Exception(f"Erro ao obter a linha: {e}")

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
        if simbolo == '\0':
            return
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
                    return (TOKEN.ABREPAR, "(", lin, col)
                elif simbolo == ")":
                    return (TOKEN.FECHAPAR, ")", lin, col)
                elif simbolo == ",":
                    return (TOKEN.VIRG, ",", lin, col)
                elif simbolo == ";":
                    return (TOKEN.PTOVIRG, ";", lin, col)
                elif simbolo == ".":
                    estado = 10
                elif simbolo == "+":
                    return (TOKEN.MAIS, "-", lin, col)
                elif simbolo == "-":
                    estado = 9
                elif simbolo == "*":
                    return (TOKEN.MULTIPLICA, "*", lin, col)
                elif simbolo == "/":
                    return (TOKEN.DIVIDE, "/", lin, col)
                elif simbolo == "{":
                    return (TOKEN.ABRECHAVE, "{", lin, col)
                elif simbolo == "}":
                    return (TOKEN.FECHACHAVE, "}", lin, col)
                elif simbolo == "[":
                    return (TOKEN.ABRECONCH, "[", lin, col)
                elif simbolo == "]":
                    return (TOKEN.FECHACONCH, "]", lin, col)
                elif simbolo == "<":
                    estado = 5  # < ou <=
                elif simbolo == ">":
                    estado = 6  # > ou >=
                elif simbolo == "=":
                    estado = 7  # = ou ==
                elif simbolo == "!":  # !=
                    estado = 8
                elif simbolo == '\0':
                    return (TOKEN.EOF, '<eof>', lin, col)
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
                    return (TOKEN.intVal, lexema, lin, col)

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
                    return (TOKEN.floatVal, lexema, lin, col)
            elif estado == 4: #String
                while True:
                    if simbolo == '"':
                        lexema += simbolo
                        return TOKEN.strVal, lexema, lin, col
                    elif simbolo in ['\n', '\0']:
                        return TOKEN.ERRO, lexema, lin, col
                    elif simbolo == '\\':
                        lexema += simbolo
                        simbolo = self.obterChar()
                        if simbolo in ['\n', '\0']:
                            return TOKEN.ERRO, lexema, lin, col

                    lexema += simbolo
                    simbolo = self.obterChar()
            elif estado == 5:
                if simbolo == '=':
                    lexema = lexema + simbolo
                    return (TOKEN.OPREL, lexema, lin, col)
                else:
                    self.unGetChar(simbolo)
                    return (TOKEN.OPREL, lexema, lin, col)
            elif estado == 6:
                if simbolo == '=':
                    lexema = lexema + simbolo
                    return (TOKEN.OPREL, lexema, lin, col)
                else:
                    self.unGetChar(simbolo)
                    return (TOKEN.OPREL, lexema, lin, col)
            elif estado == 7:
                if simbolo == '=':
                    lexema += simbolo
                    #IGUAL ==
                    return (TOKEN.OPREL, lexema, lin, col)
                else:
                    self.unGetChar(simbolo)
                    return (TOKEN.ATRIB, lexema, lin, col)
            elif estado == 8:
                if simbolo == '=':
                    lexema += simbolo
                    return (TOKEN.OPREL, lexema, lin, col)
                else:  # se o proximo simbolo nao for = , quer dizer que tem um ! solto no código
                    self.unGetChar(simbolo)  # eu volto o "ponteiro" pra posicao que eu encontrei a !
                    #return (TOKEN.erro, lexema, lin, col)
                    estado = 10  # retorno o ! dizendo que ele é um erro
            elif estado == 9:
                if simbolo == '>':
                    lexema += simbolo
                    return (TOKEN.SETA, lexema, lin, col)
                else:
                    self.unGetChar(simbolo)
                    return (TOKEN.MENOS, lexema, lin, col)
                
            elif estado == 10:
                while True:
                    lexema += simbolo
                    simbolo = self.obterChar()
                    if simbolo in [' ', '\t', '\n', ';', '\0', ')', '(']:
                        break
                   
                self.unGetChar(simbolo)
                estado = 1
                return (TOKEN.ERRO, lexema, lin, col)
            else:
                print('BUG!!!')
                
            lexema = lexema + simbolo
            simbolo = self.obterChar()
    
    @staticmethod
    def imprimir_token(token_corrente):
        (token, lexema, linha, coluna) = token_corrente
        msg = TOKEN.msg(token)
        print(f'(tk = {msg}, lex = "{lexema}", lin = {linha}, col = {coluna})')
        
    
    def testaLexico(self):
        self.tokenLido = self.getToken()
        (token, lexema, linha, coluna) = self.tokenLido
        while token != TOKEN.EOF :
            self.imprimir_token(self.tokenLido)
            self.tokenLido = self.getToken()
            (token, lexema, linha, coluna) = self.tokenLido
    


                
        

if __name__ == "__main__":
    x = Lexico('codigoFonte.txt')
    x.testaLexico()
   # x.verDados()
    
