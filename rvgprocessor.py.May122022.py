#!/usr/bin/env python3.9
# rvgProcessor reads sentences and processes them in linear time
from trace import Trace
import Vectors  # TernVec 

#   Get last assembled grammar
import pickle
#Import the last assembled grammar and lexicon
f = open('grammar.pkl', 'rb')
grammar = pickle.load(f)
featureLabels, boundaryLabels, productions, initFinal = grammar[0], grammar[1], grammar[2], grammar[3]

SynStateVec = Vectors.TernVec()     #Current state register is a Ternary Vector 
initStateVec = Vectors.TernVec()    #Inital state vector for each sentence
initStateVec.change3(productions[initFinal][2]) #init state is changeVec of initFinal production
SynStateVec.change3(initStateVec)   #Initialize current state register with initFinal produciton

#One register suffices to process center-embedding of relative clauses
RelClauseReg = Vectors.TernVec()
#Boundary registers save state for boundary backtracking
bregs = Vectors.BoundaryRegs(len(boundaryLabels))

f = open('lexicon.pkl', 'rb')   #Open the last assembled lexicon
lexicon = pickle.load(f)    # list of lexical entires to be constructed
lexDict = pickle.load(f)    # dictionary for looking up lexical entries

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

def lookupLex(sentence, state):
    ( SynStateVec, nextWord, lexList, prodList, prodIndex, Trace ) = state
    word = sentence[nextWord]
    lexList = lexDict.get(word) #Find list of lexentry subscripts
    #print(lexList)
    if not lexList:
        print(word + " is not in lexicon")
        Trace += word
        return None
    return lexList.copy()

STEP = None 

def process_Sentence(sentence, stateReg):
    "Parse a sentence, printing a trace, backtracking to boundary registers"
    "Look up words in lexicon, match and change state register until reaching Final state"
    ( SynStateVec, nextWord, lexList, prodList, prodIndex, Trace ) = stateReg

    lexList = lookupLex(sentence, stateReg) #look up first word (action lex looks up subsequent words)
    if not lexList: return Trace            #Lexical lookup fails

    global STEP
    
    while lexList: #Boundary backtracking loop
        lexEntry = lexicon[lexList.pop()]  #retrieve a lexEntry from lexicon
        prodList = lexEntry[1].copy()  #Retrieve production list from lexEntry
        prodListIndex = 0

        while prodListIndex < len(prodList):
            prodIndex = prodList[prodListIndex]
            (prodName,condVector,changeVector,actions) = productions[prodIndex]
            if STEP == "step":
                print("Comparing SynStateVec and condVector of " + prodName + ":")
                SynStateVec.showVec(featureLabels)
                condVector.showVec(featureLabels)
            if SynStateVec.match3(condVector):
                if STEP == "step":
                    print(lexEntry[0] + " matched " + prodName + ". Enter s to step, n to go to next sentence:", end='')
                    if input() == "n": STEP = "next"
                Trace += prodName + ":"     #add successful production name to Trace
                prodList.pop(prodListIndex) #remove matching production in this cycle
                prodListIndex = 0           #recycle thru productions until lex action    
                print("prodList=" + str(prodList))

                for action in actions:
                    if action == "storeRel":                # Store SynState in a relative clause register
                        RelClauseReg.change3(SynStateVec)
                        Trace += action + ":"
                    elif action == "restoreRel":            # Restore from a relative clause register
                        SynStateVec.clear()                    # Prepare to restore SynState
                        SynStateVec.change3(RelClauseReg)      # Restore from RelClauseReg
                        Trace += action + ":"
        
                    elif action == "lex": 
                        Trace += lexEntry[0] + " "
                        nextWord += 1   #advance to next word
                        if nextWord == len(sentence):   #reached end of sentence
                            if SynStateVec.match3(productions[initFinal][1]):   #Cond vector of InitFinalo produciton matches?
                                print("parse succeeds")
                                return Trace #For now, just returing one Trace per sentence
                            else: print("parse reaches end of sentence but fails to match final state")
                        else: 
                            stateReg = ( SynStateVec, nextWord, lexList, prodList, prodIndex, Trace )
                            lexList = lookupLex(sentence, stateReg)   #look up next word (action lex looks up subsequent words)
                            if not lexList: return Trace           #Lexical lookup fails                      lexEntry = lexLookup(sentence, state)
                            else: 
                                print(lexicon[lexList[0]])
                                lexListIndex = 0
                                prodListIndex = len(prodList) + 1   #break out of production cycle
                        continue

                    elif "save" in action:
                        boundaryIndex = int(action[4:])
                        stateReg = ( SynStateVec, nextWord, lexList, prodList, prodIndex, Trace )
                        bregs.save(boundaryIndex, stateReg)
                        print("save:" + boundaryLabels[boundaryIndex])

                SynStateVec.change3(changeVector)  #Update current SynStateVec (register)
            else: prodListIndex = prodListIndex + 1 #match3 fails, try next production
            #lexListIndex = lexListIndex + 1  #Done with productions, remove this lexEntry from consideration
        #resume restore stateReg from a boundary register
        if lexList: continue
        if bregs.resume(stateReg): #Any more boundaries to backtrack from?
            ( SynStateVec, nextWord, lexList, prodList, prodIndex, Trace ) = stateReg
            print("backtracking from "+Trace)
            SynStateVec.showVec(featureLabels)
            input()
        else: 
            print("parse fails to reach final state")
            return Trace

def rvg(is_step=False):
    print("Welcome to RVG.")    
    
    #Open sentence file, for version 02., either wh or rel (sentin.wh or sentin.rel)
    sentence_file_name = "sentin." + input("Enter a sentin file (bregs, wh or rel):")
    sentence_file = open(sentence_file_name, "r")

    global STEP #Version 0.3 supports STEP mode for more details about matching productions
    STEP = "step" if is_step else None
    while (True):                               #Loop for each sentence in sentence_file
        sentence = get_sentence(sentence_file)  #Tokenize a sentence
        if sentence == None:                    #No more sentences?
            break
        print(sentence)
        SynStateVec.change3(initStateVec)       #Initialize and reset registers (especially after a failed parse)
        RelClauseReg.clear()
        if STEP == "next":
            STEP = "step"
        state = ( SynStateVec, 0, 0, [], 0, "" ) #Initialize state tuple

        Trace = process_Sentence(sentence, state)  #Process a sentence and return a syntactic Trace 
        if Trace: print(Trace+'\n')                #Trace is a string of productions and actions taken to parse sentence
        input()

import sys

def main():
    global STEP
    if len(sys.argv) > 1 and sys.argv[1] == "step":
        STEP = "step"

if __name__ == '__main__':
    main()
    rvg()

