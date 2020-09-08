# Convert an OCT file to Python type npy file.

# This is an example how to convert OCT into numpy format.
# This is not a general purpose approach and specific for the required processing steps.

from OCT_reader import *

def get_OCTSpectralAll(handle):
    get_OCTSpectralRawFrame(handle, idx=0)

# If you want to download some test OCT file uncomment the next two lines
if not os.path.exists('test.oct'):
    print('File \'test.oct\' does not exist.')
    print('Do you want to download it (50 MB)?')
    if 'y' in input('y/n'):
        import gdown
        gdown.download(url='https://drive.google.com/uc?id=18xtWgvMdHw3OslDyyXZ6yMKDywhj_zdR',output='./test.oct')

handle = unzip_OCTFile('test.oct')

# get_OCTSpectralAll(handle)
