#---------------------------------------------------
# Tradutor para a linguagem b-a-ba
#
# versao 1a (mar-2024)
#---------------------------------------------------
from lexico import TOKEN, Lexico
import inspect

class Sintatico:

    def __init__(self, lexico):
        self.lexico = lexico
        self.nomeAlvo = 'alvo.out'

    def traduz(self):
        self.tokenLido = self.lexico.getToken()
        try:
            self.prog()
            print('Traduzido com sucesso.')
        except Exception as e:
            pass
        

    def consome(self, tokenAtual):
        (token, lexema, linha, coluna) = self.tokenLido
        
        if tokenAtual == token:
            self.tokenLido = self.lexico.getToken()
        else:
            #for frame in inspect.stack():
                #print(frame.function)
            msgTokenLido = TOKEN.msg(token)
            msgTokenAtual = TOKEN.msg(tokenAtual)
            print(f'Erro na linha {linha}, coluna {coluna}:')
            if token == TOKEN.erro:
                msg = lexema
            else:
                msg = msgTokenLido
            print(f'Era esperado {msgTokenAtual} mas veio {msg}')
            raise Exception

    def testaLexico(self):
        self.tokenLido = self.lexico.getToken()
        (token, lexema, linha, coluna) = self.tokenLido
        while token != TOKEN.eof:
            self.lexico.imprimeToken(self.tokenLido)
            self.tokenLido = self.lexico.getToken()
            (token, lexema, linha, coluna) = self.tokenLido

#-----------------------------Usar a Gramatica-----------------------------------------
    def prog(self):
        # <prog> -> begin <calculo> end
        self.consome(TOKEN.BEGIN)
        self.calculo()
        self.consome(TOKEN.END)
        self.consome(TOKEN.eof)
    
    def calculo(self):
        #<calculo> -> LAMBDA | <com><calculo>
        if self.tokenLido[0] in [TOKEN.ident, TOKEN.IF, TOKEN.WHILE, TOKEN.READ, TOKEN.write]:
            self.com()
            self.calculo()
        else:
            pass

    def com(self):
        # <com> -> <atrib>|<if>|<leitura>|<impressao>|<bloco>
        if self.tokenLido[0] == TOKEN.ident:
            self.atrib()
        elif self.tokenLido[0] == TOKEN.IF:
            self.se()
        elif self.tokenLido[0] == TOKEN.READ:
            self.leitura()
        elif self.tokenLido[0] == TOKEN.write:
            self.impressao()
        elif self.tokenLido[0] == TOKEN.abreChave:
            self.bloco()
        else:
            pass

    def atrib(self):
        #<atrib> -> ident = <exp> ;
        self.consome(TOKEN.ident)
        self.consome(TOKEN.atrib)
        self.exp()
        self.consome(TOKEN.ptoVirg)

    def se(self): #CONFERIR
        # <if> -> if ( <exp> ) then <com> <else_opc>
        if self.tokenLido[0] == TOKEN.IF:
            self.consome(TOKEN.IF)
            self.consome(TOKEN.abrePar)
            self.exp()
            self.consome(TOKEN.fechaPar)
            self.consome(TOKEN.then)
            self.calculo()
            self.elseopc()
        
    def elseopc(self):
        # <else_opc> -> LAMBDA | else <com> 
        if self.tokenLido[0] == TOKEN.ELSE:
            self.consome(TOKEN.ELSE)
            self.com()
        else:
            pass
    
    def leitura(self):
        # <leitura> -> read ( string , ident ) ;
        if self.tokenLido[0] == TOKEN.READ:
            self.consome(TOKEN.READ)
            self.consome(TOKEN.abrePar)
            self.consome(TOKEN.string)
            self.consome(TOKEN.virg)
            self.consome(TOKEN.ident)
            self.consome(TOKEN.fechaPar)
            self.consome(TOKEN.ptoVirg)

    def impressao(self):
        # <impressao> -> write ( <lista_out> ) ;
        if self.tokenLido[0] == TOKEN.write:
            self.consome(TOKEN.write)
            self.consome(TOKEN.abrePar)
            self.lista_out()
            self.consome(TOKEN.fechaPar)
            self.consome(TOKEN.ptoVirg)

    def lista_out(self):
        # <lista_outs> -> <out> <restoLista_outs>
        self.out()
        self.restoLista_outs()
    
    def restoLista_outs(self):
        #<restoLista_outs> -> LAMBDA | , <out> <restoLista_outs>
        if self.tokenLido[0] == TOKEN.virg:
            self.consome(TOKEN.virg)
            self.out()
            self.restoLista_outs()
        else:
            pass

    def out(self):
        #<out> -> num | ident | string
        if self.tokenLido[0] == TOKEN.num:
            self.consome(TOKEN.num)
        elif self.tokenLido[0] == TOKEN.ident:
            self.consome(TOKEN.ident)
        else:
            self.consome(TOKEN.string)
    
    def bloco(self):
        # <bloco> -> { <calculo> }
        self.consome(TOKEN.abreChave)
        self.calculo()
        self.consome(TOKEN.fechaChave)

    def exp(self):
        # <exp> -> <disj>
        self.disj()

    def disj(self):
        #<disj> -> <conj> <restoDisj>
        self.conj()
        self.restoDisj()
    
    def restoDisj(self):
        #<restoDisj> -> LAMBDA | or <conj> <restoDisj>
        while self.tokenLido[0] == TOKEN.OR:
            self.consome(TOKEN.OR)
            self.conj()
            #restoDisj() -> capturado pelo loop
        pass #LAMBDA
    
    def conj(self):
        #<conj> -> <nao> <restoConj>
        self.nao()
        self.restoConj()

    def restoConj(self):
        #<restoConj> -> LAMBDA | and <nao> <restoConj>
        while self.tokenLido[0] == TOKEN.AND:
            self.consome(TOKEN.AND)
            self.nao()
            #restoConj() -> capturado pelo loop
        pass

    def nao(self):
        # <nao> -> not <nao> | <rel>
        if self.tokenLido[0] == TOKEN.NOT:
            self.consome(TOKEN.NOT)
            self.nao()
        else:
            self.rel()
        
    def rel(self):
        # <rel> -> <soma> <restoRel>
        self.soma()
        self.restoRel()
        
    
    def restoRel(self):
        # <restoRel> -> LAMBDA | oprel <soma>
        if self.tokenLido[0] in [TOKEN.oprel]:
            self.consome(TOKEN.oprel)
            self.soma()
        else:
            pass #LAMBDA

    def soma(self):
        # <soma> -> <mult> <restoSoma>
        self.mult()
        self.restosoma()
    
    def restosoma(self):
        # <restoSoma> -> LAMBDA | + <mult> <restoSoma> | - <mult> <restoSoma>
        while self.tokenLido[0] in [TOKEN.mais, TOKEN.menos]:
            if self.tokenLido[0] == TOKEN.mais:
                self.consome(TOKEN.mais)
                self.mult()
            elif self.tokenLido[0] == TOKEN.menos:
                self.consome(TOKEN.menos)
                self.mult()
        pass #LAMBDA
        
    def mult(self):
        # <mult> -> <uno> <restoMult>
        self.uno()
        self.restomult()
    
    def restomult(self):
        # <restoMult> -> LAMBDA | / <uno> <restoMult> | * <uno> <restoMult>
        while self.tokenLido[0] in [TOKEN.multiplica, TOKEN.divide]:
            if self.tokenLido[0] == TOKEN.multiplica:
                self.consome(TOKEN.multiplica)
                self.uno()
            else:
                self.consome(TOKEN.divide)
                self.uno()
        pass #LAMBDA

    def uno(self):
            # <uno> -> + <uno> | - <uno> | <folha>
            while self.tokenLido[0] in [TOKEN.mais, TOKEN.menos]:
                if self.tokenLido[0] == TOKEN.mais:
                    self.consome(TOKEN.mais)
                else:
                    self.consome(TOKEN.menos)
            self.folha()

    def folha(self):
        # <folha> -> num | ident | ( <exp> )
        if self.tokenLido[0] == TOKEN.num:
            self.consome(TOKEN.num)
        elif self.tokenLido[0] == TOKEN.ident:
            self.consome(TOKEN.ident)
        else:
            self.consome(TOKEN.abrePar)
            self.exp()
            self.consome(TOKEN.fechaPar)

    
    
if __name__ == '__main__':
    x = Lexico('codigoFonte.txt')
    a = Sintatico(x)
    a.traduz()
