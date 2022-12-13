#!/usr/bin/env python

import unittest
import fractions as fr


class testFractions(unittest.TestCase):
    def testDummy(self):
        assert True, "Things are really bad. Get a break"

    def testFactoring(self):
        multiples = fr.factor(1)
        assert 1 in multiples, "bad factorisation of 1"
        m2 = fr.factor(2)
        facts = {2: {2: 1}, 3: {3: 1}, 4: {2: 2}, 5: {5: 1}, 6: {2: 1, 3: 1}, 7: {7: 1}, 8: {2: 3}, 9: {
            3: 2}, 10: {2: 1, 5: 1}, 11: {11: 1}, 12: {2: 2, 3: 1}, 3628800: {2: 8, 3: 4, 5: 2, 7: 1}}
        for num, repre in facts.items():
            m = fr.factor(num)
            for num, powe in repre.items():
                assert num in repre and repre[num] == powe, "Bad factorisation of "+str(
                    num)+" "+str(repre)
        m3 = fr.factor(7907*7919)
        assert 7907 in m3 and 7919 in m3, "Bad factor. Search 7907 and 7919)"
        x = 100
        m4 = fr.factor(x)
        # Yes, I am noob
        assert x == 100, "Python is passing by ref!"

    def testFractionSimplification(self):
        num = fr.factor(30)
        assert 3 in num and 5 in num and 2 in num, "Bad factor of 30"
        denom = fr.factor(10)
        assert 2 in denom and 5 in denom, "Bad factor of 10"
        rnum, rdenom = fr.simp(num, denom)
        assert 3 in rnum and set(rdenom.keys()) == {
            1}, "Bad simplification of 30/10"

        num, denom = fr.simp(fr.factor(23), fr.factor(51))
        assert 23 in num and 3 in denom and 17 in denom, "Bad factor of 23/51"
        num, denom = fr.simp(fr.factor(2), fr.factor(2))
        assert num == {1: 1} and denom == {1: 1}, "Bad simplification of 2/2"

    def testMultiplicatoin(self):
        n1 = fr.factor(999)
        n2 = fr.factor(555)
        res = fr.factor(555*999)
        # print("555*999",res)
        assert res == fr.multiplyDicti(
            n1, n2), "bad multiplicaiton of 555 999)"
        n1 = fr.factor(9)
        n2 = fr.factor(1)
        res = fr.factor(9)
        assert res == fr.multiplyDicti(n1, n2), "bad multiplicaiton of 9*1)"
        n1 = fr.factor(9)
        n2 = fr.factor(0)
        res = fr.factor(0)
        assert res == fr.multiplyDicti(n1, n2), "bad multiplicaiton of 9*0)"
        n1 = fr.factor(-1)
        n2 = fr.factor(-1)
        res = fr.factor(1)
        assert res == fr.multiplyDicti(n1, n2), "Bad multiplication of -1*-1"

    def testRepresentationToNumber(self):
        num = 7823*1997
        r1 = fr.factor(num)
        assert num == fr.repr2num(
            r1), "Bad multiplication in simplest function!"
        num = 1024*768
        r1 = fr.factor(num)
        assert num == fr.repr2num(r1), "Check your screen resolution!"

    def testFractionSum(self):
        n1, d1 = 4, 3
        n2, d2 = 4, 3
        rn, rd = fr.fsumFrac((n1, d1), (n2, d2))
        resn = fr.repr2num(rn)
        resd = fr.repr2num(rd)
        assert resn == 8, "Bad numerator in 4/3+4/3"
        assert resd == 3, "Bad denominator in 4/3+4/3"

        def autotestFrac(n1, d1, n2, d2, rn, rd):
            reprn, reprd = fr.fsumFrac((n1, d1), (n2, d2))
            resn = fr.repr2num(reprn)
            resd = fr.repr2num(reprd)
            assert resn == rn, f"Bad numerator {resn} in {n1}/{d1}+{n2}/{d2} with dicti res {reprn} / {reprd} "
            assert resd == rd, f"Bad denomenator {resd} in {n1}/{d1}+{n2}/{d2} with dicti res {reprn} / {reprd} "

        autotestFrac(1, 1, 2, 2, 2, 1)
        autotestFrac(1, 2, 2, 4, 1, 1)
        # Achievement unlocked: I've used WA to correct my assert in this one:
        autotestFrac(1, 2, 2, 3, 7, 6)
        autotestFrac(5, 6, -1, 12, 3, 4)
        autotestFrac(2, 1, -5, -5, 3, 1)
        autotestFrac(1, 2048, 1, 4096, 3, 4096)
        autotestFrac(1, 2, 1, 2, 1, 1)
        autotestFrac(1, 2, 1, -2, 0, 1)
        autotestFrac(1, 2, -1, 2, 0, 1)
        autotestFrac(-1, 2, -1, 2, -1, 1)
        autotestFrac(-1, 2, 1, -2, -1, 1)
        autotestFrac(-1, 2, -1, -2, 0, 1)
        autotestFrac(-1, -2, -1, -2, 1, 1)
        autotestFrac(1, 333, 112, 999, 115, 999)
        autotestFrac(0, 2, 0, 3, 0, 1)

        pass


if __name__ == "__main__":
    unittest.main()
