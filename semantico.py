# ---------------------------------------------------
# Tradutor para a linguagem B-A-BA plus
#
# versao 2a (28/nov/2024)
# ---------------------------------------------------
from ttoken import TOKEN

class Semantico:

    def __init__(self, nomeAlvo):
        self.tabelaSimbolos = list()
        self.tabelaSimbolos = [dict()] + self.tabelaSimbolos
        self.alvo = open(nomeAlvo, "wt")
        self.declara((TOKEN.IDENT,'len',0,0),
                     (TOKEN.FUNCTION, [(None,True), (TOKEN.INT, False)]))
        self.declara((TOKEN.IDENT,'num2str',0,0),
                     (TOKEN.FUNCTION, [(TOKEN.FLOAT,False), (TOKEN.STRING, False)]))
        self.declara((TOKEN.IDENT,'str2num',0,0),
                     (TOKEN.FUNCTION, [(TOKEN.STRING,False), (TOKEN.FLOAT, False)]))
        self.declara((TOKEN.IDENT,'trunc',0,0),
                     (TOKEN.FUNCTION, [(TOKEN.FLOAT,False), (TOKEN.INT, False)]))
        
        



    def finaliza(self):
        self.alvo.close()

    def erroSemantico(self, tokenAtual, msg):
        (token, lexema, linha, coluna) = tokenAtual
        print(f'Erro na linha {linha}, coluna {coluna}:')
        print(f'{msg}')
        raise Exception

    def gera(self, nivel, codigo):
        identacao = ' ' * 3 * nivel
        linha = identacao + codigo
        self.alvo.write(linha)

    def declara(self, tokenAtual:tuple, tipo:tuple):
        #self.declara((TUPLA),(BASE, LISTA))
        #BASE = { TOKEN.INT, TOKEN.FLOAT, TOKEN.STRING, TOKEN.FUNCTION, None }
        #LISTA = { [(Parametros, isLista), (Retorno, isLista)] }
        """ nome = lexema do ident
            tipo = (base, lista)
            base = int | float | strig | function | None # listas genericas
            Se base in [int,float,string]
                lista = boolean # True se o tipo for lista
            else
                Lista = lista com os tipos dos argumentos, mais tipo do retorno
        """
        (token, nome, linha, coluna) = tokenAtual
        if not self.consulta(tokenAtual) is None:
            msg = f'Variavel {nome} redeclarada'
            self.erroSemantico(tokenAtual, msg)
        else:
            escopo = self.tabelaSimbolos[0]
            escopo[nome] = tipo

    def consulta(self, tokenAtual):
        (token, nome, linha, coluna) = tokenAtual
        for escopo in self.tabelaSimbolos:
            if nome in escopo:
                return escopo[nome]
        return None
    
    def existeNoEscopo(self, tokenAtual):
        (token, nome, linha, coluna) = tokenAtual
    
        for escopo in self.tabelaSimbolos:
            if nome in escopo:
                return True
        return False


    def iniciaFuncao(self, tokenAtual):
        self.tabelaSimbolos = [dict()] + self.tabelaSimbolos

    def terminaFuncao(self):
        self.tabelaSimbolos = self.tabelaSimbolos[1:]

