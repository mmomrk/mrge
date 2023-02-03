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
        # print(egr.storage)
        egr.insert(1, 1)
        #print("ASDFSAF", egr.storage)
        egr.insert(1, 1, 2)
        # print(egr.storage)
        res = egr.insNewGetProb(2)
        assert res == (fr(1, 5), fr(
            4, 5)), "Get Probs with 1 in 6 chance "+str(egr.storage) + str(res)
        egr.reset()
        assert egr.insNewGetProb(0) == (
            0, 0), "Get Probs with trivial insertion after reset"
        egr.reset()
        egr.insert(*range(3))
        assert mrge.Extractor.getProbs(0, egr.storage) == (
            fr(1, 3), 0), "Get Probs with 3 uniq and new repeated 0"
        assert mrge.Extractor.getProbs(1, egr.storage) == (
            fr(1, 3), fr(1, 3)), "Get Probs with 3 uniq and new repeated 1"
        assert mrge.Extractor.getProbs(2, egr.storage) == (
            fr(1, 3), fr(2, 3)), "Get Probs with 3 uniq and new repeated 2"

    def testInsNewGetProb(self):
        egr = mrge.Extractor(preNotPostRecalc=True)
        res = egr.insNewGetProb(1110)
        assert res == (
            0, 0), "Bad insertion to probability of the first one "+str(res)
        assert egr.insNewGetProb(1111) == (fr(1, 2), fr(1, 2)),\
            "Bad calc of probability in the ins new after non-trivial insertion of second uniq"
        assert egr.insNewGetProb(1112) == (fr(1, 3), fr(2, 3)),\
            "Bad calc of probability in the ins new after non-trivial insertion of second uniq"
        assert egr.insNewGetProb(1110.1) == (fr(1, 4), fr(1, 4)),\
            "Bad calc of probability in the ins new after non-trivial insertion of second uniq"

        egr = mrge.Extractor(preNotPostRecalc=False)
        assert egr.insNewGetProb(1110) == (0, 0),\
            "Bad insertion to probability of the first one with post recalc of probability"
        res = egr.insNewGetProb(1110)
        assert res == (1, 0),\
            f"Bad insertion to trivial second insertion with post recalc {res}"
        assert egr.insNewGetProb(1111) == (0, 1),\
            "Bad insertion probability of new item with probability post-recalc"
        res = egr.insNewGetProb(0)
        assert res == (0, 0),\
            "Bad insertion probability of new item with probability post-recalc inserting 0 " + \
            str(res)
        assert egr.insNewGetProb(1) == (0, fr(1, 4)),\
            "Bad insertion probability of new item to the 1/4 place with probability post-recalc"
        # fixed=None part:
        e = mrge.Extractor()
        fixSto = {0: 1, 1: 1}
        inputArr = [0, 1]*10
        def getProb(x): return e.insNewGetProb(x, fixed=fixSto)
        res = list(map(getProb, inputArr))
        assres = [(fr(1, 2), fr(0, 1)), (fr(1, 2), fr(1, 2))]*10
        assert res == assres, f"ins new get prb fixed test not passed {res}"

    def testGetAccumulatedEntropy(self):
        erg = mrge.Extractor(preNotPostRecalc=True)
        assert erg.getAccumulatedEntropy() == 0, "Bad entropy accumulator init "
        erg.next2(1)
        erg.next2(2)
        assert erg.getAccumulatedEntropy() == 1, "Bad entropy acc calc for pre-recalc with two different numbers " + \
            str(erg.getAccumulatedEntropy())
        erg.insert(3)
        erg.next2(4)
        assert erg.getAccumulatedEntropy() == 3,\
            "Bad entropy acc calc for pre-recalc with two nexts, one insert and one next, all unique"
        erg.reset()
        assert erg.getAccumulatedEntropy() == 0, "Bad reset does not reset entropy accumulator"

        erg = mrge.Extractor(preNotPostRecalc=False)
        assert erg.getAccumulatedEntropy() == 0, "Bad entropy accumulator init with post reclac"
        erg.next2(1)
        assert erg.getAccumulatedEntropy() == 0,\
            "Bad entropy accumulator with first insertion in post reclac"
        erg.next2(2)
        assert erg.getAccumulatedEntropy() == 0,\
            "Bad entropy accumulator with second insertion that is non-trivial"
        erg.next2(1)
        assert erg.getAccumulatedEntropy() == 1,\
            "Bad entropy accumulator with thrid insertion that sould produce first bit"

    def testNumOfNewBits(self):
        e = mrge.Extractor(preNotPostRecalc=True)
        # does not affect entropy accumulator
        e.insert(1, 2, 3)
        assert e.getNumOfNewBits(
            1./4) == 2, "Bad calc of new bits when testing first char with 1/4 chance"
        # Affects entropy accumulator
        e.next2(0)
        assert e.getNumOfNewBits(mrge.Extractor.getProbs(
            0, e.storage)[0]) == 2, "Bad calc of new bit when nexting 1/4"
        e.insert(1, 1, 1, 1, 1, 1, 1)
        assert e.getNumOfNewBits(e.insNewGetProb(
            1)[0]) == 0, "Bad new bits with very probable insertion"
        e.reset()
        e.next2(1)
        assert e.getNumOfNewBits(e.insNewGetProb(
            2)[0]) == 1, "Bad new bits with 1/2 insertion"
        assert e.getNumOfNewBits(e.insNewGetProb(
            3)[0]) == 1, "Bad new bits with 1/3 insertion"
        assert e.getNumOfNewBits(e.insNewGetProb(
            4)[0]) == 2, "Bad new bits with 1/4 insertion"
        e.reset()
        e.next2(1)
        e.next2(2)
        e.next2(3)
        e.next2(4)
        e.next2(0)
        assert e.getNumOfNewBits(e.insNewGetProb(
            5)[0]) == 3, "Bad new bits with 1/6 insertion"
        e = mrge.Extractor(preNotPostRecalc=False)
        e.insert(1, 2, 3)
        assert e.getNumOfNewBits(1./3) == 1, "Bad new of post calc 1/3"
        e.next2(3)
        e.insert(1, 2)
        # 2 is because it stored .5 bit from the first 1/3 event
        assert e.getNumOfNewBits(
            1./3) == 2, f"Bad new of post calc of second 1/3 with entr {e.entropyAccumulator}"
        e1 = mrge.Extractor(revBlock=4)
        e.reset()
        for x in range(5):
            e.next2(x)
            e1.next2(x)
        assert e1.entropyAccumulator > e.entropyAccumulator, "Optimal block algo does not work"

    def testUpdateInterval(self):
        e = mrge.Extractor()
        assert e.left == 0 and e.length == 1, "Bad interval init"
        e.updateInterval(fr(1, 2), fr(1, 2))
        assert e.left == fr(1, 2) and e.length == fr(
            1, 2), "Bad int update for 1/2, 1/2"
        e.reset()
        e.next2(1)
        e.next2(0)
        assert e.left == 0 and e.length == fr(
            1, 2), f"Bad interval handling of first 1/2 prob {e.left}, {e.length}"
        e.reset()
        e.insert(1, 2, 3)
        e.next2(4)
        assert e.left == fr(3, 4) and e.length == fr(
            1, 4), f"Bad interval handling of first 1/4 left {e.left}, length {e.length}"
        e.next2(1)
        assert e.left == fr(3, 4) and e.length == fr(
            2, 20), "Bad int handling of 2/5 prob insertion after 1/4"
        e.reset()
        for _ in range(8):
            e.updateInterval(fr(1, 2), fr(1, 2))
        assert 1 - e.left == fr(1, 256) and e.length == fr(1,
                                                           256), "Bad update of 8 times the 1/2 shifted 1/2"

    def testGenerateOutputApproximation(self):
        e = mrge.Extractor()
        r1 = e.next2(1)
        assert r1 == (False, []), "Bad return of first insert"
        r2 = e.next2(0)
        assert r2 == (True, [0]), "Bad return of second insertion"
        e.reset()
        e.insert(1, 2, 3)
        r3 = e.next2(4)
        assert r3 == (True, [1, 1]), "Bad return of first 1/4 insertion"
        e.reset()
        e.insert(1, 2, 3)
        r4 = e.next2(-11)
        assert r4 == (
            True, [0, 0]), "Ba return of first 1/4 insertion with 0 shift "+str(r4)
        e.reset()
        e.insert(*[1, 2, 3]*100)
        r5 = e.next2(1)
        r6 = e.next2(1)
        assert r5 == (True, [0]), "Bad first return of 1/3 test "+str(r5)
        assert r6 == (True, [0, 0]), "Bad second return of 1/3 test"+str(r6)
        e.reset()
        e.length = fr(1, 128)
        e.left = 0
        # This made me lose a certain amount of time.
        #rl = e.generateOutputApproximation(8)
        #assert rl == [0, 0, 0, 0, 0, 0, 0, 0], f"Bad apprximation of 0 for 1/128 {rl}"
        e3 = mrge.Extractor(base=3)
        e3.next2(111)
        e3.next2(222)
        assert e3.outputBitsCount == 0, "Got one trite before 3 numbers received " + \
            str(e3.outputBitsCount)
        res3 = e3.next2(333)
        assert res3 == (True, [2]), "Bad retrieval of base 3"

    def testPickle(self):
        eout = mrge.Extractor(saveStats=".test.pickle")
        eout.insert(1, 2, 3, 4)
        ein = mrge.Extractor(loadStats=".test.pickle")
        assert ein.storage == {1: 1, 2: 1, 3: 1, 4: 1}, "Bad pickle"

    def testBlock(self):
        revlen = 4
        e = mrge.Extractor(revBlock=revlen)
        for i in range(revlen - 1):
            nexts = e.next2(i*10)
            assert nexts == (
                False, []), "Got output before reaching revBlock "+str(nexts)+str(i)
        succ, array = e.next2(555)
        assert succ and len(array) == 8,\
            "Got bad output of buffered block of length " + \
            str(revlen)+str(array)
        e = mrge.Extractor(revEntropy=11)
        for i in range(20):
            succ, bits = e.next2(i)
            if succ:
                assert len(
                    bits) == 11 and i == 4, "Buffered entropy is calculated incorrectly"
                break
        revlen = 4
        e0 = mrge.Extractor(revBlock=revlen)
        for _ in range(revlen):
            succ, arr = e0.next2(0)
            assert not succ, "Trivial insertion in buffered mode resulted in bits output"
        # This test is the motivation towards the revLenGenerousMode flag: this run could have resulted in 3 bits after inserting 556 here
        succ, arr = e0.next2(556)
        assert succ and len(
            arr) == 2, "Bad behav of buffered mode after first non-trivial post-buffer insertion "+str(arr)

    def testHistory2storage(self):
        h2s = mrge.Extractor.history2storage
        eventBank = h2s(range(10))
        assert all((x == 1 for x in eventBank.values())
                   ), "Bad history conversion for all 1"
        eb = h2s([])
        assert eb == {}, "Bad hist2sto for empty"
        eb = h2s(('a', 'b', 'a'))
        assert eb == {'a': 2, 'b': 1}, "Bad hist2sto for 'aba'"

    def testGetProbsStatic(self):
        gp = mrge.Extractor.getProbs  # (item,storage)
        h2s = mrge.Extractor.history2storage
        hist = []
        for r in range(1, 3):
            hist += range(10)
            sto = h2s(hist)
            for x in range(10):
                probs = gp(x, sto)
                assert probs == (fr(1, 10), fr(
                    x, 10)), f"Bad prob getProbs for equal probs len 10 in round {r} for item {x} with probs {probs}"
            probs11 = gp(11, sto)
            assert probs11 == (
                0, 1), "Bad prob getProbs for unexisting check in round "+str(r)
        probs = gp(1, {})
        assert probs[0] == 0, "Bad prob getProbs for unexisting storage"
        probs = gp(2, h2s(range(3)))
        assert probs == (fr(1, 3), fr(
            2, 3)), f"Pad getProbs for 1/3 probs insertion {probs}"

    def testCalcIntervalStatic(self):
        ci = mrge.Extractor.calcInterval  # curInt, probs
        defIntl = (0, 1)
        inl = ci(defIntl, (1, 0))
        assert inl == defIntl, "Bad static interval recalc for trivial case"
        probs = (fr(1, 3), fr(1, 2))
        inl = ci(defIntl, probs)
        assert inl == (fr(1, 2), fr(
            1, 3)), "Bad calcInterval behav for 1/3, 1/2"
        inl2 = ci(inl, probs)
        assert inl2 == (fr(2, 3), fr(
            1, 9)), f"Bad calcInterval for the second 1/3, 1/2 {inl2}"
        probsFromSto = mrge.Extractor.getProbs(1, {1: 5, 2: 1, 3: 4, 4: 0})
        inlFromSto = ci(defIntl, probsFromSto)
        assert inlFromSto == (
            0, fr(1/2)), "Bad calcInterval from handwritten storage"

    def testGetNumOfNewBits2Static(self):
        nbf = mrge.Extractor.getNumOfNewBits2
        # def getNumOfNewBits2(approxLen: int, prevBitsNum: int,  history: list = [], storage: dict = None, revEnt: int = 0, revBlock: int = 0, base: int = 2):
        nb1 = nbf(0, 0)
        assert nb1 == 0, "Bad num new bits trivial call"
        nb2 = nbf(1, 0)
        assert nb2 == 1, "Bad num new bits simplest case "+str(nb2)
        nb3 = nbf(1, 0, history=[1, 2, 3, 4], revBlock=4)
        assert nb3 == 8, "Bad num new simple revBlock "+str(nb3)
        nb4 = nbf(1, 0, history=[1, 2, 3], revBlock=4)
        assert nb4 == 0, "Bad num new bits revblock pre-case "+str(nb4)
        # Should ignore approxLen and recalc it inside
        nb5 = nbf(999, 0, history=[1, 2, 3, 4], revEnt=8)
        assert nb5 == 8, "Bad num new bits revEnt"
        nb6 = nbf(2, 1, history=[1, 2, 3, 4], revEnt=8)
        assert nb6 == 1, "Bad num new bits revent off by nonzero prevBits"
        nb7 = nbf(999, 0, history=[2, 3, 4], revEnt=8)
        assert nb7 == 0, "Bad num bew bits revEnt off by not enough info " + \
            str(nb7)

    def testGenerateOutputApproximation2(self):
        e = mrge.Extractor()
        goa = e.generateOutputApproximation2
        ci = mrge.Extractor.calcInterval  # interval, probs
        gp = mrge.Extractor.getProbs  # item, storage
        e.next2(1)
        a1 = goa()
        assert a1 == [], "Bad return of first insert"
        e.next2(0)
        a2 = goa()
        assert a2 == [0], "Bad return of second insertion"
        e.reset()
        e.insert(1, 2, 3)
        e.next2(4)
        a3 = goa()
        assert a3 == [
            1, 1], "Bad return of first 4 after 1 2 3 insertion "+str(a3)
        e.reset()
        e.insert(1, 2, 3)
        e.next2(0)
        a4 = goa()
        assert a4 == [0, 0], "Bad return of 0 after 1,2,3 insertion"
        e.reset()
        e.insert(*[1, 2, 3]*100)
        e.next2(1)
        e.next2(1)
        a5 = goa()
        assert a5 == [0, 0, 0], "Bad return of p=1/3 test "+str(a5)
        e.reset()
        e.length = fr(1, 128)
        e.left = 0
        al = goa()
        assert al == [0, 0, 0, 0, 0, 0,
                      0], f"Bad apprximation of 0 for 1/128 (2^7) {al}"
        e3 = mrge.Extractor(base=3)
        e3.next2(111)
        e3.next2(222)
        assert e3.outputBitsCount == 0, "Got one trite before 3 numbers received " + \
            str(e3.outputBitsCount)
        e3.next2(333)
        res3 = e3.generateOutputApproximation2()
        assert res3 == [2], "Bad retrieval of base 3 "+str(res3)
        # pt2
        e = mrge.Extractor()
        for x in [1.1, 1.2, 1.3, 1.4]:
            e.next2(x)
        # Requires working recalcInterval2
        outHist = e.generateOutputApproximation2(history=[1.2, 1.3])
        assert outHist == [
            0, 1, 1, 0], "Bad output of history-based outApprox "+str(outHist)
        outHist = e.generateOutputApproximation2(history=[1.1, 1.8])
        assert outHist == [
            0, 0], "Bad output of outApprox with not-fully-ovelapping history"

    def testRecalcInterval2(self):
        e = mrge.Extractor()
        ri = mrge.Extractor.recalcInterval2  # backlog, storage
        h2s = mrge.Extractor.history2storage  # history
        lele = ri([], {})
        assert lele == (0, 1), "Bad interval recalc of nonexistant"
        lele = ri([1], {1: 1})
        assert lele == (0, 1), "Bad interval recalc of single event"
        lele = ri([1], {0: 1})
        assert lele == (0, 1), "Bad interval recalc of inexistent event"
        lele = ri([0, 0, 0], {0: 100})
        assert lele == (0, 1), "Bad interval recalc of trivial case"
        lele = ri([1, 2], {1: 1, 2: 1})
        assert lele == (fr(1, 4), fr(
            1, 4)), "Bad interval recalc of two nontrivial events"
        lele = ri([3], {1: 1, 2: 1, 3: 1})
        assert lele == (fr(2, 3), fr(1, 3)), "Bad interval recalc of third"

    def testSoftReset(self):
        e = mrge.Extractor()
        e.next2(1)
        e.next2(0)
        e.next2(1)
        res, outp = e.next2(0)
        assert res == False, "Bad return of less than one weight bit"
        e.reset()
        e.next2(21)
        e.next2(20)
        e.next2(21)
        e.softReset()
        res, outp = e.next2(20)
        assert res and outp == [0], "Bad return after soft reset "+str(outp)

    def testRounding(self):
        e = mrge.Extractor(rounding=.2)
        e.insert(*[1, 2, 3]*100)
        succ, bits = e.next2(3)
        assert succ and len(
            bits) == 1, "Bad 1 of 3 insertion in the rounding test"
        succ, bits = e.next2(3)
        # Get data AND reset internal state EXCEPT for statistics in storage
        assert succ and len(bits) == 2 and \
            e.outputBitsCount == 0 and e.entropyAccumulator == 0 and \
            e.backlog == [] and e.left == 0 and e.length == 1 and \
            len(e.storage.keys()) > 0, "Bad softreset of 1.5 entropy example"
        e.reset()
        e.round = 0.005
        e.insert(*([0, 1]*16)[:-1])
        succ, bits = e.next2(3)
        assert succ and len(bits) == 5 and \
            e.outputBitsCount == 0 and e.entropyAccumulator == 0 and \
            e.backlog == [] and e.left == 0 and e.length == 1 and \
            len(e.storage.keys()) > 0, "Bad softreset of 2.0 entopy example"

    def testDictionaryEnumerator(self):
        cooldict = mrge.DictionaryEnumerator()
        assert len(cooldict.keys()) == 0 and len(
            cooldict.items()) == 0, "Bad enum dict init on lens"
        cooldict['a'] = 0
        cooldict[' '] = 0
        vals = list(cooldict.values())
        assert vals == [0, 0], "bad values for enum dict "+str(vals)
        assert cooldict.keys() == {'a', ' '}, "Bad keys of enum dict"
        prevID = -1
        for iditem, count in cooldict.items():
            assert type(
                iditem) == int and prevID != iditem, f"enumerator dict failed to return proper comparable keys {prevID}<{iditem}"
            prevID = iditem
        assert cooldict.__contains__('a'), "No contains operation in enum dict"
        assert not cooldict.__contains__('z'), "bug in conatins of enum dict"
        assert len(cooldict) == 2, "Bad len for enum dict"
        cooldict['e'] = 3
        assert len(cooldict) == 3, "Bad len incr for enum dict"
        cooldict['a'] += 1
        assert cooldict['a'] == 1, "Bad operation on enum dict value"
        cd = cooldict.copy()
        cooldict.clear()
        assert len(cooldict) == 0, "Bad clear of enum dict"
        assert len(cd) == 3, "Bad copy of enum dict"
        assert 'a' in cd.keys(), "Bad keys method of enum dict"
        # This is where things get confusing. I need integers as keys returned by items operation:
        for pair in ((0, 1), (1, 0), (2, 3)):
            assert pair in cd.items(), "Bad itemsrepresentation of enum dict "+str(cd.items())
        assert 1 in cd.values(), "Bad values in enum dict"
        cd.setdefault('d', 12)
        cd.setdefault('e', 12)
        assert cd['e'] == 3 and cd['d'] == 12, "Bad setdefault of enum dict"
        # I am bored and will not code .update unless i really need to
        # And a bunch of other methods too
        assert cd.get('e', 55) == 3 and cd.get('z', 55) == 55, \
            "Bad get of enum dicti"

    # TODO: add reset test
    def testConversionToStringAcceptingInput(self):
        e = mrge.Extractor()
        e.convert2stringing()
        succ, bits = e.next2('a')
        assert not succ and len(
            bits) == 0, "Bad first next of stringy "+str(bits)+str(succ)
        e.next2('b')
        e.next2('c')
        s, bits = e.next2('a')
        assert s and len(bits) == 1 and bits[0] == 0,\
            "Bad third next of stringy "+str(bits)
        #s,b = e.next2('a')
        #assert s and b and len(b) == 1 and b[0] == 0, "Bad first meaningful next of stringy "+str(b)
        s, b = e.next2('a')
        assert s and b and len(b) == 1 and b[0] == 0,\
            "Bad second meaningful next of stringy "+str(b)

        er = mrge.Extractor(preNotPostRecalc=False, str2cmp=None, revBlock=4)

        class Dummy(object):
            ...
        d = Dummy()
        assert er.input2object(d) == d and er.input2object(44) == 44,\
            "Bad identity method for er.ent handling in input2object"
        assert er.prePost == False, "Something changed flag prenotpostrecalc after init"
        assert type(e.storage) == mrge.DictionaryEnumerator
        for x in range(3):
            s, bits = er.next2(str(x))
            assert er.backlog != [], "Items are not stored while gathering er.tropy"
            assert not s and bits == [], "Uncarry of bits for revBlock"
        succ, bits = er.next2(str(4))
        assert succ and bits == [0, 0, 0, 1, 1, 0, 1, 1],\
            "Bad revblock for dict enum revBlock "+str(bits)
        # 17 and 8 are magic constants from empirical observations. Delete this test if it seems like it is wrong:
        for x in range(17):
            s, b = er.next2(str(x % 4))
            if x > 8:
                assert s and len(
                    b) > 0 and er.outputBitsCount > 0, "A reset detected after first stage of revblock is over "+str(x)


if __name__ == "__main__":
    mrge.setLogger(5)
    unittest.main()
