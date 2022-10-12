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
        s,v = egr.next(2)
        assert s and v, "non-trivial insertion resulted in no data"
        egr.reset()
        egr.next(1)
        s,v = egr.next(1)
        assert not s and not v, "trivial second insertion resulted in new data"
        egr.reset()
        egr.next(1)
        s,v = egr.next(0)


if __name__ == "__main__":
    mrge.setLogger(1)
    unittest.main()
