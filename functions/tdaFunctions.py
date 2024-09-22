from functions.baseFunctions import *


def TD_integration(input_array, delta, corr_status, order, integration_corr, corner):
    """
    Time domain integration of time series Acc>Vel - Vel>Disp
    - Inputs
    input_array : acceleration or velocity array object
    delta : sampling interval (float)
    corr_status : baseline correection status (boolean)
    order : baseline correction order (int)
    integration_corr_type: TD Correction or DF Correction
    corner: Corner frequency of highpass filter

    - Function Outputs
    output_array : Velocity or displacement array
    """

    from obspy.signal.detrend import spline
    #from scipy.integrate import cumtrapz
    from scipy.integrate import cumulative_trapezoid
    from numpy import mean

    if integration_corr == "TD Correction":
        if corr_status == True:
            output_array = spline(cumulative_trapezoid(input_array, dx= delta, initial=0), order=order, dspline=len(input_array))
        elif corr_status == False:
            output_array = cumulative_trapezoid(input_array, dx= delta, initial=0)

    if integration_corr == "FD Correction":
        array = cumulative_trapezoid(input_array, dx= delta, initial=0)
        array_bc = array - mean(array)
        output_array = iirFilter(array_bc, "highpass", [corner], delta, 3)      # 0-highcut   1-lowcut


    return output_array


def ariasIntensity(acceleration, delta, time, start_level, end_level, dec):
    """
    Calculate Arias Intensity
    - Inputs
    acceleration : acceleration data of the record (m/s**2) (array)
    delta : time interval between each sample (float)
    time : record's time domain (array)
    start_level : min arias percentage level for duration (int)
    end_level : max arias percentage level for duration (int)
    dec : decimation number

    - Funtion Outputs
    arias : arias intensity peak (float)
    aritime : arias intensity values as m/s (array)
    hus_tf : end level index value (int)
    hus_to : start level index value (int)
    husid : duration between start-end arias intensity level (float)
    """
    from numpy import where, trapz, sqrt
    #from scipy.integrate import cumtrapz
    from scipy.integrate import cumulative_trapezoid


    ncoef = 3.1416 / (2 * 9.81)
    acc = (acceleration ) * sqrt(ncoef)
    aritime = cumulative_trapezoid(acc**2) * delta
    arias = trapz(acc**2) * delta

    hus_to = where(aritime >= start_level/100 * arias)[0][0]
    hus_tf = where(aritime >= end_level/100 * arias)[0][0]

    husid = time[hus_tf] - time[hus_to]

    return round(arias, dec), aritime, hus_tf, hus_to, round(husid, dec) 



def cumulativeAbsoluteVelocity(record, delta, unit, dec):
    """
    -CAV Calculation Function
    -https://www.caee.ca/10CCEEpdf/2010EQConf-000046.pdf
    -Function Inputs
    record : acceleration data of the record (array)
    delta : time interval between each sample (float)
    unit: unit of acceleration
    dec : decimation number

    ### cavtype : Select cav to be calculated "cav" or "scav" (string) ---cancelled

    -Funtion Outputs
    cav : classic cav value (float)
    cavtime : classic cav time domain (array)
    scav : standardized cav value (float)
    scavtime : standardized cav time domain (array)
    """
    from numpy import trapz, abs, floor, ceil, max, zeros, append, full
    #from scipy.integrate import cumtrapz
    from scipy.integrate import cumulative_trapezoid
    from functions.unitcorrection import scavunit

    
    if unit == "Raw":
        # Classic CAV
        cav = trapz(abs(record)) * delta
        cavtime = cumulative_trapezoid(abs(record)) * delta
        cavtime = append(cavtime, [cavtime[-1]])

        scav = None
        scavtime = None

        return round(cav, dec), cavtime, scav, scavtime
    
    else:
        # Classic CAV
        cav = trapz(abs(record)) * delta
        cavtime = cumulative_trapezoid(abs(record)) * delta
        cavtime = append(cavtime, [cavtime[-1]])
    
        # Standardized CAV
        t0   = 1.0                                        # 1 s window
        nw   = int(floor(len(record) * delta / t0))       # number of windows
        ns   = int(ceil(t0 / delta))                      # npts in each time window

        scav = 0
        scavtime  = zeros(int(nw*ns))
        for ii in range(1,nw):
            imin = int((ii-1)*ns+1)
            imax = int(ii*ns+1)
            if imax < len(record):
                maxw = max(abs(record[imin:imax]))
                # threshold level is accepted as 0.025g 
                if maxw >= scavunit(unit):                         
                    scav =scav+trapz(abs(record[imin:imax])) * delta
                    scavtime[imin:imax] = scav
                
                else:
                    scav = scav
                    scavtime[imin:imax] = scav

                    #lendiff = len(cavtime) - len(scavtime)
                    #scavtime = append(scavtime, full(lendiff, fill_value=10))
                    

        lendiff = len(cavtime) - len(scavtime)
        if lendiff == 0:
            pass
        else:
            scavtime[-int(1/delta):] = full(int(1/delta), fill_value=scav)
            scavtime = append(scavtime, full(lendiff, fill_value=scav))


        return round(cav, dec), cavtime, round(scav, dec), scavtime

