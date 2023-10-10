

def fourierAmplitude(data, delta, npts):
    """
    Returns the Fourier spectrum of the time series
    Takes:
        data : Aceleration time-series
        delta: Time step 
        npts : Number of data points in acceleration array
    returns:
        Frequency (as numpy array)
        Fourier Amplitude (as numpy array)
    """
    from numpy.fft import rfft
    from numpy import linspace

    amp = abs(rfft(data))                          
    freq = linspace(0, int((1/delta)/2), int((npts/2)+1))

    return freq, amp




def welchMethod(data, window_length, overlap, delta, scaletype, unit):
    """
    Returns the Power Spectral Density with Welch's Method averaging
    Takes:
        data: Aceleration time-series
        window_length : Length of each segment
        overlap : Number of points to overlap between segments
        delta : Time step
        type : Power spectral density or spectral density
    returns:
        f: Frequency (as numpy array)
        a: Amplitude (as numpy array)
    """

    from scipy.signal import welch, windows
    from numpy import sqrt

    sampling_rate = 1/delta
    window_size = int(window_length * sampling_rate)
    window = windows.hann(window_size)   # hann
    f, a = welch(data, fs = sampling_rate, window = window, nperseg = window_size, noverlap = window_size//overlap)   # window_size/overlap
    
    if scaletype == "Spectral Density":
        return f, sqrt(a) 
    
    if scaletype == "Power Spectral Density":
        return f, a   
    



def periodogramMethod(data, delta, scaletype):
    """
    Returns the Power Spectral Density with Welch's Method averaging
    Takes:
        data: Aceleration time-series
        delta : Time step
        type : Power spectral density or spectral density
    returns:
        Frequency (as numpy array)
        Amplitude (as numpy array)
    """
    from scipy.signal import periodogram
    from numpy import sqrt 
    
    f, a = periodogram(data, fs = 1/delta, window = "hann") 
    
    if scaletype == "Spectral Density":
        return f, sqrt(a) 
    
    if scaletype == "Power Spectral Density":
        return f, a   




def spectrogramFunction(acceleration, delta):
    """
    Returns the Spectrogram of the time series
    Takes:
        Aceleration time-series
        Time step (delta)
    returns:
        f : Array of sample frequencies.
        t : Array of segment times.
        Sxx : Spectrogram of Aceleration.
    """
    from scipy import signal

    N = 128 #Number of point in the fft
    w = signal.blackman(N)
    f, t, Sxx = signal.spectrogram(acceleration, 1/delta, window = w, nfft=N)

    return f, t, Sxx 


