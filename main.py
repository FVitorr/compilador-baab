#---------------------------------------------------
# Tradutor para a linguagem CALC
#
# versao 1a (mar-2024)
#---------------------------------------------------
from lexico import Lexico
from sintatico import Sintatico

class Tradutor:

    def __init__(self, nomeArq):
        self.nomeArq = nomeArq
        self.arq = None
        self.lexico = None

    def inicializa(self):
        self.lexico = Lexico(self.nomeArq)
        self.sintatico = Sintatico(self.lexico)

    def traduz(self):
        self.sintatico.traduz()


# inicia a traducao
if __name__ == '__main__':
    x = Tradutor('codigoFonte.txt')
    x.inicializa()
    print(x.sintatico.semantico.tabelaSimbolos)
    x.traduz()
    #x.sintatico.testaLexico()



