import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_extras.customize_running import center_running
from numpy import argmax, linspace, around, append, full, zeros, pi, log10, array

import plotly.graph_objects as go
import pandas as pd


from functions.fdaFunctions import *
from functions.unitcorrection import *
from functions.baseFunctions import exportExcelSingle

def roundtoMultiple(num, multiple):
    return multiple * round(num / multiple)

def frequencyDomainAnalysis():

    st.info(
                    """___For more detailed information about the app, please visit___
                    [**www.modaltrace.com**](https://modaltrace.com/recana-record-analyzer)\n
                    """
                    )

    # Page Main Title 
    colored_header(
                    label="Frequency Domain Analysis",
                    description="Rapid evaluation of acceleration data in the time domain.",
                    color_name= "light-blue-70",
                )

    # Containers
    # Description
    eq_description_cont = st.container()
    eq_description_cont.markdown("Analyze the characteristics of the acceleration data in the frequency domain by calculating Fourier Amplitude Spectrum, Power Spectral and Spectral Density, Spectrogram, Response Spectrum, Response Time Series.\n\nImport file to start. Select file and data type.")

    eq_dataselect_cont = st.container()


    colored_header(
                    label="Methods",
                    description="Choose a method, select properties and calculate.",
                    color_name= "light-blue-70",
                )
    eq_methods_cont = st.container()
    
    # No of decimal places
    #st.session_state["decimal"] = 3
    
    # If no file imported raise error messega
    if "stream_df" not in st.session_state:
        st.error("___Import file to continue.___", icon="🚨")
    
    else:
        # EQ Data select
        eq_dataselect_col1, eq_dataselect_col2, eq_dataselect_col3, _ = eq_dataselect_cont.columns([2,2,2,2])

        eq_dataselect_warn_col1, _ = eq_dataselect_cont.columns([4,4])

        # Select record to export
        st.session_state["export_record_select"] = eq_dataselect_col1.selectbox(
                                                                        "Select File",
                                                                        st.session_state["stream_df"]["filename"].unique(), 
                                                                        help= "Select imported file to analyze.",
                                                                        key="1"
                                                                        )

        st.session_state["selected_export_prop"]  = st.session_state["stream_df"]["filename"].str.contains(st.session_state["export_record_select"], regex=True)
        
        # Index to check availability -get index from first trace
        export_index_ava = st.session_state["selected_export_prop"][st.session_state["selected_export_prop"]==True].index[0]
        
        eq_data_select = eq_dataselect_col2.selectbox(
                                                        "Select Data",
                                                        ("Raw", "Calibrated", "Trimmed", "Detrended", "Filtered"), 
                                                        help= "Select data type to analyze.",
                                                        )

        
        decimal = eq_dataselect_col3.number_input("Number of decimal places.", 
                                                    step=1,
                                                    min_value=2,
                                                    max_value=6,
                                                    value=4,
                                                    help="Set between 2 to 6"
                                                    )
        
        st.session_state["decimal"] = int(decimal)


        # Filter filename and data type
        st.session_state["FD_selected"] = st.session_state["stream_df"].loc[st.session_state["stream_df"]['filename'] == st.session_state["export_record_select"]]
                
        

        if eq_data_select == "Filtered":
            st.session_state["selected_export_prop"] = "filtereddata"

            if "filter_data_select" not in st.session_state:
                st.session_state["export_timedomain"] = "timesec"
            elif st.session_state["filter_data_select"] == "trimmeddata":
                st.session_state["export_time_domain"] = "trimmedtimesec"
            else: 
                st.session_state["export_time_domain"] = "timesec"


        elif eq_data_select == "Detrended":
            st.session_state["selected_export_prop"] = "detrendeddata"

            if "filter_data_select" not in st.session_state:
                st.session_state["export_timedomain"] = "timesec"
            elif st.session_state["filter_data_select"] == "trimmeddata":
                st.session_state["export_time_domain"] = "trimmedtimesec"
            else: 
                st.session_state["export_time_domain"] = "timesec"

        elif eq_data_select == "Raw":
            st.session_state["selected_export_prop"] = "rawdata"
            st.session_state["export_time_domain"] = "timesec"
            st.session_state["FD_selected"]["unit"] = "Raw"

        elif eq_data_select == "Calibrated":
            st.session_state["selected_export_prop"] = "calibrateddata"
            st.session_state["export_time_domain"] = "timesec"

        elif eq_data_select == "Trimmed":
            st.session_state["selected_export_prop"] = "trimmeddata"
            st.session_state["export_time_domain"] = "trimmedtimesec"


        ####################
        # Data availability
        ####################
        # Check calibrated data availability
        if st.session_state["selected_export_prop"] == "calibrateddata" and st.session_state["stream_df"]["calibrationstatus"].iloc[export_index_ava] == "Not Set":
            eq_dataselect_warn_col1.error("Calibrated data is not avaliable", icon="🚨")
        
        # Check trimmed data availability
        elif st.session_state["selected_export_prop"] == "trimmeddata" and st.session_state["stream_df"]["trimstatus"].iloc[export_index_ava] == "Not Set":
            eq_dataselect_warn_col1.error("Trimmed data is not avaliable", icon="🚨")

        # Check detrended data availability
        elif st.session_state["selected_export_prop"] == "detrendeddata" and st.session_state["stream_df"]["detrendstatus"].iloc[export_index_ava] == "Not Set":
            eq_dataselect_warn_col1.error("Detrended data is not avaliable", icon="🚨")

        # Check filtered data availability
        elif st.session_state["selected_export_prop"] == "filtereddata" and st.session_state["stream_df"]["filterstatus"].iloc[export_index_ava] == "Not Set":
            eq_dataselect_warn_col1.error("Filtered data is not avaliable", icon="🚨")  

        else:
            
            # Tabs and containers
            fourier_tab, spectrum_tab, spectrogram_tab, response_tab, responceTS_tab, FDparam_tab = eq_methods_cont.tabs(
                                                                            ["**Fourier Transform**", 
                                                                             "**Spectral Density**", 
                                                                             "**Spectrogram**", 
                                                                             "**Response Spectrum**",
                                                                             "**Response Time Series**",
                                                                             "**Parameters**",
                                                                             ])

            fourier_cont = fourier_tab.container()
            fourier_col1, fourier_col2,  fourier_col3, fourier_col4 = fourier_cont.columns([2,2,2,2])
            fourier_fig_cont = fourier_cont.container()
            fourier_data_cont = fourier_cont.container()

            spectrum_cont = spectrum_tab.container()
            spectrum_col1, spectrum_col2, spectrum_col3, spectrum_col4 = spectrum_cont.columns([2,2,2,2])
            welch_col1, welch_col2, welch_col3, _ = spectrum_cont.columns([2,2,2,2])
            spectrum_fig_cont = spectrum_tab.container()
            spectrum_data_cont = spectrum_tab.container()

            spectrogram_cont = spectrogram_tab.container()
            spectrogram_col1, _ = spectrogram_cont.columns([2,6])
            spectrogram_fig_cont = spectrogram_tab.container()
            spectrogram_data_cont = spectrogram_tab.container()


            response_cont = response_tab.container()
            response_col1, response_col2, response_col3, response_col4 = response_cont.columns([2,2,2,2])
            response_fig_cont = response_cont.container()
            response_data_cont = response_cont.container()

            responceTS_cont = responceTS_tab.container()
            responseTS_col1, _ = responceTS_cont.columns([2,6])
            responseTS_fig_cont = responceTS_tab.container()
            responseTS_data_cont = responceTS_tab.container()

        
            FDparam_cont = FDparam_tab.container()
            FDparam_col1, _ = FDparam_cont.columns([2,6])


            #####################################
            ### Fourier Transform
            ##################################### 
            with fourier_tab:
                center_running()


                # Select Channel
                fourier_trace_select = fourier_col1.selectbox(
                                                        "Select Channel/Trace",
                                                        st.session_state["FD_selected"]["tracename"],      
                                                        key=4           
                                                        )
                
                # Select Axis Type
                x_type = fourier_col2.selectbox(
                                                "X Axis Type",
                                                ["Logarithmic", "Regular"],      
                                                key=5,           
                                                )
                # Select Axis Type
                y_type = fourier_col3.selectbox(
                                                "Y Axis Type",
                                                ["Logarithmic", "Regular"],      
                                                key=6,           
                                                )
                

                # Filter dataframe for selected channel
                st.session_state["FD_trace_selected"] = st.session_state["FD_selected"].loc[st.session_state["FD_selected"]["tracename"] == fourier_trace_select] 
                st.session_state["FD_selected_index"] = st.session_state["FD_trace_selected"].index[0]
                
                # Calculation button
                #fourier_integration_type = fourier_col4.button("Calculate")     

                #if fourier_integration_type == True:

                #####################################
                ### Fourier Transform Figure
                #####################################
                fig_fourier = go.Figure()


                fourier_freq, fourier_amp = fourierAmplitude(st.session_state["FD_trace_selected"][st.session_state["selected_export_prop"]].iloc[0], 
                                                                 st.session_state["FD_trace_selected"]["delta"].iloc[0], 
                                                                 len(st.session_state["FD_trace_selected"][st.session_state["selected_export_prop"]].iloc[0]),
                                                                 )
                    
                linename = str(st.session_state["FD_trace_selected"]["filename"].iloc[0]) + str(" ") + str(st.session_state["FD_trace_selected"]["tracename"].iloc[0])
                fig_fourier.add_trace(go.Scatter(x= fourier_freq, 
                                                    y= fourier_amp,
                                                    line=dict(color="#1f77b4"),
                                                    mode="lines",
                                                    name= linename,
                                                    ))
                    

                    
                # Plot objects
                fig_fourier.update_layout(title_text= "<b>Fourier Transform<b>", legend_title_text = "File name - Trace", legend=dict(x=0.01, y=0.01))           # title_text= "Time Series",
                fig_fourier.update_xaxes(title_text="Frequency (Hz)", )
                fig_fourier.update_yaxes(title_text=f"Fourier Amplitude")
                fig_fourier.update_layout(height=500, xaxis_range = [0.1, int(0.5/st.session_state["FD_trace_selected"]["delta"].iloc[0])])

                if x_type == "Logarithmic":
                    fig_fourier.update_layout(xaxis_type= "log", xaxis_range = [log10(0.1), log10(int(0.5/st.session_state["FD_trace_selected"]["delta"].iloc[0]))])

                if y_type == "Logarithmic":
                    fig_fourier.update_layout(yaxis_type= "log")#, xaxis_range = [0.1, log10(int(0.5/st.session_state["FD_trace_selected"]["delta"].iloc[0]))])

                fourier_fig_cont.plotly_chart(fig_fourier, theme="streamlit", use_container_width=True, height=500)

    


            #####################################
            ### Spectrum
            ##################################### 

            with spectrum_tab:
                center_running()


                # Select Channel
                spectrum_trace_select = spectrum_col1.selectbox(
                                                        "Select Channel/Trace",
                                                        st.session_state["FD_selected"]["tracename"],      
                                                        key=7,           
                                                        )
                
                
                # Filter dataframe for selected channel
                st.session_state["FD_trace_selected"] = st.session_state["FD_selected"].loc[st.session_state["FD_selected"]["tracename"] == spectrum_trace_select] 
                st.session_state["FD_selected_index"] = st.session_state["FD_trace_selected"].index[0]
                

                # Select Scaling
                spectrum_scale_select = spectrum_col2.selectbox(
                                                        "Select Scaling",
                                                        ["Power Spectral Density", "Spectral Density"],  
                                                        help="Selects between the Spectral Density or Power Spectral Density"           
                                                        )
                               
                # Select Axis Type
                x_type = spectrum_col3.selectbox(
                                                "X Axis Type",
                                                ["Logarithmic", "Regular"],      
                                                key=8,           
                                                )
                # Select Axis Type
                y_type = spectrum_col4.selectbox(
                                                "Y Axis Type",
                                                ["Logarithmic", "Regular"],      
                                                key=9,           
                                                )
                
                # Select smoothing
                # Enable / Disable
                smoothing_check = welch_col1.checkbox("Apply Averaging", help="Reduce noise with Welch's method")

                record_length = len(st.session_state["FD_trace_selected"][st.session_state["selected_export_prop"]].iloc[0]) * st.session_state["FD_trace_selected"]["delta"].iloc[0]
                if smoothing_check == True:
                    # Window Length
                    smoothing_window = welch_col2.slider(
                                                        "Window Length",
                                                        5, roundtoMultiple(record_length, 5), roundtoMultiple(record_length/2, 5) , 5,  
                                                        help="Length of each window segment"           
                                                        )
                    
                    # Number of overlap
                    smoothing_overlap = welch_col3.slider(
                                                        "Overlap",
                                                        2, 5, 2, 1, 
                                                        help="Number of points to overlap"           
                                                        )
                

                    spec_f, spec_a =  welchMethod(st.session_state["FD_trace_selected"][st.session_state["selected_export_prop"]].iloc[0], 
                                        smoothing_window, 
                                        smoothing_overlap, 
                                        st.session_state["FD_trace_selected"]["delta"].iloc[0],
                                        spectrum_scale_select, 
                                        0,
                                        )
                
                else:
                    spec_f, spec_a =  periodogramMethod(st.session_state["FD_trace_selected"][st.session_state["selected_export_prop"]].iloc[0], 
                                        st.session_state["FD_trace_selected"]["delta"].iloc[0],
                                        spectrum_scale_select, 
                                        )


                #####################################
                ### Spectrum Figure
                #####################################
                fig_spectrum = go.Figure()

                    
                linename = str(st.session_state["FD_trace_selected"]["filename"].iloc[0]) + str(" ") + str(st.session_state["FD_trace_selected"]["tracename"].iloc[0])
                fig_spectrum.add_trace(go.Scatter(x= spec_f, 
                                                    y= spec_a,
                                                    line=dict(color="#1f77b4"),
                                                    mode="lines",
                                                    name= linename,
                                                    ))
                    
                
                # Plot objects
                fig_spectrum.update_layout(title_text= "<b>Spectral Density<b>", legend_title_text = "File name - Trace", legend=dict(x=0.01, y=0.01))           # title_text= "Time Series",
                fig_spectrum.update_xaxes(title_text="Frequency (Hz)", )
                fig_spectrum.update_yaxes(title_text=f"Spectral Density")
                fig_spectrum.update_layout(height=500, xaxis_range = [0.1, int(0.5/st.session_state["FD_trace_selected"]["delta"].iloc[0])])

                if x_type == "Logarithmic":
                    fig_spectrum.update_layout(xaxis_type= "log", xaxis_range = [log10(0.1), log10(int(0.5/st.session_state["FD_trace_selected"]["delta"].iloc[0]))])

                if y_type == "Logarithmic":
                    fig_spectrum.update_layout(yaxis_type= "log") #, xaxis_range = [0.1, log10(int(0.5/st.session_state["FD_trace_selected"]["delta"].iloc[0]))])

                spectrum_fig_cont.plotly_chart(fig_spectrum, theme="streamlit", use_container_width=True, height=500)



         

            #####################################
            ### Spectrogram
            ##################################### 
            with spectrogram_tab:
                center_running()


                # Select Channel
                spectrogram_trace_select = spectrogram_col1.selectbox(
                                                        "Select Channel/Trace",
                                                        st.session_state["FD_selected"]["tracename"],      
                                                        key=10,       
                                                        )

                # Filter dataframe for selected channel
                st.session_state["FD_trace_selected"] = st.session_state["FD_selected"].loc[st.session_state["FD_selected"]["tracename"] == spectrogram_trace_select] 
                st.session_state["FD_selected_index"] = st.session_state["FD_trace_selected"].index[0]


                #####################################
                ### Spectrogram Figure
                #####################################
                

                f, t, Sxx  = spectrogramFunction(st.session_state["FD_trace_selected"][st.session_state["selected_export_prop"]].iloc[0], 
                                                        st.session_state["FD_trace_selected"]["delta"].iloc[0], 
                                                        )
                fig_spectrogram = go.Figure()
                fig_spectrogram = go.Figure(data=go.Heatmap(
                                                            x= t,
                                                            y= f,
                                                            z= 10 * log10(Sxx),
                                                            #text=[[40.32, 43.33, 39.94], [40.12, 40.13, 43.12], [39.03, 40.23, 40.22]],
                                                            #texttemplate="%{text}",
                                                            #textfont={"size": 10},
                                                            colorscale="Jet",
                                                            hoverongaps = False,
                                                            ))
                                                            
                # Plot objects
                fig_spectrogram.update_layout(title_text= "<b>Spectrogram<b>", legend_title_text = "File name - Trace", legend=dict(x=0.01, y=0.01))           # title_text= "Time Series",
                fig_spectrogram.update_xaxes(title_text="Time (s)")
                fig_spectrogram.update_yaxes(title_text=f"Frequency (Hz)")
                fig_spectrogram.update_layout(height=600)

                spectrogram_fig_cont.plotly_chart(fig_spectrogram, theme="streamlit", use_container_width=True, height=600)


            #####################################
            ### Response Spectrum
            ##################################### 
            with response_tab:
                center_running()


                # Select Channel
                response_trace_select = response_col1.selectbox(
                                                        "Select Channel/Trace",
                                                        st.session_state["FD_selected"]["tracename"],      
                                                        key=11,       
                                                        )
                
                # Filter dataframe for selected channel
                st.session_state["FD_trace_selected"] = st.session_state["FD_selected"].loc[st.session_state["FD_selected"]["tracename"] == response_trace_select] 
                st.session_state["FD_selected_index"] = st.session_state["FD_trace_selected"].index[0]

                # Window Length
                response_resolution = response_col2.slider(
                                                        "Resolution",
                                                        0.02, 0.5, 0.1 ,0.02,
                                                        help="Response Spectrum resolution to analyze each step" ,          
                                                        key=12,
                                                        )
                    
                # Number of overlap
                response_damping = response_col3.slider(
                                                        "Damping Ratio",
                                                        0.01, 0.9, 0.05, 0.01, 
                                                        help="Damping Ratio",
                                                        key=13,     
                                                        )
                
                # INPUT DATA
                damping = response_damping
                m = 1
                dt = st.session_state["FD_trace_selected"]["delta"].iloc[0]
                resolution = response_resolution
                datapoint = int((1/resolution) * 2)
                response_T = zeros((datapoint,1))
                response_T[:,0] = linspace(resolution,2,datapoint)[:]
                response_Tl = []
                for d in response_T:
                    response_Tl.append(d[0])
                response_Tl = array(response_Tl)

                omega_n = 2 * pi / response_T
                K = m*(omega_n**2)
                            
                # SOLUTION
                u0 = responseStateSpace(damping, K, omega_n, dt, 
                    st.session_state["FD_trace_selected"][st.session_state["selected_export_prop"]].iloc[0])[0]

                # RESPONSE SPECTRUM PLOT
                response_A = (omega_n**2)*(u0/9.81) 
                response_Al = []
                for d in response_A:
                    response_Al.append(d[0])
                response_Al = array(response_Al)


                #####################################
                ### Repsponse Spectrum Figure
                #####################################
                fig_response_spectrum = go.Figure()

                linename = str(st.session_state["FD_trace_selected"]["filename"].iloc[0]) + str(" ") + str(st.session_state["FD_trace_selected"]["tracename"].iloc[0])
                
                fig_response_spectrum.add_trace(go.Scatter(
                                                            x= response_Tl, 
                                                            y= response_Al,
                                                            line=dict(color="#1f77b4"),
                                                            mode="lines",
                                                            line_width=3,
                                                            name= linename,
                                                            ))
                
                # Plot objects
                fig_response_spectrum.update_layout(title_text= "<b>Response Spectrum<b>", legend_title_text = "File name - Trace", legend=dict(x=0.01, y=0.01))           # title_text= "Time Series",
                fig_response_spectrum.update_xaxes(title_text="Period (s)")
                fig_response_spectrum.update_yaxes(title_text=f"SA (g)")
                fig_response_spectrum.update_layout(xaxis_type= "linear", yaxis_type= "linear")

                fig_response_spectrum.update_layout(height=600)

                response_fig_cont.plotly_chart(fig_response_spectrum, theme="streamlit", use_container_width=True, height=600)
                

                
            with responceTS_tab:
                center_running()
                responseTS_col1.write("In Progress...")

            with FDparam_tab:
                center_running()
                FDparam_col1.write("In Progress...")




if __name__ == "__main__":
    frequencyDomainAnalysis()



