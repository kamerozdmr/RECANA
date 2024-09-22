import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_extras.customize_running import center_running
from numpy import argmax, linspace, around, append, full, zeros, pi, log10, array

import plotly.graph_objects as go

from functions.fdaFunctions import *
from functions.unitcorrection import *
from functions.baseFunctions import exportExcelSingle
from functions.spectralAccelerationCoefficents import *

def roundtoMultiple(num, multiple):
    return multiple * round(num / multiple)

def frequencyDomainAnalysis():

    #st.info(
    #                """___For more detailed information about the app, please visit___
    #                [**www.modaltrace.com**](https://modaltrace.com/recana-record-analyzer)\n
    #                """
    #                )

    # Page Main Title 
    colored_header(
                    label="Frequency Domain Analysis",
                    description="Rapid evaluation of acceleration data in the frequency domain.",
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

    response_factor = 1
    
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
                                                                        key=1
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
            fourier_tab, spectrum_tab, spectrogram_tab, response_tab, responseTS_tab, FDparam_tab = eq_methods_cont.tabs(
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
            response_maincol1, response_maincol2 = response_cont.columns([3,1])
            response_maincol1.write("Response Spectrum")
            response_maincol2.write("Design Response Spectrum")
            response_col1, response_col2, response_col3 = response_maincol1.columns([2,2,1])
            response_dcol1, response_dcol2 = response_maincol2.columns([1,1])
            response_fig_cont = response_maincol1.container()
            response_data_cont = response_cont.container()

            responceTS_cont = responseTS_tab.container()
            responseTS_col1, responseTS_col2, responseTS_col3, responseTS_col4 = responceTS_cont.columns([2,2,2,2])
            responseTS_fig_cont = responseTS_tab.container()
            responseTS_data_cont = responseTS_tab.container()

        
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
                                                        key=2           
                                                        )
                
                # Select Axis Type
                x_type = fourier_col2.selectbox(
                                                "X Axis Type",
                                                ["Logarithmic", "Regular"],      
                                                key=3,           
                                                )
                # Select Axis Type
                y_type = fourier_col3.selectbox(
                                                "Y Axis Type",
                                                ["Logarithmic", "Regular"],      
                                                key=4,           
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
                                                        key=5,           
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
                                                key=6,           
                                                )
                # Select Axis Type
                y_type = spectrum_col4.selectbox(
                                                "Y Axis Type",
                                                ["Logarithmic", "Regular"],      
                                                key=7,           
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
                                                        key=8,       
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

                # Response Spectrum Column
                # Select Channel
                response_trace_select = response_col1.selectbox(
                                                        "Select Channel/Trace",
                                                        st.session_state["FD_selected"]["tracename"],      
                                                        key=9,       
                                                        )
                
                response_type = response_col1.selectbox(
                                                        "Select Response Spectrum Type",
                                                        ["Acceleration", "Velocity", "Displacement", "ADRS"],      
                                                        key=10,       
                                                        )
                

                # Window Length
                response_resolution = response_col2.slider(
                                                        "Resolution",
                                                        0.01, 0.1, 0.05 ,0.01,
                                                        help="Response Spectrum resolution to analyze each step" ,          
                                                        key=11,
                                                        )
                    
                # Number of overlap
                response_damping = response_col3.slider(
                                                        "Damping Ratio",
                                                        0.01, 0.25, 0.05, 0.01, 
                                                        help="Damping Ratio",
                                                        key=12,     
                                                        )
                
                # Design Spectrum Column
                
                design_code = response_dcol1.selectbox(
                                                        "Select Design Code",
                                                        ["TBEC 2018"],
                                                        #["TBEC 2018", "Eurocode 8", "ASCE 7-22"],      
                                                        key=13,       
                                                        )


                # Filter dataframe for selected channel
                st.session_state["FD_trace_selected"] = st.session_state["FD_selected"].loc[st.session_state["FD_selected"]["tracename"] == response_trace_select] 
                st.session_state["FD_selected_index"] = st.session_state["FD_trace_selected"].index[0]



                # INPUT DATA
                """
                # State Space
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
                """

                periods_limit = 3
                periods_npts = int((1/response_resolution)*periods_limit) + 1
                periods = linspace(0, periods_limit, periods_npts)

                
                unit_str = st.session_state["FD_trace_selected"]["unit"].iloc[0]
                
                response_factor = responseunit(unit_str)
                data = st.session_state["FD_trace_selected"][st.session_state["selected_export_prop"]].iloc[0] / response_factor
                dt = st.session_state["FD_trace_selected"]["delta"].iloc[0]

                spectral_acc, spectral_vel, spectral_disp = pseudoResponseSpectra(data, dt, periods, response_damping)

                fig_response_spectrum = go.Figure()

                ############################################
                ### Design Spectrum Figure        
                ############################################   
                if design_code=="TBEC 2018":
                    design_vs30 = response_dcol1.number_input(
                                                            "Vs30 Value",
                                                            value= 700,
                                                            step= 10,
                                                            min_value= 100,
                                                            max_value= 2000,
                                                            help="Vs30" ,          
                                                            key=14,
                                                            )

                    design_lon = response_dcol2.number_input(
                                                            "Longitude",
                                                            value=38.0,
                                                            step=0.1,
                                                            min_value=26.0,
                                                            max_value=45.0,
                                                            help="Longitude" ,          
                                                            key=15,
                                                            )
                    
                    design_lat = response_dcol2.number_input(
                                                            "Latitude",
                                                            value=40.0,
                                                            step=0.1,
                                                            min_value=35.0,
                                                            max_value=43.0,
                                                            help="Latitude" ,          
                                                            key=16,
                                                            )



                    
                    design_calculate = response_dcol1.button("Calculate")

                    if design_calculate:
                    
                        response_dcol1.success("Calculated")
                        sds_dd1, sd1_dd1, _ = getAccCoeff(design_lat, design_lon, design_vs30, "dd1")
                        sds_dd2, sd1_dd2, soiltype = getAccCoeff(design_lat, design_lon, design_vs30,  "dd2")

                        # Creating a dictionary with the data
                        data_ds = {
                                    'Sds DD1': [sds_dd1],
                                    'Sd1 DD1': [sd1_dd1],
                                    'Sds DD2': [sds_dd2],
                                    'Sd1 DD2': [sd1_dd2],
                                    'Soil Type': [soiltype]
                                }
                        # Creating the DataFrame
                        df_ds = pd.DataFrame(data_ds).T
                        df_ds.columns = ['Parameters                              ']
                        response_dcol1.dataframe(df_ds, use_container_width=True)
                        
                        #response_dcol1.write(f"Sds_dd1: {sds_dd1}")
                        #response_dcol1.write(f"Sd1_dd1: {sd1_dd1}")
                        #response_dcol1.write(f"Sds_dd2: {sds_dd2}")
                        #response_dcol1.write(f"Sd1_dd2: {sd1_dd2}")
                        #response_dcol1.write(f"Soil type: {soiltype}")

                        design_dd1 = horizontalAccDesignSpectrum(sds_dd1, sd1_dd1, periods)
                        design_dd2 = horizontalAccDesignSpectrum(sds_dd2, sd1_dd2, periods)

                        """
                        import folium
                        from folium.plugins import Draw
                        from streamlit_folium import st_folium

                        m = folium.Map(location=[39.0, 41.0], zoom_start=6)
                        #Draw(export=True).add_to(m)

                        with response_maincol2:

                            folium.Marker(
                                    location=[design_lon, design_lat],
                                    popup=folium.Popup(f"Longitude:{design_lon}\n \
                                                        Latitude:{design_lat}\n  \
                                                        Sds_dd1: {sds_dd1}\n \
                                                        Sd1_dd1: {sd1_dd1}\n \
                                                        Sds_dd2: {sds_dd2}\n \
                                                        Sd1_dd2: {sd1_dd2}\n \
                                                        Soil type: {soiltype}\n \
                                                        ", 
                                                        parse_html=False),
                                    tooltip="Location",
                                    ).add_to(m)
                                             
                        output = st_folium(m, width=500, height=500)
                        """

                        linename = str("DD1")
                        fig_response_spectrum.add_trace(go.Scatter(
                                                                    x= periods,
                                                                    y = design_dd1,
                                                                    #line=dict(color="#C20D0D"),
                                                                    line={'dash': 'dash',  'color': '#C20D0D'},
                                                                    mode="lines",
                                                                    line_width=3,
                                                                    name= linename,
                                                                    ))

                        linename = str("DD2")
                        fig_response_spectrum.add_trace(go.Scatter(
                                                                    x= periods,
                                                                    y = design_dd2,
                                                                    #line=dict(color="#FA8A03"),
                                                                    line={'dash': 'dash',  'color': '#FA8A03'},
                                                                    mode="lines",
                                                                    line_width=3,
                                                                    name= linename,
                                                                    ))
                        
                        #fig_response_spectrum.update_traces(patch={"line": {"width": 4, "dash": "dot"}}, selector={"legendgroup": "DD1"}) 


                
                    elif design_code=="Eurocode 8":
                        response_dcol1.warning("In progress...")


                    elif design_code=="ASCE 7-22":
                        response_dcol1.warning("In progress...")

                ############################################
                ### Acceleration Response Spectrum Figure        
                ############################################
                if response_type == "Acceleration":


                    linename = str(st.session_state["FD_trace_selected"]["filename"].iloc[0]) + str(" ") + str(st.session_state["FD_trace_selected"]["tracename"].iloc[0])
                    
                    fig_response_spectrum.add_trace(go.Scatter(
                                                                #x= response_Tl, 
                                                                #y= response_Al,
                                                                x= periods,
                                                                y = spectral_acc,
                                                                line=dict(color="#1f77b4"),
                                                                mode="lines",
                                                                line_width=3,
                                                                name= linename,
                                                                ))
                    
                    # Plot objects
                    fig_response_spectrum.update_layout(title_text= "<b>Acceleration Response Spectrum<b>", legend_title_text = "File name - Trace", legend=dict(x=0.01, y=0.01))           # title_text= "Time Series",
                    fig_response_spectrum.update_xaxes(title_text="Period (s)")
                    fig_response_spectrum.update_yaxes(title_text=f"SA (g)")
                    fig_response_spectrum.update_layout(xaxis_type= "linear", yaxis_type= "linear")

                    fig_response_spectrum.update_layout(height= 600)

                    response_fig_cont.plotly_chart(fig_response_spectrum, theme="streamlit", use_container_width=True, height=600)

                    

                    

                ############################################
                ### Velocity Response Spectrum Figure        
                ############################################
                elif response_type == "Velocity":

                    fig_response_spectrum = go.Figure()

                    linename = str(st.session_state["FD_trace_selected"]["filename"].iloc[0]) + str(" ") + str(st.session_state["FD_trace_selected"]["tracename"].iloc[0])
                    
                    fig_response_spectrum.add_trace(go.Scatter(
                                                                #x= response_Tl, 
                                                                #y= response_Al,
                                                                x= periods,
                                                                y = spectral_vel,
                                                                line=dict(color="#1f77b4"),
                                                                mode="lines",
                                                                line_width=3,
                                                                name= linename,
                                                                ))
                    
                    # Plot objects
                    fig_response_spectrum.update_layout(title_text= "<b>Velocity Response Spectrum<b>", legend_title_text = "File name - Trace", legend=dict(x=0.01, y=0.01))           # title_text= "Time Series",
                    fig_response_spectrum.update_xaxes(title_text="Period (s)")
                    fig_response_spectrum.update_yaxes(title_text=f"SV (m/s)")
                    fig_response_spectrum.update_layout(xaxis_type= "linear", yaxis_type= "linear")

                    fig_response_spectrum.update_layout(height= 600)

                    response_fig_cont.plotly_chart(fig_response_spectrum, theme="streamlit", use_container_width=True, height=600)
                    
                ############################################
                ### Displacement Response Spectrum Figure        
                ############################################
                elif response_type == "Displacement":

                    fig_response_spectrum = go.Figure()

                    linename = str(st.session_state["FD_trace_selected"]["filename"].iloc[0]) + str(" ") + str(st.session_state["FD_trace_selected"]["tracename"].iloc[0])
                    
                    fig_response_spectrum.add_trace(go.Scatter(
                                                                #x= response_Tl, 
                                                                #y= response_Al,
                                                                x= periods,
                                                                y = spectral_disp,
                                                                line=dict(color="#1f77b4"),
                                                                mode="lines",
                                                                line_width=3,
                                                                name= linename,
                                                                ))
                    
                    # Plot objects
                    fig_response_spectrum.update_layout(title_text= "<b>Displacement Response Spectrum<b>", legend_title_text = "File name - Trace", legend=dict(x=0.01, y=0.01))           # title_text= "Time Series",
                    fig_response_spectrum.update_xaxes(title_text="Period (s)")
                    fig_response_spectrum.update_yaxes(title_text=f"SD (cm)")
                    fig_response_spectrum.update_layout(xaxis_type= "linear", yaxis_type= "linear")

                    fig_response_spectrum.update_layout(height= 600)

                    response_fig_cont.plotly_chart(fig_response_spectrum, theme="streamlit", use_container_width=True, height=600)
                    
                ############################################
                ### ADRS Figure        
                ############################################
                elif response_type == "ADRS":

                    fig_response_spectrum = go.Figure()

                    linename = str(st.session_state["FD_trace_selected"]["filename"].iloc[0]) + str(" ") + str(st.session_state["FD_trace_selected"]["tracename"].iloc[0])
                    
                    fig_response_spectrum.add_trace(go.Scatter(
                                                                #x= response_Tl, 
                                                                #y= response_Al,
                                                                x= spectral_disp,
                                                                y = spectral_acc,
                                                                line=dict(color="#1f77b4"),
                                                                mode="lines",
                                                                line_width=3,
                                                                name= linename,
                                                                ))
                    
                    # Plot objects
                    fig_response_spectrum.update_layout(title_text= "<b>Acceleration/Displacement Response Spectrum<b>", legend_title_text = "File name - Trace", legend=dict(x=0.01, y=0.01))           # title_text= "Time Series",
                    fig_response_spectrum.update_xaxes(title_text="SD (cm)")
                    fig_response_spectrum.update_yaxes(title_text=f"SA (g)")
                    fig_response_spectrum.update_layout(xaxis_type= "linear", yaxis_type= "linear")

                    fig_response_spectrum.update_layout(height= 600)

                    response_fig_cont.plotly_chart(fig_response_spectrum, theme="streamlit", use_container_width=True, height=600)


            
            with responseTS_tab:
                center_running()


                # Select Channel
                responseTS_trace_select = responseTS_col1.selectbox(
                                                        "Select Channel/Trace",
                                                        st.session_state["FD_selected"]["tracename"],      
                                                        key=17,       
                                                        )
                
                responseTS_type = responseTS_col1.selectbox(
                                                        "Select Type of Response Time Series",
                                                        ["Acceleration", "Velocity", "Displacement"],      
                                                        key=18,       
                                                        )
                

                # Period
                responseTS_period = responseTS_col2.number_input(
                                                        "Period (s)",
                                                        value=0.5,
                                                        step=0.1,
                                                        min_value=0.1,
                                                        max_value=10.0,
                                                        help="The period of SDOF oscillator" ,          
                                                        key=19,
                                                        )
                    
                # Damping Ratio
                responseTS_damping = responseTS_col3.slider(
                                                        "Damping Ratio",
                                                        0.01, 0.25, 0.05, 0.01, 
                                                        help="Damping Ratio",
                                                        key=20,     
                                                        )
                
                
                # Filter dataframe for selected channel
                st.session_state["FD_trace_selected"] = st.session_state["FD_selected"].loc[st.session_state["FD_selected"]["tracename"] == responseTS_trace_select] 
                st.session_state["FD_selected_index"] = st.session_state["FD_trace_selected"].index[0]

                
                unit_str = st.session_state["FD_trace_selected"]["unit"].iloc[0]
                response_factor = responseunit(unit_str)
                data = st.session_state["FD_trace_selected"][st.session_state["selected_export_prop"]].iloc[0] / response_factor
                timedomain = st.session_state["FD_trace_selected"][st.session_state["export_time_domain"]].iloc[0]
                timedomain = timedomain.astype("float64")
                dt = st.session_state["FD_trace_selected"]["delta"].iloc[0]

                response_acc, response_vel, response_disp = responseTimeSeries(data, dt, [responseTS_period], responseTS_damping)
        

                ############################################
                ### Acceleration Response Time Series Figure        
                ############################################
                if responseTS_type == "Acceleration":

                    fig_responseTS_spectrum = go.Figure()

                    linename = str(st.session_state["FD_trace_selected"]["filename"].iloc[0]) + str(" ") + str(st.session_state["FD_trace_selected"]["tracename"].iloc[0])
                    
                    fig_responseTS_spectrum.add_trace(go.Scatter(
                                                                x= timedomain,
                                                                y = response_acc,
                                                                line=dict(color="#1f77b4"),
                                                                mode="lines",
                                                                line_width=1,
                                                                name= linename,
                                                                ))
                    
                    # Plot objects
                    fig_responseTS_spectrum.update_layout(title_text= f"<b>Acceleration Response Time Series - Period: {round(responseTS_period,3)}s<b>", legend_title_text = "File name - Trace", legend=dict(x=0.01, y=0.01))           # title_text= "Time Series",
                    fig_responseTS_spectrum.update_xaxes(title_text="Time (s)")
                    fig_responseTS_spectrum.update_yaxes(title_text=f"Response Acceleration (g)")
                    fig_responseTS_spectrum.update_layout(xaxis_type= "linear", yaxis_type= "linear")

                    fig_responseTS_spectrum.update_layout(height= 600)

                    responseTS_fig_cont.plotly_chart(fig_responseTS_spectrum, theme="streamlit", use_container_width=True, height=600)
                

                ############################################
                ### Velocity Response Time Series Figure        
                ############################################
                elif responseTS_type == "Velocity":

                    fig_responseTS_spectrum = go.Figure()

                    linename = str(st.session_state["FD_trace_selected"]["filename"].iloc[0]) + str(" ") + str(st.session_state["FD_trace_selected"]["tracename"].iloc[0])
                    
                    fig_responseTS_spectrum.add_trace(go.Scatter(
                                                                x= timedomain,
                                                                y = response_vel,
                                                                line=dict(color="#1f77b4"),
                                                                mode="lines",
                                                                line_width=1,
                                                                name= linename,
                                                                ))
                    
                    # Plot objects
                    fig_responseTS_spectrum.update_layout(title_text= f"<b>Velocity Response Time Series - Period: {round(responseTS_period,3)}s<b>", legend_title_text = "File name - Trace", legend=dict(x=0.01, y=0.01))           # title_text= "Time Series",
                    fig_responseTS_spectrum.update_xaxes(title_text="Time (s)")
                    fig_responseTS_spectrum.update_yaxes(title_text=f"Response Velocity (m/s)")
                    fig_responseTS_spectrum.update_layout(xaxis_type= "linear", yaxis_type= "linear")

                    fig_responseTS_spectrum.update_layout(height= 600)

                    responseTS_fig_cont.plotly_chart(fig_responseTS_spectrum, theme="streamlit", use_container_width=True, height=600)


                ############################################
                ### Displacement Response Time Series Figure        
                ############################################
                elif responseTS_type == "Displacement":

                    fig_responseTS_spectrum = go.Figure()

                    linename = str(st.session_state["FD_trace_selected"]["filename"].iloc[0]) + str(" ") + str(st.session_state["FD_trace_selected"]["tracename"].iloc[0])
                    
                    fig_responseTS_spectrum.add_trace(go.Scatter(
                                                                x= timedomain,
                                                                y = response_disp,
                                                                line=dict(color="#1f77b4"),
                                                                mode="lines",
                                                                line_width=1,
                                                                name= linename,
                                                                ))
                    
                    # Plot objects
                    fig_responseTS_spectrum.update_layout(title_text= f"<b>Displacement Response Time Series - Period: {round(responseTS_period,3)}s<b>", legend_title_text = "File name - Trace", legend=dict(x=0.01, y=0.01))           # title_text= "Time Series",
                    fig_responseTS_spectrum.update_xaxes(title_text="Time (s)")
                    fig_responseTS_spectrum.update_yaxes(title_text=f"Response Displacement (cm)")
                    fig_responseTS_spectrum.update_layout(xaxis_type= "linear", yaxis_type= "linear")

                    fig_responseTS_spectrum.update_layout(height= 600)

                    responseTS_fig_cont.plotly_chart(fig_responseTS_spectrum, theme="streamlit", use_container_width=True, height=600)
                


            with FDparam_tab:
                center_running()
                FDparam_col1.write("In Progress...")


if __name__ == "__main__":
    frequencyDomainAnalysis()
