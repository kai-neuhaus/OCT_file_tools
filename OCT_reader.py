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

    # Create a python_types dictionary for required data types
    # I.e. the Thorlabs concept can mean a "Raw - signed - 2 bytes" --> np.int16
    python_dtypes = {'Colored': {'4': np.int32, '2': np.int16},
                     'Real': {'4': np.float32},
                     'Raw': {'signed': {'1': np.int8, '2': np.int16},
                             'unsigned': {'1': np.uint8, '2': np.uint16}}}
    handle.update({'python_dtypes': python_dtypes})

    return handle

def get_OCTDataFileProps(handle, data_name=None, prop=None):
    """
    List some of the properties as in the Header.xml.
    """
    metadatas = handle['Ocity']['DataFiles']['DataFile']
    metadata = metadatas[np.argwhere([data_name in h['#text'] for h in handle['Ocity']['DataFiles']['DataFile']]).squeeze()]
    prop = metadata[prop]
    return prop

def get_OCTFileMetaData(handle, data_name):
    """
    The metadata for files are store in a list.
    The artifact 'data\\' stems from windows path separators and may need fixing.
    """
    # Check if data_name is available
    data_names_available = [d['#text'] for d in handle['Ocity']['DataFiles']['DataFile']]
    data_name = 'data\\'+data_name+'.data' # check this on windows
    assert data_name in data_names_available, 'Did not find {}.\nAvailable names are: {}'.format(data_name,data_names_available)

    metadatas = handle['Ocity']['DataFiles']['DataFile'] # get list of all data files
    # select the data file matching data_name
    metadata = metadatas[np.argwhere([data_name in h['#text'] for h in handle['Ocity']['DataFiles']['DataFile']]).squeeze()]
    return handle, metadata

def get_OCTSpectralRawFrame(handle, idx = 0):
    """
    Demo read raw spectral data.
    Take note that we access all parameters using the dictionary from Header.xml.
    Although, this still looks a bit messy it should not require changes for different data.
    """
    # if the metadata are all the same for each Spectral.data then this can be called separately once
    handle, metadata = get_OCTFileMetaData(handle, data_name='Spectral'+str(idx))
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
