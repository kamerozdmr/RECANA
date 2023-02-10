import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_extras.customize_running import center_running

import plotly.graph_objects as go
import pandas as pd


def earthquakeAnalysis():

    # Page Main Title 
    colored_header(
                    label="Earthquake Analysis",
                    description="Rapid evaluation of earthquake data.",
                    color_name="violet-70",
                )

    # Containers
    # Description
    eq_description_cont = st.container()
    eq_description_cont.markdown("Analyze the characteristics of the earthquake data with response spectrum, arias intensity and more. Import miniSEED file to start.")

    eq_dataselect_cont = st.container()


    colored_header(
                    label="Methods",
                    description="Choose a method, select properties and plot.",
                    color_name="violet-70",
                )
    eq_methods_cont = st.container()
    
    
    # If no file imported raise error messega
    if "stream_df" not in st.session_state:
        st.error("___Import file to continue.___", icon="🚨")
    
    else:
        # EQ Data select
        eq_dataselect_col1, eq_dataselect_col2, _ = eq_dataselect_cont.columns([2,2,6])
        
        eq_data_select = eq_dataselect_col1.selectbox(
                                                        "Select Data",
                                                        ("Raw", "Calibrated", "Trimmed", "Detrended", "Filtered"), 
                                                        help= "Select data to be analyzed. Next steps will continue with this time series.",
                                                        )

        st.table(st.session_state["stream_df"][["calibrationstatus","trimstatus","detrendstatus","filterstatus"]])

        if eq_data_select == "Filtered":
            st.session_state["export_data_select"] = "filtereddata"

            if st.session_state["filter_data_select"] == "trimmeddata":
                st.session_state["export_time_domain"] = "trimmedtimesec"
            else: 
                st.session_state["export_time_domain"] = "timesec"


        elif eq_data_select == "Detrended":
            st.session_state["export_data_select"] = "detrendeddata"

            if st.session_state["filter_data_select"] == "trimmeddata":
                st.session_state["export_time_domain"] = "trimmedtimesec"
            else: 
                st.session_state["export_time_domain"] = "timesec"

        elif eq_data_select == "Calibrated":
            st.session_state["export_data_select"] = "calibrateddata"
            st.session_state["export_time_domain"] = "timesec"

        elif eq_data_select == "Trimmed":
            st.session_state["export_data_select"] = "trimmeddata"
            st.session_state["export_time_domain"] = "trimmedtimesec"


        ####################
        # Data availability
        ####################
        # Check calibrated data availability
        if st.session_state["export_data_select"] == "calibrateddata" and st.session_state["stream_df"]["calibrationstatus"].iloc[export_index_ava] == "Not Set":
            eq_dataselect_col2.error("Calibrated data is not avaliable", icon="🚨")

        # Check trimmed data availability
        elif st.session_state["export_data_select"] == "trimmeddata" and st.session_state["stream_df"]["trimstatus"].iloc[export_index_ava] == "Not Set":
            eq_dataselect_col2.error("Trimmed data is not avaliable", icon="🚨")

        # Check detrended data availability
        elif st.session_state["export_data_select"] == "detrendeddata" and st.session_state["stream_df"]["detrendstatus"].iloc[export_index_ava] == "Not Set":
            eq_dataselect_col2.error("Detrended data is not avaliable", icon="🚨")

        # Check filtered data availability
        elif st.session_state["export_data_select"] == "filtereddata" and st.session_state["stream_df"]["filterstatus"].iloc[export_index_ava] == "Not Set":
            eq_dataselect_col2.error("Filtered data is not avaliable", icon="🚨")  

        else:

            # Columns
            methods_prop_col, methods_plot_col = eq_methods_cont.columns([1, 2])

            response_tab, arias_tab = methods_prop_col.tabs(["Response Spectrum", "Arias Intensity"])

            


if __name__ == "__main__":
    earthquakeAnalysis()
