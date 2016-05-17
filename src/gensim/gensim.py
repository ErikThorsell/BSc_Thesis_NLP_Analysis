# -*- coding: utf-8 -*-
#!/usr/bin/env python

import csv
import math
import string
import os, sys, fileinput
import re
from os import listdir
from os.path import isfile, join
from gensim import corpora, models, similarities
from collections import defaultdict

### Declarations ###
calls = []
corpusDir = "PATH/TO/CALLS"
call_list = [corpusDir + f for f in listdir(corpusDir) if (isfile(join(corpusDir, f))
                and (re.match("\d{7}\.txt", f) is not None))]

idList = (list(enumerate([call[-11:-4] for call in call_list])))


for filename in call_list:
    with open(filename, 'r' ) as myfile:
        data=myfile.read().replace('\n', ' ')
        calls.append(data)

stoplist = set('och men att det är i på'.split())
texts = [[word for word in call.lower().split() if word not in stoplist]
          for call in calls]

frequency = defaultdict(int)
for text in texts:
    for token in text:
        frequency[token] += 1

texts = [[token for token in text if frequency[token] > 1]
         for text in texts]

dictionary = corpora.Dictionary(texts)
#dictionary.save("dictionary.dict")

corpus = [dictionary.doc2bow(text) for text in texts]
#corpora.MmCorpus.serialize("corpus.mm", corpus)

lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=67)
index = similarities.MatrixSimilarity(lsi[corpus])

for call in enumerate(calls):
    callID = idList[call[0]][1]
    vec_bow = dictionary.doc2bow(call[1].lower().split())
    vec_lsi = lsi[vec_bow] # convert the query to LSI space

    sims = index[vec_lsi]
    sims = sorted(enumerate(sims), key=lambda item: -item[1])

    print("ID:" + callID)
    skipFirst = True

    for sim in sims:
        c = idList[sim[0]][1]
        s = sim[1]
        if( skipFirst ):
            skipFirst = False
        else:
            print(str(c) + "," + str(s))

