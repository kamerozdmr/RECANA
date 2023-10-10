from obspy import read
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class Record:
    def __init__(self, filedata, filename, fileformat):
        
        self.filename = filename
        self.fileformat = fileformat
        self.filedata = filedata


    def createFileParameters(self):
        # Read .mseed, .sac, .gcf files with obspy
        self.filedata = read(self.filedata)    

        # Dictionary containing record properties
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

        # Dictionary containing time domain analysis parameters
        self.TDparams_stream_dict = {"filename": [],
                                    "tracename": [],
                                    "PGA": [],
                                    "PGAtime": [],
                                    "PGAunit": [],
                                    "PGV": [],
                                    "PGVtime": [],
                                    "PGVunit": [],
                                    "PGD": [],
                                    "PGDtime": [],
                                    "PGDunit": [], 
                                    "AriasIntensity": [],
                                    "AriasIntensityunit": [],
                                    "SignificantDuration": [],
                                    "CAV": [],
                                    "StandardizedCAV": [],
                                    "CAVunit" : [],
                                    }
        
        self.TDparams_stream_df =  pd.DataFrame(data= self.TDparams_stream_dict)



        for trace_ind in range(len(self.filedata)):
            trace = self.filedata[trace_ind]
            data =  pd.Series(trace.data)     
            
            # Create Dataframe containing record properties  
            trace_dict = {"filename": self.filename, 
                    "fileformat": self.fileformat,
                    "tracename": f"Trace{trace_ind+1}-{trace.stats.channel}",
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
            self.stream_df = self.stream_df.append(trace_dict, ignore_index = True)




            # Create Dataframe containing time domain analysis parameters
            TDparams_trace_dict = {"filename": self.filename,
                                    "tracename": f"Trace{trace_ind+1}-{trace.stats.channel}",
                                    "PGA": None,
                                    "PGAtime": None,
                                    "PGAunit": None,
                                    "PGV": None,
                                    "PGVtime": None,
                                    "PGVunit": None,
                                    "PGD": None,
                                    "PGDtime": None,
                                    "PGDunit": None, 
                                    "AriasIntensity": None,
                                    "AriasIntensityunit": None,
                                    "SignificantDuration": None,
                                    "CAV": None,
                                    "StandardizedCAV": None,
                                    "CAVunit" : None,
                                    }
            
            # Append to TDparams_df
            self.TDparams_stream_df = self.TDparams_stream_df.append(TDparams_trace_dict, ignore_index = True)


    def createAscFileParameters(self):
        # Read asc file 

        pass
        #self.TDparams_stream_df = 


    def importFile(self):

        if self.fileformat == "mseed":
            self.createFileParameters()                     
        
        elif self.fileformat == "gcf":
            self.createFileParameters()

        elif self.fileformat == "SAC":
            self.createFileParameters()

        elif self.fileformat == "asc":
            self.createAscFileParameters()

        # add txt, ascii formats 

        else:
            print("unknown file format")

    

            
