#!/usr/bin/env python3.9
# rvgProcessor reads sentences and processes them in linear time
import Vectors  # TernVec 

#   Get last assembled grammar
import pickle
#Import the last assembled grammar and lexicon
f = open('grammar.pkl', 'rb')
grammar = pickle.load(f)
featureLabels, productions, initFinal = grammar[0], grammar[1], grammar[2]

SynStateVec = Vectors.TernVec()     #Current state register is a Ternary Vector 
initStateVec = Vectors.TernVec()    #Inital state vector for each sentence
initStateVec.change3(productions[initFinal][2]) #init state is changeVec of initFinal production
SynStateVec.change3(initStateVec)   #Initialize current state register with initFinal produciton

#One register suffices to process center-embedding of relative clauses
RelClauseReg = Vectors.TernVec()

f = open('lexicon.pkl', 'rb')   #Open the last assembled lexicon
lexicon = pickle.load(f)    # list of lexical entires to be constructed

def get_sentence(sentence_file):
    "Read a line from sentence_file and return it as a list of tokens."
    line = sentence_file.readline()
    if not line:
        return None
    while '%' in line:
        print(line, end='')     #show comment in output
        line = sentence_file.readline()
    print(line, end='')         #show sentence in outpu
    line = line.lower()
    if '.' in line:
        i = line.index('.')
        line = line[:i] + ' ' + line[i:]
    if '?' in line:
        i = line.index('?')
        line = line[:i] + ' ' + line[i:]
    return line.split()         #tokenize sentence (morphology will improve this way of analyzing words)

STEP = None 

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
        Trace += word
        return Trace

    global STEP
    i = 0
    matchedAlready = []
    while i < len(categories):
        prodIndex = categories[i]
        if prodIndex in matchedAlready:
            i += 1
            continue
        (prodName,condVector,changeVector,actions) = productions[prodIndex]
        if STEP == "step":
            print("Comparing StateReg and condVector of " + prodName + ":")
            StateReg.showVec(featureLabels)
            condVector.showVec(featureLabels)
        i += 1
        if StateReg.match3(condVector):
            if STEP == "step":
                print(lexentry + " matched " + prodName + ". Enter s to step, n to go to next sentence:", end='')
                if input() == "n":
                    STEP = "next"

            Trace += prodName + ":"

            if actions: 
                for action in actions:
                    if action == "storeRel":                # Store SynState in a relative clause register
                        RelClauseReg.change3(StateReg)
                        Trace += action + ":"
                    elif action == "restoreRel":            # Restore from a relative clause register
                        StateReg.clear()                    # Prepare to restore SynState
                        StateReg.change3(RelClauseReg)      # Restore from RelClauseReg
                        Trace += action + ":"

                    elif action == "lex": #For now, only action is lex
                        Trace += lexentry + " "
                        nextWord += 1   #advance to next word
                        if nextWord == len(sentence):
                            if StateReg.match3(productions[initFinal][1]):   #Cond vector of InitFinalo produciton matches?
                                print("parse succeeds")
                            else:
                                print("parse fails to match final state")
                            return Trace

            StateReg.change3(changeVector)                                  #Upodate current State register
            return process_Sentence(sentence, nextWord, StateReg, Trace)    #process next word (tail recursion)
        matchedAlready.append(prodIndex)
        i = 0   #Recycle through categories until action lex

    print("parse fails to reach final state")
    return Trace

def rvg():
    print("Welcome to RVG.")    
    
    #Open sentence file, for version 02., either wh or rel (sentin.wh or sentin.rel)
    sentence_file_name = "sentin." + input("Enter a sentin file (either wh or rel):")
    sentence_file = open(sentence_file_name, "r")

    global STEP #Version 0.3 supports STEP mode for more details about matching prodductions
    while (True):                               #Loop for each sentence in sentence_file
        sentence = get_sentence(sentence_file)  #Tokenize a sentence
        if sentence == None:                    #No more sentences?
            break
        print(sentence)
        SynStateVec.change3(initStateVec)       #Initialize and reset registers (especially after a failed parse)
        RelClauseReg.clear()
        if STEP == "next":
            STEP = "step"

        Trace = process_Sentence(sentence, 0, SynStateVec, "")  #Process a sentence and return a syntactic Trace 
        print(Trace+'\n')                       #Trace is a strong of productions and actions taken to parse sentence

import sys
def main():
    global STEP
    if len(sys.argv) > 1 and sys.argv[1] == "step":
        STEP = "step"

if __name__ == '__main__':
    main()
    rvg()

