# naamkaran
Pseudo-random word generation using random markov process.

Python implementation of [foswig.js](https://github.com/mrsharpoblunto/foswig.js/) Allows you to create pseudo-random words based off arbitrary dictionaries using Markov chains. 

### Getting Started
- Clone this repo:
```bash
git clone https://github.com/amanjain1397/naamkaran.git
cd naamkaran
```
- Usage
```bash
python main.py --h
usage: main.py [-h] --dataroot DATAROOT [--order ORDER]
               [--minLength MINLENGTH] [--maxLength MAXLENGTH]
               [--allowDuplicates ALLOWDUPLICATES] [--maxAttempts MAXATTEMPTS]
               [--noOfWords NOOFWORDS] [--toLower TOLOWER]
               [--removeSpecial REMOVESPECIAL]
  --maxLength MAXLENGTH
                        The maximum length of the generated word (default: -1)
  --allowDuplicates ALLOWDUPLICATES
                        Whether generated words are allowed to be the same as
                        words in the input dictionary (default: False)
  --maxAttempts MAXATTEMPTS
                        The maximum number of attempts to generate a word
                        before failing and throwing an error (default: 100)
  --noOfWords NOOFWORDS
                        Number of words to be generated (default: 50)
  --toLower TOLOWER     lower case the vocabulary (default: False)
  --removeSpecial REMOVESPECIAL
                        retains only alphabetic chars (default: False)
  --exceptionSymbols EXCEPTIONSYMBOLS
                        retain the string of the symbols, e.g. "@$#" (default: '')
```
The corpus text file is stored at **dataroot**. A sample text file of corpus can be found at **./sample.txt**.

### Working Example
Text files can be found at **./data/**. We will use the music band names corpus for the example. The corresponding text file can be found at **./data/band.names.txt**.

```bash
python main.py --dataroot ./data/band.names.txt --order 4 --minLength 2 --maxLength 12 --toLower 1 --removeSpecial 1 --exceptionSymbols " "
['jackstrees', 'dr johanson', 'cyndicate', 'billy full', 'dave club', 'supertramps', 'kittyhawks', 'the roses', 'sunnymen', 'pete tombs', 'publime', 'tim bucking', 'bobby voices', 'palacement', 'rocked', 'diamones', 'lively darin', 'deeelies', 'the miller', 'the flag', 'spacements', 'soundgren', 'the matthews', 'the clark', 'joe who', 'bachard', 'peter four', 'the club', 'televators', ' manic young', 'dick drake', 'steppelin', 'judas prings', 'graham parks', 'gerry mann', 'bobby voices', 'peter cult', 'the marship', 'creeders', 'jon spectors', 'marians', 'bachard', 'the cochran', 'gene vega', 'the league', 'sonny puppy', 'diamondays', 'rocked', 'happenwolf', 'warrett']
```
A mixed corpus consisting of words from different sources can also be used.
### More Info
Learn about Tries from [here](https://medium.com/basecs/trying-to-understand-tries-3ec6bede0014).
