# -*- coding: utf-8 -*-

import re
import string
from os import listdir
from os.path import isfile, join

corpusDir="PATH/TO/CALLS";

corpus = [corpusDir + f for f in listdir(corpusDir) if isfile(join(corpusDir, f))]

for filename in corpus:

        if( filename.find(".txt") > 0):
                outputFile = ''
                with open(filename,  encoding="utf-8") as file:
                        p = re.compile('[nNdD]:.*')
                        test_str = file.read()
                        outputFile = re.findall(p, test_str)

                f = open(filename, 'w')
                f.write('\n'.join( outputFile) )
