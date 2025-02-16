import streamlit as st
from mitosheet.streamlit.v1 import spreadsheet
import pandas as pd
import openpyxl
import io
import os
import re
import keyword

# Configure the app
st.set_page_config(
    page_title="MitoSheet Script Generator Demo",
    page_icon="📊",
    initial_sidebar_state="expanded",
    layout="wide",
    menu_items={
        'Get Help': 'https://docs.trymito.io/',
        'Report a bug': "https://docs.trymito.io/",
        'About': "# This is a Streamlit - MitoSheet App that lets you manipulate multiple Pandas DataFrames with an Excel Interface"
    }
)

# Load CSS
def load_css(css_file):
    with open(css_file, 'r') as f:
        return f'<style>{f.read()}</style>'

st.markdown(load_css('style.css'), unsafe_allow_html=True)

# Add custom font styles
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700&display=swap');
        
        /* Define root variables */
        :root {
            --app-font-family: 'Nunito', sans-serif;
        }
        
        /* Global font styles */
        body,
        .header-text,
        h1, h2, h3, h4, h5, h6,
        .st-emotion-cache-1629p8f h1,
        .st-emotion-cache-1629p8f h2,
        .st-emotion-cache-1629p8f h3,
        .st-emotion-cache-1629p8f p,
        .st-emotion-cache-1629p8f li,
        .st-emotion-cache-1629p8f span,
        .stMarkdown,
        .stText,
        .stTitle,
        .stHeader,
        div[data-testid="stMarkdownContainer"] p,
        div[data-testid="stMarkdownContainer"] li,
        div[data-testid="stHeader"],
        div[data-testid="stHeading"],
        div.st-emotion-cache-q8sbsg p,
        div.st-emotion-cache-1wbqy5l,
        button, 
        input, 
        select, 
        textarea {
            font-family: var(--app-font-family) !important;
            letter-spacing: 0;
        }

        /* Style the file uploader container */
        [data-testid="stFileUploader"] {
            background: linear-gradient(135deg, rgba(88, 80, 236, 0.05), rgba(88, 80, 236, 0.1)) !important;
            padding: 2rem !important;
            border-radius: 8px !important;
            border: 1px solid rgba(88, 80, 236, 0.2) !important;
        }

        /* Style the actual dropzone */
        [data-testid="stFileUploader"] > section {
            background: white !important;
            border: 2px dashed rgba(88, 80, 236, 0.3) !important;
            border-radius: 6px !important;
            color: rgb(88, 80, 236) !important;
        }

        /* Hide the Browse files button */
        [data-testid="stFileUploader"] button[data-testid="baseButton-primary"],
        button.st-emotion-cache-7ym5gk,
        .st-emotion-cache-1erivf3 button[kind="primary"] {
            display: none !important;
        }

        /* Style the button */
        [data-testid="stFileUploader"] button {
            background: rgb(88, 80, 236) !important;
            color: white !important;
            border: none !important;
            padding: 0.5rem 1.5rem !important;
            border-radius: 4px !important;
            font-weight: 600 !important;
            transition: all 0.2s ease !important;
        }

        [data-testid="stFileUploader"] button:hover {
            background: rgb(108, 99, 255) !important;
            box-shadow: 0 2px 4px rgba(88, 80, 236, 0.2) !important;
        }

        /* New attempt for delete buttons */
        .st-emotion-cache-1erivf3 button.st-emotion-cache-19rxjzo,
        .st-emotion-cache-1erivf3 button.st-emotion-cache-7ym5gk,
        .st-emotion-cache-1erivf3 button.st-emotion-cache-1q62vxm,
        div[class*="uploadedFile"] button,
        div[class*="fileUploadBlock"] button[class*="removeButton"] {
            width: 22px !important;
            height: 22px !important;
            min-height: 22px !important;
            min-width: 22px !important;
            padding: 3px !important;
            margin: 0 0 0 8px !important;
            background: rgb(88, 80, 236) !important;
            border-radius: 3px !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
        }

        /* Style the X mark */
        .st-emotion-cache-1erivf3 button.st-emotion-cache-19rxjzo p,
        .st-emotion-cache-1erivf3 button.st-emotion-cache-7ym5gk p,
        .st-emotion-cache-1erivf3 button.st-emotion-cache-1q62vxm p,
        div[class*="uploadedFile"] button p,
        div[class*="fileUploadBlock"] button[class*="removeButton"] p {
            font-size: 14px !important;
            line-height: 1 !important;
            margin: 0 !important;
            padding: 0 !important;
            color: white !important;
            transform: scale(0.8) !important;
        }
        
        /* Specific header styling */
        div[data-testid="stHeader"],
        div[data-testid="stHeading"],
        div.st-emotion-cache-q8sbsg p,
        div.st-emotion-cache-1wbqy5l {
            font-family: var(--app-font-family) !important;
            font-weight: 600;
            letter-spacing: -0.01em;
        }
        
        /* Adjust specific elements if needed */
        .stMarkdown {
            line-height: 1.6;
        }

        /* Header specific adjustments for Nunito */
        .header-text {
            font-weight: 600;
            letter-spacing: -0.01em;
        }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown(
    """
    <div class="header-container">
        <span class="header-text">MitoSheet Data Transformer</span>
    </div>
    """,
    unsafe_allow_html=True
)

st.title('Multi-File Python Script Generator Demo')

st.markdown("""
This app allows you to **manipulate multiple data files** through an intuitive Excel interface and **outputs the corresponding Python scripts** as you go. After importing your data, interact with the spreadsheet as if you're using Excel, and the app will record your transformation steps, generating the corresponding Python code.

To use the app, follow these steps:
1. Import multiple data files into Streamlit  
2. Use Mitosheet to manipulate and clean the data based on the prompts  
3. Once you're done, download the cleaned data as CSV files and view the Python scripts for each step

This app is a demo of the Mitosheet library. Learn more [here](https://trymito.io).
""")

st.header("Upload files to use MitoSheet")

# Main Content
col1, col2, col3 = st.columns([0.5, 1, 0.5])
with col1:
    st.info("""Upload files -> Click AI button - for natural language-based spreadsheet editing.
Press Win+H (Windows) or Cmd+H (Mac) to use your device's native voice dictation.""")
with col2:
    # Add a container with custom styling
    with st.container():
        uploaded_files = st.file_uploader(
            " ",  # Empty space with a single space to maintain layout
            accept_multiple_files=True,
            help="Supported formats: CSV, TXT, XLSX, Parquet",
            label_visibility="collapsed",  # This will hide the label completely
        )

# Create a container in col3 for separator inputs
with col3:
    separator_inputs = {}
    if uploaded_files:
        for uploaded_file in uploaded_files:
            if uploaded_file.name.endswith('.txt'):
                separator_inputs[uploaded_file.name] = st.text_input(
                    f"Separator for {uploaded_file.name}",
                    ',',
                    key=f"sep_{uploaded_file.name}"
                )

@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

def load_file(uploaded_file, sep=None, selected_sheet=None):
    try:
        file_type = uploaded_file.name.split('.')[-1].lower()

        if file_type == 'csv':
            df = pd.read_csv(uploaded_file)
        elif file_type == 'txt':
            # Use the separator from our inputs dictionary
            sep = separator_inputs.get(uploaded_file.name, ',')
            df = pd.read_csv(uploaded_file, sep=sep) if sep else None
            if df is None:
                st.warning("Please provide a valid separator for the TXT file.")
        elif file_type == 'xlsx':
            xls = pd.ExcelFile(uploaded_file, engine='openpyxl')
            df = pd.read_excel(xls, sheet_name=selected_sheet) if selected_sheet else None
        elif file_type == 'parquet':
            df = pd.read_parquet(uploaded_file)
        else:
            df = None
            st.warning(f"Unsupported file format for {uploaded_file.name}. Please upload CSV, TXT, XLSX, or Parquet.")
    except Exception as e:
        st.error(f"Error loading file: {e}")
        df = None

    return df

def display_mito_output(dfs, code):
    st.markdown(f"**Code Generated**")
    st.code(code)

    st.header(f"Final Output")
    for key, df_temp in dfs.items():
        st.markdown(f"**DataFrame**: {key}")
        st.write(df_temp)
        
        csv = convert_df(df_temp)
        st.download_button(
            label=f"Download {key} as CSV",
            data=csv,
            file_name=f'{key}.csv',
            mime='text/csv'
        )

def clean_name(name):
    # Remove any characters that are not alphanumeric or underscore
    cleaned = re.sub(r'\W+', '_', name)
    # Ensure the name starts with a letter or underscore
    if not cleaned[0].isalpha() and cleaned[0] != '_':
        cleaned = '_' + cleaned
    # If the name is a Python keyword, prefix it with an underscore
    if keyword.iskeyword(cleaned):
        cleaned = '_' + cleaned
    # Ensure the name is not empty
    if not cleaned:
        cleaned = '_unnamed'
    return cleaned

if uploaded_files:
    dataframes = []
    for uploaded_file in uploaded_files:
        if uploaded_file.name.endswith('.xlsx'):
            xls = pd.ExcelFile(uploaded_file, engine='openpyxl')
            sheet_names = xls.sheet_names
            selected_sheet = st.selectbox(f"Select a sheet name for {uploaded_file.name}", sheet_names)
        else:
            selected_sheet = None
        
        df = load_file(uploaded_file, selected_sheet=selected_sheet)
        
        if df is not None:
            # Use the cleaned file name (without extension) as the DataFrame name
            file_name = clean_name(os.path.splitext(uploaded_file.name)[0])
            df.name = file_name
            dataframes.append(df)

    if dataframes:
        try:
            # Call the Mitosheet spreadsheet function with all dataframes
            dfs, code = spreadsheet(*dataframes)
            # Display Mitosheet output
            display_mito_output(dfs, code)
        except Exception as e:
            st.error(f"Error processing spreadsheet: {e}")
else:
    st.info("Awaiting file upload. Supported formats: CSV, TXT, XLSX, Parquet. Or you can import a demo file to begin.")
    
    try:
        # Load demo file and interact with Mitosheet
        dfs, code = spreadsheet(import_folder='./data')
        if len(dfs) != 0:
            display_mito_output(dfs, code)
    except Exception as e:
        st.error(f"Error loading demo file: {e}")