import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_extras.customize_running import center_running

import plotly.graph_objects as go
import pandas as pd
import io

from functions.baseFunctions import butterworthKernel, iirFilter, iirResponse, detrendFunction, exportCsv, exportExcel
from functions.plotFunctions import kernelPlot


def filterandExport():
    
    # Page Main Title 
    colored_header(
                    label="Filter and Export",
                    description="Select a file and data type to filter and export.",
                    color_name="orange-70",
                )
    
    # Containers
    select_data_cont = st.container()


    colored_header(
                    label="Detrend",
                    description="Remove a trend from the data. Pass this section if not needed.",
                    color_name="orange-70",
                )
    detrend_cont = st.container()


    colored_header(
                    label="Filter",
                    description="Create a filter kernel and apply filter to time series.",
                    color_name="orange-70",
                )
    filter_properties_cont = st.container()


    filter_kernel_plot_cont = st.container()
    filter_plot_cont = st.container()


    colored_header(
                    label="Export",
                    description="Export time series.",
                    color_name="orange-70",
                )   
    export_cont = st.container()

    # If no file imported raise error messega
    if "stream_df" not in st.session_state:
        st.error("___Import file to continue.___", icon="🚨")
        #st.stop()

    else:
        # Select data column
        select_data_col1, select_data_col2, select_data_col3, select_data_col4 = select_data_cont.columns([2,2,3,5])

        # Select record to filter
        st.session_state["filter_record_select"] = select_data_col1.selectbox(
                                                                            "Select file",
                                                                            st.session_state["stream_df"]["filename"].unique(), 
                                                                            help= "Select imported file to filter.",
                                                                            )

        st.session_state["selected_prop"]  = st.session_state["stream_df"]["filename"].str.contains(st.session_state["filter_record_select"], regex=True)
        

        filter_data_select = select_data_col2.selectbox(
                                                        "Select Data",
                                                        ("Raw", "Calibrated", "Trimmed"), 
                                                        help= "Select data to be filtered. Next steps will continue with this time series.",
                                                        )
        
        if filter_data_select == "Raw":
            st.session_state["filter_data_select"] = "rawdata"
            st.session_state["time_domain"] = "timesec"

        elif filter_data_select == "Calibrated":
            st.session_state["filter_data_select"] = "calibrateddata"
            st.session_state["time_domain"] = "timesec"

        elif filter_data_select == "Trimmed":
            st.session_state["filter_data_select"] = "trimmeddata"
            st.session_state["time_domain"] = "trimmedtimesec"


        # Index to check availability -get index from first trace
        index_ava = st.session_state["selected_prop"][st.session_state["selected_prop"]==True].index[0]
    


        # Check calibrated data availability
        if st.session_state["filter_data_select"] == "calibrateddata" and st.session_state["stream_df"]["calibrationstatus"].iloc[index_ava] == "Not Set":
            select_data_col3.error("Calibrated data is not avaliable", icon="🚨")

        # Check trimmed data availability
        elif st.session_state["filter_data_select"] == "trimmeddata" and st.session_state["stream_df"]["trimstatus"].iloc[index_ava] == "Not Set":
            select_data_col3.error("Trimmed data is not avaliable", icon="🚨")

        else:
            #########################
            # Detrending column
            #########################
            detrend_col1, detrend_col2, detrend_col3 = detrend_cont.columns([2,2,8])

            fig_detrend = go.Figure()
            

            # Select detrending method
            st.session_state["detrend_method"] = detrend_col1.selectbox("Detrend Method",
                                                                    ("Line (Simple)", "Polynomial"),  
                                                                    help= "Detrend signal by subtracting simple line or polynomial trend.",
                                                                    )
            ##############
            # Line(Simple)
            if st.session_state["detrend_method"] == "Line (Simple)":

                detrend_button = detrend_col2.button("Apply Detrend")

                if detrend_button:
                    center_running()
                    for index, value in st.session_state["selected_prop"].items():
                        if value == True:
                            linename = str(st.session_state["stream_df"]["filename"].iloc[index]) + str(" ") + str(st.session_state["stream_df"]["tracename"].iloc[index])
                            data = st.session_state["stream_df"][st.session_state["filter_data_select"]].iloc[index]
                            
                            st.session_state["stream_df"]["detrendeddata"].iloc[index] = pd.Series(detrendFunction(data, "line", 1))                    
                            
                            fig_detrend.add_trace(go.Scatter(x= st.session_state["stream_df"][st.session_state["time_domain"]].iloc[index], y= st.session_state["stream_df"]["detrendeddata"].iloc[index],
                                                mode="lines",
                                                name= linename,
                                                ))   

                            # Set detrend state
                            st.session_state["stream_df"]["detrendstatus"].iloc[index] = "Set"         
            
            ##############
            # Polynomial
            elif st.session_state["detrend_method"] == "Polynomial":
                
                st.session_state["detrend_order"] = detrend_col2.number_input("Order", 
                                                                    help= "The order of the polynomial to fit.",
                                                                    value= int(2), min_value= int(1), max_value= int(5),
                                                                    )

                detrend_button = detrend_col3.button("Apply Detrend")
                
                if detrend_button:
                    center_running()
                    for index, value in st.session_state["selected_prop"].items():
                        if value == True:

                            data = st.session_state["stream_df"][st.session_state["filter_data_select"]].iloc[index]

                            st.session_state["stream_df"]["detrendeddata"].iloc[index] = pd.Series(detrendFunction(data, "polynomial", int(st.session_state["detrend_order"])))              #(data, method, ord)    
                            linename = str(st.session_state["stream_df"]["filename"].iloc[index]) + str(" ") + str(st.session_state["stream_df"]["tracename"].iloc[index])
                            fig_detrend.add_trace(go.Scatter(x= st.session_state["stream_df"][st.session_state["time_domain"]].iloc[index], y=st.session_state["stream_df"]["detrendeddata"].iloc[index],
                                                mode="lines",
                                                name= linename,
                                                ))

                            # Set detrend state
                            st.session_state["stream_df"]["detrendstatus"].iloc[index] = "Set"


            # Plot objects
            fig_detrend.update_layout(legend_title_text = "File name - Trace", legend=dict(x=0.01, y=0.01))           # title_text= "Time Series",
            fig_detrend.update_xaxes(title_text="Time (s)")
            #fig_ts.update_yaxes(title_text=f"Acceleration")

            detrend_cont.plotly_chart(fig_detrend, theme="streamlit", use_container_width=True, height=240)



            #########################
            # Filter properties column
            #########################
            
            filter_col1, filter_col2, filter_col3, filter_col4, filter_col5, filter_col6 = filter_properties_cont.columns([1,1,1,1,1,1])

            st.session_state["filter_type_select"] = filter_col1.selectbox("Filter Type",
                                                ("IIR", "FIR"))

            # Filter figure
            st.session_state["add_unfiltered_check"] = filter_plot_cont.checkbox("Add unfiltered data.")
            fig_filter = go.Figure()

            # FIR Filter process
            if st.session_state["filter_type_select"] == "FIR":
                filter_col2.warning("___FIR filter type is not available.___", icon="⚠️")



            # IIR Filter process
            elif st.session_state["filter_type_select"] == "IIR":

                # Select IIR filter type
                iirfiltertype = filter_col2.selectbox("IIR Filter Type",
                                                                    ("Band-pass", "High-pass", "Low-pass"),  
                                                                    help= "Select Butterworth filter type.",
                                                                    )

                if iirfiltertype == "Band-pass":
                    st.session_state["iir_type"] = "bandpass"

                elif iirfiltertype == "High-pass":
                    st.session_state["iir_type"] = "highpass"

                elif iirfiltertype == "Low-pass":
                    st.session_state["iir_type"] = "lowpass"

                    
                
                
                #########################
                if st.session_state["iir_type"] == "bandpass":
                    delta = st.session_state["stream_df"]["delta"].iloc[index_ava]
                    nyquist = float(int(1/delta)/2)

                    # band-pass filter objects
                    highpass_corner = filter_col3.number_input("High-pass Corner", help= "Select High-pass filter corner frequency.", value= float(2.5), min_value= 0.01, max_value= nyquist-0.1)
                    lowpass_corner = filter_col3.number_input("Low-pass Corner", help= "Select Low-pass filter corner frequency.", value= float(25), min_value= highpass_corner+0.1, max_value= nyquist-0.1)
                    st.session_state["filter_order"] = filter_col4.number_input("Order", help= "Select the order of the filter.", value= int(4), min_value= int(1), max_value= int(20))

                    st.session_state["filter_prop"] = [highpass_corner, lowpass_corner]

                    # Run filter kernel functions
                    kernel = iirResponse(st.session_state["iir_type"], st.session_state["filter_prop"], delta, st.session_state["filter_order"])    # fimp, timepoint, fimpX, hz 
                    #filter_col5.write(kernel)

                    # Plot kernel
                    kernelPlot(filter_kernel_plot_cont, kernel, nyquist, st.session_state["filter_prop"], st.session_state["iir_type"])

                    # Select if detrend data is going to used
                    filter_detrend_check = filter_col5.checkbox("Filter Detrended Data", help="Check to use detrended data for filtering.")

                    # Apply filter button
                    filter_button = filter_col6.button("Plot Time Series", help="Apply filter and plot.")




                #########################
                elif st.session_state["iir_type"] == "highpass":
                    delta = st.session_state["stream_df"]["delta"].iloc[index_ava]
                    nyquist = float(int(1/delta)/2)

                    # band-pass filter objects
                    highpass_corner = filter_col3.number_input("High-pass Corner", help= "Select High-pass filter corner frequency.", value= float(2.5), min_value= 0.01, max_value= nyquist-0.1)
                    st.session_state["filter_order"] = filter_col4.number_input("Order", help= "Select the order of the filter.", value= int(4), min_value= int(1), max_value= int(20))

                    st.session_state["filter_prop"] = [highpass_corner]

                    # Run filter kernel functions
                    kernel = iirResponse(st.session_state["iir_type"], st.session_state["filter_prop"], delta, st.session_state["filter_order"])    # fimp, timepoint, fimpX, hz 
                    #filter_col5.write(kernel)

                    # Plot kernel
                    kernelPlot(filter_kernel_plot_cont, kernel, nyquist, st.session_state["filter_prop"], st.session_state["iir_type"])

                    # Select if detrend data is going to used
                    filter_detrend_check = filter_col5.checkbox("Filter Detrended Data", help="Check to use detrended data for filtering.")

                    # Apply filter button
                    filter_button = filter_col6.button("Plot Time Series", help="Apply filter and plot.")


                #########################
                elif st.session_state["iir_type"] == "lowpass":
                    delta = st.session_state["stream_df"]["delta"].iloc[index_ava]
                    nyquist = float(int(1/delta)/2)

                    # band-pass filter objects
                    lowpass_corner = filter_col3.number_input("Low-pass Corner", help= "Select Low-pass filter corner frequency.", value= float(25.0), min_value= 2.0, max_value= nyquist-0.1)
                    st.session_state["filter_order"] = filter_col4.number_input("Order", help= "Select the order of the filter.", value= int(4), min_value= int(1), max_value= int(20))

                    st.session_state["filter_prop"] = [lowpass_corner]

                    # Run filter kernel functions
                    kernel = iirResponse(st.session_state["iir_type"], st.session_state["filter_prop"], delta, st.session_state["filter_order"])    # fimp, timepoint, fimpX, hz 
                    #filter_col5.write(kernel)

                    # Plot kernel
                    kernelPlot(filter_kernel_plot_cont, kernel, nyquist, st.session_state["filter_prop"], st.session_state["iir_type"])

                    # Select if detrend data is going to used
                    filter_detrend_check = filter_col5.checkbox("Filter Detrended Data", help="Check to use detrended data for filtering.")

                    # Apply filter button
                    filter_button = filter_col6.button("Plot Time Series", help="Apply filter and plot.")               
                    
                
                if filter_button:
                    center_running()
                    
                    # Apply filter to detrended data
                    if filter_detrend_check == True:
                        # Detrend data available
                        if st.session_state["stream_df"]["detrendstatus"].iloc[index_ava] == "Set":

                            for index, value in st.session_state["selected_prop"].items():
                                if value == True:

                                    data = st.session_state["stream_df"]["detrendeddata"].iloc[index]       
                                    filtereddata = iirFilter(data, st.session_state["iir_type"], st.session_state["filter_prop"], delta, st.session_state["filter_order"])      # 0-highcut   1-lowcut
                                    
                                    st.session_state["stream_df"]["filtereddata"].iloc[index] = filtereddata

                                    

                                    linename = str(st.session_state["stream_df"]["filename"].iloc[index]) + str(" - ") + str(st.session_state["stream_df"]["tracename"].iloc[index])
                                    fig_filter.add_trace(go.Scatter(x= st.session_state["stream_df"][st.session_state["time_domain"]].iloc[index], y=st.session_state["stream_df"]["filtereddata"].iloc[index],
                                                        mode="lines",
                                                        name= linename + str(" - Filtered"),
                                                        ))

                                    if st.session_state["add_unfiltered_check"] == True:
                                        fig_filter.add_trace(go.Scatter(x= st.session_state["stream_df"][st.session_state["time_domain"]].iloc[index], y=data,
                                                            mode="lines",
                                                            name= linename,
                                                            ))
                    
                                            
                                    # Set detrend state
                                    st.session_state["stream_df"]["filterstatus"].iloc[index] = "Set"


                        # Detrend data is not available
                        else:
                            filter_col6.error("Detrend is not applied to the data.") 

                    # Apply filter to raw calibrated or trimmed data   --- not detrended
                    elif filter_detrend_check == False:

                        for index, value in st.session_state["selected_prop"].items():
                            if value == True:

                                data = st.session_state["stream_df"][st.session_state["filter_data_select"]].iloc[index]
                                filtereddata = iirFilter(data, st.session_state["iir_type"], st.session_state["filter_prop"], delta, st.session_state["filter_order"])      # 0-highcut   1-lowcut
                                    
                                st.session_state["stream_df"]["filtereddata"].iloc[index] = filtereddata

                                    

                                linename = str(st.session_state["stream_df"]["filename"].iloc[index]) + str(" - ") + str(st.session_state["stream_df"]["tracename"].iloc[index])
                                fig_filter.add_trace(go.Scatter(x= st.session_state["stream_df"][st.session_state["time_domain"]].iloc[index], y=st.session_state["stream_df"]["filtereddata"].iloc[index],
                                                        mode="lines",
                                                        name= linename + str(" - Filtered"),
                                                        ))

                                if st.session_state["add_unfiltered_check"] == True:
                                    fig_filter.add_trace(go.Scatter(x= st.session_state["stream_df"][st.session_state["time_domain"]].iloc[index], y=data,
                                                        mode="lines",
                                                        name= linename,
                                                        ))
                    
                                            
                                # Set detrend state
                                st.session_state["stream_df"]["filterstatus"].iloc[index] = "Set"



            

            # Filter Plot objects
            fig_filter.update_layout(title_text= "<b>Filtered Time Series<b>", legend_title_text = "File name - Trace",title_x=0.5, legend=dict(x=0.01, y=0.01), height=600, transition_duration=500)           # title_text= "Time Series",
            fig_filter.update_xaxes(title_text="Time (s)")

            unit = st.session_state["stream_df"]["unit"]
            fig_filter.update_yaxes(title_text=f"Acceleration ({str(unit[index_ava])})")

            filter_plot_cont.plotly_chart(fig_filter, theme="streamlit", use_container_width=True, height=600)


        ##################
        # Export Section    
        ##################

        export_col1, export_col2, export_col3, export_col4, export_col_spacer = export_cont.columns([2,2,1,1, 2])


        # Add button
        # Select record to export
        st.session_state["export_record_select"] = export_col1.selectbox(
                                                                        "Select file",
                                                                        st.session_state["stream_df"]["filename"].unique(), 
                                                                        help= "Select imported file to filter.",
                                                                        key="1"
                                                                        )

        st.session_state["selected_export_prop"]  = st.session_state["stream_df"]["filename"].str.contains(st.session_state["export_record_select"], regex=True)
        
        # Index to check availability -get index from first trace
        export_index_ava = st.session_state["selected_export_prop"][st.session_state["selected_export_prop"]==True].index[0]

        # Select data type to export
        export_data_select = export_col2.selectbox(
                                                    "Select data",
                                                    ("Filtered", "Detrended", "Calibrated", "Trimmed"), 
                                                    help= "Select data to export.",
                                                    )
        
        if export_data_select == "Filtered":
            st.session_state["export_data_select"] = "filtereddata"

            if st.session_state["filter_data_select"] == "trimmeddata":
                st.session_state["export_time_domain"] = "trimmedtimesec"
            else: 
                st.session_state["export_time_domain"] = "timesec"


        elif export_data_select == "Detrended":
            st.session_state["export_data_select"] = "detrendeddata"

            if st.session_state["filter_data_select"] == "trimmeddata":
                st.session_state["export_time_domain"] = "trimmedtimesec"
            else: 
                st.session_state["export_time_domain"] = "timesec"

        elif export_data_select == "Calibrated":
            st.session_state["export_data_select"] = "calibrateddata"
            st.session_state["export_time_domain"] = "timesec"

        elif export_data_select == "Trimmed":
            st.session_state["export_data_select"] = "trimmeddata"
            st.session_state["export_time_domain"] = "trimmedtimesec"


        ####################
        # Data availability
        ####################
        # Check calibrated data availability
        if st.session_state["export_data_select"] == "calibrateddata" and st.session_state["stream_df"]["calibrationstatus"].iloc[export_index_ava] == "Not Set":
            export_col1.error("Calibrated data is not avaliable", icon="🚨")

        # Check trimmed data availability
        elif st.session_state["export_data_select"] == "trimmeddata" and st.session_state["stream_df"]["trimstatus"].iloc[export_index_ava] == "Not Set":
            export_col1.error("Trimmed data is not avaliable", icon="🚨")

        # Check detrended data availability
        elif st.session_state["export_data_select"] == "detrendeddata" and st.session_state["stream_df"]["detrendstatus"].iloc[export_index_ava] == "Not Set":
            export_col1.error("Detrended data is not avaliable", icon="🚨")

        # Check filtered data availability
        elif st.session_state["export_data_select"] == "filtereddata" and st.session_state["stream_df"]["filterstatus"].iloc[export_index_ava] == "Not Set":
            export_col1.error("Filtered data is not avaliable", icon="🚨")  

        else:

            # Select file format 
            export_format_select = export_col3.selectbox(
                                                        "Select file format",
                                                        (".txt", ".csv", ".xlsx"), 
                                                        help= "Select file format.",
                                                        )
            
            # Select delimiter 
            if export_format_select == ".txt" or export_format_select == ".csv":
                
                export_delimiter_select = export_col3.selectbox(
                                                            "Select delimiter",
                                                            ("comma (,)", "colon (:)", "semicolon (;)", "pipe (|)"), 
                                                            help= "Select delimiter between data and time column.",
                                                            )


            ##################
            # Download Button
            if export_format_select == ".xlsx":
                center_running()

                filename = st.session_state["export_record_select"]
                export_col4.download_button(
                                            label= "Export File",
                                            data= exportExcel(st.session_state["stream_df"], st.session_state["selected_export_prop"], st.session_state["export_data_select"], st.session_state["export_time_domain"]),
                                            file_name= f"{filename}_record_analyzer.xlsx",
                                            mime= "application/vnd.ms-excel",
                                            )


            elif export_format_select == ".csv":
                center_running()

                filename = st.session_state["export_record_select"]
                export_col4.download_button(
                                            label= "Export File",   
                                            data= exportCsv(st.session_state["stream_df"], st.session_state["selected_export_prop"], st.session_state["export_data_select"], st.session_state["export_time_domain"], export_delimiter_select),
                                            file_name= f"{filename}_record_analyzer.csv",
                                            mime="text/csv",
                                            )


            elif export_format_select == ".txt":
                center_running()

                filename = st.session_state["export_record_select"]
                export_col4.download_button(
                                            label= "Export File",   
                                            data= exportCsv(st.session_state["stream_df"], st.session_state["selected_export_prop"], st.session_state["export_data_select"], st.session_state["export_time_domain"], export_delimiter_select),
                                            file_name= f"{filename}_record_analyzer.txt",
                                            mime="text/csv",
                                            )


            



if __name__ == "__main__":
    filterandExport()
