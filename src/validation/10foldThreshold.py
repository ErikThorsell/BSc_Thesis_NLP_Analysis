# -*- coding: utf-8 -*-

#import nltk
from statistics import mean
import csv
import math
import string
from os import listdir
from os.path import isfile, join
import re
from collections import Counter
import sys

## Home made libraries ##
from methods import chunks, getSets, avgMethod, knnMethod, centerMethod


###
# 10foldThreshold.py [method] [mode] [iKnowFile]
### SET MODE ###
#   mode = 0 : Calculate best threshold
#   mode = 1 : Calculate error costs
#   mode = 2 : Calculate precision/recall curve
#   mode = 3 : Calculate ROC-plot
#   mode = 4 : Calculate and print thresh
if(len(sys.argv) != 4):
    print ("mode = 0 : Calculate best threshold")
    print ("mode = 1 : Calculate error costs")
    print ("mode = 2 : Calculate precision/recall curve")
    print ("mode = 3 : Calculate ROC-plot")
    print ("mode = 4 : Calculate and print thresh")
    print ("10foldThreshold.py [method] [mode] [iKnowFile]")
    sys.exit()

method      = sys.argv[1]
mode        = int(sys.argv[2])
iKnowFile   = sys.argv[3]

if(method == "knn"):
    knnK = int( input("Enter k for KNN algorithm: ") )




### READERS ###
def iKnowFileRead(iKnowFile):
    with open(iKnowFile , 'r') as file:
        currentRow = []
        currentSource = 1
        for line in file:

            # The program expects one line with just a source id
            # followed by any number of lines with data
            # srcId INTEGER, extId VARCHAR, percentageMatched NUMERIC,
            # percentageNew NUMERIC, nbOfEntsInRefSrc INTEGER,
            # nbOfEntsInCommon INTEGER, nbOfEntsInSimSrc INTEGER, score NUMERIC


            # Checks if the current line is a line with data or just a id
            # Data lines starts with: lb(...
            startStr = 'lb('
            start = line.find( startStr ) + len(startStr)
            if(start > -1 + len(startStr) ):
                end = line.rfind(')')
                csvStr = line[start:end]

                csvList = csvStr.split(',')

                # Change full file path to just call id.
                csvList[1] = csvList[1][-12:-5]

                #iKnow2call.add( (csvList[0], csvList[1]) )
                currentRow.append( [csvList[1], float(csvList[7])] )
            else:

                if( len(currentRow) > 0):

                    ## make similairty matrix
                    similairtyMatrix[currentSource] = {}
                    for row in currentRow:
                        similairtyMatrix[currentSource][row[0]] = row[1]
                        #print(currentSource + " " + row[0] + " " +  str(row[1]) )
                    #####


                # Start new row
                currentSource = line[-12:-5]

                # Last line
                if currentSource:
                    pattern = re.compile("^\d{7}$")
                    if not pattern.match(currentSource):
                        print("Bad call id: " + currentSource)
                        exit()
                currentRow = []

    return similairtyMatrix

def gensimFileRead(gensimFile):
    with open(gensimFile, 'r') as file:
        currentRow = []
        currentSource = 1

        for line in file:
            startStr = 'ID'
            start = line.find( startStr )

            if(line != '\n' and start == -1):
                csvList = line.split(',')
                currentRow.append( [csvList[0], float(csvList[1])] )
            else:
                if( len(currentRow) > 0):
                    ## make similairty matrix
                    similairtyMatrix[currentSource] = {}
                    for row in currentRow:
                        similairtyMatrix[currentSource][row[0]] = row[1]

                currentSource = line[3:-1]
                currentRow = []
                if currentSource:
                    pattern = re.compile("^\d{7}$")
                    if not pattern.match(currentSource):
                        print("Bad call id: " + currentSource)
                        exit()

        return similairtyMatrix


### Methods ###
def chunks(l,n):
    for i in range(0, len(l), n):
        yield l[i:i+n]

def getSets(l,k):
    sets = []

    size = int(len(l)/k+0.5)

    folds =  list( chunks(l,size) )


    for i in range(0,k):
        bigList = [item for item in folds if (folds[i] != item)]
        flatBigList = ([item for sublist in bigList for item in sublist] )
        sets.append( (folds[i],  flatBigList) )

    return sets


def avgMethod(rows):
    matchGood = 0
    matchBad = 0
    totGood = 0
    totBad = 0

    row = [0,0]
    for dictRow in rows:
        row[0] = dictRow
        row[1] = rows[dictRow]


        if( row[0] in trainingCalls ):
            statusTarget = not (row[0] in badCalls)

            if(statusTarget):
                matchGood = matchGood + row[1]
                totGood = totGood + 1
            else:
                matchBad = matchBad + row[1]
                totBad = totBad + 1

    if(totBad == 0):
        percentBad = 0
    else:
        percentBad  = round(float(matchBad)/totBad*100, 3)

    if(totGood == 0):
        percentGood = 0
    else:
        percentGood = round(float(matchGood)/totGood*100,3)

    # Threshold calculation
    certainty = round( percentGood - percentBad , 3 )
    return certainty

def minMethod(rows):
    matchGood = 0
    matchBad = 0


    row = [0,0]
    for dictRow in rows:
        row[0] = dictRow
        row[1] = rows[dictRow]

        if( row[0] in trainingCalls ):
            statusTarget = not (row[0] in badCalls)

            if(statusTarget):
                if(row[1]>matchGood):
                    matchGood = row[1]
            else:
                if(row[1]>matchBad):
                    matchBad = row[1]

    # Threshold calculation
    certainty = round( matchGood - matchBad , 3 )
    return certainty

def knnMethod(rows,k):
    matchGood = 0
    matchBad = 0
    matches = []

    row = [0,0]
    for dictRow in rows:
        row[0] = dictRow
        row[1] = rows[dictRow]

        if( row[0] in trainingCalls ):
            statusTarget = not (row[0] in badCalls)

            matches.append( (row[1], statusTarget))

    ## Calculate KNN
    matches.sort(key=lambda tup: -tup[0])                   # desc sort
    matches = matches[:k]                                   # k best matches
    matchGood = len( [item for item in matches if item[1]]) # count good
    matchBad = len(matches) - matchGood

    ## KNN => cerainty
    certainty = round( matchGood - matchBad , 3 )

    return certainty



def centerMethod(matrix, current):
    eccentricity = 0

    # [(BadCallId, distance to all other bad calls), (GoodCallId, dist to all good)]
    res = [(0,math.inf), (0,math.inf)]
    # find center
    for row in matrix:
        if( row in trainingCalls ):
            candidateStatus = not (row in badCalls)
            eccentricity = 0
            for subrow in matrix[row]:
                if( subrow in trainingCalls ):
                    targetStatus = not (subrow in badCalls )
                    if( targetStatus == candidateStatus and matrix[row][subrow] > eccentricity ):
                        eccentricity = matrix[row][subrow]


            #print( row + " " + str(candidateStatus) + " " +  str(eccentricity) )
            if( eccentricity < res[candidateStatus][1]  ):
                res[candidateStatus] = (row,eccentricity)


    matchBad = 0
    matchGood = 0
    if( res[0][0] in  matrix[current].keys() ):
        #print( current + " " + res[0][0] + " = " + str(matrix[current][res[0][0]]) )
        matchBad  = matrix[current][res[0][0]]
    #else:
        #print( res[0][0] + " not found, matchBad=0" )

    if( res[1][0] in matrix[current].keys() ):
        #print( current + " " + res[1][0] + " = " + str(matrix[current][res[1][0]]) )
        matchGood = matrix[current][res[1][0]]
    #else:
        #print( res[1][0] + " not found, matchGood=0" )
    certainty = matchGood - matchBad
    return certainty










# List of bad calls
badCalls = ["3970080","4032151","4034158","4039565","4041865","4054897","4057710",
            "4077552","4095497","4100887","4102478","4106859","4133450","4135090",
            "4139046","4151091","4163444"]

allCalls = ["2048204",      "3989879",      "4007925",  "4063312",
            "3970080",      "3989960",      "4008646",  "4067849",
            "3970214",      "3991176",      "4008766",  "4077552",
            "3971681",      "3991726",      "4012620",  "4095497",
            "3971881",      "3992294",      "4015460",  "4100887",
            "3973691",      "3993003",      "4018071",  "4102478",
            "3973834",      "3993462",      "4025548",  "4106859",
            "3975547",      "3994151",      "4031845",  "4133450",
            "3977158",      "3996055",      "4032151",  "4135090",
            "3977631",      "3996208",      "4034158",  "4139046",
            "3977900",      "3999610",      "4039565",  "4151091",
            "3978040",      "4040583",      "4163444",
            "3978742",      "4000591",      "4041865",
            "3980915",      "4001387",      "4042647",
            "3981886",      "4002468",      "4049537",
            "4002552",      "4054897",
            "3984538",      "4003145",      "4056000",
            "3985323",      "4003837",      "4057710",
            "3988675",      "4006720",      "4058401"]

sets = getSets(allCalls, 10)

finalThresholds = []
similairtyMatrix = {}

for setNumber in range(0,10):
    if(mode != 4):
        print("\n" + "-"*25 + "SET NUMBER " + str(setNumber) + "-"*25 )

    trainingCalls     = sets[setNumber][1]
    verificationCalls = sets[setNumber][0]

    # Used for simple example
    # trainingCalls     = ["1111111", "1111112", "1111113", "1111114"]

    # print( verificationCalls )
    # Just to make sure everyone is accounted for!
    # Id-certantity array
    idcArr = []

    # Max source id
    #maxSource = 67
    # iKnow doesn't give similarities to all the sources
    # Thus the rest needs to be filled in with zeros.

    # Just to make sure everyone is accounted for!
    analyzedCalls = 0

    correct = 0
    # Total score
    totalScore = 0
    totalTests = 0


    # 1 = Good, 0 = Bad
    #
    #                     Predicted
    #                 1               0
    #
    #         1   res[0][0]       res[0][1]
    #  True
    #         0   res[1][0]       res[1][1]
    #

    res = [[0,0],[0,0]]


    ## Cost Matricies, weights the different erros
    # A: Both error cost as much
    costMatrixA = [[0,0.5],
                   [0.5,0]]

    # B: False negatives, a good call that we think is bad, are expensive
    costMatrixB = [[0,0.9],
                   [0.1,0]]

    # C: False positive, a bad call that we think is good, are expensive
    costMatrixC = [[0,0.1],
                   [0.9,0]]

    costMatricies = [costMatrixA, costMatrixB, costMatrixC]



    ### START ###
    #similairtyMatrix = iKnowFileRead("OUTPUT FROM InterSystemTest.mac")
    similairtyMatrix = gensimFileRead("OUTPUT FROM gensim.py")

    ## FILE READING DONE
    idcArr = []
    for row in similairtyMatrix:
        currentSource = row
        if( currentSource in trainingCalls ):
            analyzedCalls += 1
            if( method == "avg" ):
                certainty = avgMethod( similairtyMatrix[row] )
            elif( method == "min" ):
                certainty = minMethod( similairtyMatrix[row] )
            elif( method == "knn" ):
                certainty = knnMethod( similairtyMatrix[row] , knnK)
            elif( method == "cen" ):
                # Center needs to full matrix
                certainty = centerMethod( similairtyMatrix, row )
            else:
                print("ERROR unknown method: + " + method)

            idcArr.append( (currentSource, certainty) )

    ## PRE ANALYSIS
    fMin = min( idcArr, key = lambda x: x[1])
    fMax = max( idcArr, key = lambda x: x[1])
    diff = fMax[1] - fMin[1]
    if(mode == 0 or mode == 4):
        anslist = []
        best = 0
        bestThresh = 0
        l = 0

    steps = 50
    for x in range(0,steps):
        correct = 0
        res = [[0,0],[0,0]]

        for idc in idcArr:
            currentSource = idc[0]
            certainty = idc[1]

            statusSource = not ( currentSource in badCalls )

            thresh = fMin[1] + diff * x/steps
            statusGuess = ( certainty > thresh )

            res[not statusSource][not statusGuess] +=   1

            if( statusGuess == statusSource ):
                correct = correct + 1

        a = res[0][0]
        b = res[0][1]
        c = res[1][0]
        d = res[1][1]

        if( mode == 0 or mode == 4):
            # PRINT NUMBER OF CORRECT GUESSES
            #print (correct, ",", thresh)

            if(correct > best):
                anslist = [(x,correct)]
                best = int(correct)
            elif(correct == best):
                anslist.append((x, correct))
            l = len(anslist)
            bestX = anslist[int(l/2)][0]
            bestThresh = fMin[1] + diff * bestX/steps
        elif (mode == 1):
            # PRINT COST
            cost = []
            for costMatrix in costMatricies:
                tmpCost  = a*costMatrix[0][0]
                tmpCost += b*costMatrix[0][1]
                tmpCost += c*costMatrix[1][0]
                tmpCost += d*costMatrix[1][1]
                cost.append( str(tmpCost) )

#                print (thresh, ',', ','.join(cost))
        elif (mode==2):
            ## PRECISION AND RECALL
            precision  = a/(a+c)
            recall = a/(a+b)
            F = ( 2 * precision * recall )/(precision+recall)
            #print ("Thresh, Precision, Recall, F-score")
#            print (thresh, ',', precision, ',', recall, ',', F)
        elif (mode==3):
            ## ROC-plot
            sensitivity = a/(a+b)
            specificity = d/(c+d)
#            print(1-specificity,',' ,sensitivity)


    ## POST ANALYSIS
    if(mode == 0):
        print("Best threshold: " + str(bestThresh) +
              " (x=" + str( (bestThresh-fMin[1])/(fMax[1]-fMin[1]) ) + ")" +
              " (" + str(best) + "/" + str(analyzedCalls) + " correct)")
        print("\n")
    if(mode == 0 or mode == 4):
        finalThresholds.append(
            (bestThresh, (bestThresh-fMin[1])/(fMax[1]-fMin[1]) )
        )



## POST-POST ANALYSIS (For k-folding)
print("FINAL:")
if(mode == 0):
    print ("True constant: "       + str( mean([x[0] for x in finalThresholds ]) ) )
    print ("Fractional constant: " + str( mean([x[1] for x in finalThresholds ]) ) )


if(mode == 4):
    print(  str( mean([x[0] for x in finalThresholds ]) ) )




