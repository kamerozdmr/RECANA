from obspy import read
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from obspy import UTCDateTime
import streamlit as st

class Record:
    def __init__(self, filedata, filename, fileformat):
        
        self.filename = filename
        self.fileformat = fileformat
        self.filedata = filedata


    def createFileParameters(self):
        # Read .mseed, .sac, .gcf files with obspy
        if self.fileformat == "gcf":
                
            self.filedata = read(self.filedata, format="GCF", errorret=True)
        
        else:
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

            # Do not add the trace if there is no delta value. Some gcf streams have traces with no header info. 
            if trace.stats.delta == 0:
                continue
            
            # Create Dataframe containing record properties  
            trace_dict = {"filename": self.filename, 
                    "fileformat": self.fileformat,
                    "tracename": f"Trace{trace_ind+1}-{trace.stats.channel}",
                    "rawdata": data,
                    "calibrateddata": [],
                    "trimmeddata": [],

                    "calibrationstatus": "Not Set",
                    "trimstatus": "Not Set",

                    "timesec": pd.Series(np.linspace(0, trace.stats.npts * trace.stats.delta, num=trace.stats.npts, endpoint=False), dtype="float64"),
                    "trimmedtimesec": pd.Series(np.linspace(0, trace.stats.npts * trace.stats.delta, num=trace.stats.npts, endpoint=False), dtype="float64"),

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
        # Read ASCII files
        data_all = pd.read_table(self.filedata, names=["Data"])
        # Define the string to search for division of header and data
        search_string = "USER5: "
        
        # Use str.contains() to search for the string in the 'Data' column
        index_header = data_all[data_all["Data"].str.contains(search_string)].index + 1
        data_header = data_all.iloc[:index_header[0]].reset_index()
        data_header[["Description", "Value"]] = data_header["Data"].str.split(": ", 1, expand=True)
        self.data_header = data_header.drop("Data", axis=1)
    
        self.data = data_all.iloc[index_header[0]:].reset_index()


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



        for trace_ind in range(1):
            data =  self.data["Data"]   

            # Name of the trace
            tracename_ind = data_header[self.data_header["Description"].str.contains("STREAM")].index
            tracename = data_header.Value.iloc[tracename_ind[0]]

            # Npts of the trace
            npts_ind = data_header[self.data_header["Description"].str.contains("NDATA")].index
            npts = int(data_header.Value.iloc[npts_ind[0]])

            # Delta of the trace
            delta_ind = data_header[self.data_header["Description"].str.contains("SAMPLING_INTERVAL_S")].index
            delta = float(data_header.Value.iloc[delta_ind[0]])


            # Starttime of the trace
            starttime_ind = data_header[self.data_header["Description"].str.contains("DATE_TIME_FIRST_SAMPLE_YYYYMMDD_HHMMSS")].index
            starttime = UTCDateTime.strptime(data_header.Value.iloc[starttime_ind[0]], "%Y%m%d_%H%M%S")


            # Create Dataframe containing record properties  
            trace_dict = {"filename": self.filename, 
                    "fileformat": self.fileformat,
                    "tracename": f"Trace{trace_ind+1}-{tracename}",
                    "rawdata": data.astype("float64"),
                    "calibrateddata": [],
                    "trimmeddata": [],

                    "calibrationstatus": "Not Set",
                    "trimstatus": "Not Set",

                    "timesec": pd.Series(np.linspace(0, npts * delta, num=npts, endpoint=False), dtype="float64"),
                    "trimmedtimesec": pd.Series(np.linspace(0, npts * delta, num=npts, endpoint=False), dtype="float64"),

                    "detrendeddata": [],
                    "detrendstatus": "Not Set",
                    "filtereddata":[],
                    "filterstatus": "Not Set",

                    "npts": int(npts),
                    "delta": float(delta),
                    "starttime": starttime,
                    "endtime": "Not Set",
                    "unit": "Raw",
                    }

            # Append to stream_df
            self.stream_df = self.stream_df.append(trace_dict, ignore_index = True)




            # Create Dataframe containing time domain analysis parameters
            TDparams_trace_dict = {"filename": self.filename,
                                    "tracename": f"Trace{trace_ind+1}-{tracename}",
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



        else:
            print("unknown file format")

    

            
