#!/usr/bin/env python3
import argparse
import logging
from math import log
from collections.abc import Iterable
from collections.abc import Iterator

verbosity = 0

# TODO test multibank implement vs single bank fractional addition
# TODO add retro- vs avant- probability recalculation


def parseArgs():
    parser = argparse.ArgumentParser(description="A tool for extracting random bits from an external source of entropy. This is a proof of concept for a greedy extractor algorithm (hence My Random Greedy Extractor) which tries to return close to as many output bits as there is information about the entropy source. By default stdin is read for incoming information and results are sent to stdout. Input is expected to be floating point values one number per line.")
    parser.add_argument(
        '--verbose', '-v', help="Enable verbose output of code execution. Needed for debug only", action="count")
    parser.add_argument(
        '-i', '--input', help="Process information from file", default=None, type=str)
    parser.add_argument(
        '-o', '--output', help="Send output to file", default=None, type=str)
    parser.add_argument(
        '-z', '--zfloor', help="Only generate output based on integer weights, no fractional bits optimisation", action="store_true")
    parser.add_argument(
        '-d', '--decimal', help="Only generate output based on fractional weigts, no integer bits are used. (Used for debug only)", action="store_true")
    parser.add_argument(
        '-b', '--base', help="will generate output in base-[base] format. Default 2", default=2, type=int)
    return parser.parse_args()


def setLogger(lvl, **kwargs):
    lls = [logging.CRITICAL, logging.ERROR, logging.WARNING,
           logging.INFO, logging.DEBUG, logging.NOTSET]
    if lvl < len(lls):
        ll = lls[lvl]
    else:
        ll = lls[-1]
    logging.basicConfig(
        level=ll, format='\t%(asctime)s %(levelname)s \n%(message)s', datefmt='%s', **kwargs)
    logging.debug("Setting logger debug {lvl}, {ll}, {lls}, {kwargs}")


def parseargs():
    global verbosity
    args = parseArgs()
    iFileName = args.input
    oFileName = args.output
    verbosity = args.verbose
    integersFlag = args.zfloor
    fractionalFlag = args.decimal
    base = args.base
    setLogger(verbosity)

    logging.debug("Argument space is ", args)


# Make an iterator from stdin
class ISIterator(Iterator):
    def __init__(self):
        from sys import stdin
        self.sin = stdin

    def __next__(self):
        inl = self.sin.readline().strip()
        if inl:
            return inl
        raise StopIteration()


class Extractor():
    '''
    inp - input file name
    outp - output file name
    ints - use integer divisions for generation
    fracts - use fractional divisions for generation
    base    -   base of output numbers
    instream    -   iterable containing items objects comparable
    str2cmp -   method to convert input string to object. Objects have to be pairwise comparable and a<b, b<c => a<c
    '''

    @staticmethod
    def initInp(inp, instream):
        retval = None
        if inp:
            with open(inp, 'r') as infile:
                retval = infile.readlines()
        elif instream:
            retval = instream
        else:
            retval = ISIterator()
        return retval

    @staticmethod
    def initOutp(outp):
        retval = None
        if outp:
            try:
                # file will be closed. Have to use try
                # with open(outp, 'w') as outfile:
                retval = open(outp, 'w')
            except Exception as e:
                raise e
        else:
            from sys import stdout
            retval = stdout
        return retval

    def __init__(self, inp: str = None, outp: str = None, ints: bool = True, fracts: bool = True, base: int = 2, instream: Iterable = [], str2cmp: callable = int):
        # io setup:
        self.input = Extractor.initInp(inp, instream)
        self.outp = Extractor.initOutp(outp)
        # generator output control:
        self.ints = ints
        self.fracts = fracts
        assert base >= 2, "Output base should be >=2"
        self.base = base
        self.compare = str2cmp
        # Input items are stored here:
        self.storage = {}
        # Divisions of normalised space
        self.divs = 1

    class InfoBank():
        def __init__(self, base=2, resetLead=True, resetRest=True):
            self.base = base
            self.readiness = 0
            self.bins = [0 for x in range(base)]
            self.candidate = 0
            self.resetLead = resetLead
            self.resetRest = resetRest

        def next(self, addr, weight, inw):
            #self.readiness += inw
            self.readiness += inw
            self.bins[addr] += weight
            binsmax = max(self.bins)
            if binsmax == self.bins[addr]:
                self.candidate = addr
            #logging.debug(f"Bank {self.readiness}, {self.bins}")
            if self.readiness < 1.:
                return (False, -1)  # -1 if for branchless handling
            maxval = binsmax
            maxind = self.bins.index(maxval)
            # This check is to mix return value in case of a tie:
            self.bins.pop(maxind)
            if max(self.bins) == maxval:
                # mix the output, not stuck to first pos of max value
                maxind = addr
            self.reset(lead=maxind)
            return (True, lead=maxind, leadval=maxval)

        def reset(self, lead=-1, leadval=None):
            if self.resetRest:
                self.bins = [0 for x in range(self.base)]
            if self.resetLead:

            self.readiness = 0

    # TODO

    def next(self, item):
        pass
        return False, []

    def reset(self):
        self.storage = {}

    # todo: add support of items
    def insert(self, item, *items):
        logging.info("Inserting " + str(item))
        if item in self.storage:
            self.storage[item] += 1
        else:
            self.storage[item] = 1

    def getCurrentEntropy(self):
        if not self.storage:
            return 0
        # Could be a point to optimise in the unreachably distant future:
        totalEvents = sum(self.storage.values())
        s = sum((-v/totalEvents*log(v/totalEvents, self.base)
                for k, v in self.storage.items()))
        logging.debug(
            f"Calculating entropy:\nTotal {totalEvents}, base {self.base}, events:\n{self.storage}\nCalculated entropy {s}")
        return s

    # Try to fit new probabilities into the linearised gaps
    def recalcDivs(self):
        if Extractor.sRecalcDivs(self.storage, self.divs):
            if Extractor.sRecalcDivs(self.storage, self.divs+1):
                self.divs += 1
                logging.info(f"Increasing divisions to {self.divs}")
        else:
            # Perhaps a solid proof would be nice but not today
            self.divs -= 1
            logging.info(f"Decreasing divisions to {self.divs}")

    # This method will only correct divs by 1 either up or down. Perhaps generalising would be nice
    @staticmethod
    def sRecalcDivs(events, divs):
        totalEvents = sum(events.values())
        ascending = sorted(events.keys())
        p = 0
        probs = [p := p+1.*events[x]/totalEvents for x in ascending]
        logging.debug("probabilities "+str(list(probs)))
        newStep = 1./(divs)
        prevDiv = 0
        currentDiv = newStep
        nStep = 1
        divok = False
        for pi in probs:
            logging.debug(
                f"division calc from {divs}\n{divok}\t{pi}>{currentDiv}")
            if pi > currentDiv:
                if divok:
                    nStep += 1
                    currentDiv = nStep*newStep
                    if pi > currentDiv:
                        divok = False
                        break
                    continue
            else:
                divok = True
        logging.debug(f"Divisions test {divs} passed? {divok}")
        return divok


if __name__ == "__main__":
    parseargs()
