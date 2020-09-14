
import matplotlib.pyplot as pp
from mpl_toolkits.axes_grid1 import ImageGrid, make_axes_locatable # for scaling colorbar
import numpy as np
from scipy.io import loadmat
from scipy.interpolate import interp1d
from scipy.fftpack import fft, ifft

def test_OCT_converter():
    data_dict = loadmat('test.mat')
    data = data_dict['Spectral']
    Chirp = data_dict['Chirp'][0]
    # Header = data_dict['Header'] # Restoring dict from MAT file is not yet working
    spec = data[0,:,:] # take only 1st B-frame

    pdata = spec[1000,:]
    pp.figure(num = 'Raw spectrum')
    pp.plot(pdata)

    apo_spec = data_dict['Spectral_apo'][0]
    mdata = np.mean(apo_spec,axis=0)

    spec_xs = spec.shape[0]
    spec_zs = spec.shape[1]

    # remove DC
    spec = spec - mdata
    pp.figure(num = 'DC removed spectrum')
    pp.plot(spec[1000,:])

    # linearize k - space
    k_lin = interp1d(x=Chirp, y=spec.T, axis=0)
    spec_lin = k_lin(np.arange(0,spec_zs))

    # ifft --> z - space
    spec_fft = np.log10(np.abs(ifft(spec_lin, axis=0)))
    fig = pp.figure()
    # rangeX = Header['DataFileDict']['Spectral0']['RangeX']
    # rangeZ = Header['DataFileDict']['Spectral0']['RangeZ']
    grid = ImageGrid(fig, 111, nrows_ncols=(1, 1), axes_pad=0.1, cbar_mode='single')
    imax = grid[0].imshow(spec_fft[1:spec_zs//2,:], cmap='Greys_r',vmin=-1.5,vmax=-0.5)
    cax = grid.cbar_axes[0]
    fig.colorbar(mappable=imax, cax=cax)


    pp.show()

test_OCT_converter()