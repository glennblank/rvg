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

    def showVec(self,featureLabels,showAllValues):
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
        print('\n')
        return self

#PropVec is for future versions of RVG, not used at this time
agreeseg = 0
nonagreeseg = 64

class PropVec:
    """ BitVec have two two segments of binary properties: non-agreement bits then agreement bits
        agreeseg indexes the start of the agreement segment in property vectors
        agreeseg is assigned after reading in the grammar, computed by gramasm
    """

    def __init__(self):
        self.properties = 0    #Representing a bit vector using Pythons bitwise operators

    def clear(self):
        self.properties = 0

    def props(self):
        print(self.properties)
        return self.properties

    def setBit(self, atPos, value):
        """ Set property bit at atPos to on or off """
        if atPos > nonagreeseg:
            print(atPos + "out of range")
            return False

        bit_mask = 1
        bit_mask <<= atPos      #Set bit atPos on in bit_mask
        print("bit_mask:")
        print(bit_mask)
        if value == '+':
            self.properties |= bit_mask     #Turn bit at atPos on
        else:
            self.properties &= bit_mask     #Turn bit at atPos off
        return True


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print("Testing TernVec")
#t1 = TernVec()
#t2 = TernVec()
#t1.setFeature(1,'+')
#t1.setFeature(2,'-')
#t1.setFeature(3,'?')
#t2.setFeature(0,'-')
#t2.setFeature(1,'+')
#t2.setFeature(2,'-')
#t2.setFeature(3,'+')
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

#labels = ["S","V","O","P"]
#print("t1:")
#t1.setFeature(0,"+")
#t1.showVec(labels,True)

#t2.setFeature(1,"-")
#t2.setFeature(2,"+")
#print("t2:")
#t2.showVec(labels,True)

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
