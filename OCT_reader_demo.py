# This file shows some example usage of Python functions to read an OCT file.
# To use exectute this test reader, scroll to the bottom and pass an OCT file to the function unzip_OCTFile.
# Find the comment #Example usage.
#
# Additional modules to be installed should be 'xmltodict', 'shutil', and 'gdown'.
# Tested in Python 3.7 and 3.8 (Mac, Colab)
#
# This file can be called like below assuming you have only Python 3 installed
# 'python OCT_reader_demo.py'
# Alternative you can call for specific versions 3 or 3.8
# 'python3 OCT_reader_demo.py'
# 'python3.8 OCT_reader_demo.py'
#
# The function unzip_OCTFile show an option to extract files with python.
#
# The Header.xml is converted to a dictionary named 'handle'.
# This allows to access data for different OCT files.
#
# The function get_OCTVideoImage demonstrates how to use handle to extract and show the video image.
#
# The function get_OCTIntensityImage demonstrates how to use handle to extract and show the intensity data.

import numpy as np
from scipy.fftpack import fft,ifft
from scipy.interpolate import interp1d
import matplotlib; matplotlib.use('Qt5Agg')
import matplotlib.pyplot as pp
import xmltodict
import os
import tempfile
import zipfile
import warnings
from warnings import warn
formatwarning_orig = warnings.formatwarning
warnings.formatwarning = lambda message, category, filename, lineno, line=None: \
    formatwarning_orig(message, category, filename='', lineno='', line='')


def unzip_OCTFile(filename):
    """
    Unzip the OCT file into a temp folder.
    """
    tempdir = tempfile.gettempdir()
    handle = dict()
    handle['filename'] = filename
    handle['path'] = os.path.join(tempdir, 'OCTData')

    temp_oct_data_folder = os.path.join(handle['path'],os.path.basename(filename).split('.oct')[0])
    handle['temp_oct_data_folder'] = temp_oct_data_folder
    if os.path.exists(temp_oct_data_folder) and os.path.exists(os.path.join(temp_oct_data_folder, 'Header.xml')):
        warn('Reuse data in {}\n'.format(temp_oct_data_folder))
    else:
        print('\nTry to extract {} into {}. Please wait.\n'.format(filename,temp_oct_data_folder))
        if not os.path.exists(handle['path']):
            os.mkdir(handle['path'])
        if not os.path.exists(temp_oct_data_folder):
            os.mkdir(temp_oct_data_folder)

        with zipfile.ZipFile(file=handle['filename']) as zf:
            zf.extractall(path=temp_oct_data_folder)

    # read Header.xml
    with open(os.path.join(temp_oct_data_folder, 'Header.xml'),'rb') as fid:
        up_to_EOF = -1
        xmldoc = fid.read(up_to_EOF)

    # convert Header.xml to dictionary
    handle_xml = xmltodict.parse(xmldoc)
    handle.update(handle_xml)
    return handle

def get_OCTDataFileProps(handle, data_name=None, prop=None):
    """
    List some of the properties as in the Header.xml.
    """
    metadata_all = handle['Ocity']['DataFiles']['DataFile']
    metadata_name = np.take(metadata_all, np.flatnonzero([data_name in h['#text'] for h in metadata_all]))
    props = [m[prop] for m in metadata_name]
    return props

def get_OCTFileMetaData(handle, data_name):
    """
    The metadata for files are store in a list.
    The artifact 'data\\' stems from windows path separators and may need fixing.
    """
    # Check if data_name is available
    data_names_available = [d['#text'] for d in handle['Ocity']['DataFiles']['DataFile']]
    data_name = data_name # check this on windows
    assert data_name in data_names_available, 'Did not find {}.\nAvailable names are: {}'.format(data_name,data_names_available)

    metadatas = handle['Ocity']['DataFiles']['DataFile'] # get list of all data files
    # select the data file matching data_name
    metadata = metadatas[np.argwhere([data_name in h['#text'] for h in handle['Ocity']['DataFiles']['DataFile']]).squeeze()]
    return handle, metadata

def get_OCTVideoImage(handle):
    """
    Examples how to extract VideoImage data
    """
    handle, metadata = get_OCTFileMetaData(handle, data_name='data\\VideoImage.data')
    # print(metadata)
    data_filename = os.path.join(handle['temp_oct_data_folder'], metadata['#text'])
    img_type = metadata['@Type']
    dtype = handle['python_dtypes'][img_type][metadata['@BytesPerPixel']] # This is not consistent! unsigned and signed not distinguished!
    sizeX = int(metadata['@SizeX'])
    sizeZ = int(metadata['@SizeZ'])
    data = np.fromfile(data_filename, dtype).reshape([sizeX,sizeZ])
    data = abs(data)/abs(data).max()
    return data

def get_OCTIntensityImage(handle):
    """
    Example how to extract Intensity data
    """
    handle, metadata = get_OCTFileMetaData(handle, data_name='data\\Intensity.data')
    data_filename = os.path.join(handle['temp_oct_data_folder'], metadata['#text'])
    img_type = metadata['@Type'] # this is @Real
    dtype = handle['python_dtypes'][img_type][metadata['@BytesPerPixel']] # This is not consistent! unsigned and signed not distinguished!
    sizeX = int(metadata['@SizeX'])
    sizeZ = int(metadata['@SizeZ'])
    data = (np.fromfile(data_filename, dtype=(dtype, [sizeX,sizeZ])))[0].T # there are two images. Take the first [0].
    return data

def get_OCTSpectralRawFrame(handle, spec_name = 'data\\Spectral0.data'):
    """
    Demo read raw spectral data.
    Take note that we access all parameters using the dictionary from Header.xml.
    Although, this still looks a bit messy it should not require changes for different data.
    """
    # if the metadata are all the same for each Spectral.data then this can be called separately once
    handle, metadata = get_OCTFileMetaData(handle, data_name=spec_name)
    # make False --> 'unsigned', True --> 'signed
    sign = handle['Ocity']['Instrument']['RawDataIsSigned'].replace('False','unsigned').replace('True','signed')
    apo_rng = range(int(metadata['@ApoRegionStart0']),int(metadata['@ApoRegionEnd0']))
    scan_rng = range(int(metadata['@ScanRegionStart0']),int(metadata['@ScanRegionEnd0']))
    bytesPP = metadata['@BytesPerPixel'] # probably 2
    raw_type = metadata['@Type'] # Raw
    data_filename = metadata['#text']
    data_file = os.path.join(handle['temp_oct_data_folder'], data_filename)
    dtype = handle['python_dtypes'][raw_type][sign][bytesPP]
    sizeX = int(metadata['@SizeX'])
    sizeZ = int(metadata['@SizeZ'])

    # select one [0] of two data frames
    raw_data = np.fromfile(data_file, dtype=(dtype, [sizeX,sizeZ]))[0]
    apo_data = raw_data[apo_rng]
    spec_data = raw_data[scan_rng]
    # return also apodization data
    return spec_data, apo_data

def get_OCTSpectralRawFrame2(handle, spec_name = 'data\\Spectral0.data'):
    """
    Demo read raw spectral data for a different data file.
    In this case the first Spectral0.data is all apodization data.
    The first file has now a different set of parameters
    """
    handle, metadata = get_OCTFileMetaData(handle, data_name=spec_name)
    sign = handle['Ocity']['Instrument']['RawDataIsSigned'].replace('False','unsigned').replace('True','signed')
    apo_rng = range(int(metadata['@ApoRegionStart0']),int(metadata['@ApoRegionEnd0']))
    scan_rng = range(int(metadata['@ScanRegionStart0']),int(metadata['@ScanRegionEnd0']))
    bytesPP = metadata['@BytesPerPixel'] # probably 2
    raw_type = metadata['@Type'] # Raw
    data_filename = metadata['#text']
    data_file = os.path.join(handle['temp_oct_data_folder'], data_filename)
    dtype = handle['python_dtypes'][raw_type][sign][bytesPP]
    sizeX = int(metadata['@SizeX'])
    sizeZ = int(metadata['@SizeZ'])

    # select one [0] of two data frames
    raw_data = np.fromfile(data_file, dtype=(dtype, [sizeX,sizeZ]))[0]
    apo_data = raw_data[apo_rng]
    spec_data = raw_data[scan_rng]
    # return also apodization data
    return spec_data, apo_data


def get_OCTSpectralImage(handle):
    """
    Reconstruct the image from spectral data: remove DC; k-space-lin; ifft
    """
    spec, apo_data = get_OCTSpectralRawFrame(handle, spec_name = 'data\\Spectral0.data')

    binECnt = np.float(handle['Ocity']['Instrument']['BinaryToElectronCountScaling'])
    handle, metadata = get_OCTFileMetaData(handle, data_name='data\\OffsetErrors.data')
    err_offset_fname = os.path.join(handle['temp_oct_data_folder'], metadata['#text'])
    err_offset = np.fromfile(err_offset_fname, dtype=handle['python_dtypes']['Real'][metadata['@BytesPerPixel']])

    handle, metadata = get_OCTFileMetaData(handle, data_name='data\\ApodizationSpectrum.data')
    apodization_fname = os.path.join(handle['temp_oct_data_folder'], metadata['#text'])
    apodization_data = np.fromfile(apodization_fname, dtype=handle['python_dtypes']['Real'][metadata['@BytesPerPixel']])
    # same length after ifft

    handle, metadata = get_OCTFileMetaData(handle, data_name='data\\Chirp.data')
    chirp_fname = os.path.join(handle['temp_oct_data_folder'], metadata['#text'])
    chirp_data = np.fromfile(chirp_fname, dtype=handle['python_dtypes']['Real'][metadata['@BytesPerPixel']])

    bframe = spec - np.mean(apo_data,axis=0) # Subtract DC using inline apo_data

    ip_fun = interp1d(x=chirp_data, y=bframe) # create interpolation on chirp_data
    num_samples = bframe.shape[1] # SizeZ
    bframe = ip_fun(np.arange(num_samples)) # k-space linearize

    return bframe

def demo_printing_parameters(handle):
    """
    This functions demonstrates how to access the xml paratemeters from the dictionary.
    The parameters are read in the unzip_OCTFile function.

    See this code snipped to read the Header.xml data:

    with open(os.path.join(temp_oct_data_folder, 'Header.xml'),'rb') as fid:
    up_to_EOF = -1
    xmldoc = fid.read(up_to_EOF)

    handle_xml = xmltodict.parse(xmldoc)
    handle.update(handle_xml)
    """
    # example to list properties
    print('properties:')
    print(handle.keys())  # list all keys in handle
    print(handle['Ocity'].keys())  # list all keys in Ocity. This is from Header.xml
    print(handle['Ocity']['Acquisition'].keys())  # list all keys in Acquisition
    print(handle['Ocity']['MetaInfo']['Comment'])  # get comment value from MetaInfo

    print(handle['Ocity']['Acquisition']['RefractiveIndex'])
    # print(handle['Ocity']['Acquisition']['SpeckleAveraging'].keys())
    # fastaxis = handle['Ocity']['Acquisition']['SpeckleAveraging']['FastAxis']
    # print('Speckle Averaging FastAxis: ', fastaxis)
    print(handle['Ocity']['Image'].keys())

    # example list all data files
    print('\n\ndata file names:')
    [print(h['#text']) for h in handle['Ocity']['DataFiles']['DataFile']]

    print('\nProperties:')
    print(get_OCTDataFileProps(handle, data_name='VideoImage', prop='@Type'))  # print type of video image
    print(get_OCTDataFileProps(handle, data_name='Intensity', prop='@Type'))
    print(get_OCTDataFileProps(handle, data_name='Spectral', prop='@Type'))
    print(get_OCTDataFileProps(handle, data_name='Spectral', prop='#text'))


# Example usage

# Ask if some test data should be retrieved.
if not os.path.exists('test.oct'):
    print('File \'test.oct\' does not exist.')
    print('Do you want to download it (50 MB)?')
    if 'y' in input('y/n'):
        import gdown
        gdown.download(url='https://drive.google.com/uc?id=18xtWgvMdHw3OslDyyXZ6yMKDywhj_zdR',output='./test.oct')

# handle = unzip_OCTFile('test.oct')
handle = unzip_OCTFile('/Users/kai/Documents/Acer_mirror/sdb5/Sergey Alexandrov/srSESF_OCT_data/data/RS_12032019_0008_Mode3D_1280_NSDT.oct')
# Create a python_types dictionary for required data types
# I.e. the Thorlabs concept can mean a "Raw - signed - 2 bytes" --> np.int16
python_dtypes = {'Colored': {'4': np.int32, '2': np.int16},
                 'Real': {'4': np.float32},
                 'Raw': {'signed': {'1': np.int8, '2': np.int16},
                         'unsigned': {'1': np.uint8, '2': np.uint16}}}
print('dtype raw_signed_2 =',python_dtypes['Raw']['signed']['2']) # example
handle.update({'python_dtypes': python_dtypes})

# print some parameters from the xml file
demo_printing_parameters(handle)

# get and plot VideoImage
data = get_OCTVideoImage(handle)
fig,ax = pp.subplots(1,num='VideoImage')
ax.set_title(fig.canvas.get_window_title())
im = ax.imshow(data,cmap='Greys',vmin=0.0,vmax=0.4)
pp.colorbar(mappable=im)

# get and plot IntensityImage
data = get_OCTIntensityImage(handle)
fig,ax = pp.subplots(1,num='Intensity')
ax.set_title(fig.canvas.get_window_title())
im = ax.imshow(data,cmap='Greys_r',vmin=30,vmax=50)
pp.colorbar(mappable=im)

# get and processed spectral data, and plot the image
data = get_OCTSpectralImage(handle)
fig, ax = pp.subplots(1,num='Spectral')
im = ax.imshow(np.log10(abs(ifft(data)))[:,0:1024].T,vmin=-1.3,vmax=-0.5, cmap='Greys_r',aspect=2,interpolation='antialiased')
ax.set_title(fig.canvas.get_window_title())
pp.colorbar(mappable=im)
pp.show()

