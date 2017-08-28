# Standard imports
import os
import time
import itertools

# TopEFT
from TopEFT.gencode.EFT import *

# Logger
import logging
logger = logging.getLogger(__name__)

nonZeroCouplings = ("RC3phiq", "RCtW")
nonZeroCouplings = ("IC3phiq", "ICtW")

n = 5

# values
couplingValues = [ i*10.0/n for i in range(-n,n+1) ]

## this is how it should be done. However, becomes too expensive quite fast
#couplingPairs = []
#for a in itertools.permutations(cuW, len(cuB)):
#    tmp = zip(a,cuB)
#    for t in tmp:
#        if t not in couplingPairs: couplingPairs.append(t)#(round(t[0],2),round(t[1],2)))

# this is the workaround
couplingPairs = [a for a in itertools.permutations(couplingValues,2)] + zip(couplingValues,couplingValues)
couplingPairs = [(round(a[0],2), round(a[1],2)) for a in couplingPairs]

#logger.info( len(couplingPairs) )

#processes = ['ttZ','ttW','ttH']
processes = ['ttZ']
#submitCMD = "submitBatch.py --title='2D'"
submitCMD = "echo"

for p in processes:
    for c in couplingPairs:
        couplingStr = "%s %s %s %s"%(nonZeroCouplings[0], c[0], nonZeroCouplings[1], c[1])
        os.system(submitCMD+" 'python calcXSec.py --model TopEffTh --process "+p+" --couplings "+couplingStr+"'")
        if not "echo" in submitCMD:
            time.sleep(60) # need to distribute load, shouldn't start with 40 jobs at a time
