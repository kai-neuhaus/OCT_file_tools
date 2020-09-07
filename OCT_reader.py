# This file shows some example usage of Python functions to read an OCT file.
# To use exectute this test reader, scroll to the bottom and pass an OCT file to the function unzip_OCTFile.
#
# Additional modules to be installed should be 'xmltodict' and 'shutil'
#
# This file can be called like below assuming you have only Python 3 installed
# 'python OCT_reader.py'
# Alternative you can call for specific versions 3 or 3.8
# 'python3 OCT_reader.py'
# 'python3.8 OCT_reader.py'
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
import matplotlib.pyplot as pp
import xmltodict
import os
import tempfile
import zipfile
import shutil
import json
import warnings
from warnings import warn
formatwarning_orig = warnings.formatwarning
warnings.formatwarning = lambda message, category, filename, lineno, line=None: \
    formatwarning_orig(message, category, filename='', lineno='', line='')


def unzip_OCTFile(filename):
    """
    Unzip the OCT file into a temp folder.

    :param filename:
    :return:
    """
    tempdir = tempfile.gettempdir()
    handle = dict()
    handle['filename'] = filename
    handle['path'] = os.path.join(tempdir, 'OCTData')



    named_oct_data_folder = os.path.join(handle['path'],os.path.basename(filename).strip('.oct'))
    handle['named_oct_data_folder'] = named_oct_data_folder
    if os.path.exists(named_oct_data_folder):
        warn('Reuse data in {}\n'.format(named_oct_data_folder))
    else:
        print('\nTry to extract {} into {}. Please wait.\n'.format(filename,named_oct_data_folder))
        if not os.path.exists(handle['path']):
            os.mkdir(handle['path'])
        if not os.path.exists(named_oct_data_folder):
            os.mkdir(named_oct_data_folder)

        with zipfile.ZipFile(file=handle['filename']) as zf:
            zf.extractall(path=named_oct_data_folder)

        # Thorlabs stores incompatible folder names in zip.
        # Need to create data explicitly.
        # walk_object = os.walk(named_oct_data_folder)
        # for root, dirs, files in walk_object:
        #     if not os.path.exists(os.path.join(named_oct_data_folder, 'data')):
        #         os.mkdir(os.path.join(named_oct_data_folder, 'data'))
        #     for file in files:
        #         if not 'Header.xml' in file:
        #             src = os.path.join(root, file)
        #             dst = os.path.join(root,'data',file.lstrip('data\\\\'))
        #             shutil.move(src,dst)

    # make folder 's' to indicate it is in use (open)
    if not os.path.exists(os.path.join(named_oct_data_folder,'s')):
        os.mkdir(os.path.join(named_oct_data_folder,'s'))
    else:
        warn('Folder \'s\' exists.')

    with open(os.path.join(named_oct_data_folder, 'Header.xml'),'rb') as fid:
        up_to_EOF = -1
        xmldoc = fid.read(up_to_EOF)

    handle_xml = xmltodict.parse(xmldoc)
    handle.update(handle_xml)
    return handle

def get_OCTDataFileProps(handle, data_name=None, prop=None):
    """
    List some of the properties as in the Header.xml.
    :param handle:
    :param data_name:
    :param prop:
    :return:
    """
    metadatas = handle['Ocity']['DataFiles']['DataFile']
    metadata = metadatas[np.argwhere([data_name in h['#text'] for h in handle['Ocity']['DataFiles']['DataFile']]).squeeze()]
    prop = metadata[prop]
    return prop

def get_OCTFileMetaData(handle, data_name):
    # Update data types if required
    python_dtypes = {'Colored':{'4':np.int32, '2':np.int16}, 'Real':{'4':np.float32}, 'Raw':{'2':np.uint16}}
    handle.update({'python_dtypes':python_dtypes})

    # Check if data_name is available
    data_names_available = [d['#text'] for d in handle['Ocity']['DataFiles']['DataFile']]
    data_name = 'data\\'+data_name+'.data' # check this on windows
    assert data_name in data_names_available, 'Did not find {}.\nAvailable names are: {}'.format(data_name,data_names_available)

    metadatas = handle['Ocity']['DataFiles']['DataFile'] # get list of all data files
    # select the data file matching data_name
    metadata = metadatas[np.argwhere([data_name in h['#text'] for h in handle['Ocity']['DataFiles']['DataFile']]).squeeze()]
    print(metadata)
    return handle, metadata

def get_OCTVideoImage(handle):
    """
    Examples how to extract VideoImage data
    :param handle:
    :param data_name:
    :return:
    """
    handle, metadata = get_OCTFileMetaData(handle, 'VideoImage')
    data_filename = os.path.join(handle['named_oct_data_folder'], metadata['#text'])
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
    :param handle:
    :return:
    """
    handle, metadata = get_OCTFileMetaData(handle, data_name='Intensity')
    data_filename = os.path.join(handle['named_oct_data_folder'], metadata['#text'])
    img_type = metadata['@Type'] # this is @Real
    dtype = handle['python_dtypes'][img_type][metadata['@BytesPerPixel']] # This is not consistent! unsigned and signed not distinguished!
    sizeX = int(metadata['@SizeX'])
    sizeZ = int(metadata['@SizeZ'])
    data = (np.fromfile(data_filename, dtype=(dtype, [sizeX,sizeZ])))[0].T # there are two images. Take the first [0].
    return data

def get_OCTSpectralImage(handle):
    handle, metadata = get_OCTFileMetaData(handle, data_name='Spectral0')
    data_filename = os.path.join(handle['named_oct_data_folder'], metadata['#text'])
    img_type = metadata['@Type'] # this is @Real
    dtype = handle['python_dtypes'][img_type][metadata['@BytesPerPixel']] # This is not consistent! unsigned and signed not distinguished!
    sizeX = int(metadata['@SizeX'])
    sizeZ = int(metadata['@SizeZ'])
    data = (np.fromfile(data_filename, dtype=(dtype, [sizeX,sizeZ])))[0].T # there are two images. Take the first [0].
    # metadata['Ocity'][]
    return data

def close_OCTFile(handle):
    """
    remove 's' folder.
    :param handle:
    :return:
    """

    if os.path.exists(os.path.join(handle['named_oct_data_folder'],'s')):
      os.rmdir(os.path.join(handle['named_oct_data_folder'], 's'))
    else:
      warn('Subfolder \'s\' as label not existing.')



# Example usage
handle = unzip_OCTFile('/Users/kai/Documents/Acer_mirror/sdb5/Sergey Alexandrov/srSESF_OCT_data/data/AfterCXL2D(2).oct');

# example to list properties
print('properties:')
print(handle.keys()) #list all keys in handle
print(handle['Ocity'].keys()) #list all keys in Ocity. This is from Header.xml
print(handle['Ocity']['Acquisition'].keys()) #list all keys in Acquisition
print(handle['Ocity']['MetaInfo']['Comment']) #get comment value from MetaInfo

print(handle['Ocity']['Acquisition']['RefractiveIndex'])
print(handle['Ocity']['Acquisition']['SpeckleAveraging'].keys())
fastaxis = handle['Ocity']['Acquisition']['SpeckleAveraging']['FastAxis']
print('Speckle Averaging FastAxis: ',fastaxis)
print(handle['Ocity']['Image'].keys())

# example list all data files
print('\n\ndata file names:')
[print(h['#text']) for h in handle['Ocity']['DataFiles']['DataFile']]

print(get_OCTDataFileProps(handle, data_name = 'VideoImage', prop='@Type')) #print type of video image
print(get_OCTDataFileProps(handle, data_name = 'Intensity', prop='@Type'))

# get and plot VideoImage
data = get_OCTVideoImage(handle)
pp.figure(num='VideoImage')
pp.title()
pp.imshow(data,cmap='Greys',vmin=0.0,vmax=0.4)
pp.colorbar()

# get and plot IntensityImage
data = get_OCTIntensityImage(handle)
pp.figure(num='Intensity')
pp.imshow(data,cmap='Greys_r',vmin=30,vmax=50)

pp.colorbar()

# data = get_OCTSpectralImage(handle)

pp.show()

close_OCTFile(handle)
