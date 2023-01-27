#!/usr/bin/env python3
import argparse
import logging
from math import log
from collections.abc import Iterable
from collections.abc import Iterator
from fractions import Fraction as fr
import pickle

verbosity = 0


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
        '-e', '--rev-entropy', help="Collect data until able to produce this number of bits (less latency, faster bit generation). If rev block and rev entropy are set together then the first one to occur will be executed", type=int, default=0)
    parser.add_argument(
        '-n', '--rev-block', help="Collect this number of inputs, then start producing output (less latency, faster bit generation). For practical uses revEntropy is more recommended. If rev block and rev entropy are set together then the first one to occur will be executed", type=int, default=0)
    parser.add_argument(
        '-p', '--post-recalc', help="Recalculate probabilities after storing input: new items are treated to have 0 probability. Useful for dealing with non-comparable items (flag works, but non-comparable is TODO, not implemented)", action='store_true', default=False)
    parser.add_argument(
        '-s', '--save-stats', help="Save input to this file to reuse this statistics later", type=str, default=None)
    parser.add_argument(
        '-l', '--load-stats', help="Load statistics of input from this file to get a jump-start. Could be same as in the --save-stats flag", type=str, default=None)
    parser.add_argument('-r', '--round', help="Round. Allow this amount of bits to be lost here and there. Assumed to be 0..1. Lower values would result in more information output but would lead to use of bigger integer numbers in the code. Bigger numbers are a bad thing when overflow is to be considered. Zero and negative turn this flag off and probably lead to bad things (default)", type=float, default=-1)
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
    '''
    More like init
    '''
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


class DictionaryEnumerator(dict):
    '''
    This is a class to allow mrge to operate over any items, not only the ones with defined compare operation
    '''

    def __init__(self):
        self.id = 0
        self.lookup = {}
        self.count = {}

    def __contains__(self, *ar, **kw):
        return self.lookup.__contains__(*ar, **kw)

    def __delitem__(self, *ark, **kw):
        # Not sure if it is a nice thing to do, but
        self.count.__delitem__(self.lookup(ark[0]))
        return self.lookup.__delitem__(*ark, **kw)

    def __repr__(self):
        items = list((x, self.__getitem__(x)) for x in self.lookup.keys())
        # for some reason f"{{items}}" STOPPED working and started retrieving "{items}" string
        return (f"DE_{items}_DE")

    # Trez importance
    def __getitem__(self, item):
        return self.count.__getitem__(self.lookup.__getitem__(item))

    def __eq__(self, value):
        if type(self) != type(value):
            return False
        return self.lookup == value.lookup and self.count == value.count

    def __iter__(self):
        # Not tested. Not trusted
        return self.lookup.__iter__()

    def __len__(self):
        # All those ,/ make me look like a pro
        return len(self.lookup)

    # nope
    # def __or__

    def __reversed__(self):
        # Not tested. Not trusted
        return self.lookup.__reversed__()

    def __setitem__(self, item, value):
     # This is the main method, basically
        itemid = self.lookup.setdefault(item, self.id)
        if itemid == self.id:
            self.id += 1
        self.count[itemid] = value

    def __sizeof__(self):
        # Not tested
        return self.lookup.__sizeof__()+self.count.__sizeof__()+self.id.__sizeof__()

    def clear(self):
        self.lookup.clear()
        self.count.clear()
        self.id = 0

    def copy(self):
        cp = DictionaryEnumerator()
        cp.id = self.id
        cp.lookup = self.lookup.copy()
        cp.count = self.count.copy()
        return cp

    def get(self, key, default=None):
        return self.count.get(self.lookup.get(key), default)

    def items(self):
        # Second meaningful and actualy useful method for the class
        return {(intID, self.count[intID]) for intID in self.lookup.values()}

    def keys(self):
        return self.lookup.keys()

    def values(self):
        return self.count.values()

    # def pop():
    # def popitem
    # def update
    # def fromkeys

    def setdefault(self, key, default=None):
        itemid = self.lookup.setdefault(key, self.id)
        if self.id == itemid:
            self.id += 1
        return self.count.setdefault(itemid, default)

    def getID(self, key):
        return self.lookup[key]


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

    def __init__(self, base: int = 2, preNotPostRecalc: bool = True,   revBlock: int = 0, revEntropy: int = 0, saveStats: str = None,  loadStats: str = None,   inp: str = None, outp: str = None,  instream: Iterable = [], str2cmp: callable = float, rounding: float = -1):
        '''
        base    -   base of output numbers
        preNotPostRecalc    -   calculate event probability before storing the event to the statistics that probability is calculated with (see lightning probability for clarifications). Note: setting this to False is sort of bit better for security at the cost of latency delay by 1 event per each new event
        revBlock    -   allow algorithm to store data silently to release output after this amount of data points
        revEntropy  -   allow algorithm to store data silently to release output after this amount of entropy is available to be produced
        saveStats   -   save dictionary to this filename to resume processing with this information
        loadStats   -   load data dictionary from this filename
        inp - input file name
        outp - output file name
        instream    -   iterable containing items objects comparable
        str2cmp -   method to convert input string to object. If uncomparable items are given as input, then 'None' or 'str' should be written. WARNING: most likely you want to use preNotPostRecalc flag set to False when this happens
        revBlockGenerousMode    -   TODO? keep on recalculating history until you get output (works if we get more trivial insertions than revBlock setting, hence 0 output at revBlock insertion)
        round   -   allow this amount of bits to be lost. Expected to be 0..1
        '''
        # Algo settings:
        assert base >= 2, "Output base should be >=2"
        self.base = base
        # Possible security vulnerability: # Or perhaps a way to use objects without comparison defined
        self.prePost = preNotPostRecalc
        # Greedy parameters to configure speed vs latency:
        self.revBlock = revBlock
        # TODO: remove *Accumulating flags when refactor and place next2() instead of next()
        self.revBlockAccumulating = revBlock > 0
        self.revEntropy = revEntropy
        self.revEntropyAccumulating = revEntropy > 0
        self.storeStatisticsFName = saveStats
        self.loadStatisticsFName = loadStats
        # io setup:
        self.input = Extractor.initInp(inp, instream)
        self.outp = Extractor.initOutp(outp)
        self.input2object = str2cmp
        if str2cmp is None:
            self.input2object = lambda x: x
        # Input items are stored here:
        if self.loadStatisticsFName:
            with open(self.loadStatisticsFName, 'rb') as infile:
                self.storage = pickle.load(infile)
        elif str2cmp in (None, str):
            self.storage = DictionaryEnumerator()
        else:
            self.storage = {}
        self.backlog = []
        # Parameters for interval calculation
        self.entropyAccumulator = 0
        self.outputBitsCount = 0
        self.left = 0
        self.length = 1
        self.round = rounding

    @staticmethod
    def getProbs(item, storage: dict):
        ''' Get an item and calculate it probability based on dictionary. Also calculate probability to get something less than given item
        If there is no such item in storage then prob is zero. Adding to storage before calculating probability is handled by insNewGetProb()
        return (probaility density, Probability function value)
        '''
        totalEvents = sum(storage.values())
        if totalEvents == 0:
            return (0, 0)
        lessThan = 0
        itemComparable = item
        # for non-comparable inputs
        if type(storage) == DictionaryEnumerator:
            if item not in storage.keys():
                return (0, 1)
            itemComparable = storage.getID(item)
        # Count number of events smaller than given:
        for stored, count in storage.items():
            # Optimisation could happen here if we sort the array perhaps
            if stored >= itemComparable:
                continue
            lessThan += count
        lessThanFrac = fr(lessThan, totalEvents)
        logging.debug(
            f"GetProbs finished with prob X/{totalEvents} and less than frac {lessThanFrac}. Generated by event {item}({itemComparable}) from storage {storage}")
        if item in storage.keys():
            return fr(storage[item], totalEvents), lessThanFrac
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
        probs = Extractor.getProbs(item, self.storage)
        if not self.prePost:
            self.insert(item)
        return probs

    @staticmethod
    def getNumOfNewBits2(approxLen: int, prevBitsNum: int,  history: list = [], storage: dict = None, revEnt: int = 0, revBlock: int = 0, base: int = 2):
        '''
        Return amount of bits to be taken from approximation's back
        If revBlock or revEnt is enabled, then history is considered for recalculation of approximation length with given base
        prevBitsNum will act as a deactivator for revEnt and revBlock action
        '''
        logging.debug(
            f"Entered gNONB2 with apprLen {approxLen}, prevBits {prevBitsNum}, hist {history}, revEnt|Block={revEnt}|{revBlock}")
        # Perhaps there is a better way to rewrite these conditions
        if prevBitsNum == 0 and (revBlock or revEnt):
            if revBlock and len(history) < revBlock:
                return 0
            if revEnt or (revBlock and len(history) >= revBlock):
                if not storage:
                    storage = Extractor.history2storage(history)
                # TODO BUG HERE # most likely not anymore
                newApprox = Extractor.soutputApproximation2(
                    history=history, storage=storage, base=base)
                logging.debug(f"new approximation for rev check {newApprox}")
                approxLen = len(newApprox)
            if revEnt and approxLen < revEnt:
                return 0
        return approxLen-prevBitsNum

    # redo here. This is not correct and should consider interval fit into the cell completely to avoid approximation instability
    # Done. Use getNumOfNewBits2 instead
    def getNumOfNewBits(self, probability):
        '''
        check entropy increase, check bits extraction settings, calculate number of output bits on this step
        0 accumulator in case of revBlock or revEntropy modes is a flag of block gather
        '''
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
        # self.left = self.left + self.length*probSmallerThan
        # self.length = self.length * probability
        updatedInterval = Extractor.calcInterval(
            (self.left, self.length), (probability, probSmallerThan))
        if updatedInterval:
            self.left, self.length = updatedInterval

    @ staticmethod
    def calcInterval(interval, probs):
        probability, probSmallerThan = probs
        intLeft, intLength = interval
        if probability == 0:
            # watch it. seems logical
            return interval
        assert 0 <= probability <= 1, "Bad probability passed to updateInterval " + \
            str(probability)
        assert 0 <= probSmallerThan <= 1, "Bad integral probability passed to updateInterval"
        return (intLeft+intLength*probSmallerThan,
                intLength*probability)

    @ staticmethod
    def history2storage(history):
        from collections import defaultdict
        storage = defaultdict(lambda: 0)
        # Perhaps a map would be more professional-looking
        for event in history:
            storage[event] += 1
        return storage

    # Generally speaking it might be more proper to make history a boolean flag instead of list
    def generateOutputApproximation2(self, history=None):
        '''
        return full binary sequence based on the state of class
        '''
        intervalLeft = self.left
        intervalRight = self.left + self.length
        return Extractor.soutputApproximation2(history=history, storage=self.storage, base=self.base, intervalLeft=intervalLeft, intervalRight=intervalRight)

    @ staticmethod
    def soutputApproximation2(history=None, storage=None, base=2, intervalLeft=0, intervalRight=1):
        logging.debug(
            f"Entering approx with hist {history}, stor {storage} LR:{intervalLeft}..{intervalRight}")
        if history:
            intervalLeft, length = Extractor.recalcInterval2(
                history, storage)
            intervalRight = intervalLeft+length
            # logging.debug( f"Changed interval to LR: {intervalLeft}..{intervalRight}")
        approximationApproximation = 0
        retValues = []
        step = fr(1, base)
        coverOK = True
        # Purists will refactor here. This is essentially a base-inary search of interval
        while coverOK:
            for s in range(base):
                appRight = approximationApproximation+step
                #logging.debug(f"Approx iter {s}/{base}, step {step}, interval lr {intervalLeft} {intervalRight}, approx LR {approximationApproximation} {appRight}")
                if intervalLeft < appRight and\
                        intervalRight > appRight:
                    coverOK = False
                    #logging.debug("approx break Right condition")
                    break
                # could have written big condition in one if
                if intervalLeft < approximationApproximation and\
                        intervalRight >= approximationApproximation:
                    coverOK = False
                    #logging.debug("approx break Left condition")
                    break
                if intervalLeft >= approximationApproximation and \
                        intervalRight <= appRight:
                    retValues.append(s)
                    break
                elif intervalRight < intervalLeft:
                    logging.critical(
                        "Approximation found illogical condition {intervalRight}<{intervalLeft} on step {s}/{base-1} having interval step {step} and interval [{intervalLeft}:{intervalRight}]")
                    import sys
                    sys.exit(1)
                approximationApproximation += step
            else:
                logger.warn(
                    "Approximation moved through whole range of base and found no positive nor negative conditions")
                return retValues
            step = step/base
        return retValues

    def generateOutputApproximation(self, length):
        outputApprox = self.left+self.length/2
        outputRight = self.left+self.length
        approximationApproximation = 0
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

    @ staticmethod
    def recalcInterval2(backlog, storage):
        '''
        A method to get interval based on history. Used to recalc approximation interval for the revEnt and revBlock cases.
        backlog -   array of history
        storage -   dictionary of cases. May contain more events than backlog
        '''
        left = 0
        length = 1
        interval = (left, length)
        for item in backlog:
            probs = Extractor.getProbs(item, storage)
            interval = Extractor.calcInterval(interval, probs)
            # logging.debug( f"Recalcing interval for {item} gave {interval} iwth probs {probs} and storage {storage}")
        return interval

    # Used to update interval after revBlock or revEntropy has been met
    def recalcInterval(self, history):
        '''
        Reset self.left and self.length based on history taken from items array
        '''
        self.left = 0
        self.length = 1
        for item in history:
            self.updateInterval(*Extractor.getProbs(item, self.storage))

    def next2(self, item):
        #logging.debug(f"Enter next2 with new item {item}")
        probs = self.insNewGetProb(item)
        self.left, self.length = Extractor.calcInterval(
            (self.left, self.length), probs)
        approx = self.generateOutputApproximation2()
        newBits = Extractor.getNumOfNewBits2(
            len(approx), self.outputBitsCount, history=self.backlog,
            storage=self.storage, revEnt=self.revEntropy,
            revBlock=self.revBlock, base=self.base)
        self.entropyAccumulator += self.getEntropyOfThis(item, prob=probs[0])
        if (self.revBlock or self.revEntropy) and newBits:
            logging.debug("Detected rev-Block/Entropy been satisfied")
            self.revBlock = 0
            self.revEntropy = 0
            # This is not quite optimal since this method has already been called in getNumOfNewBits2. Refactor maybe
            approx = self.generateOutputApproximation2(self.backlog)
            # backlog=[] is a flag to not recalc interval in getNumOfNewBits2
            self.entropyAccumulator = self.getTotalTheoreticalEntropy()
            # interval recalc is performed in generateOutputApprox..<-refactor?
            self.recalcInterval(self.backlog)
            self.backlog = []
            # if this branch is met then kind of an incorrect probs is passed to debug output
        self.outputBitsCount += newBits
        logging.debug(
            f"Nexted {item} to form {self.storage} now entorpy is {self.entropyAccumulator:.2f} with probs {probs} and output bits {self.outputBitsCount} and new bits is {newBits}")
        if not newBits:
            return (False, [])
        # soft reset part <- for refactor
        if self.round > 0 and self.entropyAccumulator - self.round < self.outputBitsCount:
            logging.critical("THIS IS NOT FINISHED")
            logging.debug(f"Doing soft reset with round={self.round}")
            self.softReset()
        return (True,  approx[-newBits:])

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
            self.left, self.length = Extractor.recalcInterval2(
                self.backlog, self.storage)
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

    # TODO: add proper init for ENUMERATOR
    def convert2stringing(self, storage={}):
        self.reset()
        # store strings to self.storage
        self.input2object = lambda x: x
        # allow storage to accept strings
        self.storage = DictionaryEnumerator()
        # self.storage = DictionaryEnumerator(storage)
        # make judgements after information is retrieved because corresponding comparable id grows monotonously
        self.prePost = False

    def loop(self):
        for line in self.input:
            if line == '' or line == '\n' or line == '\r\n':
                continue
            try:
                item = self.input2object(line)
            except ValueError:
                self.convert2stringing()
            # succ, arr = self.next(item)
            succ, arr = self.next2(item)
            if succ:
                if verbosity > 3:
                    self.outp.write('>> ')
                self.outp.write(''.join(map(str, arr)))
                if verbosity > 3:
                    self.outp.write('\n')
                self.outp.flush()

    def reset(self):
        '''
        This is complete reset of the extractor state
        '''
        # logging.debug(f"RESET")
        self.softReset(hardReset=True)
        self.storage = {}
        self.revBlockAccumulating = True
        self.revEntropyAccumulating = True

    def softReset(self, hardReset=False):
        '''
        This is a reset to allow saving of storage. This will lose some of the accumulated entropy, but will allow the fraction maths to be reset and start accumulating scary numbers again
        '''
        if not hardReset:
            logging.debug(
                f"Soft Reset from state: output {self.outputBitsCount}, accumulated entropy {self.entropyAccumulator:.1f}, left {self.left}, length {self.length}")
        self.outputBitsCount = 0
        self.entropyAccumulator = 0
        self.left = 0
        self.length = 1
        self.backlog = []
        if type(self.storage) == DictionaryEnumerator:
            self.convert2stringing()

    def insert(self, *items):
        ''' Method is used for testing. To insert items without recalculating stuff in the process
        '''
        logging.info("Inserting " + str(items))
        for item in items:
            if item is None:
                continue
            if self.revBlock or self.revEntropy:
                self.backlog.append(item)
            # if item in self.storage:
            self.storage.setdefault(item, 0)
            self.storage[item] += 1
            # else:
            # self.storage[item] = 1
        if self.storeStatisticsFName:
            with open(self.storeStatisticsFName, 'wb') as outFile:
                pickle.dump(self.storage, outFile)

    def totalEvents(self):
        # No need for special case {}
        return sum(self.storage.values())

    def getEntropyOfThis(self, item, prob=None):
        if prob is None:
            prob = Extractor.getProbs(item, self.storage)[0]
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
