#!/usr/bin/env python3

import unittest
import mrge
import os


class testMRGE(unittest.TestCase):
    def testDummy(self):
        assert True, "Things are really bad. Get a break"

    def testIterable(self):
        egr1 = mrge.Extractor(instream=range(10))
        assert egr1.input, "Failed to create input from range"
        testFileName = "delit.test"
        with open(testFileName, 'w') as of:
            of.write("123")
        with open(testFileName, 'r') as ifl:
            egr2 = mrge.Extractor(instream=ifl.readlines())
            assert egr2.input, "Failed to create input from file"
        assert os.path.exists(testFileName), "Failed to create test input file"
        os.remove(testFileName)
        egr3 = mrge.Extractor()
        assert egr3.input, "Failed to create input from stdin"

    def testOutput(self):
        ofleName = "delit_test.out"
        egr = mrge.Extractor(outp=ofleName)
        assert egr.outp, "Failed to create output"
        phrase = "test-o"
        egr.outp.write(phrase)
        egr.outp.close()
        assert os.path.exists(ofleName), "Failed to create output file"
        with open(ofleName, 'r') as outFile:
            assert phrase in outFile.read(), "Failed to write to test file"
        os.remove(ofleName)

    def testEntropyCounter(self):
        egr = mrge.Extractor()
        assert egr.getCurrentEntropy() == 0, "Bad init of class. No zero entropy"
        egr.insert('a')
        egr.insert('b')
        assert egr.getCurrentEntropy() == 1, "Bad entropy count for trivial case"
        egr.reset()
        egr.insert('o')
        assert egr.getCurrentEntropy() == 0, "Bad entropy of first event"
        egr.reset()
        prevEnt = -0.00001
        for x in range(8):
            egr.insert(x)
            ent = egr.getCurrentEntropy()
            assert ent > prevEnt, "Entropy does not grow when needed"
            prevEnt = ent
        egr.reset()
        prevEnt = -0.00001
        for x in range(2, 10):
            for y in range(x):
                egr.insert(y)
            ent = egr.getCurrentEntropy()
            assert ent >= prevEnt, "Entropy does not grow when needed"
            prevEnt = ent

    @unittest.skip("TODO: REMOVE SKIP AFTER BANK IS DONE")
    def testRecalcDivs(self):
        egr = mrge.Extractor()
        assert egr.divs == 1, "Bad divs init"
        egr.insert(1)
        egr.recalcDivs()
        assert egr.divs == 1, "Bad divs after one item"
        egr.insert(2)
        egr.recalcDivs()
        assert egr.divs == 2, "Bad divs after second item"
        for x in range(3, 9):
            egr.insert(x)
            egr.recalcDivs()
        assert egr.divs == 8, "Bad divs after third batch of items"
        for x in range(2):
            egr.insert(8)
        egr.recalcDivs()
        assert egr.divs < 8, "Failed to downgrade divisions"

    def testExtraction(self):
        egr = mrge.Extractor()
        success, values = egr.next(1)
        assert not success and not values, "First insertion resulted in getting data. Not right"
        s, v = egr.next(2)
        # TODO remove comment when done
        # assert s and v, "non-trivial insertion resulted in no data"
        egr.reset()
        egr.next(1)
        s, v = egr.next(1)
        # assert not s and not v, "trivial second insertion resulted in new data"
        egr.reset()
        egr.next(1)
        s, v = egr.next(0)
        # assert s and v == 0, "Bad reaction to the first zero insertion"
        # TODO

    def testInfoBankProbEquality(self):
        bnk = mrge.Extractor.InfoBank(base=2)
        iters = 1000000
        from math import log
        from random import random
        # for x in range(20, 1000, 1):
        def aw1(p): return (-p*log(p, 2), -(1-p)*log(1-p, 2))
        def aw2(p): return (t := -p*log(p, 2)-(1-p)*log(1-p, 2), t)
        def aw3(p): return (-log(p, 2), -log(1-p, 2))
        def w1(p): return (1./p, 1./(1-p))
        def w2(p): return (-log(p, 2), -log(1-p, 2))
        def w3(p): return (-p*log(p, 2), -(1-p)*log(1-p, 2))
        def w4(p): return (1./(1-p), 1./p)

        for awn, aw in enumerate((aw1, aw2, aw3)):
            for wn, w in enumerate((w1, w2, w3, w4)):
                print(awn, wn)
                for p in range(1, 11):
                #for x in range(3, 8):
                    x = 2**p
                    frac = 1./x
                    i0 = -frac*log(frac, 2)
                    i1 = -(1-frac)*log(1-frac, 2)
                    n0 = n1 = 0
                    # ________
                    sw0, sw1 = w(frac)
                    iw0, iw1 = aw(frac)
                    for t in range(iters):
                        if random() < frac:
                            s, v = bnk.next(0, sw0, iw0)
                        else:
                            s, v = bnk.next(1, sw1, iw1)
                        n0 += s*(1-v)
                        n1 += s*v
        #            if n0+n1 > 100:
        #                assert 1.*(max(n0, n1) - min(n0, n1))/(n0+n1) < .010, "Bank is wrong"
                    # hack to exclude div by 0
                    n0 += 1
                    n1 += 1
                    resstr = f"{x}\t{n0}\t{n1}\t{(r:=1.*(max(n0, n1) - min(n0, n1))/(n0+n1)):.4f}\t{(d:=max(n0,n1)/min(n0,n1)):.4f}\t{d*x/(x+1):.4f}\t{d*(x-1)/x:.4f}"
                    with open('investi.gate'+str(10+10*awn+wn), 'a') as fle:
                        fle.write(resstr+'\n')
                    print(resstr)


if __name__ == "__main__":
    mrge.setLogger(5)
    unittest.main()
