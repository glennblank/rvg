class TernVec:
    """Purpose: ternary vector operators are the "machine" code of RVG.
       Logically, ternary vectors are ordered sequences of features,
       each of which have one of three possible values: +, -, or ?.
       On a binary machine, ternary vectors are implemented as pairs of binary
       vectors, each of which is as Int in Python.
       Calling the first integer in each pair HI, and the second LO,
       encode ternary values as follows:
       +HI & -LO ==> "+" ("1" or "on")
       -HI & +LO ==> "-" ("0" or "off")
       -HI & -LO ==> "?" ("2" or "mask)
       This particular code happens to make for a very efficient match3.
       """

    def __init__(self):
        self.HI = 0    #Representing a bit vector as an Int
        self.LO = 0    #Representing a bit vector as an Int

    def clear(self):
        self.HI = 0    #Set to "?"
        self.LO = 0    #Set to "?"

    def isClear(self):
        if self.HI == 0 and self.LO == 0:
            return True
        else:
            return False

    def setFeature(self, atPos, ternValue):
        """ Given an int atPos and a ternValue "+", "-", or "?", encode a feature in self TernVec """
        bit_mask = 1
        bit_mask <<= atPos  #Left shift to atPos
        if ternValue == '+':
            self.HI |= bit_mask     #Turn on HI bit
            self.LO &= ~bit_mask    #Turn off LO bit
        elif ternValue == '-':
            self.HI &= ~bit_mask    #Turn off HI bit
            self.LO |= bit_mask     #Turn on LO bit
        elif ternValue == '?':
            self.HI &= ~bit_mask    #Turn off HI bit
            self.LO &= ~bit_mask    #Turn off LO bit
        else:
            print("Invalid ternary value:" + ternValue)


    def match3(self,other):
        """ Two Ternary Vectors match if binary values or identical or either one is '?' """
        if self.HI & other.LO or self.LO & other.HI :
            return False
        else: return True

    def change3(self,other):
        """ Change self with other TernVec; "?" has no effect """
        AllOn = ~0     
        self.HI = (self.HI | other.HI) & (AllOn ^ other.LO)
        self.LO = (self.LO | other.LO) & (AllOn ^ other.HI)

    def refine3(self,other):
        """ Refine self '?' features  by other's '+' or "-" values (assumes they match) """
        self.HI |= other.HI
        self.LO != other.HI

    def showVec(self,featureLabels,showAllValues=True):
        """ Display a ternary vector in symbolic form.
            That is, print feature values (i.e. + - ?) and feature labels. E.g., +S -V
            IF showAllValues is True then print all feature values, including "?"
            ELSE only features with values of + or -
        """
        bit_mask = 1
        for fNum in range(0,len(featureLabels)):
            if self.HI & bit_mask:
                print('+', featureLabels[fNum], sep='', end=' ')
            elif self.LO & bit_mask:
                print(f'-', featureLabels[fNum], sep='', end=' ')
            elif showAllValues:
                print('?', featureLabels[fNum], sep='', end=' ')

            bit_mask <<= 1   #Left shift to next bit in vectors
        print(" ")   #print starts new line
        return self

class StateRegister:
    def __init__(self):
        self.SynStateVec = TernVec()
        self.nextWord = 0
        self.lexList = []
        self.lexIndex = 0
        self.prodList = []
        self.prodListIndex = 0
        self.trace = ""

from array import *

class BoundaryRegs:
    """ Boundary Registers maintain a fixed, finite amount of state information
        to which the sentence processor can backtrack """
    def __init__(self, howManyRegisters):
        self.HIValues = array('Q', [0] * howManyRegisters)  #Unsigned Long, 64 bits
        self.LOValues = array('Q', [0] * howManyRegisters)  #Unsigned Long, 64 bits
        self.nextWord = array('B', [0] * howManyRegisters)
        self.lexList = [None] * howManyRegisters
        self.lexIndex = array('B', [0] * howManyRegisters)
        self.prodList = [None] * howManyRegisters
        self.prodListIndex = array('B', [0] * howManyRegisters)
        self.trace = [""] * howManyRegisters
        self.resumes = list()
        self.lastResume = 0
        #self.resumes  = array('B', [0] * howManyRegisters)  #Unsigned Byte, 8 bits

    def clear(self):
        #self.lastResume = -1
        for i in range(len(self.HIValues)):
            self.HIValues[i] = 0
            self.LOValues[i] = 0
            self.nextWord[i] = 0
            self.lexList[i] = None
            self.lexIndex[i] = 0
            self.prodList[i] = None
            self.prodListIndex[i] = 0
            self.trace[i] = ""
            self.resumes.clear()
            self.lastResume = 0

    def save(self, boundaryIndex, stateReg):
        "save fromStateVec data to register at boundaryIndex and update lastResume"
        self.HIValues[boundaryIndex] = stateReg.SynStateVec.HI
        self.LOValues[boundaryIndex] = stateReg.SynStateVec.LO
        self.nextWord[boundaryIndex] = stateReg.nextWord
        self.lexList[boundaryIndex] = stateReg.lexList.copy()
        self.prodList[boundaryIndex] = stateReg.prodList.copy()
        self.prodListIndex[boundaryIndex] = stateReg.prodListIndex
        self.trace[boundaryIndex] = str(stateReg.trace)
        self.resumes.append(boundaryIndex)

    def resume(self, stateReg):
        "resume state from register at lastResume to toStateVec and update lastResume"

        #if self.lastResume < 0:
        #    return False    #Cannot resume any more states from boundary registers
        if not self.resumes:
            return False
        self.lastResume = self.resumes.pop()
        stateReg.SynStateVec.HI = self.HIValues[self.lastResume]
        stateReg.SynStateVec.LO = self.LOValues[self.lastResume]
        stateReg.nextWord = self.nextWord[self.lastResume]
        stateReg.lexList = self.lexList[self.lastResume]
        stateReg.prodList = self.prodList[self.lastResume]
        stateReg.prodListIndex = self.prodListIndex[self.lastResume]
        stateReg.trace = self.trace[self.lastResume]
        return True   

def test_TernVec():
    t1 = TernVec()
    t2 = TernVec()

    t1.setFeature(1,'+')
    t1.setFeature(2,'-')
    t1.setFeature(3,'?')
    t2.setFeature(0,'-')
    t2.setFeature(1,'+')
    t2.setFeature(2,'-')
    t2.setFeature(3,'+')
    #if t1.match3(t2):
    #    print("match3 succeeds")
    #else: print("match3 fails")
    #t2.setFeature(1,'-')
    #if t1.match3(t2):
    #    print("match3 succeeds")
    #else: print("match3 fails")
    #t2.setFeature(1,'?')
    #if t1.match3(t2):
    #    print("match3 succeeds")
    #else: print("match3 fails")

    labels = ["S","V","O","P"]
    print("t1:", end =" ")
    #t1.setFeature(0,"+")
    t1.showVec(labels,True)

    #t2.setFeature(1,"-")
    #t2.setFeature(2,"+")
    print("t2:", end =" ")
    t2.showVec(labels,True)

    #t1.change3(t2)
    #print("After change3, t2:")
    #t1.showVec(labels,True)

    #t1.clear()
    #t2.clear()
    #t2.setFeature(0,'-')
    #t2.setFeature(1,'+')
    #t2.setFeature(2,'?')
    #print("before t1.refine")
    #t1.refine3(t2)
    #print("t2 before refine3:")
    #t2.showVec(labels,True)

def test_bregs():
    #Testing BoundaryRegs for backtracking behavior, should reverse initial vectors
    ### Note: this test is now out of date
    bregs = BoundaryRegs(3)
    t1 = TernVec()
    t2 = TernVec()

    t1.setFeature(1,'+')
    t1.setFeature(2,'-')
    t1.setFeature(3,'?')
    t2.setFeature(0,'-')
    t2.setFeature(1,'+')
    t2.setFeature(2,'-')
    t2.setFeature(3,'+')
    
    labels = ["S","V","O","P"]
    print("t1:", end =" ")
    t1.setFeature(0,"+")
    t1.showVec(labels,True)

    t2.setFeature(1,"-")
    t2.setFeature(2,"+")
    print("t2:", end =" ")
    t2.showVec(labels,True)
 
    nextWord = 1
    lexList = []
    prodList = []
    prodIndex = 10
    Trace = ""
    stateReg1 = ( t1, nextWord, lexList, prodList, prodIndex, Trace )
    nextWord = 2
    prodIndex = 20
    stateReg2 = ( t2, nextWord, lexList, prodList, prodIndex, Trace )

    bregs.save(2,stateReg1)
    bregs.save(1,stateReg2)
    stateReg3 = ( t1, nextWord, lexList, prodList, prodIndex, Trace )
    bregs.resume(stateReg3)
 
    print("t1 after resume:", end =" ")
    t1.showVec(labels,True)
    print("nextWord=" + str(nextWord))
    
    stateReg4 = ( t2, nextWord, lexList, prodList, prodIndex, Trace )
    bregs.resume(stateReg4)
    print("t2 after resume:", end =" ")
    t2.showVec(labels,True)
    bregs.save(2,stateReg2) #Trigger reusing register behavior
    bregs.save(2,stateReg1) #Trigger reusing register behavior
    bregs.resume(stateReg2)
    print("t2 after resume:", end =" ")
    t2.showVec(labels,True)
    if bregs.resume(t1):
        print("Should bregs.resume fail?")
    else:
        print("bregs.resume returns false as it should")

#if __name__ == '__main__':
    #test_bregs()
