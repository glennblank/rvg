
#********** lexasm assembles RVG lexicons for readable source code into vectors and other structures ****
# A lexicon consists of a collection of lexical entries 

reserved = {
   'entries' : 'ENTRIES',
   'e'       : 'ENTRY',
   'macros_cat' : 'MACROS_CAT'
}

literals = "+-?.#"

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
    file_name = input('Enter .lex file name:') + ".lex"
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
productions = grammar[2]

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
        if not tok: error_exit("productions then initfinal","EOF")
        if tok.type == 'NAME': featureLabels.append(tok.value)
        else: break

macroCats_dict = { }

def macros_cat():
    global tok
    macroName = None
    macroCategories = [ ]
    while True:
        tok = lexer.token()
        if not tok: return
        if (tok.value == '#' or tok.type == 'ENTRIES') and macroName: 
            macroCats_dict[macroName] = macroCategories
            #print("Macro: " + macroName)
            #print(macroCats_dict[macroName])
            if tok.type == 'ENTRIES': return  #last macro defined
            macroName = tok.value  #Set up a new macro
            macroCategories = []   #Set up a new macro categories list  
        if tok.value == '#':
            tok = lexer.token()
            macroName = tok.value
            continue
        if tok.type == 'NAME':  #Add category to categories list
            i = 0   # Look for index of production matching category name
            found = False
            for p in productions:
                if tok.value == p[0]:       #first item in production is its name
                    macroCategories.append(i)    #add its index to list
                    found = True
                    break
                else: i+=1
            if not found: error_exit("category name",tok.value)

def get_categories(categories):
    global tok
    tok = lexer.token()
    section_header('cat',True)
    while True:
        tok = lexer.token()
        if not tok or tok.type == 'ENTRY':
            break
        
        if tok.value == "#":    #Found a macro
            tok = lexer.token()
            macroCategories = macroCats_dict[tok.value]
            categories.extend(macroCategories)
            continue

        i = 0   # Look for index of production matching category name
        found = False
        for p in productions:
            if tok.value == p[0]:       #first item in production is its name
                categories.append(i)    #add its index to list
                found = True
                break
            else: i+=1
        if not found: error_exit("production name",tok.value)
    return categories

from Vectors import TernVec
lexDict = dict()  #Lookup can find a single lexEntry or a list of lexEntry

def entries_section():
    global tok
    tok = lexer.token()
    if section_header("macros_cat",False):
        macros_cat()
        #print(macroCats_dict)
    section_header('entries',True)
    tok = lexer.token()
    index = 0               #index of lexEntry in lexicon

    while True:
        if not tok:
            break
        section_header('e', True)  
        tok = lexer.token()
        if tok.type == 'NAME':
            spelling = tok.value.lower()
        elif tok.value in literals:
            spelling = tok.value
        else:
           error_exit("spelling",tok.value)
        #tok = lexer.token()
        #section_header('cond', True)
        #condVector = parse_vector()

        categories = get_categories([])

        lexEntry = (spelling,categories)
        #print(lexEntry)
        lexicon.append(lexEntry)
        
        #add spelling to lexDict for lookup with index to lexicon
        if spelling not in lexDict: lexDict[spelling] = [index]
        else: lexDict[spelling].append(index)
        index = index + 1

def lexasm():
    global data
    data = get_data(data)
    entries_section()
    print(lexDict)
    
    f = open('lexicon.pkl', 'wb')
    pickle.dump(lexicon,f)
    pickle.dump(lexDict,f)
    f.close

if __name__ == '__main__':
     lexasm()
     print("lexasm done")

