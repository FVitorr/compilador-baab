#---------------------------------------------------
# Tradutor para a linguagem CALC
#Classe TOKEN e enumeração:
# A enumeração TOKEN define os tipos de tokens que serão reconhecidos pela linguagem CALC. 
# Esses tokens incluem palavras-chave, operadores e símbolos especiais usados na linguagem.
#---------------------------------------------------

from enum import IntEnum
class TOKEN(IntEnum):
    ERRO = 1
    EOF = 2
    IDENT = 3
    INT = 4
    STRING = 5
    IF = 6
    ELSE = 7
    WHILE = 8
    BEGIN = 9
    END = 10
    PROGRAM = 11
    ABREPAR = 12
    FECHAPAR = 13
    VIRG = 14
    PTOVIRG = 15
    FUNCTION = 17
    OPREL = 18
    ABRECONCH = 19
    FECHACONCH = 20
    IN = 21
    DO = 22
    AND = 23
    OR = 24
    NOT = 25
    MAIS = 26
    MENOS = 27
    MULTIPLICA = 28
    DIVIDE = 29
    READ = 30
    WRITE = 31
    VAR = 32
    ABRECHAVE = 33
    FECHACHAVE = 34
    ATRIB = 35
    THEN = 36
    ASPAS_SIMPLES = 37
    ASPAS_DUPLA = 38
    FOR = 39
    LIST = 41
    FLOAT = 43
    RANGE = 44
    RETURN = 45
    SETA = 46
    DPTO = 47
    MOD = 48
    LEN = 49


    @classmethod
    def msg(cls, token):
        nomes = {
            1:'erro',
            2:'<eof>',
            3:'ident',
            4:'intVal',
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
            17:'function',
            18:'oprel',
            19:'[',
            20:']',
            21:'in',
            22:'do',
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
            41:'ListVal',
            43:'floatVal',
            44:'range',
            45:'return',
            46:'->',
            47:':',
            48:'%',
            49:'len'
        }
        return nomes[token]

    @classmethod
    def reservada(cls, lexema):
        reservadas = {
            'begin': TOKEN.BEGIN,
            'end': TOKEN.END,
            'if': TOKEN.IF,
            'then': TOKEN.THEN,
            'while': TOKEN.WHILE,
            'else': TOKEN.ELSE,
            'read': TOKEN.READ,
            'write': TOKEN.WRITE,
            'var': TOKEN.VAR,
            'and': TOKEN.AND,
            'or': TOKEN.OR,
            'not': TOKEN.NOT,
            'for': TOKEN.FOR,
            'function': TOKEN.FUNCTION,
            'list': TOKEN.LIST,
            'int': TOKEN.INT,
            'float': TOKEN.FLOAT,
            'in': TOKEN.IN,
            'do': TOKEN.DO,
            'return': TOKEN.RETURN,
            'range': TOKEN.RANGE,
            'len': TOKEN.LEN,
        }
        if lexema in reservadas:
            return reservadas[lexema]
        else:
            return TOKEN.IDENT
