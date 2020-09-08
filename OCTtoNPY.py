# Convert an OCT file to Python type npy or mat file.

# This is an example how to convert OCT into numpy format or ML format.

# No processing is yet performed.

# Take note that we ignore here the apo_data which may need to be stored as well if the data are supposed to be processed.
# That means, you may want to extract also Chirp.data, ErrorOffset.data, etc. by calling somewhere
#
#     handle, metadata = get_OCTFileMetaData(handle, data_name='data\\Chirp.data')
#     chirp_fname = os.path.join(handle['temp_oct_data_folder'], metadata['#text'])
#     chirp_data = np.fromfile(chirp_fname, dtype=handle['python_dtypes']['Real'][metadata['@BytesPerPixel']])
#

from OCT_reader import *

def get_OCTSpectralAll(handle):
    #
    spec_names = get_OCTDataFileProps(handle, data_name='Spectral', prop='#text') # get all Spectral file data

    spec3d = []
    for sn in spec_names:
        print(sn)
        spec, apo_data = get_OCTSpectralRawFrame(handle, spec_name = sn)
        spec3d.append(spec)

    return spec3d

handle = unzip_OCTFile('test.oct') # see OCT_reader_demo.py to retrieve test.oct

spec3d = np.array(get_OCTSpectralAll(handle))

print(spec3d.shape)

# np.save('test_oct', spec3d)

from scipy.io.matlab import savemat
savemat('test_oct.mat',{'data':spec3d})