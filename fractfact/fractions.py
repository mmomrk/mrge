#!/usr/bin/env python

from collections import OrderedDict as odi

# Most of the methods here are obsolete and will be taken from fractions module


# Wheel factorisation to return dictionary of primes and powers
def factor(inum: int) -> dict:
    num = inum
    if num == 1:
        return {1: 1}
    if num == 0:
        return {}
    lazy = [2, 3, 5, 7]
    res = odi()
    # res = odi({2: 0, 3: 0, 5: 0, 7: 0})
    # res = odi({2:0,3:0,5:0,7:0,11:0,13:0,17:0,19:0,23:0,29:0}) #nope
    if num < 0:
        res[-1] = 1
        num = -num
    for prime in lazy:
        while num//prime*prime == num:
            if prime in res:
                res[prime] += 1
            else:
                res[prime] = 1
            num = num//prime
    testn = 11
    wp = 0
    # next = [ 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173 179, 181, 191, 193, 197, 199]
    plu = [2, 4, 2, 4, 6, 2, 6, 4, 2, 4, 6, 6, 2, 6, 4, 2, 6, 4, 6, 8, 4,
           2, 4, 2, 4, 14, 4, 6, 2, 10, 2, 6, 6, 4, 6, 6, 2, 10, 2, 4, 2, 12]
    while testn*testn <= num:
        testn = int(testn)
        if num//testn*testn == num:
            # print("-", num, testn, res)
            if testn in res:
                res[testn] += 1
            else:
                res[testn] = 1
            num = num//testn
        else:
            testn += plu[wp]
            wp = (wp + 1) % len(plu)
    if num != 1:
        if num in res:
            res[num] += 1  # it seems legit
        else:
            res[num] = 1
    res[1] = 1  # This must be
    # print(inum, " -> ", res)
    return res


# Sugar,sugar
def fsimp(num: int, denom: int):
    return simp(factor(num), factor(denom))


# Fraction simplification
def simp(num: dict, denom: dict) -> dict:
    if num == {}:
        return {}, {1: 1}
    # print("Simp entr ", num,denom)
    numset = set(num.keys())
    denomset = set(denom.keys())
    simplify = numset & denomset
    # 1/1 =  /  # ... not
    for prime in simplify - {1}:
        mini = min(num[prime], denom[prime])
        num[prime] -= mini
        if num[prime] == 0:
            num.pop(prime)
        denom[prime] -= mini
        if denom[prime] == 0:
            denom.pop(prime)
    if -1 in denom.keys():
        denom.pop(-1)
        # there is a chance of a bug here, but i've thrown a bunch of tests on it
        num[-1] = 1

    # print("simp leave", num,denom)
    return num, denom


def multiplyDicti(d1: dict, d2: dict) -> dict:
    if len(d1) > len(d2):
        lesser = d2.copy()
        bigger = d1.copy()
    else:
        lesser = d1.copy()
        bigger = d2.copy()
    if len(lesser) == 0:
        return {}
    for prime in lesser.keys():
        if prime == 1:
            continue
        if prime in bigger:
            if prime == -1:
                bigger.pop(prime)
            else:
                bigger[prime] += lesser[prime]
        else:
            bigger[prime] = lesser[prime]
    # print(d1, d2, "=", bigger)
    return bigger


# Dictionary of prime powers to number
def repr2num(n: dict) -> int:
    if n == {}:
        return 0
    res = 1
    for pr, powe in n.items():
        for _ in range(powe):
            res *= pr
    return res


# Honey,honey
def fsumFrac(fr1, fr2) -> dict:
    n1, d1 = fr1
    n2, d2 = fr2
    return sumFrac(factor(n1), factor(d1), factor(n2), factor(d2))


def sumFrac(in1: dict, id1: dict, in2: dict, id2: dict) -> (dict, dict):
    if in1 == {}:
        return simp(in2, id2)
    if in2 == {}:
        return simp(in1, id1)
    n1, d1 = simp(in1, id1)
    n2, d2 = simp(in2, id2)
    comdenom = multiplyDicti(d1, d2)
    numLeft = repr2num(multiplyDicti(n1, d2))
    numRight = repr2num(multiplyDicti(d1, n2))
    numerator = numLeft+numRight
    #print(f"Mult {in1}/{id1} by {in2}/{id2}. WIth common denumerator {comdenom} and left num sum {numLeft} and right numsum {numRight} resulted in numerator {numerator}")
    return simp(factor(numerator), comdenom)
