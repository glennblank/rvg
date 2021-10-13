# rvg
Register Vector Grammar (RVG) is an architecture for natural language processing that processes sentences in linear time.

Glenn Blank published papers describing RVG in Communications of the ACM, Vol. 32, No. 10. "A finite and real-time processor for natural language,
"Semantic interpretation in linear time in the ATIS domain" in Applied Intelligence, 1995 / 10 Vol. 5; Iss. 4, https://ur.booksc.eu/book/6318458/bcd8fa, etc.

At its core, RVG is a finite state machine in which states are Vectors of ternary valued features (+, -, or ?).
The third value (?) can match either + or - values and will not change either + or 1. 
Thus ternary value vectors can propagate constraints through a state Register Vector.

Version 0.1 illustrates with a simple example. Subsequent versions will add other aspects of RVG described in the aforementioned papers.

For example:
Who does Marcha love?
produces the syntactic trace:
WH:who QUES:does SUBJ:NAME:george VERB:love OBJ:NGAP:CLOSE:? 
The word "who" triggers a production WH, whose change vector turns on feature GAP (+GAP) in the state register.
The final production CLOSE requires -GAP in the state regsiter. So somewhere between WH and CLOSE, GAP must be turned off.
Most productions, such as QUES and VERB in this example, ignore feature GAP, i.e., ?GAP in both condition and change vectors.
Thus + for feature GAP passes through productions QUES and VERB in the state Register Vector.
Production NGAP has +GAP in its condition vector and -GAP its change vector. So it can match GAP and turn it off. 
Production NGAP also requires +DET..HEAD (the features for a noun phrase) in its condition vector and and -DET..HEAD in its change vector.
So production NGAP effectively recognize a gap where a noun phrase is expected.
Productions SUBJ and OBJ turn on +DET.. HEAD for a noun phrase, in the appropriate states (SUBJ before VERB and OBJ after VERB).
Thus For this sentence, between "love" and "?", production OBJ fires, then production NGAP, and finally CLOSE.
Thus syntactic constraints propagate efficiently through the state Register Vector.

This respository is implemented in Python 3.9.x. (Earlier implementations were in Stepstone Objective-C, no longer available.)

Version 0.1 demonstates how RVG processes WH-questions: following the words who or what, there must be a noun phrase gap in the sentence.
python rvg parses sentences from sentin.txt, production syntactic traces like the one shown above.
python gramasm.py assembles a grammar, a collection of production rules with ternary vector conditions and changes. In versjon 0.1, the grammar is in wh.syn.
python lexasm.py assembles a lexicon of words with syntactic categories corresponding to productions in the grammar. In vesion 01, the lexicon is wh.lex

### Running
(Prerequisites: Python 3.9)
To try out this project locally (after installing the files from this repository and going to this directory), execute:
python3.9 rvg.py
Glenn D. Blank, 10/12/2021
