# OCT_reader for Thorlabs OCT files
Needs the modules `xmltodict` and `gdown`, so please install those before with pip.

**The examples are not endorsed by Thorlabs. Please use the provide examples at your own risk.**

Feel free to leave an issue to comment or if you have questions.

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

# OCTtoNPY: Convert OCT to npy or mat
The OCTtoNPY is a crude example to convert OCT file as npy or mat file.

Again, the example currently only saves the raw data.

If you want to perform processing you will need also to read and write the process data files such as
Chirp.data, ErrorOffset.data, and maybe others.

I.e. by using the three lines of code somewhere the Chirp.data are obtained and can then
be saved in whatever format desired:
```
    handle, metadata = get_OCTFileMetaData(handle, data_name='data\\Chirp.data')
    chirp_fname = os.path.join(handle['temp_oct_data_folder'], metadata['#text'])
    chirp_data = np.fromfile(chirp_fname, dtype=handle['python_dtypes']['Real'][metadata['@BytesPerPixel']])
```
Do the same for all other required data.

You need to correctly interpret the `dtype` to get the right number format which can be obtained from the xml fields
@Type and @BytesPerPixel.
Otherwise you will need to consult `Header.xml` directly.

#Caveats
**Specifically not all parameters are the same or present between all systems.**

The Header.xml contains a field `Instrument.Model` which could be used to capture differences between systems.

**The function `demo_printing_parameters` may need to be edited depending on what parameters are available in your Header.xml**

**Also the parameters may depend on the configuration used.**

In the best case you get a KeyError if a parameter is missing or has a different name.

Then you must identify the relevant parameter in the Header.xml yourself and change the your own code.