#!/usr/bin/env python3

import unittest
import mrge
from fractions import Fraction as fr
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

    # Redo TODO
    def testEntropyCounter(self):
        egr = mrge.Extractor()
        assert egr.getTotalTheoreticalEntropy() == 0, "Bad init of class. No zero entropy"
        egr.insert('a')
        egr.insert('b')
        assert egr.getTotalTheoreticalEntropy() == 2, "Bad entropy count for trivial case"
        egr.reset()
        egr.insert('o')
        assert egr.getTotalTheoreticalEntropy() == 0, "Bad entropy of first event"
        egr.reset()
        prevEnt = -0.00001
        for x in range(8):
            egr.insert(x)
            ent = egr.getTotalTheoreticalEntropy()
            assert ent > prevEnt, "Entropy does not grow when needed"
            prevEnt = ent
        egr.reset()
        prevEnt = -0.00001
        for x in range(2, 10):
            for y in range(x):
                egr.insert(y)
            ent = egr.getTotalTheoreticalEntropy()
            assert ent >= prevEnt, "Entropy does not grow when needed"
            prevEnt = ent

    def testInsertTotal(self):
        egr = mrge.Extractor()
        assert egr.totalEvents() == 0, "Bad event count to 0"
        # shuld not complain
        egr.insert(1)
        assert egr.totalEvents() == 1, "Bad event count to 1"
        egr.insert(1, 2, 3)
        assert egr.totalEvents() == 4, "Bad event count to 4"
        egr.insert(*range(3))
        assert egr.totalEvents() == 7, "Bad event count to 7"
        # should not happen in oneround but should not complain to insertion either
        egr.insert('a', 'b', 'c')
        egr.insert(1., 2., 3.)
        egr.reset()
        egr.insert(None)
        assert egr.storage == {
        }, "None event is not filtered from insertion to storage "+str(egr.storage)

    def testGetAverageEntropyOfNext(self):
        egr = mrge.Extractor()
        egr.insert(*range(4))
        assert 1.99 < egr.getAverageEntropyOfNext(
        ) < 2.01, "Bad recalc of entropy of next for 4 unique"
        egr = mrge.Extractor()
        egr.insert(None)
        assert egr.getAverageEntropyOfNext(
        ) == 0, "Bad handling of empty dicti in get average entropy of next"
        egr = mrge.Extractor()
        egr.insert(1, 1)
        assert egr.getAverageEntropyOfNext(
        ) == 0, "Bad handling of trivial dicti in get average entropy of next"
        egr.insert(2)
        egr.reset()
        assert egr.getAverageEntropyOfNext(
        ) == 0, "Bad reset failed to set average entropy of next to zero"

    def testGetProbs(self):
        egr = mrge.Extractor()
        assert egr.getProbs(0) == (0, 0), "Get Probs with trivial insertion"
        egr.insert(1)
        assert egr.getProbs(0) == (0, 0), "Get Probs with unique insertion"
        egr.insert(1, 1)
        assert egr.getProbs(0) == (
            0, 0), "Get Probs with unique insertion with repeated values"
        egr.insert(1, 1, 2)
        assert egr.getProbs(0) == (
            0, 0), "Get Probs with unique insertion with repeated and various values"
        assert egr.getProbs(2) == (fr(1, 6), fr(
            5, 1)), "Get Probs with 1 in 6 chance "+str(egr.getProbs(2))+str(egr.storage)
        egr.reset()
        assert egr.getProbs(0) == (
            0, 0), "Get Probs with trivial insertion after reset"
        egr.insert(*range(3))
        assert egr.getProbs(0) == (
            fr(1, 3), 0), "Get Probs with 3 uniq and new repeated 0"
        assert egr.getProbs(1) == (
            fr(1, 3), 1), "Get Probs with 3 uniq and new repeated 0"
        assert egr.getProbs(2) == (
            fr(1, 3), 2), "Get Probs with 3 uniq and new repeated 0"

    def testInsNewGetProb(self):
        # TODO LEFT HERE
        egr = mrge.Extractor(preNotPostRecalc=True)
        assert egr.insNewGetProb(1110) == (
            0, 0), "Bad insertion to probability of the first one"
        assert egr.insNewGetProb(1111) == (fr(1, 2), fr(
            1, 2)), "Bad calc of probability in the ins new after non-trivial insertion of second uniq"

    def testGetAccumulatedEntropy(self):
        return
        erg = mrge.Extractor(preNotPostRecalc=True)
        assert erg.getAccumulatedEntropy() == 0, "Bad entropy accumulator init "
        erg.next(1)
        erg.next(2)
        assert erg.getAccumulatedEntropy() == 1, "Bad entropy acc calc for pre-recalc with two different numbers " + \
            str(erg.getAccumulatedEntropy())
        erg.insert(3)
        erg.next(4)
        assert erg.getAccumulatedEntropy(
        ) == 3, "Bad entropy acc calc for pre-recalc with two nexts, one insert and one next, all unique"
        erg.reset()
        assert erg.getAccumulatedEntropy() == 0, "Bad reset does not reset entropy accumulator"

        erg = mrge.Extractor(preNotPostRecalc=False)
        assert erg.getAccumulatedEntropy() == 0, "Bad entropy accumulator init with post reclac"
        erg.next(1)
        assert erg.getAccumulatedEntropy(
        ) == 0, "Bad entropy accumulator with first insertion in post reclac"
        erg.next(2)
        assert erg.getAccumulatedEntropy(
        ) == 0, "Bad entropy accumulator with second insertion that is non-trivial"
        erg.next(1)
        assert erg.getAccumulatedEntropy(
        ) == 1, "Bad entropy accumulator with thrid insertion that sould produce first bit"

    def testExtraction(self):
        pass
        # TODO


if __name__ == "__main__":
    mrge.setLogger(5)
    unittest.main()
