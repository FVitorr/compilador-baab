from ttoken import TOKEN

class Semantico:
    def __init__(self, nomeAlvo):
        self.tabelaSimbolos = dict()
        self.alvo = open(nomeAlvo, "wt")
        self.declara('len',(TOKEN.FUNCTION, ((None, True), (TOKEN.INT, False))))
        self.declara('num2str',(TOKEN.FUNCTION, ((TOKEN.FLOAT, True), (TOKEN.STRING, False))))
        self.declara('str2num',(TOKEN.FUNCTION, ((TOKEN.STRING, True), (TOKEN.FLOAT, False))))
        self.declara('trunc',(TOKEN.FUNCTION, ((TOKEN.FLOAT, True), (TOKEN.INT, False))))
    
    def finaliza(self):
        self.alvo.close()

    def erroSemantico(self, tokenAtual, msg):
        (token, lexema, linha, coluna) = tokenAtual
        print(f'Erro na linha {linha}, coluna {coluna}:')
        print(f'{msg}')
    
    def gera(self,nivel, codigo):
        identacao = '  ' * 3 * nivel
        linha = f'{identacao}{codigo}\n'
        self.alvo.write(linha)
    
    def declara(self,nome, tipo):
        pass