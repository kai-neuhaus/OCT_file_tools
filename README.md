# OCT_reader for Thorlabs OCT files
Needs the modules `xmltodict` and `gdown`, so please install those before with pip.

**The examples are not endorsed by Thorlabs. Please use the provide examples at your own risk.**

For some online demo click the file OCT_reader_colab.ipynb.

For some local experiments download the file OCT_reader_demo.py.
This experimental file contains all functions required.

The file OCT_reader.py can be imported as demonstrated in OCTtoNPY.py.

**Do not assume that OCT_reader.py is complete.**

*The code is for demonstration purpose and you may need to change it.*

The processing example does not yet apply any window function.
Only DC removal, k-space linearization, and the ifft is applied.
Furthe improvement on the processing steps can be applied.

The file OCT_reader_demo.py and OCT_reader_colab.ipynb contain all functions required.

The file OCT_reader.py is collates required functions that can be accessed by importing OCT_reade like:

`from OCT_reader import *`
