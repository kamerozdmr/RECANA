""" 
06.10.2022
author : kamerozdmr https://github.com/kamerozdmr
mail : kamer.oz@outlook.com
"""

import streamlit as st
from streamlit_option_menu import option_menu
import base64
from pathlib import Path

# Import Functions
from functions.stFunctions import *

from steps.import_and_trim import importandTrim
from steps.filter_and_export import filterandExport
from steps.spectral_analysis import spectralAnalysis


# Page configs 
# https://www.webfx.com/tools/emoji-cheat-sheet/                      https://emojipedia.org/symbols/
st.set_page_config(page_title="Record Analyzer",
                    page_icon="img/logo_low.png",
                    layout="wide"
                    )

# Remove Streamlit footer and main page  --- custom css code
hide_st_style = """ <style> #MainMenu {visibility: hidden;}
                footer {visibility: hidden;} 
                
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
    st.sidebar.markdown('''<img src='data:image/png;base64,{}' class='img-fluid' width=300 height=100>'''.format(img_to_bytes("img/logotext.png")), unsafe_allow_html=True)

    # Add vertical space
    st.sidebar.write("\n")
    st.sidebar.write("\n")
    st.sidebar.write("\n")
    st.sidebar.write("\n")

    # Import Option menu 
    with st.sidebar:
        selected = option_menu(
            menu_title="Steps",
            options=["Import and Trim", "Filter and Export", "Spectral Analysis"],
            icons=["box-arrow-in-up", "filter", "graph-up"],        # https://icons.getbootstrap.com/
            menu_icon= "bar-chart-steps",
            default_index=0,
        )

    # Run option menu functions
    if selected == "Import and Trim":
        importandTrim()

    if selected == "Filter and Export":
        filterandExport()
        
    if selected == "Spectral Analysis":
        spectralAnalysis()
        

    # Info box
    st.sidebar.warning("___Complete the steps in order.___", icon="⚠️")

    # Add vertical space
    st.sidebar.write("\n")
    st.sidebar.write("\n")
    st.sidebar.write("\n")
    st.sidebar.write("\n")
    st.sidebar.write("\n")
    st.sidebar.write("\n")
    st.sidebar.write("\n")

    # Add info box
    st.sidebar.title("About")
    st.sidebar.info(
    """
    Web App URL: \n <https://recana.streamlit.app/>
    GitHub repo: \n <https://github.com/kamerozdmr/RecordAnalyzer>
    """
    )

if __name__ == '__main__':
    main()