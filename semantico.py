# ---------------------------------------------------
# Tradutor para a linguagem B-A-BA plus
#
# versao 1a (21/nov/2024)
# ---------------------------------------------------
from ttoken import TOKEN

class Semantico:

    def __init__(self, nomeAlvo):
        self.tabelaSimbolos = dict()
        self.alvo = open(nomeAlvo, "wt")
        self.declara('len', (TOKEN.FUNCTION, ((None,True), (TOKEN.INT, False))))
        self.declara('num2str', (TOKEN.FUNCTION, ((TOKEN.FLOAT,False), (TOKEN.STRING, False))))
        self.declara('str2num', (TOKEN.FUNCTION, ((TOKEN.STRING,False), (TOKEN.FLOAT, False))))
        self.declara('trunc', (TOKEN.FUNCTION, ((TOKEN.FLOAT,False), (TOKEN.INT, False))))

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

    def declara(self, nome, tipo):
        """ nome = lexema do ident
            tipo = (base, lista)
            base = int | float | strig | function | None # None para listas genericas
            Se base in [int,float,string]
                lista = boolean # True se o tipo for uma lista da base
            else
                Lista = lista com os tipos dos arguentos, sendo
                o tipo de cada argumento um par (base,lista)
                Retorno = o ultimo tipo da lista sera o tipo do retorno            
        """
        if nome in self.tabelaSimbolos:
            msg = f'A Variavel {nome} ja foi declarada'
            self.erroSemantico(tipo[0], msg)
        else:
            self.tabelaSimbolos[nome] = tipo
    
    def consulta(self, nome):
        if nome in self.tabelaSimbolos:
            return self.tabelaSimbolos[nome]
        else:
            return None