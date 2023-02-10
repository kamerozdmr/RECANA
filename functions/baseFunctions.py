from obspy import read
from obspy.signal.detrend import simple, polynomial
from scipy import signal, fftpack
import numpy as np
import pandas as pd
import io


def readRecord(filepath, filename, trace):
    # Read record
    record = read(f"{filepath}/{filename}")[trace]
    delta = record.stats.delta
    npts = record.stats.npts
    starttime = record.stats.starttime
    return record.data, delta, npts, starttime


def butterworthKernel(btype, prop, delta, order):
    fn = 0.5 * int(1/delta)

    if btype == "bandpass":
        highcut = prop[0]
        lowcut = prop[1]
        b, a = signal.butter(order, [highcut/fn, lowcut/fn], btype = btype)
    elif btype == "lowpass":
        lowcut = prop[0]
        b, a = signal.butter(order, lowcut/fn, btype = btype)
    elif btype == "highpass":
        highcut = prop[0]
        b, a = signal.butter(order, highcut/fn, btype = btype)
    else:
        print(" Filter type error!!! ")

    return b, a


def iirFilter(data, btype, prop, delta, order):
    # Appyly butterworth filter
    b, a = butterworthKernel(btype, prop, delta, order = order)

    return signal.filtfilt(b, a, data)          # , method = "gust"


def iirResponse(btype, prop, delta, order):
    
    sps = int(1/delta)
    nyquist = sps / 2

    # get filter parameters
    filtKernB, filtKernA = butterworthKernel(btype, prop, delta, order)
    
    # generate the impulse
    implen = 1001
    impres = np.zeros(implen)               # 1001
    impres[int((implen+1)/2)] = 1           # 501
    timepoint = np.linspace(0, implen, implen, endpoint=False)

    # apply the filter
    fimp = signal.filtfilt(filtKernB, filtKernA, impres, axis=-1)

    # compute power spectrum
    fimpX = np.abs(fftpack.fft(fimp))**2
    hz = np.linspace(0, nyquist, int(np.floor(len(impres)/2)+1))


    return fimp, timepoint, fimpX, hz        


def getFrequencyResponse(a, b, fs): 
    w, h = signal.freqz(a, b, worN = 1024)
    return w * fs/(2*np.pi), -20 * np.log10(abs(h))


def detrendFunction(data, method, ord):
    if method == "line":
        detrd = simple(np.array(data))
        return detrd
    
    elif method == "polynomial":
        detrd = polynomial(np.array(data), order= ord)
        return detrd


#####################
# Export Functions

def editDelimiter(delimiter):

    if delimiter == "comma (,)":
        return ","
    elif delimiter == "colon (:)":
        return ":"
    elif delimiter == "semicolon (;)":
        return ";"
    elif delimiter == "pipe (|)":
        return "|"



def exportExcel(stream_df, export_prop, export_data_select, export_time_domain):

    buffer = io.BytesIO()
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        for index, value in export_prop.items():
            if value == True:
                df = pd.DataFrame({"Data" : list(stream_df[export_data_select].iloc[index]),
                                    "Time": list(stream_df[export_time_domain].iloc[index])})
                sheetname = str(stream_df["tracename"].iloc[index])
                # Write each dataframe to a different worksheet.
                df.to_excel(writer, sheet_name = sheetname) 
        # Close the Pandas Excel writer and output the Excel file to the buffer
        writer.save()               

    return buffer



def exportCsv(stream_df, export_prop, export_data_select, export_time_domain, delimiter):
    df_csv = pd.DataFrame()

    for index, value in export_prop.items():
        if value == True:
            tracename = str(stream_df["tracename"].iloc[index])
            columndata, columntime = tracename + str("-Data"), tracename + str("-Time")
            df_csv[columndata] = list(stream_df[export_data_select].iloc[index])
            df_csv[columntime] = list(stream_df[export_time_domain].iloc[index])

    return df_csv.to_csv(sep=editDelimiter(delimiter), index=False).encode('utf-8')




if __name__ == "__main__":
    pass

