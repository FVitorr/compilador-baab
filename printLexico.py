from ttoken import TOKEN
from lexico import Lexico

class PrintLexico(Lexico):
    def testaLexico(self):
        self.tokenLido = self.getToken()
        (token, lexema, linha, coluna) = self.tokenLido
        while token != TOKEN.EOF or lexema == 'end':
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

a = PrintLexico('codigoFonte.txt')
a.testaLexico()