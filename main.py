#---------------------------------------------------
# Tradutor para a linguagem CALC
#
# versao 1a (mar-2024)
#---------------------------------------------------
from lexico import Lexico
from sintatico import Sintatico
import sys
import json

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


''' if len(sys.argv) != 2:
            print("Uso correto: python tradutor.py <arquivo>")
        else:
            arquivo = sys.argv[1]
            x = Tradutor(arquivo)
            x.inicializa()
            x.traduz()
'''

# inicia a traducao
if __name__ == '__main__':
    x = Tradutor('codigoFonte.txt')
    x.inicializa()
    x.traduz()
    #x.lexico.testaLexico()