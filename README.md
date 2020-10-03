# OCT_converter
Requires the package `xmltodict`.
## Usage
```
import OCT_converter

OCT_converter.OCTtoMATraw( '<filename>.oct' )
```

This should generate a file `<filename>.mat`.

## Read and process the OCT.mat file
An example to read and process a `<filename>.mat` is given in `test_OCT_convert.m` and `test_OCT_convert.py`.

You can retrieve a test OCT-file using the Python module `gdown`
```
import gdown

gdown.download(url='https://drive.google.com/uc?id=18xtWgvMdHw3OslDyyXZ6yMKDywhj_zdR',output='./test.oct')

```
and convert it with the `OCT_converter` to `test.mat` to be able to run the examples.

# OCT_reader for Thorlabs OCT files
*Some details related to differences using a mat-file between MATLAB and Python.*

*The example to generate and import a mat-file for Python is provided if the data file is required for Python and MATLAB.\
Saving the data in a native Python data format is easily possible by changing the line*
```
savemat(re.split('\.[oO][cC][tT]',oct_filename)[0]+'.mat', mat_data)
```
to something like
```
save(re.split('\.[oO][cC][tT]',oct_filename)[0], mat_data)
```

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
Further improvement on the processing steps can be applied.

The file OCT_reader_demo.py and OCT_reader_colab.ipynb contain all functions required.

The file OCT_reader.py collates all required functions that can be accessed by importing OCT_reade like:

`from OCT_reader import *`

# OCTtoNPY: Convert OCT to npy or mat
The OCTtoNPY is a crude example to convert OCT file as npy or mat file.

Again, the example currently only saves the raw data.

If you want to perform processing you will need also to read and write the process data files such as
Chirp.data, ErrorOffset.data, and maybe others.
If you use the 'mat' format you can store those values in different data fields or structure components.

For python a dictionary could be pickled or use hdf5 format (h5py).

*The latest MATLAB versions use in their 'mat'-file formats hdf5. On the other hand, the hdf5 format seems
a better standardised format for storing large amount of data, as well as mixed meta-information, images, and even code.*

The code below seems a bit overkill assuming you have the data already unzipped.
However, extracting the metadata from the `Header.xml` can provide a more reliable data recovery
depending on different acquisition configurations or different systems.
```
    handle, metadata = get_OCTFileMetaData(handle, data_name='data\\Chirp.data')
    chirp_fname = os.path.join(handle['temp_oct_data_folder'], metadata['#text'])
    chirp_data = np.fromfile(chirp_fname, dtype=handle['python_dtypes']['Real'][metadata['@BytesPerPixel']])
```

You need to correctly interpret the `dtype` to get the right number format which can be obtained from the xml fields
@Type and @BytesPerPixel.
Otherwise you will need to consult `Header.xml` directly.

# Caveats
**Specifically parameters are different between systems and configurations**

*This means the code may need to be adapted each time a new configuration of some acquisition is used
or the data come from another system.*

The Header.xml contains a field `Instrument.Model` which could be used to capture differences between systems.

**The function `demo_printing_parameters` may need to be edited depending on what parameters are available in your Header.xml**


You may get a KeyError if a parameter is missing or has a different name.

Then you must identify the relevant parameter in the Header.xml yourself and change the code.