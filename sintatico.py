#---------------------------------------------------
# Tradutor para a linguagem b-a-ba
#
# versao 1a (mar-2024)
#---------------------------------------------------
from lexico import TOKEN, Lexico
from semantico import Semantico
import inspect

class Sintatico:

    def __init__(self, lexico):
        self.lexico = lexico
        self.nomeAlvo = 'alvo.out'
        self.semantico = Semantico(self.nomeAlvo)

    def traduz(self):
        print('Iniciando a tradução...')
        self.tokenLido = self.lexico.getToken()
        self.prog()
        print('Traduzido com sucesso.')


    def consome(self, tokenAtual):
        (token, lexema, linha, coluna) = self.tokenLido
        
        tokenAnterior = self.tokenLido
        if tokenAtual == token:
            self.tokenLido = self.lexico.getToken()
            return tokenAnterior
        else:
            #for frame in inspect.stack():
                #print(frame.function)
            msgTokenLido = TOKEN.msg(token)
            msgTokenAtual = TOKEN.msg(tokenAtual)
            if msgTokenAtual == ";":
                print(self.lexico.getErroPos(linha - 1,  -1))
            else:
                print(self.lexico.getErroPos(linha,coluna))

            print(f'\033[91m[!] Erro na linha {linha}, coluna {coluna}:\033[0m')
            if token == TOKEN.ERRO:
                msg = lexema
            else:
                msg = msgTokenLido
            print(f'\033[91m\tEra esperado {msgTokenAtual} mas veio {msg} \033[0m')
            raise Exception

    def testaLexico(self):
        self.tokenLido = self.lexico.getToken()
        (token, lexema, linha, coluna) = self.tokenLido
        while token != TOKEN.EOF:
            self.lexico.imprimeToken(self.tokenLido)
            self.tokenLido = self.lexico.getToken()
            (token, lexema, linha, coluna) = self.tokenLido

#-----------------------------Usar a Gramatica-----------------------------------------
    def prog(self):
        # <prog> -> <funcao> <RestoFuncoes>
        self.funcao()
        self.restoFuncoes()
    
    def restoFuncoes(self):
        #<RestoFuncoes> -> <funcao> <RestoFuncoes> | LAMBDA
        if self.tokenLido[0] == TOKEN.FUNCTION:
            self.funcao()
            self.restoFuncoes()
        else:
            pass #LAMBDA
    '''def funcao(self): 
     # <funcao> -> function ident ( <params> ) <tipoResultado> <corpo>
     self.consome(TOKEN.FUNCTION)
     salvaIdent = tokenLido
     self.consome(TOKEN.ident)
     self.consome(TOKEN.AbrePar)
     salvaArgs = params( )
     self.consome(TOKEN.FechaPar)
     salvaRetorno = tipoResultado( )
     corpo( )
      info = salvaArgs + salvaRetorno
     self.semantico.declara(salvaIdent[1], (TOKEN.FUNCTION, info)'''
    def funcao(self):
        #<funcao> -> function ident ( <params> ) <tipoResultado> <corpo>
        self.consome(TOKEN.FUNCTION)
        IDENT = self.consome(TOKEN.IDENT)
        self.consome(TOKEN.ABREPAR)
        argumentos = self.params()
        self.consome(TOKEN.FECHAPAR)
        RETURN = self.tipoResultado()
        self.semantico.declara(IDENT, (TOKEN.FUNCTION, argumentos + RETURN))
        self.semantico.iniciaFuncao(self.tokenLido)
        for p in argumentos:
            (tt, (tipo,info)) = p
            self.semantico.declara(tt, (tipo, info))
        self.corpo()
        self.semantico.terminaFuncao()
    
    def tipoResultado(self):
        #<tipoResultado> -> LAMBDA | -> <tipo>
        if self.tokenLido[0] == TOKEN.SETA:
            self.consome(TOKEN.SETA)
            tipo = self.tipo()
        else:
            tipo = None    
        token = (0,0,0,0)
        return [(token,tipo)]
    
    def params(self):
        #<params> -> <tipo> ident <restoParams> | LAMBDA
        if self.tokenLido[0] in [TOKEN.INT, TOKEN.FLOAT, TOKEN.STRING]:
            tipo = self.tipo()
            IDENT = self.consome(TOKEN.IDENT)
            resto = self.restoParams()
            return [(IDENT,tipo)] + resto
        else:
            return []

    def restoParams(self):
        #<restoParams> -> LAMBDA | , <tipo> ident <restoParams>
        if self.tokenLido[0] == TOKEN.VIRG:
            self.consome(TOKEN.VIRG)
            tipo = self.tipo()
            IDENT = self.consome(TOKEN.IDENT)
            resto = self.restoParams()
            return [(IDENT,tipo)] + resto
        else:
            return []

    def corpo(self):
        #<corpo> -> begin <declaracoes> <calculo> end
        self.consome(TOKEN.BEGIN)
        self.declaracoes()
        self.calculo()
        self.consome(TOKEN.END)
        #self.consome(TOKEN.EOF)
    
    def declaracoes(self):
        #<declaracoes> -> <declara> <declaracoes> | LAMBDA
        if self.tokenLido[0] in [TOKEN.INT, TOKEN.FLOAT, TOKEN.STRING]:
            self.declara()
            self.declaracoes()
        else:
            pass #LAMBDA
    
    def declara(self):
        #<declara> -> <tipo> <idents> ;
        self.tipo()
        self.idents()
        self.consome(TOKEN.PTOVIRG)

    def idents(self):
        #<idents> -> ident <restoIdents> 
        self.consome(TOKEN.IDENT)
        self.restoIdents()
    
    def restoIdents(self):
        #<restoIdents> -> , ident <restoIdents> | LAMBDA 
        if self.tokenLido[0] == TOKEN.VIRG:
            self.consome(TOKEN.VIRG)
            self.consome(TOKEN.IDENT)
            self.restoIdents()
        else:
            pass
    
    def tipo(self):
        #<tipo> -> string <opcLista> | int <opcLista> | float <opcLista> 
        if self.tokenLido[0] == TOKEN.FLOAT:
            FLOAT = self.consome(TOKEN.FLOAT)
            opcLista = self.opcLista()
            tipo = TOKEN.FLOAT
        elif self.tokenLido[0] == TOKEN.INT:
            INT = self.consome(TOKEN.INT)
            opcLista = self.opcLista() 
            tipo = TOKEN.INT
        else:
            STRING = self.consome(TOKEN.STRING)
            opcLista = self.opcLista()
            tipo = TOKEN.STRING 
        
        return tipo, opcLista

    def opcLista(self):
        #<opcLista> -> [ list ] | LAMBDA
        if self.tokenLido[0] == TOKEN.ABRECONCH:
            self.consome(TOKEN.ABRECONCH)
            self.consome(TOKEN.LIST)
            self.consome(TOKEN.FECHACONCH)

            return True
        else:
            return False

    def calculo(self):
        #<calculo> -> LAMBDA | <com><calculo>
        if self.tokenLido[0] in [TOKEN.IDENT, TOKEN.IF, TOKEN.WHILE, TOKEN.READ, 
                                 TOKEN.WRITE, TOKEN.ABRECHAVE, TOKEN.FOR, TOKEN.RETURN]:
            self.com()
            self.calculo()
        else:
            pass

    def com(self):
        #<com> -> <atrib> | <if> | <leitura> | <escrita> | <bloco> | <for> | <while> | <retorna> | <call> 
        if self.tokenLido[0] == TOKEN.IDENT:
            self.atrib()
        elif self.tokenLido[0] == TOKEN.IF:
            self.se()
        elif self.tokenLido[0] == TOKEN.READ:
            self.leitura()
        elif self.tokenLido[0] == TOKEN.WRITE:
            self.escrita()
        elif self.tokenLido[0] == TOKEN.ABRECHAVE:
            self.bloco()
        elif self.tokenLido[0] == TOKEN.FOR:
            self.FOR()
        elif self.tokenLido[0] == TOKEN.WHILE:
            self.WHILE()
        else:
            self.retorna()
    
    
    def retorna(self):
        #<retorna> -> return <expOpc> ;
        self.consome(TOKEN.RETURN)
        self.expOpc()
        self.consome(TOKEN.PTOVIRG)
    
    def expOpc(self):
        #<expOpc> -> LAMBDA | <exp>
        if self.tokenLido[0] in [TOKEN.intVal, TOKEN.IDENT, TOKEN.ABREPAR, 
                                 TOKEN.floatVal, TOKEN.NOT, TOKEN.MAIS, TOKEN.MENOS, TOKEN.strVal]:
            self.exp()
        else:
            pass
    
    def WHILE(self):
        #<while> -> while ( <exp> ) <com>
        self.consome(TOKEN.WHILE)
        self.consome(TOKEN.ABREPAR)
        self.exp()
        self.consome(TOKEN.FECHAPAR)
        self.com()
    
    def FOR(self):
        #<for> -> for ident in <range> do <com>
        self.consome(TOKEN.FOR)
        self.consome(TOKEN.IDENT)
        self.consome(TOKEN.IN)
        self.range()
        self.consome(TOKEN.DO)
        self.com()
    
    def range(self):
        #<range> -> <lista> | range ( <exp> , <exp> <opcRange> )
        if self.tokenLido[0] == TOKEN.RANGE:
            self.consome(TOKEN.RANGE)
            self.consome(TOKEN.ABREPAR)
            self.exp()
            self.consome(TOKEN.VIRG)
            self.exp()
            self.opcRange()
            self.consome(TOKEN.FECHAPAR)
        else:
            self.lista()
    
    def lista(self):
        #<lista> -> ident <opcIndice> | [ <elemLista> ]
        if self.tokenLido[0] == TOKEN.IDENT:
            self.consome(TOKEN.IDENT)
            self.opcIndice()
        else:
            self.consome(TOKEN.ABRECONCH)
            self.elemLista()
            self.consome(TOKEN.FECHACONCH)
    
    def elemLista(self):
        #<elemLista> -> LAMBDA | <elem> <restoElemLista>
        if self.tokenLido[0] in [TOKEN.intVal, TOKEN.IDENT, TOKEN.strVal, TOKEN.floatVal]:
            self.elem()
            self.restoElemLista()
        else:
            pass
    
    def restoElemLista(self):
        #<restoElemLista> -> LAMBDA | , <elem> <restoElemLista>
        if self.tokenLido[0] == TOKEN.VIRG:
            self.consome(TOKEN.VIRG)
            self.elem()
            self.restoElemLista()
        else:
            pass

    def elem(self):
        #<elem> -> intVal | floatVal | strVal | ident 
        if self.tokenLido[0] == TOKEN.intVal:
            self.consome(TOKEN.intVal)
        elif self.tokenLido[0] == TOKEN.floatVal:
            self.consome(TOKEN.floatVal)
        elif self.tokenLido[0] == TOKEN.strVal:
            self.consome(TOKEN.strVal)
        else:
            self.consome(TOKEN.IDENT)

    
    def opcRange(self):
        #<opcRange> -> , <exp> | LAMBDA
        if self.tokenLido[0] == TOKEN.VIRG:
            self.consome(TOKEN.VIRG)
            self.exp()
        else:
            pass
    
    def atrib(self):
        #<atrib> -> ident <opcIndice> = <exp> ;
        self.consome(TOKEN.IDENT)
        self.opcIndice()
        self.consome(TOKEN.ATRIB)
        self.exp()
        self.consome(TOKEN.PTOVIRG)

    def se(self): #CONFERIR
        # <if> -> if ( <exp> ) then <com> <else_opc>
        if self.tokenLido[0] == TOKEN.IF:
            self.consome(TOKEN.IF)
            self.consome(TOKEN.ABREPAR)
            self.exp()
            self.consome(TOKEN.FECHAPAR)
            self.consome(TOKEN.THEN)
            self.com()
            self.elseopc()
        
    def elseopc(self):
        # <else_opc> -> LAMBDA | else <com> 
        if self.tokenLido[0] == TOKEN.ELSE:
            self.consome(TOKEN.ELSE)
            self.com()
        else:
            pass
    
    def leitura(self):
        # <leitura> -> read ( strVal , ident ) ;
        if self.tokenLido[0] == TOKEN.READ:
            self.consome(TOKEN.READ)
            self.consome(TOKEN.ABREPAR)
            self.consome(TOKEN.strVal)
            self.consome(TOKEN.VIRG)
            self.consome(TOKEN.IDENT)
            self.consome(TOKEN.FECHAPAR)
            self.consome(TOKEN.PTOVIRG)

    def escrita(self):
        #<escrita> -> write ( <lista_out> ) ;
        if self.tokenLido[0] == TOKEN.WRITE:
            self.consome(TOKEN.WRITE)
            self.consome(TOKEN.ABREPAR)
            self.lista_outs()
            self.consome(TOKEN.FECHAPAR)
            self.consome(TOKEN.PTOVIRG)

    def lista_outs(self):
        # <lista_outs> -> <out> <restoLista_outs>
        self.out()
        self.restoLista_outs()
    
    def restoLista_outs(self):
        #<restoLista_outs> -> LAMBDA | , <out> <restoLista_outs>
        if self.tokenLido[0] == TOKEN.VIRG:
            self.consome(TOKEN.VIRG)
            self.out()
            self.restoLista_outs()
        else:
            pass

    def out(self):
        #<out> -> <folha>
        self.folha()
    
    def bloco(self):
        # <bloco> -> { <calculo> }
        self.consome(TOKEN.ABRECHAVE)
        self.calculo()
        self.consome(TOKEN.FECHACHAVE)

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
        #<restoRel> -> LAMBDA | oprel <soma>
        if self.tokenLido[0] == TOKEN.OPREL:
            self.consome(TOKEN.OPREL)
            self.soma()
        else:
            pass #LAMBDA

    def soma(self):
        # <soma> -> <mult> <restoSoma>
        self.mult()
        self.restosoma()
    
    def restosoma(self):
        # <restoSoma> -> LAMBDA | + <mult> <restoSoma> | - <mult> <restoSoma>
        while self.tokenLido[0] in [TOKEN.MAIS, TOKEN.MENOS]:
            if self.tokenLido[0] == TOKEN.MAIS:
                self.consome(TOKEN.MAIS)
                self.mult()
            elif self.tokenLido[0] == TOKEN.MENOS:
                self.consome(TOKEN.MENOS)
                self.mult()
        pass #LAMBDA
        
    def mult(self):
        # <mult> -> <uno> <restoMult>
        self.uno()
        self.restomult()
    
    def restomult(self):
        # <restoMult> -> LAMBDA | / <uno> <restoMult> | * <uno> <restoMult> | % <uno> <restoMult>
        while self.tokenLido[0] in [TOKEN.MULTIPLICA, TOKEN.DIVIDE, TOKEN.MOD]:
            if self.tokenLido[0] == TOKEN.MULTIPLICA:
                self.consome(TOKEN.MULTIPLICA)
                self.uno()
            elif self.tokenLido[0] == TOKEN.DIVIDE:
                self.consome(TOKEN.DIVIDE)
                self.uno()
            else:
                self.consome(TOKEN.MOD)
                self.uno()
        pass #LAMBDA

    def uno(self):
        # <uno> -> + <uno> | - <uno> | <folha>
        while self.tokenLido[0] in [TOKEN.MAIS, TOKEN.MENOS]:
            if self.tokenLido[0] == TOKEN.MAIS:
                self.consome(TOKEN.MAIS)
            else:
                self.consome(TOKEN.MENOS)
        self.folha()

    def folha(self):
        #<folha> -> intVal | floatVal | strVal | <call> | <lista> | ( <exp> ) 
        if self.tokenLido[0] == TOKEN.intVal:
            self.consome(TOKEN.intVal)
        elif self.tokenLido[0] == TOKEN.floatVal:
            self.consome(TOKEN.floatVal)
        elif self.tokenLido[0] == TOKEN.strVal:
            self.consome(TOKEN.strVal)
        elif self.tokenLido[0] == TOKEN.IDENT or self.tokenLido[0] == TOKEN.ABRECONCH:
            self.lista()
        elif self.tokenLido[0] == TOKEN.ABREPAR:
            self.consome(TOKEN.ABREPAR)
            self.exp()
            self.consome(TOKEN.FECHAPAR)
        else:
            self.call()
    
    def call(self):
        #<call> -> ident ( <lista_outs> ) 
        if self.tokenLido[0] == TOKEN.IDENT:
            self.consome(TOKEN.IDENT)
            self.consome(TOKEN.ABREPAR)
            self.lista_outs()
            self.consome(TOKEN.FECHAPAR)

    def opcIndice(self):
        #<opcIndice> -> LAMBDA | [ <exp> <restoElem> ]
        if self.tokenLido[0] == TOKEN.ABRECONCH:
            self.consome(TOKEN.ABRECONCH)
            self.exp()
            self.restoElem()
            self.consome(TOKEN.FECHACONCH)
        else:
            pass
    
    def restoElem(self):
#       <restoElem> -> LAMBDA | : <exp>
        if self.tokenLido[0] == TOKEN.DPTO:
            self.consome(TOKEN.DPTO)
            self.exp()
        else:
            pass

    
    
if __name__ == '__main__':
    x = Lexico('codigoFonte.txt')
    a = Sintatico(x)
    a.traduz()
