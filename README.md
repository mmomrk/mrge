# MRGE

## My Randomness Greedy Extractor

This is a tool to process random events into random numbers, i.e the
randomness extractor.

The input of the tool could be any (generally speaking) stream of events that could be distinguished from one another. *At the time this text is written only a subset of events that have defined compare operation is accepted as input*.

The output of the tool is a stream of truly randomly distributed numbers that have the same entropy as the input source.

The main features of MRGE are:

- Requires no prior information about source statistics and distribution
- Generates output starting at the first non-trivial event (zero latency)
- Entropy of the output is equal (*not strictly all of the time, but it jumps to the floor of input entropy when ready*) to the entropy of the input
- Preserves "fractional" bits: will generate output of 15 bits for 10 events with 1.5 bit entropy
- Increases (*or decreases*) output bits per event when gathers more information about entropy source


The other nice features are:

- Can store its state in order to use previous statistics of the entropy source to get a jump-start when restarted
- Has ability to sacrifice latency to get a bigger throughput (the --rev_block and the --rev_entropy flags)
- Can work with stdin/stdout or files input/output (or generally speaking anything with same interfaces)
- Can output random numbers in any base


The price for the abovementioned features is:

- Requires a lot more computational power for its operation compared to conventional randomness extractors
- Written in Python
- Contains at least one bug at the moment this document is written


## Help output

usage: mrge.py [-h] [--verbose] [-i INPUT] [-o OUTPUT] [-b BASE]
               [-e REV_ENTROPY] [-n REV_BLOCK] [-p] [-s SAVE_STATS]
               [-l LOAD_STATS]

A tool for extracting random bits from an external source of entropy. This is
a proof of concept for a greedy extractor algorithm (hence My Random Greedy
Extractor) which tries to return close to as many output bits as there is
information about the entropy source. By default stdin is read for incoming
information and results are sent to stdout. Input is expected to be floating
point values one number per line.

options:

  -h, --help            show this help message and exit

  --verbose, -v         Enable verbose output of code execution. Needed for
                        debug only. INFO level is -vvv

  -i INPUT, --input INPUT
                        Process information from file

  -o OUTPUT, --output OUTPUT
                        Send output to file

  -b BASE, --base BASE  will generate output in base-[base] format. Default 2

  -e REV_ENTROPY, --rev-entropy REV_ENTROPY
                        Collect data until able to produce this number of bits
                        (less latency, faster bit generation)

  -n REV_BLOCK, --rev-block REV_BLOCK
                        Collect this number of inputs, then start producing
                        output (less latency, faster bit generation). For
                        practical uses revEntropy is more recommended

  -p, --post-recalc     Recalculate probabilities after storing input: new
                        items are treated to have 0 probability. Useful for
                        dealing with non-comparable items (flag works, but
                        non-comparable is TODO, not implemented)

  -s SAVE_STATS, --save-stats SAVE_STATS
                        Save input to this file to reuse this statistics later

  -l LOAD_STATS, --load-stats LOAD_STATS
                        Load statistics of input from this file to get a jump-
                        start. Could be same as in the --save-stats flag


## Example

```
$echo -e "1\n2\n3\n4\n5" > test.input
$./mrge.py -i test.input
111111

$echo -e "1\n4\n2\n5\n3" | ./mrge.py
110111

$echo -e "1\n4\n2\n5\n3" | ./mrge.py --rev-block 5
00100010101

$echo -e "1\n4\n2\n5\n3" | ./mrge.py --rev-block 5 --base 7
0642
```

Note: most likely this output will change in a little while

## Theoretical background

The tool constantly updates a probability function and probability density of the input source. Based on that information it maps the input event stream onto the 0..1 interval hence converging to some division of the interval with monotonously growing precision.

## Known bugs

- The output of the approximation method is unstable. Have to bind getNumOfNewBits method to it

## Purpose

I got fired and have some time for an old project of mine. Perhaps it could be worth a PhD or a cookie or something. Or perhaps it has been invented before and published by somebody. 

When 1.0 version is released I'll check if it is possible and worth the effort to integrate it into The Kernel.

## Licence

MIT. Can't stop Rock and Roll
