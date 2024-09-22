
def absmax(a, axis=None):
    from numpy import where
    amax = a.max(axis)
    amin = a.min(axis)
    return abs(where(-amin > amax, amin, amax))


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
    #w = signal.hann(N)
    w = signal.get_window("hann", N)
    f, t, Sxx = signal.spectrogram(acceleration, 1/delta, window = w, nfft=N)

    return f, t, Sxx 


def responseStateSpace(xi, K, omega_n, dt, E):
    """
    Calculate Response Spectrum with state space method
    """

    from numpy import zeros, array, linalg, real, eye, exp
    from scipy.linalg import eig

    u = []
    u0 = zeros((len(omega_n),1)) 

    for j in range(len(omega_n)):
        wn = omega_n[j,0]
        A = array([[0, 1],[-wn**2, -2*xi*wn]])
        D, V = eig(A)
        ep = array([[exp(D[0]*dt),0],[0, exp(D[1]*dt)]])
        Ad = V.dot(ep).dot(linalg.inv(V))
        Bd = linalg.inv(A).dot(Ad - eye(len(A)))
        z = [[0], [0]]
        d= zeros((len(E),1))
        v= zeros((len(E),1))
        
        for i in range(len(E)):
            z = real(Ad).dot(z) + real(Bd).dot([[0],[-E[i]*9.81]])
            d[i] = z[0,0] 
            v[i] = z[1,0]
            u.append(d)
            
        u0[j] = max(abs(d))        
    return u0, u  



def computeAandB(xi, w, dt):
    """
    From the paper by Nigam and Jennings (1968), computes the two matrices.
    https://core.ac.uk/download/pdf/216194346.pdf
    https://eqsig.readthedocs.io/en/latest/_modules/eqsig/sdof.html

    :param xi: critical damping ratio
    :param w: angular frequencies
    :param dt: time step
    :return: matrices A and B
    """

    from numpy import sqrt, exp, sin, cos, array

    xi2 = xi ** 2  # D2
    w2 = w ** 2  # W2
    one_ov_w2 = 1 / w2  # A7
    sqrt_b2 = sqrt(1 - xi2)
    w_sqrt_b2 = w * sqrt_b2  # A1

    exp_b = exp(-xi * w * dt)  # A0
    two_b_ov_w2 = (2 * xi ** 2 - 1) / (w ** 2 * dt)
    two_b_ov_w3 = 2 * xi / (w ** 3 * dt)

    sin_wsqrt = sin(w_sqrt_b2 * dt)  # A2
    cos_wsqrt = cos(w_sqrt_b2 * dt)  # A3

    # A matrix
    a_11 = exp_b * (xi / sqrt_b2 * sin_wsqrt + cos_wsqrt)  # Eq 2.7d(1)
    a_12 = exp_b / (w * sqrt_b2) * sin_wsqrt  # Eq 2.7d(2)
    a_21 = -w / sqrt_b2 * exp_b * sin_wsqrt    # Eq 2.7d(3)
    a_22 = exp_b * (cos_wsqrt - xi / sqrt_b2 * sin_wsqrt)  # Eq 2.7d(4)

    a = array([[a_11, a_12], [a_21, a_22]])

    # B matrix
    bsqrd_ov_w2_p_xi_ov_w = two_b_ov_w2 + xi / w
    sin_ov_wsqrt = sin_wsqrt / w_sqrt_b2
    xwcos = xi * w * cos_wsqrt
    wsqrtsin = w_sqrt_b2 * sin_wsqrt

    # Eq 2.7e
    b_11 = exp_b * (bsqrd_ov_w2_p_xi_ov_w * sin_ov_wsqrt + (two_b_ov_w3 + one_ov_w2) * cos_wsqrt) - two_b_ov_w3
    b_12 = -exp_b * (two_b_ov_w2 * sin_ov_wsqrt + two_b_ov_w3 * cos_wsqrt) - one_ov_w2 + two_b_ov_w3
    b_21 = exp_b * (bsqrd_ov_w2_p_xi_ov_w * (cos_wsqrt - xi / sqrt_b2 * sin_wsqrt)
                    - (two_b_ov_w3 + one_ov_w2) * (wsqrtsin + xwcos)) + one_ov_w2 / dt
    b_22 = -exp_b * (two_b_ov_w2 * (cos_wsqrt - xi / sqrt_b2 * sin_wsqrt) - two_b_ov_w3 * (wsqrtsin + xwcos)) - one_ov_w2 / dt

    b = array([[b_11, b_12], [b_21, b_22]])

    return a, b



def responseNigamJennings(acc, dt, periods, xi):
    """
    Implementation of the response spectrum calculation from Nigam and Jennings (1968).

    Ref: Nigam, N. C., Jennings, P. C. (1968) Digital calculation of response spectra from strong-motion earthquake
    records. National Science Foundation.
    https://core.ac.uk/download/pdf/216194346.pdf
    https://eqsig.readthedocs.io/en/latest/_modules/eqsig/sdof.html

    acc: acceleration in g (array)
    periods: response periods of interest (array)
    dt: time step of the acceleration time series (float)
    xi: critical damping factor (float) (e.g. 0.05)
    
    return: response displacement(), response velocity, response acceleration (array)
    """
    from numpy import array, zeros, zeros_like, newaxis, pi

    acc = -array(acc, dtype=float)
    periods = array(periods, dtype=float)
    # Check the periods array, if starts from 0, configure starting index
    if periods[0] == 0:
        s = 1
    else:
        s = 0

    w = (2*pi) / periods[s:]
    w2 = w ** 2


    dt = float(dt)
    xi = float(xi)

    # Calculate A and B constants
    a, b = computeAandB(xi, w, dt)

    # Generate arrays
    resp_disp = zeros([len(periods), len(acc)], dtype=float)
    resp_vel = zeros([len(periods), len(acc)], dtype=float)

    for i in range(len(acc) - 1):  
        # x_i+1 = A cross (u, v) + B cross (acc_i, acc_i+1)  # Eq 2.7a
        resp_disp[s:, i + 1] = (a[0][0] * resp_disp[s:, i] + a[0][1] * resp_vel[s:, i] + b[0][0] * acc[i] + b[0][1] * acc[i + 1])
        resp_vel[s:, i + 1] = (a[1][0] * resp_disp[s:, i] + a[1][1] * resp_vel[s:, i] + b[1][0] * acc[i] + b[1][1] * acc[i + 1])
    
    if s:
        sdof_acc = zeros_like(resp_disp, dtype=float)
        sdof_acc[s:] = -2 * xi * w[:, newaxis] * resp_vel[s:] - w2[:, newaxis] * resp_disp[s:]
        sdof_acc[0] = acc
    else:
        sdof_acc = -2 * xi * w[:, newaxis] * resp_vel[s:] - w2[:, newaxis] * resp_disp[s:]

    return sdof_acc, resp_vel, resp_disp





def pseudoResponseSpectra(motion, dt, periods, xi):
    """
    Computes the maximum response displacement, pseudo velocity and pseudo acceleration.

    :param motion: array floats, acceleration in g
    :param dt: float, the time step
    :param periods: array floats, The period of SDOF oscilator
    :param xi: float, fraction of critical damping (e.g. 0.05)
    :return: tuple floats, (spectral displacement, pseudo spectral velocity, pseudo spectral acceleration)
    """
    from numpy import array, ones_like, where, pi

    periods = array(periods, dtype=float)
    if periods[0] == 0:
        w = ones_like(periods)
        w[1:] = 2 * pi / periods[1:]
    else:
        w = 2 * pi / periods

    _, _, resp_disp = responseNigamJennings(motion, dt, periods, xi)

    sds = absmax(resp_disp, axis=1)
    svs = w * sds
    sas = w ** 2 * sds

    # When period = 0, SA = PGA
    sas = where(periods < dt * 1, absmax(motion), sas)

    return sas, svs*9.81, sds*9.81*100


def responseTimeSeries(motion, dt, periods, xi):
    """
    Computes the elastic response to the acceleration time series

    :param motion: array floats, acceleration in g
    :param dt: float, the time step
    :param periods: array floats, The period of SDOF oscillator
    :param xi: float, fraction of critical damping (e.g. 0.05)
    :return: tuple of float arrays, (response displacements, response velocities, response accelerations)
    """

    response_acc, response_vel, response_disp = responseNigamJennings(motion, dt, periods, xi)
    return response_acc[0], response_vel[0]*9.81, response_disp[0]*9.81*100



def horizontalAccDesignSpectrum(Sds, Sd1, T):
    from numpy import zeros
    
    TA = 0.2 * Sd1 / Sds
    TB = Sd1 / Sds
    TL = 6
    npts = len(T)
    designspectrum = zeros(npts)

    for i in range(len(T)):
        if T[i] < TA :
            designspectrum[i] = (0.4 + 0.6*(T[i] / TA))*Sds
        elif T[i] >= TA and T[i] <= TB:
            designspectrum[i] = Sds
        elif T[i] > TB and T[i] <= TL:
            designspectrum[i] = Sd1 / T[i]
        elif T[i] > TL:
            designspectrum[i] = Sd1*TL/(T[i]**2)

    return designspectrum



def verticalAccDesignSpectrum(Sds, Sd1, T):
    from numpy import zeros
    TA = 0.2 * Sd1 / Sds
    TB = Sd1 / Sds
    TL = 6
    TAD , TBD , TLD = TA / 3 , TB/3 , TL/2

    npts = len(T)
    designspectrum = zeros(npts)

    for i in range(len(T)):
        if T[i] < TAD :
            designspectrum[i] = ((0.32 + 0.48*(T[i]/TAD)) * Sds)
        elif T[i] >= TAD and T[i] <= TBD:
            designspectrum[i] = (0.8 * Sds)
        elif T[i] > TBD :
            designspectrum[i] = (0.8 * Sds * TBD / T[i])

    return designspectrum



def horizontalDispDesignSpectrum(Sds, Sd1, T):
    from numpy import zeros
    
    TA = 0.2 * Sd1 / Sds
    TB = Sd1 / Sds
    TL = 6
    npts = len(T)
    designspectrum = zeros(npts)

    for i in range(len(T)):
        if T[i] < TA :
            deger = ((0.4 + 0.6*(T[i] / TA))*Sds)
        elif T[i] >= TA and T[i] <= TB:
            deger = (Sds)
        elif T[i] > TB and T[i] <= TL:
            deger = (Sd1 / T[i])
        elif T[i]> TL:
            deger = (Sd1*TL/(T[i]**2))

        designspectrum[i] = ((T[i]**2)/(4*(3.14)**2)*(9.81)*deger)

    return designspectrum
