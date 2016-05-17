# -*- coding: utf-8 -*-
import os
import pgf
from subprocess import call

def graphElement(name,gr,e):
    gStr = gr.graphvizAbstractTree(e)
    f = open(name,'w')
    f.write(gStr)


QSPNeg = False
QSPPos = False
QSproblem = False
QSmedvetslos = False
QSandning = ["breathe_V", "andning_nn_1_N"]
def dpsQS(e,term):
    global QSPNeg
    global QSproblem
    global QSPPos
    global QSmedvetslos
    eNext = e.unpack()

    if (eNext[0] == "UseCl"):
        for expr in eNext[1]:
            if (str(expr) == "PNeg"):
                QSPNeg = True
    if (eNext[0] == "UseV"):
        for expr in eNext[1]:
            for andn in QSandning :
                if (str(expr) == andn):
                    QSproblem = True

    if (eNext[0] == "UseCl"):
        for expr in eNext[1]:
            if (str(expr) == "PPos"):
                QSPPos = True

    if (eNext[0] == "medvetsloes_av_1_1_A"):
        QSmedvetslos = True

    for expr in eNext[1]: # för varje barn så kör vi dps igen
        dpsQS(expr, term)


# ---------------------------------------------------------------- QS slut


## MAIN ##
gr = pgf.readPGF("BetterLang.pgf")
swe = gr.languages["BetterLangSwe"]

i = 0
j = 0
#3981886gf
with open('test.txt', 'r') as reader:

    # Parse tree ----------------------------------
    for line in reader:
        i = swe.parse(line)
        p, e = i.next()

        fil = open("graf" + str(j) + ".dot", 'w')
        fil.write(gr.graphvizAbstractTree(e))
        fil.close()
        os.system("dot -Tpng graf" + str(j) + ".dot -o graf" + str(j) + ".png")
        j = j + 1
    reader.seek(0)


    # QS ----------------------------------------------
    QSetta = False
    wordcount = 0

    for line in reader:
        wordcount = wordcount + len(line.split()) # räknar antal ord

        i = swe.parse(line)
        p,e = i.next()

        if wordcount < 500:
            QSPNeg = False
            QSPPos = False
            QSproblem = False
            QSmedvetslos = False
            dpsQS(e,"")

            #QS True
            if((QSPNeg == True and QSproblem == True) or
               (QSPPos == True and QSmedvetslos == True)):
                print("QS: 1")
                QSetta = True
                break
    #QS False
    if (QSetta == False):
        print("QS: 0")
