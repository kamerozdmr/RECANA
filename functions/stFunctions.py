import base64
import streamlit as st


@st.cache(allow_output_mutation=True)
def get_base64_of_bin_file(png_file):
    with open(png_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


def build_markup_for_logo(
    png_file,
    background_position="24px 5%",
    margin_top="5%",
    image_width="84px",
    image_height=""):

    binary_string = get_base64_of_bin_file(png_file)
    return """
            <style>
                [data-testid="stSidebarNav"] {
                    background-image: url("data:image/png;base64,%s");
                    background-repeat: no-repeat;
                    background-position: %s;
                    margin-top: %s;
                    background-size: %s %s;
                }
            </style>
            """ % (
                    binary_string,
                    background_position,
                    margin_top,
                    image_width,
                    image_height,
                    )


def add_logo(png_file):
    logo_markup = build_markup_for_logo(png_file)
    st.markdown(
        logo_markup,
        unsafe_allow_html=True,

    )

def sidebarHeight():
    st.markdown(f'''
        <style>
        section[data-testid="stSidebar"] .css-ng1t4o {{width: 12rem;}}
        </style>
    ''',unsafe_allow_html=True
    )


def sidebarLogoOptionMenu(png_file, header_sidebar):
    LOGO_IMAGE = png_file

    st.sidebar.markdown(
        """
        <style>
        .container {
            display: flex;
        }
        .logo-text {
            font-weight:48px ;
            font-size:32px !important;
            color: #EEEEEE !important;
            padding-top: 3px !important;
        }
        .logo-img {
            float:right;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown(
        f"""
        <div class="container">
            <img class="logo-img" src="data:image/png;base64,{base64.b64encode(open(LOGO_IMAGE, "rb").read()).decode()}">
            <p class="logo-text">{header_sidebar}</p>
        </div>
        """,
        unsafe_allow_html=True
    )