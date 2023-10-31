import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_extras.customize_running import center_running
from numpy import argmax, linspace, around, append, full, array

import plotly.graph_objects as go
import pandas as pd


from functions.tdaFunctions import *
from functions.unitcorrection import *
from functions.baseFunctions import exportExcelSingle

def timeDomainAnalysis():
    
    st.info(
                    """___For more detailed information about the app, please visit___
                    [**www.modaltrace.com**](https://modaltrace.com/recana-record-analyzer)\n
                    """
                    )
    
    # Page Main Title 
    colored_header(
                    label="Time Domain Analysis",
                    description="Rapid evaluation of acceleration data in the time domain.",
                    color_name="violet-70",
                )

    # Containers
    # Description
    eq_description_cont = st.container()
    eq_description_cont.markdown("Analyze the characteristics of the acceleration data in the time domain by calculating velocity and displacement time series, Arias Intensity and Cumulative Absolute Velocity.\n\nImport file to start. Select file and data type.")

    eq_dataselect_cont = st.container()


    colored_header(
                    label="Methods",
                    description="Choose a method, select properties and calculate.",
                    color_name="violet-70",
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
        st.session_state["TD_selected"] = st.session_state["stream_df"].loc[st.session_state["stream_df"]['filename'] == st.session_state["export_record_select"]]
                
        

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
            st.session_state["TD_selected"]["unit"] = "Raw"

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
            AVD_tab, arias_tab, CAV_tab, TDparam_tab = eq_methods_cont.tabs(["**Acceleration-Velocity-Displacement**", 
                                                                             "**Arias Intensity**", 
                                                                             "**Cumulative Absolute Velocity**", 
                                                                             "**Parameters**",
                                                                             ])

            AVD_cont = AVD_tab.container()
            AVD_col1, AVD_col2,  AVD_col3, AVD_col4 = AVD_cont.columns([2,2,2,2])
            AVD_fig_cont = AVD_cont.container()
            AVD_data_cont = AVD_cont.container()

            arias_cont = arias_tab.container()
            arias_col1, arias_col2 = arias_cont.columns([2,6])
            arias_fig_cont = arias_cont.container()
            arias_data_cont = arias_cont.container()

            CAV_cont = CAV_tab.container()
            CAV_col1, _ = CAV_cont.columns([2,6])
            CAV_fig_cont = CAV_tab.container()
            CAV_data_cont = CAV_tab.container()

            TDparam_cont = TDparam_tab.container()


            #####################################
            ### Acceleration - Velocity - Displacement Time Series
            ##################################### 
            with AVD_tab:
                center_running()


                # Select Channel
                AVD_trace_select = AVD_col1.selectbox(
                                                        "Select Channel/Trace",
                                                        st.session_state["TD_selected"]["tracename"],                 
                                                        )
                
                # Select Integration Type
                AVD_integration_type = AVD_col2.selectbox(
                                                        "Select Integration Type",
                                                        ["TD Integration", "FD Integration"], 
                                                        help= "Select the integration type between time domain and frequency domain."                
                                                        )     
                
                # Raise exception for FD integration --- method is not ready
                if AVD_integration_type == "FD Integration":
                    AVD_excp = RuntimeError("Frequency domain integration is not available")
                    AVD_fig_cont.exception(AVD_excp)
                    
                    st.stop()


                AVD_bas_cor = AVD_col3.checkbox("Apply baseline correction for each integration.")
                
                AVD_order = None
                if AVD_bas_cor == True:

                    AVD_order = AVD_col4.slider(
                                                "Select order of baseline correction.",
                                                1,5,1,                 
                                                )
                
                
                # Filter dataframe for selected channel
                st.session_state["TD_trace_selected"] = st.session_state["TD_selected"].loc[st.session_state["TD_selected"]["tracename"] == AVD_trace_select] 
                st.session_state["TD_selected_index"] = st.session_state["TD_trace_selected"].index[0]



                #####################################
                ### Acceleration Time Series Figure
                #####################################
                fig_AVD_Acc = go.Figure()

                # Acceleration and time arrays
                acc = st.session_state["TD_trace_selected"][st.session_state["selected_export_prop"]].iloc[0]
                acc = acc.astype("float64")
                timedomain = st.session_state["TD_trace_selected"][st.session_state["export_time_domain"]].iloc[0]
                timedomain = timedomain.astype("float64")

                # Get unit of acceleration
                unit_str = st.session_state["TD_trace_selected"]["unit"].iloc[0]
                
                linename = str(st.session_state["TD_trace_selected"]["filename"].iloc[0]) + str(" ") + str(st.session_state["TD_trace_selected"]["tracename"].iloc[0])
                fig_AVD_Acc.add_trace(go.Scatter(x= timedomain, 
                                                 y= acc,
                                                line=dict(color="#1f77b4"),
                                                mode="lines",
                                                name= linename,
                                                ))
                
                
                pga = round(max(acc, key=abs), st.session_state["decimal"])  
                t_pga = round(timedomain[argmax(abs(acc))], st.session_state["decimal"])


                st.session_state["TDparams_df"]["PGA"].iloc[st.session_state["TD_selected_index"]] = pga
                st.session_state["TDparams_df"]["PGAtime"].iloc[st.session_state["TD_selected_index"]] = t_pga
                st.session_state["TDparams_df"]["PGAunit"].iloc[st.session_state["TD_selected_index"]] = unit_str

                fig_AVD_Acc.add_trace(go.Scatter(x= [t_pga], 
                                                 y= [pga],
                                                marker=dict(color="#d62728"),
                                                marker_symbol="circle-open", marker_size=10,
                                                name= f"PGA = {pga} {unit_str}",
                                                #showlegend=False
                                                ))
                
                # Plot objects
                fig_AVD_Acc.update_layout(title_text= "<b>Acceleration Time Series<b>", legend_title_text = "File name - Trace", legend=dict(x=0.01, y=0.01))           # title_text= "Time Series",
                fig_AVD_Acc.update_xaxes(title_text="Time (s)")
                fig_AVD_Acc.update_yaxes(title_text=f"Acceleration - {unit_str}")
                fig_AVD_Acc.update_layout(height=400,
                                        legend=dict(
                                        orientation="h",
                                        yanchor="bottom",
                                        y=-0.38,
                                        xanchor="left",
                                        x=0
                                        ))
                AVD_fig_cont.plotly_chart(fig_AVD_Acc, theme="streamlit", use_container_width=True, height=180)



                #####################################
                ### Velocity Time Series Figure
                #####################################
                fig_AVD_Vel = go.Figure()
                
                # Get unit of velocity and factor
                vel_unit, vel_factor = velocityunit(unit_str)

                # Acceleration to velocity integration
                acc_corrected = acc / vel_factor
                
                vel = TD_integration(acc_corrected, st.session_state["TD_trace_selected"]["delta"].iloc[0], AVD_bas_cor , AVD_order)


                linename = str(st.session_state["TD_trace_selected"]["filename"].iloc[0]) + str(" ") + str(st.session_state["TD_trace_selected"]["tracename"].iloc[0])
                fig_AVD_Vel.add_trace(go.Scatter(x= timedomain, 
                                                 y=vel,
                                                line=dict(color="#ff7f0e"),  # 2ca02c, d62728, 9467bd
                                                mode="lines",
                                                name= linename,
                                                ))
                
                # Find PGV
                pgv = round(max(vel, key=abs), st.session_state["decimal"])
                t_pgv = round(timedomain[argmax(abs(vel))], st.session_state["decimal"])

                st.session_state["TDparams_df"]["PGV"].iloc[st.session_state["TD_selected_index"]] = pgv
                st.session_state["TDparams_df"]["PGVtime"].iloc[st.session_state["TD_selected_index"]] = t_pgv
                st.session_state["TDparams_df"]["PGVunit"].iloc[st.session_state["TD_selected_index"]] = vel_unit

                fig_AVD_Vel.add_trace(go.Scatter(x= [t_pgv], 
                                                 y= [pgv],
                                                marker=dict(color="#d62728"),
                                                marker_symbol="circle-open", marker_size=10,
                                                name= f"PGV = {pgv} {vel_unit}",
                                                #showlegend=False
                                                ))

                # Plot objects
                fig_AVD_Vel.update_layout(title_text= "<b>Velocity Time Series<b>", legend_title_text = "File name - Trace", legend=dict(x=0.01, y=0.01))           # title_text= "Time Series",
                fig_AVD_Vel.update_xaxes(title_text="Time (s)")
                fig_AVD_Vel.update_yaxes(title_text=f"Velocity - {vel_unit}")
                fig_AVD_Vel.update_layout(height=400,
                                        legend=dict(
                                        orientation="h",
                                        yanchor="bottom",
                                        y=-0.38,
                                        xanchor="left",
                                        x=0
                                        ))
                AVD_fig_cont.plotly_chart(fig_AVD_Vel, theme="streamlit", use_container_width=True, height=180)



                #####################################
                ### Displacement Time Series Figure
                #####################################
                fig_AVD_Disp = go.Figure()
                
                # Get unit of velocity and factor
                disp_unit, disp_factor = displacementunit(vel_unit)

                # Acceleration to velocity integration
                disp_corrected = vel / disp_factor

                disp = TD_integration(disp_corrected, st.session_state["TD_trace_selected"]["delta"].iloc[0], AVD_bas_cor , AVD_order)


                linename = str(st.session_state["TD_trace_selected"]["filename"].iloc[0]) + str(" ") + str(st.session_state["TD_trace_selected"]["tracename"].iloc[0])
                fig_AVD_Disp.add_trace(go.Scatter(x= timedomain, 
                                                 y=disp,
                                                line=dict(color="#2ca02c"),  # 2ca02c, d62728, 9467bd
                                                mode="lines",
                                                name= linename,
                                                ))
                
                # Find PGD
                pgd = round(max(disp, key=abs), st.session_state["decimal"])
                t_pgd = round(timedomain[argmax(abs(disp))], st.session_state["decimal"])

                st.session_state["TDparams_df"]["PGD"].iloc[st.session_state["TD_selected_index"]] = pgd
                st.session_state["TDparams_df"]["PGDtime"].iloc[st.session_state["TD_selected_index"]] = t_pgd
                st.session_state["TDparams_df"]["PGDunit"].iloc[st.session_state["TD_selected_index"]] = disp_unit


                fig_AVD_Disp.add_trace(go.Scatter(x= [t_pgd], 
                                                 y= [pgd],
                                                marker=dict(color="#d62728"),
                                                marker_symbol="circle-open", marker_size=10,
                                                name= f"PGD = {pgd} {disp_unit}",
                                                #showlegend=False
                                                ))


                # Plot objects
                fig_AVD_Disp.update_layout(title_text= "<b>Displacement Time Series<b>", legend_title_text = "File name - Trace", legend=dict(x=0.01, y=0.01))           # title_text= "Time Series",
                fig_AVD_Disp.update_xaxes(title_text="Time (s)")
                fig_AVD_Disp.update_yaxes(title_text=f"Displacement - {disp_unit}")
                fig_AVD_Disp.update_layout(height=400,
                                            legend=dict(
                                            orientation="h",
                                            yanchor="bottom",
                                            y=-0.38,
                                            xanchor="left",
                                            x=0
                                            ))
                AVD_fig_cont.plotly_chart(fig_AVD_Disp, theme="streamlit", use_container_width=True, height=180)

                
                # AVD Dataframe 
                AVD_data_cont.subheader("Data Table")

                AVD_dict = {"Time (s)": timedomain, 
                            f"Acceleration ({unit_str})": around(acc, decimals= st.session_state["decimal"]),
                            f"Velocity ({vel_unit})": around(vel, decimals= st.session_state["decimal"]),
                            f"Displacement ({disp_unit})": around(disp, decimals= st.session_state["decimal"]),
                            }
                
                AVD_df = pd.DataFrame(data = AVD_dict)

                AVD_data_cont.dataframe(AVD_df, use_container_width=True)


                # Data Table Download
                filename = str(st.session_state["TD_trace_selected"]["filename"].iloc[0])
                tracename = str(st.session_state["TD_trace_selected"]["tracename"].iloc[0])
                AVD_data_cont.download_button(
                                            label= "Export Data Table",
                                            data= exportExcelSingle(AVD_df),
                                            file_name= f"{filename}-{tracename}-AVD-Time-Series.xlsx",
                                            mime= "application/vnd.ms-excel",
                                            )



            #####################################
            ### Arias Intensity
            #####################################
            with arias_tab:
                
                center_running()
                
                # Select Channel
                arias_trace_select = arias_col1.selectbox(
                                                        "Select Channel/Trace.",
                                                        st.session_state["TD_selected"]["tracename"],                 
                                                        )

                # Select two points to estimate the duration 
                start_level, end_level = arias_col2.select_slider(
                                                            "Duration estimated between two points of the Arias Intensity",
                                                            options = linspace(0,100, 99, dtype= int),
                                                            value = (5, 95),
                                                            
                                                            )
                
                # Filter dataframe for selected channel
                st.session_state["TD_trace_selected"] = st.session_state["TD_selected"].loc[st.session_state["TD_selected"]["tracename"] == arias_trace_select] 
                st.session_state["TD_selected_index"] = st.session_state["TD_trace_selected"].index[0]



                #####################################
                ### Arias Intensity Figure
                #####################################
                #from plotly.subplots import make_subplots
                fig_arias = go.Figure() #make_subplots(specs=[[{"secondary_y": True}]])

                # Acceleration and time arrays
                acc = st.session_state["TD_trace_selected"][st.session_state["selected_export_prop"]].iloc[0]
                timedomain = st.session_state["TD_trace_selected"][st.session_state["export_time_domain"]].iloc[0]
                
                # Get unit of Arias Intensity
                arias_factor, arias_unit, = ariasunit(st.session_state["TD_trace_selected"]["unit"].iloc[0])

                # Calculate arias intensity
                arias, aritime, hus_tf, hus_to, husid = ariasIntensity( acc / arias_factor,
                                                                        st.session_state["TD_trace_selected"]["delta"].iloc[0],
                                                                        timedomain,
                                                                        start_level,
                                                                        end_level,
                                                                        st.session_state["decimal"]
                                                                        )
                
                st.session_state["TDparams_df"]["AriasIntensity"].iloc[st.session_state["TD_selected_index"]] = arias
                st.session_state["TDparams_df"]["AriasIntensityunit"].iloc[st.session_state["TD_selected_index"]] = arias_unit
                st.session_state["TDparams_df"]["SignificantDuration"].iloc[st.session_state["TD_selected_index"]] = husid

                #st.write(arias, hus_tf, hus_to, husid)
                
                linename = str(st.session_state["TD_trace_selected"]["filename"].iloc[0]) + str(" ") + str(st.session_state["TD_trace_selected"]["tracename"].iloc[0])
                fig_arias.add_trace(go.Scatter( x= timedomain, 
                                                y= aritime,
                                                line=dict(color="#63acd7"),
                                                mode="lines",
                                                line_width=3,
                                                name= linename,
                                                ))                
                
                fig_arias.add_trace(go.Scatter( x= [0, max(timedomain)], 
                                                y= [aritime[hus_to], aritime[hus_to]],
                                                name= f"{int(start_level)}%",
                                                line_dash= "dash",
                                                line_color="#98df8a",                                            #showlegend=False
                                                ))

                fig_arias.add_trace(go.Scatter( x= [0, max(timedomain)], 
                                                y= [aritime[hus_tf], aritime[hus_tf]],
                                                name= f"{int(end_level)}%",
                                                line_dash="dash",
                                                line_color="#2ca02c",
                                                #showlegend=False
                                                ))
                            
                
                
                fig_arias.add_vrect(x0=timedomain[hus_to], 
                                    x1=timedomain[hus_tf], 
                                    annotation_text= f"Significant Duration: {husid}s",
                                    annotation_position="top left",
                                    annotation_textangle = 0,
                                    line_width= 1, 
                                    fillcolor="#d62728", 
                                    opacity=0.2)


                # Plot objects
                fig_arias.update_layout(title_text= "<b>Arias Intensity<b>", 
                                        legend_title_text = "File name - Trace", 
                                        legend=dict(
                                                    orientation="h",
                                                    yanchor="bottom",
                                                    y=-0.2,
                                                    xanchor="left",
                                                    x=0
                                                    ))           # title_text= "Time Series",
                
                fig_arias.update_xaxes(title_text="Time (s)")
                fig_arias.update_yaxes(title_text=f"Arias Intensity - {arias_unit}")
                fig_arias.update_layout(height=640,
                                        legend=dict(
                                        orientation="h",
                                        yanchor="bottom",
                                        y=-0.2,
                                        xanchor="left",
                                        x=0
                                        ))
                arias_fig_cont.plotly_chart(fig_arias, theme="streamlit",  use_container_width=True, height=640)

                # Arias Intensity Dataframe 
                arias_data_cont.subheader("Data Table")

                arias_dict = {"Time (s)": timedomain[:-1], 
                            f"Arias Intensity ({arias_unit})": around(aritime, decimals= st.session_state["decimal"]),
                            }
                
                arias_data_df = pd.DataFrame(data = arias_dict)

                arias_data_cont.dataframe(arias_data_df, use_container_width=True)               

                # Data Table Download
                filename = str(st.session_state["TD_trace_selected"]["filename"].iloc[0])
                tracename = str(st.session_state["TD_trace_selected"]["tracename"].iloc[0])
                arias_data_cont.download_button(
                                            label= "Export Data Table",
                                            data= exportExcelSingle(arias_data_df),
                                            file_name= f"{filename}-{tracename}-Arias-Intensity.xlsx",
                                            mime= "application/vnd.ms-excel",
                                            )



            #####################################
            ### Cumulative Absolute Velocity
            #####################################
            with CAV_tab:
                
                center_running()
                # Select Channel
                CAV_trace_select = CAV_col1.selectbox(
                                                        "Select Channel / Trace",
                                                        st.session_state["TD_selected"]["tracename"],                 
                                                        )
                
                
                # Filter dataframe for selected channel
                st.session_state["TD_trace_selected"] = st.session_state["TD_selected"].loc[st.session_state["TD_selected"]["tracename"] == CAV_trace_select] 
                st.session_state["TD_selected_index"] = st.session_state["TD_trace_selected"].index[0]



                #####################################
                ### CAV Figure
                #####################################
                fig_cav = go.Figure()

                # Acceleration and time arrays
                acc = st.session_state["TD_trace_selected"][st.session_state["selected_export_prop"]].iloc[0]
                timedomain = st.session_state["TD_trace_selected"][st.session_state["export_time_domain"]].iloc[0]
                
                # Get unit of CAV
                cav_unit, cav_factor = velocityunit(st.session_state["TD_trace_selected"]["unit"].iloc[0])
                
                # Calculate CAV
                cav, cavtime, scav, scavtime  = cumulativeAbsoluteVelocity( acc / cav_factor,
                                                                            st.session_state["TD_trace_selected"]["delta"].iloc[0],
                                                                            st.session_state["TD_trace_selected"]["unit"].iloc[0],
                                                                            st.session_state["decimal"],
                                                                            )
                
                st.session_state["TDparams_df"]["CAV"].iloc[st.session_state["TD_selected_index"]] = cav
                st.session_state["TDparams_df"]["StandardizedCAV"].iloc[st.session_state["TD_selected_index"]] = scav
                st.session_state["TDparams_df"]["CAVunit"].iloc[st.session_state["TD_selected_index"]] = cav_unit

                linename = str(st.session_state["TD_trace_selected"]["filename"].iloc[0]) + str(" ") + str(st.session_state["TD_trace_selected"]["tracename"].iloc[0])
                fig_cav.add_trace(go.Scatter( x= timedomain, 
                                                y= cavtime,
                                                line=dict(color="#2ca02c"),
                                                mode="lines",
                                                line_width=4,
                                                name= linename + "  CAV",
                                                ))                
                if cav_unit != "Raw":
                    fig_cav.add_trace(go.Scatter( x= timedomain, 
                                                    y= scavtime,
                                                    line=dict(color="#d62728"),
                                                    mode="lines",
                                                    line_width=2,
                                                    name= linename + "  Standardized CAV",
                                                
                                                    ))   
                                

                # Plot objects
                fig_cav.update_layout(title_text= "<b>Cumulative Absolute Velocity<b>", 
                                        legend_title_text = "File name - Trace", 
                                        legend=dict(
                                                    orientation="h",
                                                    yanchor="bottom",
                                                    y=-0.2,
                                                    xanchor="left",
                                                    x=0
                                                    ))           # title_text= "Time Series",
                
                fig_cav.update_xaxes(title_text="Time (s)")
                fig_cav.update_yaxes(title_text=f"Cumulative Absolute Velocity - {cav_unit}")
                fig_cav.update_layout(height=640)
                CAV_fig_cont.plotly_chart(fig_cav, theme="streamlit",  use_container_width=True, height=640)


                # Cumulative Absolute Velocity Dataframe 
                CAV_data_cont.subheader("Data Table")
                
                #CAV_data_cont.write(len(timedomain))
                #CAV_data_cont.write(len(cavtime))
                #CAV_data_cont.write(len(scavtime))

                if cav_unit == "Raw":
                    CAV_dict = {"Time (s)": timedomain, 
                                f"CAV ({cav_unit})": around(cavtime, decimals= st.session_state["decimal"]),
                                }
                    
                else:
                    CAV_dict = {"Time (s)": timedomain, 
                                f"CAV ({cav_unit})": around(cavtime, decimals= st.session_state["decimal"]),
                                f"SCAV ({cav_unit})": around(scavtime, decimals= st.session_state["decimal"]),
                                }
                
                CAV_data_df = pd.DataFrame(data = CAV_dict)

                CAV_data_cont.dataframe(CAV_data_df, use_container_width=True)      
               


                # Data Table Download
                filename = str(st.session_state["TD_trace_selected"]["filename"].iloc[0])
                tracename = str(st.session_state["TD_trace_selected"]["tracename"].iloc[0])
                CAV_data_cont.download_button(
                                            label= "Export Data Table",
                                            data= exportExcelSingle(CAV_data_df),
                                            file_name= f"{filename}-{tracename}-CAV.xlsx",
                                            mime= "application/vnd.ms-excel",
                                            )

            

            #####################################
            ### Time Domain Parameters
            #####################################     
            with TDparam_tab:
                
                center_running()

                TDparam_cont.dataframe(st.session_state["TDparams_df"], use_container_width=True)

                filename = str(st.session_state["TD_trace_selected"]["filename"].iloc[0])
                #tracename = str(st.session_state["TD_trace_selected"]["tracename"].iloc[0])
                TDparam_cont.download_button(
                                            label= "Export Parameters Table",
                                            data= exportExcelSingle(st.session_state["TDparams_df"]),
                                            file_name= f"{filename}-TD-Parameters.xlsx",
                                            mime= "application/vnd.ms-excel",
                                            )




if __name__ == "__main__":
    timeDomainAnalysis()