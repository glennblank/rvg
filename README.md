rvg
===
Register Vector Grammar (RVG) is an architecture for natural language processing that processes sentences in linear time.

Glenn Blank published papers describing RVG in Communications of the ACM, Vol. 32, No. 10. "A finite and real-time processor for natural language,
"Semantic interpretation in linear time in the ATIS domain" in Applied Intelligence, 1995 / 10 Vol. 5; Iss. 4, https://ur.booksc.eu/book/6318458/bcd8fa, etc.

At its core, RVG is a finite state machine in which states are Vectors of ternary valued features (+, -, or ?).
The third value (?) can match either + or - values and will not change either + or 1. 
Thus ternary value vectors can propagate constraints through a state Register Vector.

Version 0.1 illustrate with a simple example, involving WH-questions.

For example:

```
Who does Marcha love?
produces the syntactic trace:
WH:who QUES:does SUBJ:NAME:george VERB:love OBJ:NGAP:CLOSE:? 
```

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
python lexasm.py assembles a lexicon of words with syntactic categories corresponding to productions in the grammar. In version 0.1, the lexicon is wh.lex.

Version 0.2 demonstrates how RVG processes embedding similarly to the human sentence proecssor. Right-embedding can iterate indefinietly in the same space, i.e., 
Martha owns a stick that beat the dog that beat the cat that ate the kid.
Center-embedding is sharply limited in human sentence processing and can thus requires only storing state in one register, rather than an unbounded stack:
The robot that the man who loves Martha owns broke. 
That's about as much center-embedding of relative clauses as we're likely to generate or understand easily (i.e, in linear time).

Version 0.3 also demonstrates how gap constraint from Wh-questions can pass through any number of Complement clauses:
Who does the woman believe that George saw that Martha loves?
RVG handles long-distance discontinuities that gives transformational or phrase structure grammars fit

Version 0.4 (May 2022) adds boundary backtracking, so that RVG can handle ambiguity by backtracking to a finite set of registers associated with grammatical boundaries (such as Subject, Predicate, Object, start of Noun Phrase and NP post-modifiers, Prepositon).
So long as the number of registers to which the processor can backtrack, overall processing time is linear, just as human sentence processing is. Morever, finite regisg
er resources accounts for "garden-path" processing which are beyond the capacity of registers, which the processor reuses.

### Dependencies

`rvgprocessor.py` reads `gramasm.pkl` and `lexicon.pkl`, which `gramasm.py` and `lexasm.py` assemble from source code in `wh.syn` and `wh.lex`, respectively. Grammars and lexicons can be edited in a text editor and reassembled, though for version 0.1, wh.syn and wh.lex are hard-wired into gramasm.py and lexasm.py, respectively.

gramasm.py and lexasm.py use `PLY`, a Python implmeentation of YACC as a tokenizer of RVG grammars and lexicons. See https://github.com/dabeaz/ply

#### Install Requirements

To install all required dependencies for this project, execute:

```bash
pip install -r requirements.txt
```

### Running

(Prerequisites: `Python 3.9`)

To try out this project locally (after installing the files from this repository and going to this directory), execute:

```bash
python3 rvg.py
```
RVG will prompt for the name of a sentence file, for version 0.2, enter either wh or rel (for sentin.wh of version 0.1 or sentin.rel of version 0.2).

In version 0.3, RVG accepts an argument to STEP through each production and action, while showing state vectors and cond vectors:

```bash
python3 rvg.py -s
```

In version 0.4, RVG also accepts an argument to orshow behavior of backtracking, i.e., when the processor explicitly saves state and when it backtracks. 

```bash
python3 rvg.py -b
```
To reassemble the grammar `rel.syn` (see note about PLY above):

```bash
python3 gramasm.py
```

gramasm will then prompt for a .syn file; wh and rel are available (rel.syn incorporates grammar of wh.syn and bregs.syn incorporate the grammatical capacity of wh.syn and rel.syn, so that it can parse sentin.wh, sentin.rel and sentin.bregs.

To reassemble the lexicon `rel.lex` (see note about PLY above):

```bash 
python3 lexasm.py
```

lexasm will then prompt for a .lex file; wh and rel are available (rel.lex incorporates lexicon capability of rel.lex)

Glenn D. Blank, 10/12/2021 (0.1), 10/27/2021 (0.2), 11/25/2021 (0.3), 5/25/2022 (0.4)