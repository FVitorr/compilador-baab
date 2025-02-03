#---------------------------------------------------
# Tradutor para a linguagem b-a-ba
#
# versao 1a (mar-2024)
#---------------------------------------------------
from lexico import TOKEN, Lexico
from semantico import Semantico
import re
import inspect


RED = "\033[31m"  # Código ANSI para vermelho
RESET = "\033[0m"  # Código ANSI para resetar a cor
class Sintatico:

    def __init__(self, lexico):
        self.lexico = lexico
        self.identacao = 0
        self.nomeAlvo = 'alvo.py'
        self.semantico = Semantico(self.nomeAlvo)

    def traduz(self):
        try:
            print('Iniciando a tradução...')
            self.tokenLido = self.lexico.getToken()
            self.prog()
            print('[#] Traduzido com sucesso.')
        except Exception as e:
            print('Erro na tradução.')
            print(e)


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


    def testar_lexico(self):
        self.tokenLido = self.get_token()
        token, lexema, linha, coluna = self.tokenLido
        while token != TOKEN.EOF:
            Lexico.imprimir_token(self.tokenLido)
            self.tokenLido = self.get_token()
            token, lexema, linha, coluna = self.tokenLido
        Lexico.imprimir_token(self.tokenLido)

#-----------------------------Usar a Gramatica-----------------------------------------
    def prog(self):
        # <prog> -> <funcao> <RestoFuncoes>
        self.codigoInicial()
        self.funcao()
        self.restoFuncoes()
        self.semantico.verificar_main()
        self.consome(TOKEN.EOF)
        self.codigoFinal()

        l = self.semantico.tabelaSimbolos

    
    def restoFuncoes(self):
        #<RestoFuncoes> -> <funcao> <RestoFuncoes> | LAMBDA
        if self.tokenLido[0] == TOKEN.FUNCTION:
            self.funcao()
            self.restoFuncoes()
        else:
            pass #LAMBDA

    
    def funcao(self):
        #<funcao> -> function ident ( <params> ) <tipoResultado> <corpo>
        self.consome(TOKEN.FUNCTION)
        salvarIdent = self.tokenLido
        self.consome(TOKEN.IDENT)
        self.consome(TOKEN.ABREPAR)
        ARGS, codigo_1 = self.params()
        self.consome(TOKEN.FECHAPAR)
        RETURN, codigo_2 = self.tipoResultado()
        self.semantico.declara(salvarIdent, (TOKEN.FUNCTION, ARGS + RETURN))
        self.semantico.iniciaFuncao(self.tokenLido)
        for p in ARGS:
            (tt, (tipo,info)) = p
            self.semantico.declara(tt, (tipo, info))

        codigo = ' def ' + salvarIdent[1] + '(' + 'self' + codigo_1 + ')' + codigo_2 + ':\n'
        self.semantico.gera(1, codigo)

        self.corpo()
        self.semantico.verificaRetornoFuncao(self.tokenLido, RETURN[0][1])
        self.semantico.terminaFuncao()
    
    def tipoResultado(self):
        #<tipoResultado> -> LAMBDA | -> <tipo>
        if self.tokenLido[0] == TOKEN.SETA:
            self.consome(TOKEN.SETA)
            tipo = self.tipo()
        else:
            tipo = None    
        token = (0,0,0,0)
        return [(token,tipo)], self.semantico.tipos_retorno[tipo]
    
    def params(self):
        #<params> -> <tipo> ident <restoParams> | LAMBDA
        if self.tokenLido[0] in [TOKEN.INT, TOKEN.FLOAT, TOKEN.STRING]:
            tipo = self.tipo()
            salvarIdent = self.consome(TOKEN.IDENT)
            tipoParam = (salvarIdent, tipo)
            resto, resto_codigo = self.restoParams()
            tipoArgs = [tipoParam] + resto
            return tipoArgs, ', ' + salvarIdent[1] + resto_codigo
        else:
            return [], ''

    def restoParams(self):
        #<restoParams> -> LAMBDA | , <tipo> ident <restoParams>
        if self.tokenLido[0] == TOKEN.VIRG:
            self.consome(TOKEN.VIRG)
            tipo = self.tipo()
            salvarIdent = self.consome(TOKEN.IDENT)
            tipo_param = (salvarIdent, tipo)
            resto, resto_codigo = self.restoParams()
            tipos_args = [tipo_param] + resto
            return tipos_args, ', ' + salvarIdent[1] + resto_codigo 
        else:
            return [], ''

    def corpo(self):
        #<corpo> -> begin <declaracoes> <calculo> end
        self.consome(TOKEN.BEGIN)
        self.identacao = 2
        self.declaracoes()
        self.calculo()
        self.consome(TOKEN.END)
        self.semantico.gera(self.identacao, '\n')
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
        tipo = self.tipo()
        salvarIdent = self.idents()
        self.consome(TOKEN.PTOVIRG)

        for tt in salvarIdent:
            self.semantico.declara(tt, tipo)

        
        if tipo == (TOKEN.INT, False):
            self.gerarCodigoDeclaracoes(salvarIdent, '0')
        elif tipo == (TOKEN.FLOAT, False):
            self.gerarCodigoDeclaracoes(salvarIdent, '0.0')
        elif tipo == (TOKEN.STRING, False):
            self.gerarCodigoDeclaracoes(salvarIdent, '""')
        elif tipo[1] is True:
            self.gerarCodigoDeclaracoes(salvarIdent, '[]')
        

    def idents(self):
        #<idents> -> ident <restoIdents> 
        salvarIdent = self.consome(TOKEN.IDENT)
        resto = self.restoIdents()

        return [salvarIdent] + resto
    
    def restoIdents(self):
        #<restoIdents> -> , ident <restoIdents> | LAMBDA 
        if self.tokenLido[0] == TOKEN.VIRG:
            self.consome(TOKEN.VIRG)
            salvarIdent = self.consome(TOKEN.IDENT)
            return [salvarIdent] + self.restoIdents()
        else:
            return []
    
    def tipo(self):
        #<tipo> -> string <opcLista> | int <opcLista> | float <opcLista> 
        if self.tokenLido[0] == TOKEN.STRING:
            self.consome(TOKEN.STRING)
            opcLista = self.opcLista()
            return TOKEN.STRING, opcLista
        elif self.tokenLido[0] == TOKEN.INT:
            self.consome(TOKEN.INT)
            opcLista = self.opcLista() 
            return TOKEN.INT, opcLista
        else:
            self.consome(TOKEN.FLOAT)
            opcLista = self.opcLista()
            return TOKEN.FLOAT, opcLista



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
        entrou = False
        while self.tokenLido[0] in [TOKEN.IDENT, TOKEN.IF, TOKEN.READ, TOKEN.WRITE,
                                     TOKEN.ABRECHAVE, TOKEN.FOR, TOKEN.WHILE, TOKEN.RETURN]:
            self.com()
            entrou = True
        if not entrou:
            self.semantico.gera(self.identacao, 'pass\n')

    def com(self):
        #<com> -> <atrib> | <if> | <leitura> | <escrita> | <bloco> | <for> | <while> | <retorna> | <call>  ;
        if self.tokenLido[0] == TOKEN.IDENT:
            salvarIdent = self.tokenLido
            result = self.semantico.consulta(salvarIdent)
            if result is None:
                msg = f'Variavel {salvarIdent[1]} não declarada'
                self.semantico.erroSemantico(salvarIdent, msg)
            else:
                (tipo, info) = result
                if (tipo == TOKEN.FUNCTION):
                    _, codigo = self.call()
                    self.consome(TOKEN.PTOVIRG)
                    codigo =  codigo + '\n'
                    self.semantico.gera(self.identacao, codigo)
                else:
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
        tipo, codigo = self.expOpc()

        function, tipo_retorno = self.semantico.retornoFuncao()

        if tipo_retorno != tipo:
            msg = f'[!] O retorno esperado para a {function} é {tipo_retorno} mas foi encontrado {tipo}'
            self.semantico.erroSemantico(self.tokenLido, msg)
        
        self.semantico.retorno = True
        self.consome(TOKEN.PTOVIRG)
        codigo = 'return ' + codigo + '\n'
        self.semantico.gera(self.identacao, codigo)
    
    def expOpc(self):
        #<expOpc> -> LAMBDA | <exp>
        if self.tokenLido[0] in [TOKEN.intVal, TOKEN.IDENT, TOKEN.ABREPAR, 
                                 TOKEN.floatVal, TOKEN.NOT, TOKEN.MAIS, TOKEN.MENOS, TOKEN.strVal]:
            return self.exp()
        else:
            return None, ''
            #pass
    
    def WHILE(self):
        #<while> -> while ( <exp> ) <com>
        salvarWhile = self.consome(TOKEN.WHILE)
        self.consome(TOKEN.ABREPAR)
        tipoExp, codigo = self.exp()

        if tipoExp != (TOKEN.INT, False):
            msg = (f'[!] -> WHILE - Parâmetro Inesperado! Esperado \'{self.semantico.tipos[(TOKEN.INT, False)]}\', '
                   f'mas recebeu \'{self.semantico.tipos[tipoExp]}\'!')
            self.semantico.erroSemantico(salvarWhile, msg)

        self.consome(TOKEN.FECHAPAR)
        codigo = 'while ' + codigo + ':\n'
        self.semantico.gera(self.identacao, codigo)
        self.identacao += 1
        self.com()
        self.identacao -= 1    

    def FOR(self):
        #<for> -> for ident in <range> do <com>
        self.consome(TOKEN.FOR)
        if self.semantico.consulta(self.tokenLido) is not None:
            salvar_ident = self.tokenLido
            tipo_ident = self.semantico.consulta(self.tokenLido)
            self.consome(TOKEN.IDENT)
            self.consome(TOKEN.IN)
            tipo_range, codigo = self.range()

            if tipo_ident[0] != tipo_range[0] and tipo_range[1] is True:
                msg = (f'[!] -> FOR - Identificador \'{salvar_ident[1]}\' Incompatível! Esperado '
                       f'\'{self.semantico.tipos[(tipo_range[0], False)]}\', mas recebeu '
                       f'\'{self.semantico.tipos[tipo_ident]}\'!')
                self.semantico.erroSemantico(salvar_ident, msg)
            elif tipo_ident != (TOKEN.INT, False) and tipo_range == (TOKEN.INT, False):
                msg = (f'[!] -> FOR - Identificador \'{salvar_ident[1]}\' Incompatível! Esperado '
                       f'\'{self.semantico.tipos[(TOKEN.INT, False)]}\', mas recebeu '
                       f'\'{self.semantico.tipos[tipo_ident]}\'!')
                self.semantico.erroSemantico(salvar_ident, msg)
            
            self.consome(TOKEN.DO)
            codigo = 'for ' + salvar_ident[1] + ' in ' + codigo + ':\n'
            self.semantico.gera(self.identacao, codigo)
            self.identacao += 1
            self.com()
            self.identacao -= 1
        else:
            msg = f'[!] -> Identificador \'{self.tokenLido[1]}\' não declarado!'
            self.semantico.erroSemantico(self.tokenLido, msg)
    
    def range(self):
        #<range> -> <lista> | range ( <exp> , <exp> <opcRange> )
        if self.tokenLido[0] == TOKEN.RANGE:
            
            self.consome(TOKEN.RANGE)
            self.consome(TOKEN.ABREPAR)
            tipoExp, codigo_1 = self.exp() #TIPO INTEIRO
            if tipoExp != (TOKEN.INT, False):
                msg = '[!] O primeiro parametro da função range deve ser inteiro'
                self.semantico.erroSemantico(self.tokenLido, msg)
            self.consome(TOKEN.VIRG)
            tipoExp2, codigo_2 = self.exp() #TIPO INTEIRO
            print(tipoExp2)
            if tipoExp2 !=  (TOKEN.INT, False):
                msg = '[!] O segundo parametro da função range deve ser inteiro'
                self.semantico.erroSemantico(self.tokenLido, msg)
            tipoExp3, codigo_3 = self.opcRange() #LAMBDA | TIPO INTEIRO
            if tipoExp3 !=  (TOKEN.INT, False) and tipoExp3 != None:
                msg = '[!] O Terceiro parametro da função range deve ser inteiro'
                self.semantico.erroSemantico(self.tokenLido, msg)
            self.consome(TOKEN.FECHAPAR)
            codigo = 'range' + '(' + codigo_1 + ', ' + codigo_2 + codigo_3 + ')'
            return (TOKEN.INT, False), codigo
        else:
            return self.lista()
    
    def lista(self):
        #<lista> -> ident <opcIndice> | [ <elemLista> ]
        if self.tokenLido[0] == TOKEN.IDENT:
            salvaIdent = self.tokenLido
            tipo = self.semantico.consulta(salvaIdent)
            if tipo is None:
                msg = f'{RED}Variavel {salvaIdent[1]} não declarada{RESET}'
                self.semantico.erroSemantico(salvaIdent, msg)
            else:
                self.consome(TOKEN.IDENT)
                tipoOpc, codigo = self.opcIndice(tipo)
                return tipoOpc, salvaIdent[1] + codigo
        else:
            self.consome(TOKEN.ABRECONCH)
            tipoElem, codigo = self.elemLista()
            if tipoElem is None:
                msg = f'[!] -> Listas só podem conter elementos do mesmo tipo!'
                self.semantico.erroSemantico(self.tokenLido, msg)
            self.consome(TOKEN.FECHACONCH)
            return tipoElem, '[' + codigo + ']'
    
    def elemLista(self):
        #<elemLista> -> LAMBDA | <elem> <restoElemLista>
        if self.tokenLido[0] in [TOKEN.intVal, TOKEN.IDENT, TOKEN.strVal, TOKEN.floatVal]:
            tipoElem, codigo_1 = self.elem()
            tipoRestoElem, codigo_2 = self.restoElemLista(tipoElem)
            if tipoRestoElem is not None:
                tipoRestoElem = (tipoRestoElem[0], True)
            return tipoRestoElem, codigo_1 + codigo_2
        else:
            return (None, True), ''
    
    def restoElemLista(self, tipo):
        #<restoElemLista> -> LAMBDA | , <elem> <restoElemLista>
        if self.tokenLido[0] == TOKEN.VIRG:
            self.consome(TOKEN.VIRG)
            tipoElem, codigo_1 = self.elem()
            tipoElem = self.semantico.checarOper(tipo, TOKEN.VIRG, tipoElem)
            tipoRestoElem, codigo_2 = self.restoElemLista(tipoElem)
            codigo = ', ' + codigo_1 + codigo_2
            return tipoRestoElem, codigo
        else:
            return tipo, ''
    
    def opcRange(self):
        #<opcRange> -> , <exp> | LAMBDA
        if self.tokenLido[0] == TOKEN.VIRG:
            self.consome(TOKEN.VIRG)
            tipoExp, codigo = self.exp()
            codigo = ', ' + codigo
            return tipoExp, codigo
        else:
            return None, ''
                
    def elem(self):
        #<elem> -> intVal | floatVal | strVal | ident 
        if self.tokenLido[0] == TOKEN.intVal:
            self.consome(TOKEN.intVal)
            return (TOKEN.INT, False), self.tokenLido[1]
        elif self.tokenLido[0] == TOKEN.floatVal:
            self.consome(TOKEN.floatVal)
            return (TOKEN.FLOAT, False), self.tokenLido[1]
        elif self.tokenLido[0] == TOKEN.strVal:
            self.consome(TOKEN.strVal)
            return (TOKEN.STRING, False), self.tokenLido[1]
        elif self.tokenLido[0] == TOKEN.IDENT:
            if self.semantico.consulta(self.tokenLido) is not None:
                salvaToken = self.tokenLido
                tipo_ident = self.semantico.consulta(self.tokenLido)
                self.consome(TOKEN.IDENT)
                return tipo_ident, salvaToken[1]
            else:
                msg = f'[!] -> Identificador \'{self.tokenLido[1]}\' não declarado!'
                self.semantico.erroSemantico(self.tokenLido, msg)

    def atrib(self):
        #<atrib> -> ident <opcIndice> = <exp> ;
        if self.semantico.consulta(self.tokenLido) is None:
            msg = f'\t{RED}Variavel {salvarIdent[1]} não declarada{RESET}'
            self.semantico.erroSemantico(salvarIdent, msg)
        else:
            salvarIdent = self.tokenLido
            tipoIdent = self.semantico.consulta(self.tokenLido)
            self.consome(TOKEN.IDENT)
            tipoOpc, codigo_1 = self.opcIndice(tipoIdent)

            self.consome(TOKEN.ATRIB)
            tipoExp, codigo_2 = self.exp()
            
            if self.semantico.checarOper(tipoExp, tipoOpc, TOKEN.ATRIB) is None:
                msg = f'[!] Atribuição Inválida! Esperado \'{self.semantico.tipos[tipoOpc]}\', mas recebeu \'{self.semantico.tipos[tipoExp]}\'!'
                self.semantico.erroSemantico(salvarIdent, msg)
        
            self.consome(TOKEN.PTOVIRG)
            codigo = salvarIdent[1] + codigo_1 + ' = ' + codigo_2 + '\n'
            self.semantico.gera(self.identacao, codigo)

    def se(self): #CONFERIR
        # <if> -> if ( <exp> ) then <com> <else_opc>
        salvarToken = self.tokenLido
        if self.tokenLido[0] == TOKEN.IF:
            self.consome(TOKEN.IF)
            self.consome(TOKEN.ABREPAR)
            tipo_exp, codigo = self.exp()

            if tipo_exp != (TOKEN.INT, False):
                msg = (f'[!] -> IF - Parâmetro Inesperado! Esperado \'{self.semantico.tipos[(TOKEN.INT, False)]}\', '
                    f'mas recebeu \'{self.semantico.tipos[tipo_exp]}\'!')
                self.semantico.erroSemantico(salvarToken, msg)

            self.consome(TOKEN.FECHAPAR)
            codigo = 'if ' + codigo + ':\n'
            self.semantico.gera(self.identacao, codigo)
            self.consome(TOKEN.THEN)
            self.identacao += 1
            self.com()
            self.identacao -= 1
            self.elseopc()
        
    def elseopc(self):
        # <else_opc> -> LAMBDA | else <com> 
        if self.tokenLido[0] == TOKEN.ELSE:
            self.consome(TOKEN.ELSE)
            codigo = 'else: \n'
            self.semantico.gera(self.identacao, codigo)
            self.identacao += 1
            self.com()
            self.identacao -= 1
        else:
            pass
    
    def leitura(self):
        # <leitura> -> read ( <exp> , ident ) ;
        token_read = self.tokenLido
        self.consome(TOKEN.READ)
        self.consome(TOKEN.ABREPAR)
        tipoExp, codigo_1 = self.exp()
        if tipoExp != (TOKEN.STRING, False):
            msg = (f'[!]Era Esperado \'{self.semantico.tipos[(TOKEN.STRING, False)]}\', '
                   f'mas recebeu \'{self.semantico.tipos[tipoExp]}\'!')
            self.semantico.erroSemantico(token_read, msg)

        self.consome(TOKEN.VIRG)
        tipo_ident = self.semantico.consulta(self.tokenLido)
        salvar_ident = self.tokenLido[1]
        if tipo_ident is None:
            msg = f'[!] -> Identificador {self.tokenLido[1]} não declarado!'
            self.semantico.erroSemantico(self.tokenLido, msg)
        else:
            self.consome(TOKEN.IDENT)
        self.consome(TOKEN.FECHAPAR)
        self.consome(TOKEN.PTOVIRG)

        if tipo_ident[1] is True:
            msg = '[!] Função \'read\' retorna tipo \'str\' por default, não tipo \'[list]\'!'
            self.semantico.erroSemantico(salvar_ident, msg)

        tipo_input = self.semantico.tipos[tipo_ident]
        codigo = salvar_ident + ' = ' + tipo_input + '(input(' + codigo_1 + '))\n'
        self.semantico.gera(self.identacao, codigo)

    def escrita(self):
        #<escrita> -> write ( <lista_out> ) ;
        self.consome(TOKEN.WRITE)
        self.consome(TOKEN.ABREPAR)
        args, codigo = self.lista_outs()
        self.consome(TOKEN.FECHAPAR)
        self.consome(TOKEN.PTOVIRG)
        codigo = 'print' + '(' + codigo + ')\n'
        self.semantico.gera(self.identacao, codigo)

    def lista_outs(self):
        # <lista_outs> -> <out> <restoLista_outs>
        arg, codigo = self.out()
        resto_args, resto_codigo = self.restoLista_outs()
        return [arg] + resto_args, codigo + resto_codigo
    
    def restoLista_outs(self):
        # <restoLista_outs> -> LAMBDA | , <out> <restoLista_outs>
        if self.tokenLido[0] == TOKEN.VIRG:
            self.consome(TOKEN.VIRG)
            arg, codigo = self.out()
            resto_args, resto_codigo = self.restoLista_outs()
            return [arg] + resto_args, ', ' + codigo + resto_codigo
        else:
            return [], ''

    def out(self):
        #<out> -> <folha>
        return self.folha()
    
    def bloco(self):
        # <bloco> -> { <calculo> }
        self.consome(TOKEN.ABRECHAVE)
        self.calculo()
        self.consome(TOKEN.FECHACHAVE)

    def exp(self):
        # <exp> -> <disj>
        return self.disj()

    def disj(self):
        #<disj> -> <conj> <restoDisj>
        tipoConj, codigo_1 = self.conj()
        tipoDisj, codigo_2 = self.restoDisj(tipoConj)
        return tipoDisj, codigo_1 + codigo_2
    
    def restoDisj(self, tipo):
        #<restoDisj> -> LAMBDA | or <conj> <restoDisj>
        if self.tokenLido[0] == TOKEN.OR:
            self.consome(TOKEN.OR)
            tipoConj, codigo_1 = self.conj()
            tipoAux = self.semantico.checarOper(tipo, tipoConj, TOKEN.OR)
            tipoDisj, codigo_2 = self.restoDisj(tipoAux)
            return tipoDisj," or " + codigo_1 +  codigo_2
        else:
            return tipo, ''

    def conj(self):
        #<conj> -> <nao> <restoConj>
        nao, codigo_1 = self.nao()
        tipoRestoConj, codigo_2 = self.restoConj(nao)
        return tipoRestoConj, codigo_1 + codigo_2

    def restoConj(self, tipo):
        #<restoConj> -> LAMBDA | and <nao> <restoConj>
        if self.tokenLido[0] == TOKEN.AND:
            self.consome(TOKEN.AND)
            nao, codigo_1 = self.nao()
            nTipo = self.semantico.checarOper(tipo, nao, TOKEN.AND)
            tipoConj, codigo_2 = self.restoConj(nTipo)
            return tipoConj, " and " + codigo_1 + codigo_2
        else:
            return tipo, ''

    def nao(self):
        # <nao> -> not <nao> | <rel>
        if self.tokenLido[0] == TOKEN.NOT:
            self.consome(TOKEN.NOT)
            tipoNao, codigo_1 = self.nao()
            return tipoNao, " not " + codigo_1
        else:
            return self.rel()
        
    def rel(self):
        # <rel> -> <soma> <restoRel>
        soma, codigo_1 = self.soma()
        tipoRel, codigo_2 = self.restoRel(soma)
        return tipoRel, codigo_1 + codigo_2
        
    
    def restoRel(self, tipo):
        #<restoRel> -> LAMBDA | oprel <soma>
        if self.tokenLido[0] == TOKEN.OPREL:
            salvarOpRel = self.tokenLido[1]
            self.consome(TOKEN.OPREL)
            soma, codigo_1 = self.soma()
            tipoAux = self.semantico.checarOper(tipo, soma, TOKEN.OPREL)
            codigo = ' ' + salvarOpRel + ' ' + codigo_1
            return tipoAux, codigo
        else:
            return tipo, ''
        
    def soma(self):
        # <soma> -> <mult> <restoSoma>
        mult, codigo_1 = self.mult()
        tipoSoma, codigo_2 = self.restosoma(mult)
        return tipoSoma, codigo_1 + codigo_2
    
    def restosoma(self, tipo):
        # <restoSoma> -> LAMBDA | + <mult> <restoSoma> | - <mult> <restoSoma>
        if self.tokenLido[0] == TOKEN.MAIS: 
            self.consome(TOKEN.MAIS)
            mult, codigo_1 = self.mult()
            nTipo = self.semantico.checarOper(tipo, mult, TOKEN.MAIS)
            tipoSoma, codigo_2 = self.restosoma(nTipo)
            return tipoSoma, " + " + codigo_1 + codigo_2
        elif self.tokenLido[0] == TOKEN.MENOS:
            self.consome(TOKEN.MENOS)
            mult, codigo_1 = self.mult()
            nTipo = self.semantico.checarOper(tipo, mult, TOKEN.MENOS)
            tipoSoma, codigo_2 = self.restosoma(nTipo)
            return tipoSoma, " - " + codigo_1 + codigo_2
        else:
            return tipo, ''
        
    def mult(self):
        # <mult> -> <uno> <restoMult>
        uno, codigo_1 = self.uno()
        tipoMult, codigo_2 = self.restomult(uno)
        return tipoMult, codigo_1 + codigo_2
    
    def restomult(self, tipo):
        # <restoMult> -> LAMBDA | / <uno> <restoMult> | * <uno> <restoMult> | % <uno> <restoMult>
        if self.tokenLido[0] == TOKEN.MULTIPLICA:
            self.consome(TOKEN.MULTIPLICA)
            uno, codigo_1 = self.uno()
            nTipo = self.semantico.checarOper(tipo, uno, TOKEN.MULTIPLICA)
            tipoMult, codigo_2 = self.restomult(nTipo)
            return tipoMult, " * " + codigo_1 + codigo_2
        elif self.tokenLido[0] == TOKEN.DIVIDE:
            self.consome(TOKEN.DIVIDE)    
            uno, codigo_1 = self.uno()
            nTipo = self.semantico.checarOper(tipo, uno, TOKEN.DIVIDE)
            tipoMult, codigo_2 = self.restomult(nTipo)
            return tipoMult, " / " + codigo_1 + codigo_2
        elif self.tokenLido[0] == TOKEN.MOD:
            self.consome(TOKEN.MOD)
            uno, codigo_1 = self.uno()
            nTipo = self.semantico.checarOper(tipo, uno, TOKEN.MOD)
            tipoMult, codigo_2 = self.restomult(nTipo)
            return tipoMult, " % " + codigo_1 + codigo_2
        else:
            return tipo, ''


    def uno(self):
        # <uno> -> + <uno> | - <uno> | <folha>
        if self.tokenLido[0] == TOKEN.MAIS:
            self.consome(TOKEN.MAIS)
            tipoUno, codigo_1 = self.uno()
            return tipoUno, '+' +  codigo_1
        elif self.tokenLido[0] == TOKEN.MENOS:
            self.consome(TOKEN.MENOS)
            tipoUno, codigo_1 = self.uno()
            return tipoUno, '-' +  codigo_1
        else:        
            return self.folha()
        
    def folha(self):
        # <folha> -> intVal | floatVal | strVal | <call> | <lista> | ( <exp> )
        if self.tokenLido[0] == TOKEN.intVal:
            codigo = self.tokenLido[1]
            self.consome(TOKEN.intVal)
            return (TOKEN.INT, False), codigo
        elif self.tokenLido[0] == TOKEN.intVal:
            codigo = self.tokenLido[1]
            self.consome(TOKEN.intVal)
            return (TOKEN.FLOAT, False), codigo
        elif self.tokenLido[0] == TOKEN.strVal:
            codigo = self.tokenLido[1]
            self.consome(TOKEN.strVal)
            return (TOKEN.STRING, False), codigo
        elif self.tokenLido[0] == TOKEN.IDENT or self.tokenLido[0] == TOKEN.ABRECONCH:
            result = self.semantico.consulta(self.tokenLido)
            if self.tokenLido[0] == TOKEN.ABRECONCH:
                tipo_lista, codigo = self.lista()
                return tipo_lista, codigo
            elif result is None:
                msg = f'[!] -> Identificador \'{self.tokenLido[1]}\' não declarado!'
                self.semantico.erroSemantico(self.tokenLido, msg)
            else:
                (tipo, info) = result
                if tipo == TOKEN.FUNCTION:
                    tipo_call, codigo = self.call()
                    return tipo_call, codigo
                else:
                    tipo_lista, codigo = self.lista()
                    return tipo_lista, codigo
        else:
            self.consome(TOKEN.ABREPAR)
            tipo_exp, codigo = self.exp()
            self.consome(TOKEN.FECHAPAR)
            return tipo_exp, '(' + codigo + ')'

    
    def call(self):
        #<call> -> ident ( <lista_outs_opc> )
        salvarFunc = self.tokenLido
        if self.tokenLido[0] == TOKEN.IDENT:
            self.consome(TOKEN.IDENT)
            self.consome(TOKEN.ABREPAR)
            args, codigo  = self.lista_outs_opc()
            self.consome(TOKEN.FECHAPAR)
            args_func = self.semantico.consulta(salvarFunc)

            if salvarFunc[1] in ['len', 'num2str', 'str2num', 'trunc']:
                info = args_func[1][:-1]
                param, msg = self.semantico.verificar_parametros(info, args)

                if param is False:
                    msg = f'[!] -> Função \'{salvarFunc[1]}\' esperava {info} parâmetros, mas recebeu {len(args)}!'
                    self.semantico.erroSemantico(salvarFunc, msg)

                cod_func = self.semantico.funcoes_nativas[salvarFunc[1]]
                return args_func[1][-1], cod_func + '(' + codigo + ')'
            else:
                info = [item[1] for item in args_func[1][:-1]]
                param, msg = self.semantico.verificar_parametros(info, args)

                if param is False:
                    msg = f'[!] -> Função \'{salvarFunc[1]}\' esperava {info} parâmetros, mas recebeu {args}!'
                    self.semantico.erroSemantico(salvarFunc, msg)
                
                return args_func[1][-1][-1], 'self.' + salvarFunc[1] + '(' + codigo + ')'
    
    def lista_outs_opc(self):
        #<lista_outs_opc> -> LAMBDA | <lista_outs>
        if self.tokenLido[0] in [TOKEN.intVal, TOKEN.IDENT, TOKEN.strVal, TOKEN.floatVal, TOKEN.ABREPAR]:
            return self.lista_outs()
        else: 
            return [], ''

    def opcIndice(self, tipo):
        #<opcIndice> -> LAMBDA | [ <exp> <restoElem> ]
        if self.tokenLido[0] == TOKEN.ABRECONCH:
            if tipo[1] is not True:
                msg = (f'[!] -> Tentativa de acessar um índice de uma variável do tipo'
                f' {self.semantico.tipos[tipo]}! Apenas objetos indexáveis como listas '
                f'suportam a operação de indexação.')
                self.semantico.erroSemantico(self.tokenLido, msg)

            salvarToken = self.tokenLido
            self.consome(TOKEN.ABRECONCH)
            tipoExp, codigo_1 = self.exp()

            if tipoExp != (TOKEN.INT, False):
                msg = '[!] -> O índice de uma lista deve ser um número inteiro!'
                self.semantico.erroSemantico(self.tokenLido, msg)

            tipoElem, codigo_2 = self.restoElem(tipoExp)

            if tipoElem  != (TOKEN.INT, False) and tipoElem != (None, True):
                msg = (f'[!] -> Os índices de fatiamento devem ser do tipo '
                       f'\'{self.semantico.tipos[(TOKEN.INT, False)]}\' '
                       f'ou \'{self.semantico.tipos[None]}\', não \'{self.semantico.tipos[tipoElem]}\'!')
                self.semantico.erroSemantico(self.tokenLido, msg)
            
            if tipoElem == (None, True):
                tipoElem = (tipo[0], True)
            else:
                tipoElem = (tipo[0], False)

            self.consome(TOKEN.FECHACONCH)
            return tipoElem, '[' + codigo_1 + codigo_2 + ']'
        else:
            return tipo, ''
    
    def restoElem(self, tipo):
#       <restoElem> -> LAMBDA | : <exp>
        if self.tokenLido[0] == TOKEN.DPTO:
            self.consome(TOKEN.DPTO)
            tipo, codigo = self.exp()
            tipoAux = self.semantico.checarOper(tipo, tipo, TOKEN.DPTO)
            return tipoAux, ':' + codigo
        else:
            return tipo, ''

    # ------------------------------------------------ GERAÇÃO DE CÓDIGO ------------------------------------------------ #

    def verificar_import_math(self):
        fonte = re.sub(r'#.*', '', self.lexico.fonte)
        pattern = r'(?<=\s|[+\-*/%=<>,;!():])trunc\('  # Expressão Regular que controla o import math (math.trunc())
        return 'import math\n\n\n' if re.findall(pattern, fonte) else ''

    def codigoInicial(self):
        codigo_inicial = self.verificar_import_math()

        codigo_inicial += \
            'class ' + 'Program' + ':\n' + \
            '    def __init__(self):\n' + \
            '        pass\n\n'
        self.semantico.gera(0, codigo_inicial)

    def codigoFinal(self):
        codigo_final = \
            '\nif __name__ == \'__main__\':\n' + \
            '    prog = ' + 'Program' + '()\n' + \
            '    prog.main()\n'
        self.semantico.gera(0, codigo_final)

    def gerarCodigoDeclaracoes(self, idents, atrib):
        codigo_1, codigo_2 = '', ' = '
        for identificador in idents:
            codigo_1 += identificador[1] + ', '
            codigo_2 += atrib + ', '
        codigo = codigo_1[:-2] + codigo_2[:-2] + '\n'
        self.semantico.gera(self.identacao, codigo)

    
    
if __name__ == '__main__':
    x = Lexico('codigoFonte.txt')
    a = Sintatico(x)
    a.traduz()
