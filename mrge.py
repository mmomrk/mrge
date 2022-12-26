#!/usr/bin/env python3
import argparse
import logging
from math import log
from collections.abc import Iterable
from collections.abc import Iterator
from fractions import Fraction as fr
import pickle

verbosity = 0

# TODO test multibank implement vs single bank fractional addition
# TODO add retro- vs avant- probability recalculation


def parseFlags():
    parser = argparse.ArgumentParser(description="A tool for extracting random bits from an external source of entropy. This is a proof of concept for a greedy extractor algorithm (hence My Random Greedy Extractor) which tries to return close to as many output bits as there is information about the entropy source. By default stdin is read for incoming information and results are sent to stdout. Input is expected to be floating point values one number per line.")
    parser.add_argument(
        '--verbose', '-v', help="Enable verbose output of code execution. Needed for debug only. INFO level is -vvv", action="count", default=0)
    parser.add_argument(
        '-i', '--input', help="Process information from file", default=None, type=str)
    parser.add_argument(
        '-o', '--output', help="Send output to file", default=None, type=str)
    parser.add_argument(
        '-b', '--base', help="will generate output in base-[base] format. Default 2", default=2, type=int)
    parser.add_argument(
        '-e', '--rev-entropy', help="Collect data until able to produce this number of bits (less latency, faster bit generation)", type=int, default=0)
    parser.add_argument(
        '-n', '--rev-block', help="Collect this number of inputs, then start producing output (less latency, faster bit generation). For practical uses revEntropy is more recommended", type=int, default=0)
    parser.add_argument(
        '-p', '--post-recalc', help="Recalculate probabilities after storing input: new items are treated to have 0 probability. Useful for dealing with non-comparable items (flag works, but non-comparable is TODO, not implemented)", action='store_true', default=False)
    parser.add_argument(
        '-s', '--save-stats', help="Save input to this file to reuse this statistics later", type=str, default=None)
    parser.add_argument(
        '-l', '--load-stats', help="Load statistics of input from this file to get a jump-start. Could be same as in the --save-stats flag", type=str, default=None)
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
    args = parseFlags()
    verbosity = args.verbose
    setLogger(verbosity)
    eFlags = {'base': args.base, 'preNotPostRecalc': not args.post_recalc, 'revBlock': args.rev_block, 'revEntropy': args.rev_entropy,
              'saveStats': args.save_stats, 'loadStats': args.load_stats, 'inp': args.input, 'outp': args.output}
    logging.debug(f"Argument space is {args}\n{eFlags}")
    return eFlags


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
    @staticmethod
    def initInp(inp: str, instream: Iterable) -> Iterable:
        ''' return something iterable: either an input file list of lines or input stream or stdin as iterable
        '''
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
            logging.debug("Initialised stdout as output")
            from sys import stdout
            retval = stdout
        return retval

    def __init__(self, base: int = 2, preNotPostRecalc: bool = True,   revBlock: int = 0, revEntropy: int = 0, saveStats: str = None,  loadStats: str = None,   inp: str = None, outp: str = None,  instream: Iterable = [], str2cmp: callable = float):
        '''
        base    -   base of output numbers
        preNotPostRecalc    -   calculate event probability before storing the event to the statistics that probability is calculated with (see lightning probability for clarifications)
        revBlock    -   allow algorithm to store data silently to release output after this amount of data points
        revEntropy  -   allow algorithm to store data silently to release output after this amount of entropy is available to be produced
        saveStats   -   save dictionary to this filename to resume processing with this information
        loadStats   -   load data dictionary from this filename
        inp - input file name
        outp - output file name
        instream    -   iterable containing items objects comparable
        str2cmp -   method to convert input string to object. Objects have to be pairwise comparable and a<b, b<c => a<c. TODO: remove this restriction with orderedDict
        revBlockGenerousMode    -   TODO? keep on recalculating history until you get output (works if we get more trivial insertions than revBlock setting, hence 0 output at revBlock insertion)
        '''
        # Algo settings:
        assert base >= 2, "Output base should be >=2"
        self.base = base
        # Possible security vulnerability: # Or perhaps a way to use objects without comparison defined
        self.prePost = preNotPostRecalc
        # Greedy parameters to configure speed vs latency:
        self.revBlock = revBlock
        self.revBlockAccumulating = revBlock > 0
        self.revEntropy = revEntropy
        self.revEntropyAccumulating = revEntropy > 0
        self.storeStatisticsFName = saveStats
        self.loadStatisticsFName = loadStats
        # io setup:
        self.input = Extractor.initInp(inp, instream)
        self.outp = Extractor.initOutp(outp)
        self.input2object = str2cmp
        # Input items are stored here:
        if self.loadStatisticsFName:
            with open(self.loadStatisticsFName, 'rb') as infile:
                self.storage = pickle.load(infile)
        else:
            self.storage = {}
        self.backlog = []
        # Parameters for interval calculation
        self.entropyAccumulator = 0
        self.outputBitsCount = 0
        self.left = 0
        self.length = 1

    def getProbs(self, item):
        ''' Get an item and calculate it probability based on dictionary. Also calculate probability to get something less than given item
        If there is no such item in storage then prob is zero. Adding to storage before calculating probability is handled by insNewGetProb()
        '''
        if self.totalEvents() == 0:
            return (0, 0)
        lessThan = 0
        for stored, count in self.storage.items():
            # Optimisation could happen here if we sort the array perhaps
            if stored >= item:
                continue
            lessThan += count
        lessThanFrac = fr(lessThan, self.totalEvents())
        if item in self.storage.keys():
            return fr(self.storage[item], self.totalEvents()), lessThanFrac
        return (0, lessThanFrac)

    def insNewGetProb(self, item):
        """ Insert item and return (its probability, probability to get item smaller than given)
        Function respects the constructor flag of pre-insertion or post-insertion probability calculation. See lightning example
        """
        if len(self.storage.keys()) == 0:
            self.insert(item)
            return (0, 0)
        if self.prePost:
            self.insert(item)
        probs = self.getProbs(item)
        if not self.prePost:
            self.insert(item)
        return probs

    # TODO redo here. This is not correct and should consider interval fit into the cell completely to avoid approximation instability
    def getNumOfNewBits(self, probability):
        # check entropy increase, check bits extraction settings, calculate number of output bits on this step
        # 0 accumulator in case of revBlock or revEntropy modes is a flag of block gather
        if self.outputBitsCount == 0:
            if self.revBlock:
                if self.totalEvents() >= self.revBlock:
                    return int(self.getTotalTheoreticalEntropy()//1)
                return 0
            if self.revEntropy:
                theory = self.getTotalTheoreticalEntropy()
                if theory >= self.revEntropy:
                    return int(theory//1)
                return 0
        newInfo = self.getEntropyOfThis(None, probability)
        accu = self.getAccumulatedEntropy()
        newBits = (accu+newInfo)//1 - accu//1
        return int(newBits)

    def updateInterval(self, probability, probSmallerThan):
        '''
        update stored data on leftmost interval fraction and on interval length
        '''
        if probability == 0:
            return
        assert 0 <= probability <= 1, "Bad probability passed to updateInterval"
        assert 0 <= probSmallerThan <= 1, "Bad integral probability passed to updateInterval"
        self.left = self.left + self.length*probSmallerThan
        self.length = self.length * probability

    # TODO error is around this function. Got to reconsider intervals calculation algo. Approximation gives unstable results of last digit
    def generateOutputApproximation(self, length):
        outputApprox = self.left+self.length/2
        outputRight = self.left+self.length
        approximationApproximation = 0
        plus = fr(1, 2)
        retValues = []
        step = fr(1, self.base)
        for _ in range(length):
            for s in range(self.base-1):
                # if outputApprox <= approximationApproximation + step:
                if outputRight <= approximationApproximation + step and self.left >= approximationApproximation:
                    retValues.append(s)
                    break
                approximationApproximation += step
            else:
                retValues.append(self.base-1)
            step = step/self.base
        logging.debug(f"Approximation is {retValues}")
        return retValues
        # calculate middle point
        # return number from 0..1 in given base
        pass

    def recalcInterval(self, items):
        self.left = 0
        self.length = 1
        for item in items:
            self.updateInterval(*self.getProbs(item))

    def next(self, item):
        probs = self.insNewGetProb(item)
        newBits = self.getNumOfNewBits(probs[0])
        self.entropyAccumulator += self.getEntropyOfThis(item, prob=probs[0])
        self.updateInterval(*probs)
        logging.debug(
            f"Nexted {item} to form {self.storage} now entorpy is {self.entropyAccumulator} with probs {probs} and output bits {self.outputBitsCount} and new bits is {newBits}")
        if self.revBlockAccumulating or self.revEntropyAccumulating:
            if self.totalEvents() >= self.revBlock:
                self.revBlockAccumulating = False
            self.recalcInterval(self.backlog)
            self.entropyAccumulator = self.getTotalTheoreticalEntropy()
            if self.entropyAccumulator >= self.revEntropy:
                self.revEntropyAccumulating = False
            logging.debug(
                f"Recalculated stuff due to block nature. Now inserted {item} to form {self.storage} now entorpy is {self.entropyAccumulator} with probs {probs} and output bits {self.outputBitsCount} and new bits is {newBits}")
        if newBits > 0:
            # If in block mode and it's time to spit new bits: recalc interval and update entropyAccumulator accordingly
            randnum = self.generateOutputApproximation(
                int(self.entropyAccumulator//1))
            self.outputBitsCount += newBits
            return (True, randnum[-newBits:])
        else:
            return (False, [])

        # get probability and Probability not greater than
        # add entropy accumulator, get number of new bits based on config << getNumOfNewBits
        # recalc left , recalc length
        # if bits returned > 0: generate output approximation and throw n bits and reset entropy accumulator
        pass
        return False, []

    def loop(self):
        for line in self.input:
            if line == '' or line == '\n' or line == '\r\n':
                continue
            item = self.input2object(line)
            succ, arr = self.next(item)
            if succ:
                if verbosity > 3:
                    self.outp.write('>> ')
                self.outp.write(''.join(map(str, arr)))
                if verbosity > 3:
                    self.outp.write('\n')
                self.outp.flush()

    def reset(self):
        self.entropyAccumulator = 0
        self.outputBitsCount = 0
        self.left = 0
        self.length = 1
        self.storage = {}
        self.backlog = []

    def insert(self, *items):
        ''' Method is used for testing. To insert items without recalculating stuff in the process
        '''
        logging.info("Inserting " + str(items))
        for item in items:
            if item is None:
                continue
            if self.revBlock or self.revEntropy:
                self.backlog.append(item)
            if item in self.storage:
                self.storage[item] += 1
            else:
                self.storage[item] = 1
        if self.storeStatisticsFName:
            with open(self.storeStatisticsFName, 'wb') as outFile:
                pickle.dump(self.storage, outFile)

    def totalEvents(self):
        # No need for special case {}
        return sum(self.storage.values())

    def getEntropyOfThis(self, item, prob=None):
        if prob is None:
            prob = self.getProbs(item)[0]
        if prob == 0:
            return 0
        ent = -log(1.*prob, self.base)
        return ent

    def getAverageEntropyOfNext(self):
        if self.totalEvents() == 0:
            return 0
        return self.getTotalTheoreticalEntropy()/self.totalEvents()

    def getAccumulatedEntropy(self):
        return self.entropyAccumulator

    def getTotalTheoreticalEntropy(self):
        if not self.storage:
            return 0
        # Sum of -n*log(p) in given base
        s = sum((-1.*v*log(1.*v/self.totalEvents(), self.base)
                for k, v in self.storage.items()))
        logging.debug(
            f"Calculating entropy:\nTotal {self.totalEvents()}, base {self.base}, events:\n{self.storage}\nCalculated entropy {s}")
        return s


if __name__ == "__main__":
    params = parseargs()
    e = Extractor(**params)
    e.loop()
