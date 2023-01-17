from obspy import read
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class Record:
    def __init__(self, filedata, filename, fileformat):
        
        self.filename = filename
        self.fileformat = fileformat
        self.filedata = read(filedata)    # read with obspy

        # Import the file
        #self.importFile(filedata)


    def importMseed(self):

        
        self.stream_dict = {"filename": [], 
                            "fileformat": [],
                            "tracename": [],
                            "rawdata": [],
                            "calibrateddata": [],
                            "calibrationstatus": [],
                            "trimmeddata": [],
                            "trimstatus": [],
                            "timesec": [],
                            "trimmedtimesec": [],

                            "detrendeddata": [],
                            "detrendstatus": [],
                            "filtereddata":[],
                            "filterstatus": [],

                            "npts": [],
                            "delta": [],
                            "starttime": [],
                            "endtime": [],
                            "unit": [],
                            }

        self.stream_df =  pd.DataFrame(data= self.stream_dict)


        for trace_ind in range(len(self.filedata)):
            trace = self.filedata[trace_ind]
            data =  pd.Series(trace.data)       #pd.Series(trace.data)
            df = {"filename": self.filename, 
                    "fileformat": self.fileformat,
                    "tracename": f"Trace {trace_ind+1} - {trace.stats.channel}",
                    "rawdata": data,
                    "calibrateddata": [],
                    "trimmeddata": [],

                    "calibrationstatus": "Not Set",
                    "trimstatus": "Not Set",

                    "timesec": pd.Series(np.linspace(0, trace.stats.npts * trace.stats.delta, num=trace.stats.npts, endpoint=False)),
                    "trimmedtimesec": pd.Series(np.linspace(0, trace.stats.npts * trace.stats.delta, num=trace.stats.npts, endpoint=False)),

                    "detrendeddata": [],
                    "detrendstatus": "Not Set",
                    "filtereddata":[],
                    "filterstatus": "Not Set",

                    "npts": int(trace.stats.npts),
                    "delta": float(trace.stats.delta),
                    "starttime": trace.stats.starttime.datetime,
                    "endtime": trace.stats.endtime.datetime,
                    "unit": "Raw",
                    
                    }

            # Append to stream_df
            self.stream_df = self.stream_df.append(df, ignore_index = True)


    def importFile(self):

        if self.fileformat == "mseed":
            self.importMseed()                     # Run file format function
        
        elif self.fileformat == "gcf":
            self.importMseed()

        else:
            print("unknown file format")

    

            
