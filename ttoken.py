#---------------------------------------------------
# Tradutor para a linguagem CALC
#Classe TOKEN e enumeração:
# A enumeração TOKEN define os tipos de tokens que serão reconhecidos pela linguagem CALC. 
# Esses tokens incluem palavras-chave, operadores e símbolos especiais usados na linguagem.
#---------------------------------------------------

from enum import IntEnum
class TOKEN(IntEnum):
    erro = 1
    eof = 2
    ident = 3
    num = 4
    string = 5
    IF = 6
    ELSE = 7
    WHILE = 8
    BEGIN = 9
    END = 10
    PROGRAM = 11
    abrePar = 12
    fechaPar = 13
    virg = 14
    ptoVirg = 15
    pto = 16
    oprel = 18
    AND = 23
    OR = 24
    NOT = 25
    mais = 26
    menos = 27
    multiplica = 28
    divide = 29
    READ = 30
    write = 31
    VAR = 32
    abreChave = 33
    fechaChave = 34
    atrib = 35
    then = 36
    ASPAS_SIMPLES = 37
    ASPAS_DUPLA = 38
    FOR = 39

    @classmethod
    def msg(cls, token):
        nomes = {
            1:'erro',
            2:'<eof>',
            3:'ident',
            4:'numero',
            5:'string',
            6:'if',
            7:'else',
            8:'while',
            9:'begin',
            10:'end',
            11:'program',
            12:'(',
            13:')',
            14:',',
            15:';',
            16:'.',
            18:'oprel',
            23:'and',
            24:'or',
            25:'not',
            26:'+',
            27:'-',
            28:'*',
            29:'/',
            30:'read',
            31:'write',
            32:'var',
            33:'{',
            34:'}',
            35:'=',
            36:'then',
            37:'"',
            38:"'",
            39:'for',
        }
        return nomes[token]

    @classmethod
    def reservada(cls, lexema):
        reservadas = {
            'begin': TOKEN.BEGIN,
            'end': TOKEN.END,
            'if': TOKEN.IF,
            'then': TOKEN.then,
            'while': TOKEN.WHILE,
            'else': TOKEN.ELSE,
            'read': TOKEN.READ,
            'write': TOKEN.write,
            'var': TOKEN.VAR,
            'and': TOKEN.AND,
            'or': TOKEN.OR,
            'not': TOKEN.NOT,
            'for': TOKEN.FOR
        }
        if lexema in reservadas:
            return reservadas[lexema]
        else:
            return TOKEN.ident
