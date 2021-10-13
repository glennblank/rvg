
#********** lexasm assembles RVG lexicons for readable source code into vectors and other structures ****
# A lexicon consists of a collection of lexical entries

reserved = {
   'entries' : 'ENTRIES',
   'e'       : 'ENTRY'
}

literals = "+-?."

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
import ply.lex as lex
lexer = lex.lex()
# Prepare to process tokens from data file
tok = None
data = ""

#Provide some data to tokenize and parse
def get_data(data):
#   file_name = input('Enter .syn file name:')
    file_name = "wh.lex"
#   file_name += ".lex"
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

#   Get last assembled grammar
import pickle
#A grammar consosts of various sections, some required, others optional
f = open('grammar.pkl', 'rb')
grammar = pickle.load(f)
featureLabels, productions, initfinal = grammar[0], grammar[1], grammar[2]

lexicon = [ ]    # list of lexical entires to be constructed

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

def get_categories(categories):
    global tok
    tok = lexer.token()
    section_header('cat',True)
    while True:
        tok = lexer.token()
        if not tok or tok.type == 'ENTRY':
            break
        
        i = 0   # Look for index of production matching category name
        found = False
        for p in productions:
            if tok.value == p[0]:
                categories.append(i)
                found = True
                break
            else:
                i+=1
        if not found:
            error_exit("production name",tok.value)
    return categories

from Vectors import TernVec
           
def entries_section():
    global tok
    tok = lexer.token()
    section_header('entries',True)
    tok = lexer.token()
    while True:
        if not tok:
            break
        section_header('e', True)  
        tok = lexer.token()
        if tok.type == 'NAME':
            lexeme = tok.value.lower()
        elif tok.value in literals:
            lexeme = tok.value
        else:
           error_exit("lexeme",tok.value)
        #tok = lexer.token()
        #section_header('cond', True)
        #condVector = parse_vector()

        categories = get_categories([])

        lexEntry = (lexeme,categories)
        print(lexEntry)
        lexicon.append(lexEntry)

def lexasm():
    global data
    data = get_data(data)
    entries_section()
    f = open('lexicon.pkl', 'wb')
    pickle.dump(lexicon,f)
    f.close
#    f = open('grammar.pkl', 'rb')
#    grammar=pickle.load(f)
#    print("after pickle dump & load")
#    print(grammar)

if __name__ == '__main__':
     lexasm()
     print("lexasm done")

