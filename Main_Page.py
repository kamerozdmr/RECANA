""" 
06.10.2022
author : kamerozdmr https://github.com/kamerozdmr
mail : kamermozdemir@gmail.com
"""

import streamlit as st
from streamlit_option_menu import option_menu
import base64
from pathlib import Path
from streamlit_extras.add_vertical_space import add_vertical_space

# Import Functions
from functions.stFunctions import *

from steps.import_and_trim import importandTrim
from steps.filter_and_export import filterandExport
from steps.frequency_domain_analysis import frequencyDomainAnalysis
from steps.time_domain_analysis import timeDomainAnalysis

# Page configs
# https://www.webfx.com/tools/emoji-cheat-sheet/                      https://emojipedia.org/symbols/
st.set_page_config(page_title="Record Analyzer",
                    page_icon="img/logo_low.png",
                    layout="wide"
                    )

# Remove Streamlit footer and main page  --- custom css code
hide_st_style = """ <style> #MainMenu {visibility: hidden;}
                footer {visibility: hidden;} 
                header {visibility: hidden;}
                </style> 
                """

# header {visibility: hidden;}   Add to delete header

st.markdown(hide_st_style, unsafe_allow_html=True)

# Functions

def main():
    # Page Functions
    sidebar_base()

def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded

def sidebar_base():
    # Option menu base format
    #sidebarHeight()
    #add_logo("img/logo.png")
    #st.sidebar.title("Pages")
    #st.sidebar.markdown("___Adjust sidebar height___")

    # Import sidebar logo
    st.sidebar.markdown('''<img src='data:image/png;base64,{}' class='img-fluid' width=280 height=100>'''.format(img_to_bytes("img/logotext.png")), unsafe_allow_html=True)

    # Add vertical space
    with st.sidebar:
        add_vertical_space(2)
    
    
    # Import Option menu 
    with st.sidebar:
        selected = option_menu(
            menu_title="Steps",
            options=["Import and Trim", "Filter and Export", "Time Domain Analysis", "Frequency Domain Analysis"],
            icons=["box-arrow-in-up", "filter", "graph-up", "soundwave"],        # https://icons.getbootstrap.com/
            menu_icon= "bar-chart-steps",
            default_index=0,
            # default red #e2001a
            styles={
                    "container": {"padding": "0!important", "background-color": "#dde5dc"},
                    "icon": {"color": "#0151ba", "font-size": "24px"}, 
                    "nav-link": {"font-size": "16px", "text-align": "left", "margin":"3px", "--hover-color": "#eee"},
                    "nav-link-selected": {"background-color": "#B4B1B1"},
                    "menu-icon": {"color": "#0151ba"},
                    },
        )

    # Run option menu functions
    if selected == "Import and Trim":
        importandTrim()

    if selected == "Filter and Export":
        filterandExport()

    if selected == "Time Domain Analysis":
        timeDomainAnalysis()

    if selected == "Frequency Domain Analysis":
        frequencyDomainAnalysis()


    # Add vertical space
    #with st.sidebar:
        #add_vertical_space(1)

    # Add info box
    st.sidebar.title("About")
   

    st.sidebar.info(
                    """
                    >___Web Application for signal processing and analysis of acceleration data for Earthquake Engineering___\n
                    [_For more detailed information about the app, please visit_ **www.modaltrace.com**](https://modaltrace.com/recana-record-analyzer)\n
                    ___kamermozdemir@gmail.com___\n
                    _v0.5_ - _31.10.2023_
                    """
                    )
    
                    #[**GitHub repository**](https://github.com/kamerozdmr/RECANA)\n          [**For Detailed Information**](https://modaltrace.com/)\n

if __name__ == '__main__':
    main()
