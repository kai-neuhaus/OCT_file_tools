import numpy as np
from scipy.fftpack import fft,ifft
from scipy.interpolate import interp1d
import matplotlib; matplotlib.use('Qt5Agg')
import matplotlib.pyplot as pp
import xmltodict
import os
import re
import zipfile
import warnings
from warnings import warn
formatwarning_orig = warnings.formatwarning
warnings.formatwarning = lambda message, category, filename, lineno, line=None: \
    formatwarning_orig(message, category, filename='', lineno='', line='')

# Collection of functions to convert from different OCT file configurations
def shorten_dict_keys( in_dict ):
    '''
    The MAT format does not allow key lengths larger 31 characters.
    '''
    out_dict = {}
    for k,v in in_dict.items():
        if v is None:
            # raise(ValueError('v:{} is None key:{}'.format(v,k)))
            v = 'None'
        if len(k)>30:
            while len(k) > 30:
                k = ''.join([w[:-1] for w in re.findall('[A-Z][^A-Z]*', k)])
        if isinstance(v,dict):
            out_dict[k] = shorten_dict_keys(v)
        else:
            out_dict[k] = v
    return out_dict

def OCTtoMATraw(filename):
    """
    Convert OCT to MAT file format.
    Keep all data raw; do not process.
    """
    mat_data = {}
    mat_data['Spectral'] = []
    with zipfile.ZipFile(file=filename) as zf:

        for item in zf.filelist:
            print(item.filename)
            if 'Header' in item.filename:
                mat_data['Header'] = xmltodict.parse(zf.read(item.filename))
                mat_data['Header'] = shorten_dict_keys(mat_data['Header'])

            elif 'Spectral' in item.filename:
                # mat_data['Header']['Ocity']['DataFiles']['DataFile']
                mat_data['Spectral'].append(zf.read(item.filename))
            # elif 'Chirp' in item.filename:
            #     byte_obj = np.frombuffer(zf.read(item.filename),dtype=np.int16)
            #     print(byte_obj)
            #     mat_data['Chirp'] = byte_obj
            # elif 'ApodizationSpectrum' in item.filename:
            #     mat_data['ApodizationSpectrum'] = item.filename
            # elif 'OffsetErrors' in item.filename:
            #     mat_data['OffsetErrors'] = zf.read(item.filename)

    from scipy.io.matlab import savemat
    savemat(re.split('.[oO][cC][tT]',filename)[0]+'.mat', mat_data)


def header_to_dict(temp_oct_data_folder):
    # read Header.xml
    with open(os.path.join(temp_oct_data_folder, 'Header.xml'),'rb') as fid:
        up_to_EOF = -1
        xmldoc = fid.read(up_to_EOF)

    # convert Header.xml to dictionary
    handle_xml = xmltodict.parse(xmldoc)
    handle.update(handle_xml)


def OCT_data_types(handle):
    # Create a python_types dictionary for required data types
    # I.e. the Thorlabs concept can mean a "Raw - signed - 2 bytes" --> np.int16
    python_dtypes = {'Colored': {'4': np.int32, '2': np.int16},
                     'Real': {'4': np.float32},
                     'Raw': {'signed': {'1': np.int8, '2': np.int16},
                             'unsigned': {'1': np.uint8, '2': np.uint16}}}
    handle.update({'python_dtypes': python_dtypes})


def get_OCTSpectralAll(handle):
    #
    spec_names = get_OCTDataFileProps(handle, data_name='Spectral', prop='#text') # get all Spectral file data

    spec3d = []
    for sn in spec_names:
        print(sn)
        spec, apo_data = get_OCTSpectralRawFrame(handle, spec_name = sn)
        spec3d.append(spec)

    return spec3d

handle = OCTtoMATraw('test.oct') # see OCT_reader_demo.py to retrieve test.oct

# spec3d = np.array(get_OCTSpectralAll(handle))
#
# print(spec3d.shape)
#
# # np.save('test_oct', spec3d)
#
