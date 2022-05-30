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

initStateVec = Vectors.TernVec()
initStateVec.change3(productions[initFinal][2]) #init state is changeVec of initFinal production

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

def lookupLex(sentence, currStateReg):
    word = sentence[currStateReg.nextWord]
    currStateReg.lexList = lexDict.get(word) #Find list of lexentry subscripts
    if not currStateReg.lexList:
        print(word + " is not in lexicon")
        currStateReg.trace += word
        return None
    return currStateReg.lexList

def tryActions(actions, currStateReg, sentence, prodName):
    for action in actions:
        if action == "lex": 
            currStateReg.trace += prodName + ":" + lexicon[currStateReg.lexList[currStateReg.lexIndex]][0] + " "
            currStateReg.nextWord += 1                  #advance to next word
            if currStateReg.nextWord == len(sentence):  #reached end of sentence
                if currStateReg.SynStateVec.match3(productions[initFinal][1]):   #Cond vector of InitFinal produciton matches?
                    print("parse succeeds: " + currStateReg.trace)
                    return None #For now, just returing one Trace per sentence
                else: 
                    print("parse reaches end of sentence but fails to match final state")
                    return None
            else: 
                currStateReg.lexList = lookupLex(sentence, currStateReg)   #look up next word (action lex looks up subsequent words)
                if not currStateReg.lexList: return None     #Lexical lookup fails                      lexEntry = lexLookup(sentence, state)
                else: 
                    currStateReg.lexIndex = 0
                    currStateReg.prodList = lexicon[currStateReg.lexList[currStateReg.lexIndex]][1].copy() #Retrieve lexEntry's production list
            return "lex"

        elif "save" in action:
            boundaryIndex = int(action[4:])
            bregs.save(boundaryIndex, currStateReg)
            if STEP: print("save:" + boundaryLabels[boundaryIndex])

        elif action == "storeRel":                # Store SynState in a relative clause register
            RelClauseReg.change3(currStateReg.SynStateVec)
            currStateReg.trace += action + ":"
        elif action == "restoreRel":            # Restore from a relative clause register
            currStateReg.SynStateVec.clear()    # Prepare to restore SynState
            currStateReg.SynStateVec.change3(RelClauseReg) # Restore from RelClauseReg
            currStateReg.trace += action + ":"

    return True

STEP = None 

def process_Sentence(sentence, currStateReg):
    "Parse a sentence, printing a trace, backtracking to boundary registers"
    "Look up words in lexicon, match and change state register until reaching Final state"

    global STEP
    currStateReg.lexList = lookupLex(sentence, currStateReg) #look up first word (action lex looks up subsequent words)
    if not currStateReg.lexList: return ""               #Lexical lookup fails

    furthestParse = ""
    startWithCurrStateReg = True
    while startWithCurrStateReg or bregs.resume(currStateReg): #Any boundary register to backtrack from?
        if startWithCurrStateReg: startWithCurrStateReg = False
        else: 
            if STEP: print("backtracking from "+boundaryLabels[bregs.lastResume] + " " + currStateReg.trace)

        while currStateReg.lexIndex < len(currStateReg.lexList) or currStateReg.prodListIndex < len(currStateReg.prodList): 
            if currStateReg.prodListIndex < len(currStateReg.prodList):
                currStateReg.lexIndex -= 1
            else: 
                lexEntry = lexicon[currStateReg.lexList[currStateReg.lexIndex]]  #retrieve a lexEntry from lexicon
                currStateReg.prodList = lexEntry[1].copy()  #Retrieve production list from lexEntry
                currStateReg.prodListIndex = 0

            while currStateReg.prodListIndex < len(currStateReg.prodList):
                lexEntry = lexicon[currStateReg.lexList[currStateReg.lexIndex]]  #retrieve a lexEntry from lexicon
                prodIndex = currStateReg.prodList[currStateReg.prodListIndex]
                (prodName,condVector,changeVector,actions) = productions[prodIndex]
                if STEP == 1:
                    print(currStateReg.trace + "\nComparing SynStateVec and condVector of " + prodName + ":")
                    currStateReg.SynStateVec.showVec(featureLabels)
                    condVector.showVec(featureLabels)
                if currStateReg.SynStateVec.match3(condVector):
                    currStateReg.prodList.pop(currStateReg.prodListIndex) #remove matching production in this cycle
                    currStateReg.prodListIndex = 0           #recycle thru productions until lex action    
                    if STEP == 1:
                        print(lexEntry[0] + " matched " + prodName + ". Enter s to step, n to go to next sentence:", end='')
                        if input() == "n": STEP = "next"
 
                    if actions:
                        result = tryActions(actions, currStateReg, sentence, prodName)
                        if result == None: return None
                                             
                    currStateReg.SynStateVec.change3(changeVector)  #Update current SynStateVec (register)
                    if result != "lex": currStateReg.trace += prodName + ":"
                    else: result = True
                else: currStateReg.prodListIndex += 1 #match3 fails, try next production
            currStateReg.lexIndex += 1 #Done with productions, consider next lexEntry
        if len(currStateReg.trace) > len(furthestParse): furthestParse = currStateReg.trace 
    print("Parse fails at: " + furthestParse)

def rvg(step):
    print("Welcome to RVG.")    
    
    while True:
        extension = input("Enter a sentin file extension (wh, rel or bregs):")
        if extension in ("wh","rel","bregs"): break
        else: print("Sentin files available are wh, rel or bregs")
    sentence_file_name = "sentin." + extension
    sentence_file = open(sentence_file_name, "r")

    global STEP #Version 0.3 supports STEP mode for more details about matching productions
    STEP = step
    while True:                               #Loop for each sentence in sentence_file
        sentence = get_sentence(sentence_file)  #Tokenize a sentence
        if sentence == None:                    #No more sentences?
            break
        print(sentence)
        currStateReg = Vectors.StateRegister()
        currStateReg.SynStateVec.change3(initStateVec) #Initialize and reset registers (especially after a failed parse)
        bregs.clear()
        RelClauseReg.clear()
        if STEP == "next": STEP = 1

        #STEP="step"
        process_Sentence(sentence, currStateReg)  #Process a sentence and return a syntactic Trace 
        input()
        

import sys

def main():
    global STEP
    if len(sys.argv) > 1 and sys.argv[1] == "step":
        STEP = "step"

if __name__ == '__main__':
    main()
    rvg()

