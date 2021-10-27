
#********** gramasm assembles RVG grammars for readable source code into vectors and other structures ****
# A grammar consists of a collection of productions, each of which has a cond: TernVec, a Cchange: TernVec,
# aand an optional list of actions:, notatbly lex for advancing to the next word, etc.

#Importing an available library, ply.lex, to tokenize the grammar file
import ply.lex as lex

reserved = {
   'ordering_features' : 'ORDERINGFEATURES',
   'defaultcond'    : 'DEFAULTCOND',
   'productions'    : 'PRODUCTIONS',
   'p'              : 'P',
   'cond'           : 'COND', 
   'change'         : 'CHANGE', 
   'action'         : 'ACTION',
   'lex'            : 'LEX',
   'storeRel'       : 'storeRel',
   'restoreRel'     : 'restoreRel',
   'init_final'     : 'INITFINAL'
}

literals = "+-?.{}"

def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value,'NAME')    # Check for reserved words
    return t

# Ignored characters
t_ignore = " \t"

t_ignore_COMMENT = r'%.*' #Comment from % to end of line

#Tokens are keywords for the assembler
tokens = ( ['NAME'] + list(reserved.values() ))
            
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
#    t.lexer.lineno += t.value.count("\n")

def t_error(t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()
# Prepare to process tokens from data file
tok = None
data = ""

#Provide some data to tokenize and parse
def get_data(data):
    file_name = input('Enter .syn file name:') + ".syn"
    with open(file_name) as file_handle:
        for line in file_handle:
            data = data + line
    file_handle.close()
    lexer.input(data)
    return data

import sys  #For sys.exit()  
def error_exit(expected,found):
    if (tok):
        line = str(tok.lexer.lineno)
        msg = "Expected " + expected + " but found " + found + " at line " + line
    else:
        msg = "Expected " + expected + " but found " + found 
    sys.exit(msg)

featureLabels = [ ]    # list of feature labels
productions = [ ]       # list of productions

def section_header(section_name, require=False):
    global tok
    if tok.value != section_name:
        if require:
            error_exit(section_name,tok.value)
        else: 
            return False
    return True

def features_section():
    global tok
    tok = lexer.token()
    section_header('ordering_features', True)
    while True:
        tok = lexer.token()
        if not tok:
            error_exit("productions then initfinal","EOF")
        if tok.type == 'NAME':
            featureLabels.append(tok.value)
        else:
            break

def actions_list(actions):
    global tok
    while True:
        tok = lexer.token()
        if not tok:
            error_exit("initfinal","EOF")
        if tok.type in ('LEX','storeRel', 'restoreRel'):
            actions.append(tok.value)
        else:
            break
    return actions

from Vectors import TernVec

def parse_vector(defaultVec):
    tVec = TernVec()
    tVec.change3(defaultVec)
    global tok
    dotRange = False
    while True:
        tok = lexer.token()
        if not tok:
            error_exit("initfinal","EOF")
        if tok.value in ('+','-','?'):
            sign = tok.value
        elif tok.value == '.':
            tok = lexer.token()
            section_header('.',True)
            dotRange = True
        else:
            # tVec.showVec(featureLabels,True)
            return tVec
        tok = lexer.token()
        if tok.value in featureLabels:
            if dotRange:
                rangeFeat = featureLabels.index(tok.value)
                for i in range(setFeat+1,rangeFeat+1):
                    tVec.setFeature(i,sign)
                dotRange = False
            else: 
                setFeat = featureLabels.index(tok.value)
                tVec.setFeature(setFeat,sign)
        else:
            error_exit("ordering feature",tok.value)
    return tVec
 
defaultCond = TernVec()
defaultChange = TernVec()
          
def defaultCondVector():
    if not section_header("defaultcond",False):
        return
    global defaultCond
    defaultCond.change3(parse_vector(defaultCond))

def productions_section():
    if not section_header('productions'):
        return
    global tok
    tok = lexer.token()
    while True:
        if not tok:
            error_exit("initfinal","EOF")
        section_header('p', True)  
        tok = lexer.token()
        if tok.type == 'NAME':
            prodName = tok.value
        else:
           error_exit("production name",tok.value)
        tok = lexer.token()
        section_header('cond', True)
        condVector = parse_vector(defaultCond)

        section_header('change',True)
        changeVector = parse_vector(defaultChange)
        if section_header('action'):
            actions = actions_list([])
        else:
            actions = None
        production = (prodName,condVector,changeVector,actions)
        productions.append(production)
        if section_header('initfinal'):
            break

def initfinal_section():
    section_header('initfinal',True)
    global tok
    tok = lexer.token()
    prodIndex = 0
    for prod in productions:
        prodname = prod[0]
        if prodname == tok.value:
            return prodIndex
        else:
            prodIndex += 1
    error_exit("production name",tok.value)

import pickle
#A grammar consosts of various sections, some required, others optional
def gramasm():
    global data
    data = get_data(data)
    features_section()
    defaultCondVector()
    productions_section()
    initfinal = initfinal_section()
    grammar = (featureLabels,productions,initfinal)
    f = open('grammar.pkl', 'wb')
    pickle.dump(grammar,f)
    f.close

if __name__ == '__main__':
     gramasm()   
     print("gramasm done")
# print(featureLabels, sep = ", ")

