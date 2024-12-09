#---------------------------------------------------
# Tradutor para a linguagem CALC
#
# versao 1a (mar-2024)
#---------------------------------------------------
from lexico import Lexico
from sintatico import Sintatico
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


# inicia a traducao
if __name__ == '__main__':
    x = Tradutor('codigoFonte.txt')
    x.inicializa()
    x.traduz()
        
    l = x.sintatico.semantico.tabelaSimbolos

    for j in range(0,len(l)):
        for chave, valor in l[j].items():
            print(f'Escopo: {j} -> "{chave}": "{valor}"')
    #x.sintatico.testaLexico()



