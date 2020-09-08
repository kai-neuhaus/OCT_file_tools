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