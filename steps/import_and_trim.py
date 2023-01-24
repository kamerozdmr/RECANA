import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_extras.customize_running import center_running

import numpy as np
import plotly.graph_objects as go
import pandas as pd

def importandTrim():
    from classes.recordClass import Record
    
    # Headers and containers
    # Page Main Title 
    colored_header(
                    label="Import and Trim",
                    description="Select a file to analyze.",
                    color_name="blue-70",
                )
    import_container = st.container()


    colored_header(
                    label="Set Properties",
                    description="Set calibration factor and acceleration unit for the selected file.",
                    color_name="blue-70",
                )
    import_properties = st.container()


    colored_header(
                    label="Trim",
                    description="Select a range to trim.",
                    color_name="blue-70",
                )
    trim_options = st.container()
    

    colored_header(
                    label="Plot Time Series",
                    description="Select data type and plot time series.",
                    color_name="blue-70",
                )
    import_plot_container = st.container()


    #if "uploaded_files" not in st.session_state:
    #    st.session_state["uploaded_files"] = None

    # Divide into 2 columns
    ######################
    read_rec_col, info_col = import_container.columns([2, 3])

    # Import file
    files = read_rec_col.file_uploader("Import acceleration data", accept_multiple_files=True, type=["mseed", "gcf"])
    
    ######################
    # Calibration section   
    # Apply calibration factor
    calib_col1, calib_col2, calib_col3, calib_col4 = import_properties.columns([3, 2, 2, 2])
    
    ######################
    # Trim option section 
    trim_col1, trim_col2 = trim_options.columns([7,2])

    ######################
    # Create figure


    # Plot button
    # PLot option columns
    plot_col1, plot_col2, plot_col3 = import_plot_container.columns([2,2,4])

    st.session_state["plot_select"] = plot_col1.selectbox("Select Data",
                                        ("Raw", "Calibrated", "Trimmed"), 
                                        help= "Select data type.",
                                        )
    
    # Enable plot button when the record read
    if "plot_but" not in st.session_state:
        st.session_state.disabled = True

    # Enable trim button when calibrated
    if "trim_but" not in st.session_state:
        st.session_state.disabled_trim = True


    plot_button = plot_col2.button("Plot Time Series", key="plot_but", disabled=st.session_state.disabled)
    #st.session_state.disabled = True
    fig_ts = go.Figure()


    

    if not files:
        pass
    else:           #len(files) != 0:
        st.session_state["uploaded_files"] = files


    if "uploaded_files" not in st.session_state:
        read_rec_col.warning("___Currently supported file formats : .mseed, .gcf___", icon="⚠️")

    else:
        
        st.session_state.disabled = False
        
        # Read record button
        read_record_button = read_rec_col.button("Read Records", help="Read imported files.")

        
        # Create expander
        expander_record_properties = info_col.expander("See record properties.")


        if read_record_button:
            center_running()
            if not files:
                read_rec_col.error("___File not found to import.___", icon="🚨")

            else:
                concat_class = []

                for ind in range(len(files)):
                    file_name, file_format = files[ind].name.split(".")
                    
                    # Create Record instance   
                    record = Record(files[ind], file_name, file_format)

                    # Run funtion that imports record file 
                    record.importFile()

                    # List of stream instances that are going to be concatenated
                    concat_class.append(record.stream_df)

                    
                # Concatenate stream instances
                record.stream_df = pd.concat(concat_class).reset_index()

                # Store values in a session state
                st.session_state["stream_df"] = record.stream_df

                # Expander
                expander_df = record.stream_df[["filename", "fileformat", "tracename", "npts", "delta", "starttime", "endtime"]]
                expander_record_properties.dataframe(expander_df)

                # Plot 
                for _, row in st.session_state["stream_df"].iterrows():
                    linename = str(row["filename"]) + str(" ") + str(row["tracename"])
                    fig_ts.add_trace(go.Scatter(x=row["timesec"], y=row["rawdata"],
                                    mode="lines",
                                    name= linename,
                                    ))


        if "stream_df" not in st.session_state:
            read_rec_col.warning("___Files could not be read.___", icon="⚠️")
            

        else:
            read_rec_col.success("___Ready___", icon="✔️")
            
            # Select record to calibrate
            record_select = calib_col1.selectbox(
            "Select file",
            st.session_state["stream_df"]["filename"].unique(), 
            help= "Set selected file's parameters.")

            calib_col1.caption(f"_{record_select}_")

            st.session_state["selected_prop"] = st.session_state["stream_df"]["filename"].str.contains(record_select, regex=True)
            

            # Apply Calibration factor
            calib_factor = calib_col2.number_input("Calibration factor.", help= "Factor to divide raw values for to convert chosen unit.", value=1)
            calib_col2.caption(f"_Input box {calib_factor}_")


            # Select unit
            select_unit = calib_col3.selectbox("Select unit.", ("g", "mg", "ug", "m/s2", "cm/s2"), help="Chosen unit of acceleration.")
            calib_col3.caption(f"_Unit is {select_unit}_")


            # Apply button
            apply_calib_button = calib_col4.button("Set Properties")

            # When pressed execute
            if apply_calib_button:
                center_running()
                st.session_state.disabled_trim = False
                for index, value in st.session_state["selected_prop"].items():
                    if value == True:
                        
                        # arr = np.array(st.session_state["stream_df"]["rawdata"].iloc[[index]])  / calib_factor
                        handler = st.session_state["stream_df"]
                        del st.session_state["stream_df"]

                        handler["calibrateddata"].iloc[[index]] = handler["rawdata"].iloc[[index]] / calib_factor
                        #handler["trimmeddata"].iloc[[index]] = handler["calibrateddata"].iloc[[index]]
                        st.session_state["stream_df"] = handler
                        
                        #calib_col4.write(st.session_state["stream_df"]["calibrateddata"].iloc[[index]])

                        # Set calibration state
                        st.session_state["stream_df"]["calibrationstatus"].iloc[index] = "Set"
                        


                st.session_state["stream_df"]["unit"] = select_unit

                calib_col4.success("___Done___", icon="✔️")


            # Trim range select
            for index, value in st.session_state["selected_prop"].items():
                if value == True:
                    duration = int(st.session_state["stream_df"]["npts"].iloc[[index]] * st.session_state["stream_df"]["delta"].iloc[[index]])

            trim_range = trim_col1.slider("Select trimming range in seconds", 0, duration, (0, duration))

            # Trim button
            trim_button = trim_col2.button("Trim Record", key="trim_but", disabled=st.session_state.disabled_trim)

            if trim_button:
                center_running()
                for index, value in st.session_state["selected_prop"].items():      #.items
                    if value == True:
                        
                        rl, rh = trim_range
                        duration_trimmed = int(rh - rl)
                        sps = int(1 / st.session_state["stream_df"]["delta"].iloc[[index]])

                        #deneme = st.session_state["stream_df"]["calibrateddata"].iloc[index].truncate(before=int(rl*sps), after=int(rh*sps-1))
                        #st.session_state["stream_df"]["trimmeddata"].iloc[index] = pd.Series(deneme)

                        # Trim acceleration data
                        st.session_state["stream_df"]["trimmeddata"].iloc[index] = pd.Series(st.session_state["stream_df"]["calibrateddata"].iloc[index].truncate(before=int(rl*sps), after=int(rh*sps-1)))

                        # Trim time domain
                        st.session_state["stream_df"]["trimmedtimesec"].iloc[index] = pd.Series(st.session_state["stream_df"]["timesec"].iloc[index][0 : int(rh*sps - rl*sps)])

                        #trim_col2.text(st.session_state["stream_df"]["trimmeddata"].iloc[index])
                        #trim_col2.text((st.session_state["stream_df"]["trimmedtimesec"].iloc[index]))


                        # Set calibration state
                        st.session_state["stream_df"]["trimstatus"].iloc[index] = "Set"

                trim_col2.success("___Done___", icon="✔️")



            # Plot selected data
            if plot_button:
                center_running()
                # Selected data type selectbox
                selected_plot = st.session_state["plot_select"] 

                if selected_plot == "Raw":
                    # Plot 
                    for _, row in st.session_state["stream_df"].iterrows():
                        linename = str(row["filename"]) + str(" ") + str(row["tracename"])
                        fig_ts.add_trace(go.Scatter(x=row["timesec"], y=row["rawdata"],
                                        mode="lines",
                                        name= linename,
                                        ))
                
                if selected_plot == "Calibrated":
                    if st.session_state["stream_df"]["calibrationstatus"].iloc[0] == "Set":          #st.session_state["calibrate_state"] == True:
                        # Plot 
                        for _, row in st.session_state["stream_df"].iterrows():
                            linename = str(row["filename"]) + str(" ") + str(row["tracename"])
                            fig_ts.add_trace(go.Scatter(x=row["timesec"], y=row["calibrateddata"],
                                            mode="lines",
                                            name= linename,
                                            ))
                    else:
                        plot_col3.warning("___Data not calibrated.___", icon="⚠️")

                if selected_plot == "Trimmed":
                    if st.session_state["stream_df"]["trimstatus"].iloc[0] == "Set":                 #st.session_state["trim_state"] == True:
                        # Plot 
                        for _, row in st.session_state["stream_df"].iterrows():
                            linename = str(row["filename"]) + str(" ") + str(row["tracename"])
                            fig_ts.add_trace(go.Scatter(x=row["trimmedtimesec"], y=row["trimmeddata"],
                                            mode="lines",
                                            name= linename,
                                            ))
                    else:
                        plot_col3.warning("___Data not trimmed.___", icon="⚠️")


                unit = st.session_state["stream_df"]["unit"]
                fig_ts.update_yaxes(title_text=f"Acceleration ({str(unit[0])})")

            
                



    # Plot objects
    fig_ts.update_layout(legend_title_text = "File name - Trace", legend=dict(x=0.01, y=0.01), height=600)           # title_text= "Time Series",
    fig_ts.update_xaxes(title_text="Time (s)")
    #fig_ts.update_yaxes(title_text=f"Acceleration")

    import_plot_container.plotly_chart(fig_ts, theme="streamlit", use_container_width=True, height=600)





if __name__ == "__main__":
    importandTrim()
