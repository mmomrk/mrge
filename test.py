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

    # This funciton is a mess but more tests is not less tests
    def testGetProbs(self):
        egr = mrge.Extractor(preNotPostRecalc=False)
        assert egr.insNewGetProb(0) == (
            0, 0), "Get Probs with trivial insertion"
        egr.reset()
        egr.insert(1)
        res = egr.insNewGetProb(0)
        assert res == (0, 0), "Get Probs with unique insertion "+str(res)
        egr.reset()
        egr.insert(1, 1)
        assert egr.insNewGetProb(0) == (
            0, 0), "Get Probs with unique insertion with repeated values"
        egr.reset()
        egr.insert(1, 1)
        egr.insert(1, 1, 2)
        assert egr.insNewGetProb(0) == (
            0, 0), "Get Probs with unique insertion with repeated and various values"
        egr.reset()
        print(egr.storage)
        egr.insert(1, 1)
        print("ASDFSAF", egr.storage)
        egr.insert(1, 1, 2)
        print(egr.storage)
        res = egr.insNewGetProb(2)
        assert res == (fr(1, 5), fr(
            4, 5)), "Get Probs with 1 in 6 chance "+str(egr.storage) + str(res)
        egr.reset()
        assert egr.insNewGetProb(0) == (
            0, 0), "Get Probs with trivial insertion after reset"
        egr.reset()
        egr.insert(*range(3))
        assert egr.getProbs(0) == (
            fr(1, 3), 0), "Get Probs with 3 uniq and new repeated 0"
        assert egr.getProbs(1) == (
            fr(1, 3), fr(1, 3)), "Get Probs with 3 uniq and new repeated 1"
        assert egr.getProbs(2) == (
            fr(1, 3), fr(2, 3)), "Get Probs with 3 uniq and new repeated 2"

    def testInsNewGetProb(self):
        egr = mrge.Extractor(preNotPostRecalc=True)
        res = egr.insNewGetProb(1110)
        assert res == (
            0, 0), "Bad insertion to probability of the first one "+str(res)
        assert egr.insNewGetProb(1111) == (fr(1, 2), fr(
            1, 2)), "Bad calc of probability in the ins new after non-trivial insertion of second uniq"
        assert egr.insNewGetProb(1112) == (fr(1, 3), fr(
            2, 3)), "Bad calc of probability in the ins new after non-trivial insertion of second uniq"
        assert egr.insNewGetProb(1110.1) == (fr(1, 4), fr(
            1, 4)), "Bad calc of probability in the ins new after non-trivial insertion of second uniq"

        egr = mrge.Extractor(preNotPostRecalc=False)
        assert egr.insNewGetProb(1110) == (
            0, 0), "Bad insertion to probability of the first one with post recalc of probability"
        res = egr.insNewGetProb(1110)
        assert res == (
            1, 0), "Bad insertion to trivial second insertion with post recalc "+str(res)
        assert egr.insNewGetProb(1111) == (
            0, 1), "Bad insertion probability of new item with probability post-recalc"
        res = egr.insNewGetProb(0)
        assert res == (
            0, 0), "Bad insertion probability of new item with probability post-recalc inserting 0 "+str(res)
        assert egr.insNewGetProb(1) == (0, fr(
            1, 4)), "Bad insertion probability of new item to the 1/4 place with probability post-recalc"

    def testGetAccumulatedEntropy(self):
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

    def testNumOfNewBits(self):
        e = mrge.Extractor(preNotPostRecalc=True)
        # does not affect entropy accumulator
        e.insert(1, 2, 3)
        assert e.getNumOfNewBits(
            1./4) == 2, "Bad calc of new bits when testing first char with 1/4 chance"
        # Affects entropy accumulator
        e.next(0)
        assert e.getNumOfNewBits(e.getProbs(
            0)[0]) == 2, "Bad calc of new bit when nexting 1/4"
        e.insert(1, 1, 1, 1, 1, 1, 1)
        assert e.getNumOfNewBits(e.insNewGetProb(
            1)[0]) == 0, "Bad new bits with very probable insertion"
        e.reset()
        e.next(1)
        assert e.getNumOfNewBits(e.insNewGetProb(
            2)[0]) == 1, "Bad new bits with 1/2 insertion"
        assert e.getNumOfNewBits(e.insNewGetProb(
            3)[0]) == 1, "Bad new bits with 1/3 insertion"
        assert e.getNumOfNewBits(e.insNewGetProb(
            4)[0]) == 2, "Bad new bits with 1/4 insertion"
        e.reset()
        e.next(1)
        e.next(2)
        e.next(3)
        e.next(4)
        e.next(0)
        assert e.getNumOfNewBits(e.insNewGetProb(
            5)[0]) == 3, "Bad new bits with 1/6 insertion"
        e = mrge.Extractor(preNotPostRecalc=False)
        e.insert(1, 2, 3)
        assert e.getNumOfNewBits(1./3) == 1, "Bad new of post calc 1/3"
        e.next(3)
        e.insert(1, 2)
        # 2 is because it stored .5 bit from the first 1/3 event
        assert e.getNumOfNewBits(
            1./3) == 2, f"Bad new of post calc of second 1/3 with entr {e.entropyAccumulator}"
        e1 = mrge.Extractor(revBlock=4)
        e.reset()
        for x in range(5):
            e.next(x)
            e1.next(x)
        assert e1.entropyAccumulator > e.entropyAccumulator, "Optimal block algo does not work"


if __name__ == "__main__":
    mrge.setLogger(5)
    unittest.main()
