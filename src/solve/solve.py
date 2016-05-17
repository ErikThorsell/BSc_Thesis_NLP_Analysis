# -*- coding: utf-8 -*-
import csv
import math
import string
import os, sys, fileinput
import re
from os import listdir
from os.path import isfile, join
from collections import Counter
from bs4 import BeautifulSoup, Tag
from multiprocessing import Pool

### SET MODE ###
#   mode = 0 : Run all solvers against the answer file
#   mode = 1 : Calculate score for each call
#   mode = 2 : Calculate score based on answer file

if(len(sys.argv) < 2):
    print ("mode = 0 : Run all solvers against the answer file. solve.py 0 [question letter]")
    print ("mode = 1 : Calculate score for each call")
    print ("mode = 2 : Calculate score based on answer file")
    print ("mode = 3 : computes all questions for specific call. run solve.py 3 [callid]")
    print ("Please use: solve.py  [mode]")
    sys.exit()

mode = int(sys.argv[1])

### Set what calls to parse ###
#fileSuffix = "stripped"
#fileSuffix = "noCaller"
#fileSuffix = "stt"

# Parse a given document to XML using Beautiful Soup.

def parseXML(document):
    xmlDir = "PATH/TO/CORENLP/PARSED/CALLS" + fileSuffix + "/"
    xml = document[-11:] + ".out"
    soup = BeautifulSoup(open(xmlDir+xml), "html.parser")
    return soup

# Fetch the question titles for an answer file.
def getQuestionTitles(answerFile):
    with open(answerFile, 'r') as csvfile:
        sreader = csv.reader(csvfile, delimiter=',')
        qna = list()

        # Skip first line
        next(sreader)

        # Question names
        names = next(sreader)
        return names[1:-1]

# Return all answers for a question number and a csv answer file.
def getQuestion(number, answerFile):
    with open(answerFile, 'r') as csvfile:
        sreader = csv.reader(csvfile, delimiter=',')
        qna = list()

        # Skip first line
        next(sreader)

        # Question names
        names = next(sreader)
        qName = names[number+1]

        #print qName
        for row in sreader:
            callId = row[0][3:-2]
            answer = row[number+1]
            #print callId, ': ', answer
            qna.append( [callId, answer, qName] )

    return qna

# Return the answer for a specific question and callId.
def getQuestionByCallId(number,callId,answerFile):
    with open(answerFile, 'r') as csvfile:
        sreader = csv.reader(csvfile, delimiter=',')
        qna = list()

        # Skip first line
        next(sreader)

        # Question names
        names = next(sreader)
        qName = names[number+1]

        for row in sreader:
            currentCallId = row[0][3:-2]
            if(currentCallId == callId):
                answer = row[number+1]
                return  [callId, answer, qName]

        print (callId + " was not found")

    return qna

# Take a line and return who said it and the line in lower case.
def callLine(fileLine):
    firstColon = fileLine.find(':')
    author = fileLine[0:firstColon].strip().upper()
    line = fileLine[firstColon+1:]
    lineLower = line.lower()
    return [author, lineLower]

# Return a sentence given a sentence soup.
def sentenceStringFromSoup(sentenceSoup):
    tokens = sentenceSoup.tokens
    words = []
    for word in tokens("word"):
        words.append( word.text )
    return ' '.join(words)

# Return who said what sentence, given a soup and a sentence id.
def findSpeaker(soup, sentenceID ):
    if( sentenceID == 0):
        return -1
    for sentence in soup("sentence", id=str(sentenceID) ):
        for w in sentence("word"):
            if( w.text == ':' ):
                wid = int( w.parent['id'] )
                return  ( sentence.find(id=(wid-1)).word.text )
        else:
            return findSpeaker(soup, int(sentenceID)-1 )

# Answers the question B 1.1 - Where is the call made from?
def QB(document):
    home = ["hemma","hemmifrån","lägenhet","hus","villa"]
    matchHome = []
    hospital = ["sjukvård","sjukhus","hemtjänst","hemtjänsten"]
    matchHospital = []
    public = ["jobb", "park","utomhus","tåg","buss","tunnelbana","spårvagn"]
    matchPublic = []

    with open(document, 'r') as file:
        for line in file:
            cLine = callLine(line)

            # To only get the caller one can add:
            # if(cLine[0] = 'c'):
            cWords = re.sub("[^\wåäöÅÄÖ]", " ",  cLine[1]).split()
            for w in home:
                if w in cWords:
                    matchHome.append( [w, 1 ] )

            for w in hospital:
                if w in cWords:
                    matchHospital.append( [w, 2] )

            for w in public:
                if w in cWords:
                    matchPublic.append( [w, 3] )

        if( len(matchHome) == 0 and len(matchHospital) == 0 and len(matchPublic) == 0):
            return 4

        # maxMatch[n][1] is the same for every n.
        # Find the one with the most matches.
        # Maybe we should add extra attention to the case where multiple
        # answers has the same number of matches
        maxMatch = max( [matchHome, matchHospital, matchPublic], key=lambda x: len(x) )
        return maxMatch[0][1]

# Answers the question C 1.2 - Who is calling?
def QC(document):
    related = ["sambo","fru","make","maka","pojkvän","flickvän",
               "son","dotter","mormor","morfar","farmor","farfar",
               "moster","morbor","faster","farbror","kusin",
               "syssling","mamma","pappa","mor","far"]
    matchRelated = []
    staff = ["sköterska","doktor","läkare","från vårdcentral"]
    matchStaff = []
    homeCare = ["vårdare","hemtjänst"]
    matchHomeCare = []
    patient = ["jag"]
    matchPatient = []

    with open(document, 'r') as file:
        for line in file:
            cLine = callLine(line)

            # To only get the caller one can add:
            # if(cLine[0] = 'c'):
            cWords = re.sub("[^\wåäöÅÄÖ]", " ",  cLine[1]).split()

            cList = []

            for w in cWords:
                cList.append(w)

            for w in related:
                if w in cList:
                    matchRelated.append( [w, 1] )
                    related.remove(w)

            for w in staff:
                if w in cList:
                    matchStaff.append( [w, 2] )
                    staff.remove(w)

            for w in homeCare:
                if w in cList:
                    matchHomeCare.append( [w, 3] )
                    homeCare.remove(w)

        if (len(matchPatient) > 5):
            return 4

        if( len(matchRelated) == 0 and len(matchStaff) == 0 and len(matchHomeCare) == 0):
            return 5

        maxMatch = max( [matchRelated, matchStaff, matchHomeCare], key=lambda x: len(x) )
        return maxMatch[0][1]

# Answers the question D 1.3 - Have the caller seen or heard the patient?
def QD(document):
    looks = ["kladdig"," sår "," grå ","blå","svettig","blöt","blek",
             "ansiktet","dreglar","svullen"," röd"]
    with open(document, 'r') as file:
        for line in file:
            cLine = callLine(line)

            # To only get the caller one can add:
            # if(cLine[0] = 'c'):
            cWords = re.sub("[^\wåäöÅÄÖ]", " ",  cLine[1]).split()

            for w in looks:
                if w in cWords:
                    return 1
    return 0

# Answers the question E 1.4 - Linguistic difficulties for the caller?
def QE(document):
    terms = ["förstår inte vad du säger","är du påverkad"]
    with open(document, 'r') as file:
        for line in file:
            cLine = callLine(line)
            for w in terms:
                if w in cLine:
                    return 1
    return 0

# Answers the question F 1.5 - Linguistic difficulties for the patient?
def QF(document):
    sv = 0
    dumb = 0

    with open(document, 'r') as file:
        for line in file:
            cLine = callLine(line)
            cWords = re.sub("[^\wåäöÅÄÖ]"," ", cLine[1]).split()

            for w in cWords:
                if (w == "svenska"):
                    sv = sv + 1
                if (w == "döv"):
                    dumb = dumb + 1
        if sv > 1:
            return 1
        if dumb > 0:
            return 2
        return 0

# Answers the question G 1.6 - How old is the caller?
def QG(document):
    age = ["gammal","ålder","personnummer","år","födelsedatum"]
    with open(document, 'r') as file:
        for line in file:
            cLine = callLine(line)
            cWords = re.sub("[^\wåäöÅÄÖ]"," ", cLine[1]).split()

            for w in cWords:
                if w in age:
                    return 1
    return 0

# Answers the question H 2.1 - Is it a transport between two hospitals?
def QH(document):
    nLines = 0
    transport = ["transport","vårdhem","sjukhem","vårdcentral","hemtjänst",
                 "vårdbiträde","hemtjänstpersonal","brukare"]
    with open(document, 'r') as file:
        for line in file:
            cLine = callLine(line)

            # To only get the caller one can add:
            # if(cLine[0] = 'c'):
            cWords = re.sub("[^\wåäöÅÄÖ]", " ",  cLine[1]).split()

            for w in transport:
                if w in cWords:
                    return 1
    return 0

# Answers the question I 2.2 - Is there a description of what the patient are
# currently doing in the call?
def QI(document):
    position = ["ligger hon","ligger han","skriker","gråter","gråta",
                "sin säng","vad gör ","ligger i ","han ligger ner ",
                "han ligger i ","hon ligger ner","hon ligger i ","ligger på ",
                "sitter ner","sitter upp","sitter i ","satt sig","kräks",
                "spyr","sover nu","döende","medvetslös","mår illa"]
    with open(document, 'r') as file:
        for line in file:
            cLine = callLine(line)

            for w in position:
                if w in cLine[1]:
                    return 1
    return 0

# Answers the question J 2.3 - Is there a description of what the patient looks
# like?
def QJ(document):
    looks = ["kladdig"," sår "," grå ","blå","svettig","blöt","blek",
             "ansiktet","dreglar","svullen"," röd"]
    with open(document, 'r') as file:
        for line in file:
            cLine = callLine(line)

            # To only get the caller one can add:
            # if(cLine[0] = 'c'):
            cWords = re.sub("[^\wåäöÅÄÖ]", " ",  cLine[1]).split()

            for w in looks:
                if w in cWords:
                    return 1
    return 0

# Answers the question K 2.4 - Does the caller repeat the patient's symptoms
# more than 4 times?
def QK(document):
    return 0

# Answers the question L 2.5 - Is the development of the symptom over time
# spoken about?
def QL(document):
    time = ["i morse","under morgonen","under dagen","förändrat","tillstånd",
            "blivit sämre","blivit värre","förra veckan", "nyligen",
            "stund sedan","dagar","veckor","veckan","timme","timmar",
            "tidigare haft","avtagit","ökat","varit dålig"]
    with open(document, 'r') as file:
        for line in file:
            cLine = callLine(line)
            for term in time:
                if term in cLine[1]:
                    return 1
    return 0

# Answers the question M 2.6 - Is the current state of the patient put in
# comparison to how the patient is usually feeling?
def QM(document):
    states = ["i vanliga fall","brukar vara ","brukar inte ","ändrats",
            "tidigare","har haft"]
    with open(document, 'r') as file:
        for line in file:
            cLine = callLine(line)
            for state in states:
                if state in cLine[1]:
                    return 1
    return 0

# Answers the question N 2.6 - Does the caller say that the patient have more
# than two issues?
def QN(document):
    callId = document[-11:-4]
    with open('QN_' + fileSuffix + '.txt', 'r') as f:
        for line in f:
            cid = line[:-11]
            res = int( line[15:] )

            if( callId == cid ):
                return res
    return 0


# Answers the question O 2.8 - Are there contradictions in the description of
# the patient's situation?
def QO(document):
    return 0


# Answers the question P 2.9 - Is the caller able to answer the dispatcher's
# questions?
def QP(document):
    nop = 0
    qs = 0
    soup = parseXML(document)
    for sentence in soup("sentence"):
        sentenceID = sentence['id']
        for pos in sentence("pos", string="MAD"):
            if pos.parent.word.text == "?":
                qs = qs + 1
                for token in soup("sentence", id=str(int(sentenceID)+1)):
                    sent = []
                    for word in token("word"):
                        sent.append(word.text.lower())
                    if "vet inte" in (" ".join(sent)):
                        nop = nop + 1
    if nop > qs/2:
        return 0
    else:
        return 1


# Answers the question Q 2.10 - Is the caller answering the dispatcher's
# questions?
def QQ(document):
    ans = 0
    qs = 0
    answers = ["aa","ja"," mm "," a ","nä","nej","kanske","precis","okej","yes",
               " jo"," x ","xx","xxx","xxxx","xxxxx","xxxxxx"]
    soup = parseXML(document)
    for sentence in soup("sentence"):
        sentenceID = sentence['id']
        for pos in sentence("pos", string="MAD"):
            if pos.parent.word.text == "?":
                qs = qs + 1
                for token in soup("sentence", id=str(int(sentenceID)+1)):
                    for word in token("word"):
                        if word.text.lower() in answers:
                            ans = ans + 1
    if ans < qs/2:
        return 0
    else:
        return 1


# Answers the question R 2.11 - Are there more than 3 earlier diseases
# described in the call?
def QR(document):
    callId = document[-11:-4]
    with open('QR_' + fileSuffix + '.txt', 'r') as f:
        for line in f:
            cid = line[:-11]
            res = int( line[15:] )

            if( callId == cid ):
                #print( callId + " " + str(res) )
                return res
    return 0


# Answers the question S 2.12 - Is there a descripion of issues with breathing,
# circulation and consciousness in the call within 30 seconds?
def QS(document):
    soup = parseXML(document)
    terms = ["andas","andning","luft","andades","andningen",
             "medveten","medvetande"]
    for key in terms:
        for sentence in soup("sentence"):
            for w in sentence("word", string=key):
                charOff = w.parent.characteroffsetbegin.text
                wordOff = int(charOff)/5
                if(wordOff > 130):
                    return 0
                else:
                    return 1
    return 0

# Answers the question T 3.1 - Is the dispatcher summarazing or repeating what
# the caller is saying?
def QT(document):
    prevCaller = ""
    summarized = 0
    with open(document, 'r') as file:
        for line in file:
            cLine = callLine(line)
            if(cLine[0] == 'C'):
                prevCaller = cLine[1]
            elif(cLine[0] == 'D'):
                cWords = re.sub("[^\wåäöÅÄÖ]", " ",  prevCaller.upper()).split()
                dWords = re.sub("[^\wåäöÅÄÖ]", " ",  cLine[1].upper()).split()
                common =  set(cWords)&set(dWords)

                summarized += len(common)

    return (summarized > 5)

# Answers the question U 3.2 - Is the dispatcher using any aids?
def QU(document):
    with open(document, 'r') as file:
        p = re.compile('\\b(polis|kollega)\\b:.*', re.IGNORECASE | re.UNICODE)
        file_str = file.read()
        outputFile = re.findall(p, file_str)
    if len(outputFile) > 0 :
        return 1
    else :
        return 0

# Answers the question V 3.3 - Is the dispatcher making sure that the patient
# is breathing?
def QV(document):
    soup = parseXML(document)
    terms = ["andas","andning","luft","andades", "andningen"]
    for key in terms:
        for sentence in soup("sentence"):
            sentenceID =  sentence['id']
            allOfThem = sentence.find_all("word", string=re.compile(".*"+key+".*", re.I))
            for w in allOfThem:
                tokenID = w.parent['id']
                speaker = findSpeaker(soup, sentenceID)
                if( speaker == 'D' or speaker == 'N' ):
                    return 1
    return 0

# Answers the question W 3.4 - Is the dispatcher leading the call?
def QW(document):
    callerWords = []
    dispWords   = []
    with open(document, 'r') as file:
        for line in file:
            cLine = callLine(line)
            if(cLine[0] == 'C'):
                callerWords.append( len(cLine[1]) )
            elif(cLine[0] == 'D'):
                dispWords.append( len(cLine[1]) )

    # Check n longest sentences
    n    = 1
    topD = sorted(callerWords)[-n:]
    topC = sorted(dispWords)[-n:]
    return (sum(topD) > sum(topC))

# Answers the question X 3.5 - Is the dispatcher focusing on other things than
# the patient's disease?
def QX(document):
    keys = []
    with open(document, 'r') as file:
        for line in file:
            cLine = callLine(line)
            lowerline = cLine[1].lower()
            if(cLine[0] == 'D'):
                for key in keys:
                    if( lowerline.find(key) > -1 ):
                        return 1
    return 0

# Answers the question Y 3.6 - Is the dispatcher asking multiple questions in
# the same sentence?
def QY(document):
    with open(document, 'r') as file:
        ## selects only rows where dispatcher talks
        p = re.compile('d:.*', re.IGNORECASE | re.UNICODE)
        file = re.findall(p, file.read())
        for line in file:
            ## regex for searching after question marks
            p = re.compile('\?', re.IGNORECASE | re.UNICODE)
            outputFile = re.findall(p, line)
            if (len(outputFile) > 1) :
                #print( document[-12:-4] + " :" + line )
                return 1
                break
    return 0

# Answers the question Z 3.7 - Is the dispatcher asking questions about what
# the caller is saying?
def QZ(document):
    keys = ['var','när','hur']
    with open(document, 'r') as file:
        for line in file:
            cLine = callLine(line)
            lowerline = cLine[1].lower()
            if(cLine[0] == 'D'):
                for key in keys:
                    if( lowerline.find(key) > -1 ):
                        return 1
    return 0


#### Handling results from Solvers ####

# Calculates the number of correct answers for a given solver.
# Writes the result for each solver to a file, specified as 'output'.
def calculateResult(calls, solverTuple, answers):
    correct = 0
    total = 0
    res = [ [0,0],[0,0] ]
    questionNumber = ord(solverTuple[2])-ord('A')-1
    questionName = getQuestion(questionNumber, answers)

    output = open("results/" + fileSuffix + "/" + solverTuple[2] + ".txt",'w')
    output.write("-"*70 + "\n" + questionName[0][2] + "(using solver: " + solverTuple[2] + ")\n" +  "-"*70 + '\n')
    solver = solverTuple[0]

    # Fetch a call from the list
    for call in calls:
        # Run the algorithm on the call
        alg = solver(call)
        # Check the correct answer
        # [-11:-4] is substr to remove .txt and path. (Assumes all ids are the same length.)
        callId = call[-11:-4]
        ans = getQuestionByCallId(questionNumber, callId, answers)

        if( (not ans) or (ans[1] == '') ):
            output.write("No solution for: " + call + '\n')
            continue

        res[not int(ans[1])][not alg] +=   1

        verdict = (int(ans[1]) == alg)
        output.write(callId + ": Algorithm: " + str(alg) + ", Answer: " + ans[1] + ", Correct: " + str(verdict) + '\n')

        if( verdict ):
            correct = correct + 1
        total = total + 1

    output.write("\t\t\t     Predicted\n")
    output.write(" "*25 + "1\t\t0 \n")
    output.write("-"*50 + '\n')
    output.write("True\t1\t|\t" + str(res[0][0]) + "\t\t" + str(res[0][1]) + '\n')
    output.write("    \t0\t|\t" + str(res[1][0]) + "\t\t" + str(res[1][1]) + '\n')
    output.write(str(correct) + "/" + str(total) + '\n')
    return [correct, total]


## Calculate the score for a call given a call, a solver and an answer file.
def calculateScore(call, solvers, answerFile):
    score = 0
    qts = getQuestionTitles(answerFile)
    for n in range(len(solvers)):
        questionNumber = n
        questionName = qts[n]

        guess  = int(solvers[n][0](call))
        weight = solvers[n][1]

        if( guess != 0 ):
            score += weight

    return (call, score)

## Wrapper function for calculateScore, takes a list of calls.
def calculateScores(calls, solvers,answerFile):
    callScores = []
    with Pool() as p:
        callScores = p.starmap(calculateScore,[(call,solvers,answerFile) for call in calls])
    return callScores

## Counts how man of the calls have a score > goodThreshold
def calculateGrades(callScores, goodThreshold):
    total = 0
    correct = 0
    res = [[0,0],
           [0,0]]

    for (call, score) in callScores:
        callid = call[-11:-4]

        if( int(score) > goodThreshold ):
            status = True
        else:
            status = False

        correctStatus = not (callid in badCalls)
        res[not correctStatus][not status] += 1
        total += 1
        if( status == correctStatus ):
            correct += 1

        print(callid + " (score: " + str(score) + "):\t" + str(status) + "\t=  " + str(correctStatus) )

    print ("Correct: ", correct, "/", total)
    print ()
    print (" ")
    print ("\t\t\t     Predicted")
    print ("\t\t\tGood\t\tBad ")
    print ("-"*50)
    print ("True\tGood\t|\t", res[0][0], "\t\t", res[0][1])
    print ("\tBad\t|\t", res[1][0], "\t\t", res[1][1])

def printMatrixForScore(callScores, goodThreshold, fixedScore):
    total = 0
    correct = 0

    res = [[0,0],
           [0,0]]

    matLoc = []

    for (call,score) in callScores:
        if( int(score) == fixedScore ):
            callid = call[-11:-4]
            if( int(score) > goodThreshold ):
                status = True
            else:
                status = False

            correctStatus = not (callid in badCalls)
            matLoc.append( (callid, int(status), int(correctStatus) ) )
            res[not correctStatus][not status] +=   1
            total += 1
            if( status == correctStatus ):
                correct += 1

    print ("\t\t\t     Predicted")
    print ("\t\t\tGood\t\tBad ")
    print ("-"*50)
    print ("True\tGood\t|\t", res[0][0], "\t\t", res[0][1])
    print ("\tBad\t|\t", res[1][0], "\t\t", res[1][1])
    print()
    print ("For score=" + str(fixedScore) + " we got: ", correct, "/", total)
    print("-"*50)

    ## Verbos mode, debugging.
    if( len(sys.argv)>2 and sys.argv[2] == 'v'):
        print(matLoc)


## Looks at the answerFile instead of caluclating
def scoreFromAnswer(call, solvers,answerFile):
    score = 0
    qts = getQuestionTitles(answerFile)
    for n in range(len(solvers)):
        questionNumber = n
        questionName = qts[n]
        if( solvers[n][0] != 0):
            qna = getQuestionByCallId( n, call[-11:-4], answerFile)

            if( qna[1] ):
                guess  = int(qna[1])
            else:
                guess = 0
            weight = int(solvers[n][1])
            if( guess != 0 ):
                score += weight

    return int(score)

## Wrapper function for calculateScore, takes a list of calls.
def scoresFromAnswer(calls, solvers,answerFile):
    callScores = []
    score = 0
    for call in calls:
        score = scoreFromAnswer(call, solvers, answerFile)
        callScores.append((call, score))
    return callScores


def getVectorsFromAnswers(calls, solvers, answerFile):
    vecs = []
    for call in calls:
        score = 0
        qts = getQuestionTitles(answerFile)
        vec = []
        for n in range(len(solvers)):
            questionNumber = n
            questionName = qts[n]
            #print(call[-11:-4] + " solver: " + solvers[n][2])
            qna = getQuestionByCallId( n, call[-11:-4], answerFile)

            if( qna[1] ):
                guess  = int(qna[1])
            else:
                guess = 0

            weight = solvers[n][1]
            if( guess != 0 ):
                score += weight
                vec.append(weight)
            else:
                vec.append(0)

        vecs.append(vec)
    return vecs


############ MAIN ###############
# Call id from directory: corpus[0][-11:-4]
corpusDir = "/PATH/TO/CALLS/" + fileSuffix + "/"

corpus = [corpusDir + f for f in listdir(corpusDir) if (isfile(join(corpusDir, f))
            and (re.match("\d{7}\.txt", f) is not None))]

## The bad call ids, if known - add all low quality call IDs to this list, as
#  strings.
badCalls = []

answerFile = "PATH/TO/ANSWER/FILE"

## Add the solvers. (Solver function, weight)
solvers = [ (QB, 0, 'B'), #0
            (QC, 1, 'C'), #1
            (QD, 1, 'D'), #2
            (QE,-1, 'E'), #3
            (QF,-1, 'F'), #4
            (QG, 1, 'G'), #5
            (QH, 0, 'H'), #6
            (QI, 0, 'I'), #7
            (QJ, 1, 'J'), #8
            (QK,-1, 'K'), #9
            (QL, 1, 'L'), #10
            (QM, 1, 'M'), #11
            (QN,-1, 'N'), #12
            (QO,-1, 'O'), #13
            (QP, 1, 'P'), #14
            (QQ, 0, 'Q'), #15
            (QR,-1, 'R'), #16
            (QS, 1, 'S'), #17
            (QT, 1, 'T'), #18
            (QU, 0, 'U'), #19
            (QV, 1, 'V'), #20
            (QW, 1, 'W'), #21
            (QX,-1, 'X'), #22
            (QY,-1, 'Y'), #23
            (QZ, 1, 'Z')  #24
          ]

if(mode == 0):
    ## See how well it performs
    finalTotal = 0
    finalCorrect = 0

    if( len(sys.argv) > 2 ):
        questionNumber = ord(sys.argv[2])-ord('A')-1
        res = calculateResult(corpus, solvers[questionNumber], answerFile)
        finalCorrect += res[0]
        finalTotal += res[1]
    else:
        with Pool() as p:
            res = p.starmap(calculateResult, [(corpus,solver,answerFile)
                for solver in solvers if solver[0] != 0 ])

        finalCorrect = sum( r[0] for r in res )
        finalTotal   = sum( r[1] for r in res )

    print("\nFinal score: " + str(finalCorrect) + "/" + str(finalTotal)
        + " ~ " + str(round( float(finalCorrect)/finalTotal,2 )*100) + "%" )

elif(mode == 1):
    # score must be higher than goodThreshold to consider the call good
    goodThreshold = 8

    callScores = calculateScores(corpus, solvers, answerFile)
    calculateGrades(callScores, goodThreshold)


    print("\n\n" + "-"*63)
    print("-"*20 + " Matrix for each score " + "-"*20  )
    print("-"*63 + "\n")

    fMin = min( callScores, key = lambda x: x[1])
    fMax = max( callScores, key = lambda x: x[1])

    for i in range(int(fMin[1]), int(fMax[1])+1):
        printMatrixForScore(callScores, goodThreshold, i)
        print("\n")

elif(mode == 2):
    goodThreshold = 1
    answerScores = scoresFromAnswer(corpus,solvers,answerFile)
    calculateGrades(answerScores, goodThreshold)


    print("\n\n" + "-"*63)
    print("-"*20 + " Matrix for each score " + "-"*20  )
    print("-"*63 + "\n")

    fMin = min( answerScores, key = lambda x: x[1])
    fMax = max( answerScores, key = lambda x: x[1])

    print(fMax)

    for i in range(int(fMin[1]), int(fMax[1])+1):
        printMatrixForScore(answerScores, goodThreshold, i)
        print("\n")

elif(mode == 3):
    if( len(sys.argv) < 3 ):
        print("Please use: solve.py 3 [callid]")

    corpus = [ call for call in corpus if (call[-11:-4] == sys.argv[2]) ]
    if(not corpus):
        print("No such call id.")
        exit()

    ## See how well it performs
    finalTotal = 0
    finalCorrect = 0
    for n in range(len(solvers)):
        questionNumber = n
        if( solvers[n][0] != 0):
            res = calculateResult(corpus, questionNumber, solvers[questionNumber], answerFile)
            finalCorrect += res[0]
            finalTotal += res[1]

    print("\nFinal score: " + str(finalCorrect) + "/" + str(finalTotal))
