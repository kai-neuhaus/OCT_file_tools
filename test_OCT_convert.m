function test_OCT_convert()
    close('all');
    load('test.mat')
    
    pdata = (squeeze(Spectral(1,1000,:)));
    figure('name','Raw spectrum');plot(pdata)

    mdata = (squeeze(mean(Spectral_apo(1,:,:))))';

    spec = single(squeeze(Spectral(1,:,:)));
    spec_size = size(spec);
    spec_xs = spec_size(1);
    spec_zs = spec_size(2);

    % remove DC
    for i = 1:spec_xs
        spec(i,:) = spec(i,:) - mdata;
    end
    figure('name','DC removed spectrum');plot(spec(1000,:));hold('on')

    % linearize k-space
    spec_lin = interp1(Chirp,spec',(1:spec_zs-1))';

    % ifft --> z-space
    spec_fft = log10(abs(ifft(spec_lin,[],2)));
    f=figure();
    rangeX = str2double(Header.DataFileDict.Spectral0.RangeX);
    rangeZ = str2double(Header.DataFileDict.Spectral0.RangeZ);
    imagesc(spec_fft(:,1:spec_zs/2)','XData',[0,rangeX],'YData',[0,rangeZ],[-1.5,0.5]);
    f.Position = f.Position .* [1,1, rangeX*0.2, rangeZ*0.2]
    colormap('gray');
    colorbar();
end