# MRGE

## My Randomness Greedy Extractor

This is a tool to process random events into random numbers, i.e the
randomness extractor.

The input of the tool could be any (generally speaking) stream of events that could be distinguished from one another. 

The output of the tool is a stream of truly randomly distributed numbers that have the same entropy as the input source.

The main features of MRGE are:

- Requires no prior information about source statistics and distribution
- Generates output starting at the first non-trivial event (zero latency)
- Entropy of the output is equal (*not strictly all of the time, but it jumps to the floor of input entropy when ready*) to the entropy of the input
- Preserves "fractional" bits: will generate output of 15 bits for 10 events with 1.5 bit entropy, theoretically. IRL getting 10 inputs of exactly 1.5 bit each is very unlikely
- Increases (*or decreases*) output bits per event when gathers more information about entropy source


The other nice features are:

- Can store its state in order to use previous statistics of the entropy source to get a jump-start when restarted
- Has ability to sacrifice latency to get a bigger throughput (the --rev_block and the --rev_entropy flags)
- Can work with stdin/stdout or files input/output (or generally speaking anything with same interfaces)
- Can output random numbers in any base


The price for the abovementioned features is:

- Requires a lot more computational power for its operation compared to conventional randomness extractors
- Written in Python


## Help output

```
usage: mrge.py [-h] [--verbose] [-i INPUT] [-o OUTPUT] [-b BASE] [-e REV_ENTROPY] [-n REV_BLOCK] [-p] [-s SAVE_STATS] [-l LOAD_STATS] [-r ROUND]
               [-c {int,str,none,float}] [-f [FIXED]]

A tool for extracting random bits from an external source of entropy. This is a proof of concept for a greedy extractor algorithm (hence My Random
Greedy Extractor) which tries to return close to as many output bits as there is information about the entropy source. By default stdin is read for
incoming information and results are sent to stdout. Input is expected to be floating point values one number per line.

options:
  -h, --help            show this help message and exit
  --verbose, -v         Enable verbose output of code execution. Needed for debug only. INFO level is -vvv
  -i INPUT, --input INPUT
                        Process information from file
  -o OUTPUT, --output OUTPUT
                        Send output to file
  -b BASE, --base BASE  will generate output in base-[base] format. Default 2
  -e REV_ENTROPY, --rev-entropy REV_ENTROPY
                        Collect data until able to produce this number of bits (less latency, faster bit generation). If rev block and rev entropy
                        are set together then the first one to occur will be executed
  -n REV_BLOCK, --rev-block REV_BLOCK
                        Collect this number of inputs, then start producing output (less latency, faster bit generation). For practical uses
                        revEntropy is more recommended. If rev block and rev entropy are set together then the first one to occur will be executed
  -p, --post-recalc     Recalculate probabilities after storing input: new items are treated to have 0 probability. Useful for dealing with non-
                        comparable items (flag works, but non-comparable is TODO, not implemented)
  -s SAVE_STATS, --save-stats SAVE_STATS
                        Save input to this file to reuse this statistics later
  -l LOAD_STATS, --load-stats LOAD_STATS
                        Load statistics of input from this file to get a jump-start. Could be same as in the --save-stats flag
  -r ROUND, --round ROUND
                        Round. Allow this amount of bits to be lost here and there. Assumed to be 0..1. Lower values would result in more information
                        output but would lead to use of bigger integer numbers in the code. Bigger numbers are a bad thing when overflow is to be
                        considered. Zero and negative turn this flag off and probably lead to bad things (default)
  -c {int,str,none,float}, --convert {int,str,none,float}
                        Use other method to process string input instead of float. 'none' is synonim to 'str' when working in the command line
  -f [FIXED], --fixed [FIXED]
                        This argument will block insertions to Extractor.storage and predefine probabilities if value is provided. Example syntax:
                        '7/22' - this will set p(0)=fr(7,22), p(1)=1-p(0). Only 0-1 input is supported with this flag. Setting '-c int' is
                        recommended. Not properly tested
```

## Example

Note: construction '| sed -e "s/ /\n/g" |' replaces whitespaces with the newline character as required for the input of the program to work correctly. And to show sequence of numbers clearly in the console

```
$ echo -e "1 2 3 4 5" | sed -e "s/ /\n/g" > test.input
$ ./mrge.py -i test.input
111111

$ echo -e "1 4 2 5 3" | sed -e "s/ /\n/g" | ./mrge.py
$ echo -e "1 3 2 5 4" | sed -e "s/ /\n/g" | ./mrge.py
110100

$ echo -e "1 4 2 5 3" | sed -e "s/ /\n/g" | ./mrge.py --rev-block 5
0010001010

$ echo -e "1 4 2 5 3" | sed -e "s/ /\n/g" | ./mrge.py --rev-block 5 --base 7
0642

$ echo -e "Never gonna give you up
Never gonna let you down
Never gonna run around and desert you
Never gonna make you cry
Never gonna say goodbye
Never gonna tell a lie and hurt you" | sed -e "s/ /\n/g" | ./mrge.py -p -c str
000101100111100110110100010000010010
```

## Theoretical background

The extractor's backbone is a method of information-weighted graphs inexact isomorphisms. More in the article

## Known bugs

- TBD

## Purpose

I got fired and have some time for an old project of mine. Perhaps it could be worth a PhD or a cookie or something. Or perhaps it has been invented before and published by somebody. 

When 1.0 version is released I'll check if it is possible and worth the effort to integrate it into The Kernel.

## Codebase TODO

- (DONE) Add handling of non-comparable input
- (DONE) Add rounding flag for soft-resetting
- Add default setting of post not pre handling because security of the first bit. Or maybe not. Should be discussed with the professionals. Not an issue with statistics storage pickling though
- Add rounding by percentage of performance or by integer overflow
- Make an information demon to tweak parameters of extractor on the go?
- (Option) Make a wizard to setup proper options in advance?

## Scientific TODO

- Make theoretical base on the topic of reversability
- Investigate behaviour of the extractor for the purpose of manipulation in the long perspective
- Calculate asymptote of fraction numbers bitness growth as a function of input size
- Calculate algorithm complexity
- Second order extractor to track and fix input distribution drift
- Think hard about the philosophy of the capacity of entropy source and its relation to the analytical curve representation

## Applications TODO

- Use it to track unnatural package activity in the local network. Sort of snort
- Make a tool to squeeze the extractor into low-resource MC's by the input profile and provided specs or something
- Server-side anti-bot

## TODO that is unlikely to ever be TODONE

- Finish theory and implement in code the randomness extraction by CHOFCH in the Fibonacci-base space

## Licence

MIT. Can't stop Rock and Roll as soon as I feel comfortable.
