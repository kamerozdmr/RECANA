import streamlit as st


def spectralAnalysis():
    st.title("Spectral Analysis") 

    st.markdown("In progress...")

    # If no file imported raise error messega
    if "stream_df" not in st.session_state:
        st.error("___Import file to continue.___", icon="🚨")
        #st.stop()
    

if __name__ == "__main__":
    spectralAnalysis()
