# rvgProcessor reads sentences and processes them in linear time
import Vectors  # TernVec 

#   Get last assembled grammar
import pickle
#Import the last assembled grammar and lexicon
f = open('grammar.pkl', 'rb')
grammar = pickle.load(f)
featureLabels, productions, initFinal = grammar[0], grammar[1], grammar[2]

initStateVec = Vectors.TernVec()    #For now, state is just a StateVec
initStateVec.change3(productions[initFinal][2]) #init state is changeVec of initFinal production

f = open('lexicon.pkl', 'rb')   #Open the last assembled lexicon
lexicon = pickle.load(f)    # list of lexical entires to be constructed

#Open sentence file
#   file_name = input('Enter .syn file name:')
sentence_file_name = "sentin.txt"
sentence_file = open(sentence_file_name, "r")

def get_sentence(sentence_file):
    "Read a line from sentence_file and return it as a list of tokens."
    line = sentence_file.readline()
    if not line:
        return None
    while '%' in line:
        print("Skipping comment: " + line)
        line = sentence_file.readline()
    print(line, end='')
    line = line.lower()
    if '.' in line:
        i = line.index('.')
        line = line[:i] + ' ' + line[i:]
    if '?' in line:
        i = line.index('?')
        line = line[:i] + ' ' + line[i:]
    return line.split()

def process_Sentence(sentence, nextWord, StateReg, Trace):
    "Look up words in lexicon, maatch and change state register until reaching Final state"
    word = sentence[nextWord]
    lexentry = None
    for lex in lexicon: #Find lexical entry in Lexicon
        if lex[0] == word:  #A simplistic lookup to be improved with mroph trie later
            lexentry = lex[0]   #Retrive matching lexentry
            categories = lex[1] #Retrieve production list from lexentry 
            break
    if not lexentry:
        print(word + " is not in lexicon")
        return

    i = 0
    matchedAlready = []
    while i < len(categories):
        prodIndex = categories[i]
        if prodIndex in matchedAlready:
            i += 1
            continue
        (prodName,condVector,changeVector,actions) = productions[prodIndex]
        i += 1
#        print(lexentry + " " + prodName)
        if StateReg.match3(condVector):
            Trace += prodName + ":"
            StateReg.change3(changeVector)
            if actions and actions[0] == "lex": #For now, only action is lex
                Trace += lexentry + " "
                nextWord += 1   #advance to next word
                if nextWord == len(sentence):
                    if StateReg.match3(initStateVec):
                        print("parse succeeds")
                    else:
                        print("parse fails to match final state")
                    return Trace
                return process_Sentence(sentence, nextWord, StateReg, Trace)
            matchedAlready.append(prodIndex)
            i = 0   #Recycle through categories until action lex
    print("parse fails to reach final state")
    return Trace

def rvg():
    print("Wlecome to RVG")
    while (True):
        sentence  = get_sentence(sentence_file)
        if sentence == None:
            return
        print(sentence)
        Trace = process_Sentence(sentence, 0, initStateVec, "")
        print(Trace+'\n')

if __name__ == '__main__':
    rvg()
    

