Invest PDF Extractor
========================

This simple project is an exercise to extract text from PDFs and apply NLP to
match and/or classify particular pieces of information.

Setup
---------------

This project requires Python 3.

Setup virtual env:
```
$ virtualenv venv
$ source venv/bin/activate
```

Install required packages:
```
make init
```

Running
---------------
The main entry script is miner_text_extractor.py which expects a path to a PDF file as
a command line argument, e.g.:
`python miner_text_extractor.py data/raw/ADVFormBrochure_PrivateEquity/105343_494224_brochure.pdf`

This extracts the text from the PDF per page per sentence and then applies matching
rules, to find instances in the text.
