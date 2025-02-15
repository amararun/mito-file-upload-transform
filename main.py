import streamlit as st
from mitosheet.streamlit.v1 import spreadsheet
import pandas as pd
import openpyxl
import io
import os
import re
import keyword

# Must be the first Streamlit command
st.set_page_config(
    page_title="MitoSheet Script Generator Demo",
    initial_sidebar_state="expanded",
    layout="wide",
    menu_items={
        'Get Help': 'https://docs.trymito.io/',
        'Report a bug': "https://docs.trymito.io/",
        'About': "# This is a Streamlit - MitoSheet App that lets you manipulate multiple Pandas DataFrames with an Excel Interface"
    }
)

# Custom CSS for modern styling
st.markdown("""
<style>
    /* Modern color scheme */
    :root {
        --primary-color: #4F46E5;
        --background-color: #F9FAFB;
        --card-background: #FFFFFF;
        --text-color: #111827;
    }

    /* Card-like containers */
    .stMarkdown, .stButton, .stDownloadButton {
        background-color: var(--card-background);
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        margin-bottom: 1rem;
    }

    /* Button styling */
    .stButton > button, .stDownloadButton > button {
        width: 100%;
        background-color: var(--primary-color);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.375rem;
        font-weight: 500;
        transition: all 150ms ease-in-out;
    }

    .stButton > button:hover, .stDownloadButton > button:hover {
        background-color: #4338CA;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }

    /* Info boxes */
    .stAlert {
        background-color: #EEF2FF;
        color: #3730A3;
        border: 1px solid #C7D2FE;
        padding: 1rem;
        border-radius: 0.5rem;
    }

    /* Headers */
    h1, h2, h3 {
        color: var(--text-color);
        font-weight: 600;
        margin-bottom: 1rem;
    }

    /* File uploader */
    .stUploadButton {
        background-color: var(--card-background);
        border: 2px dashed #E5E7EB;
        border-radius: 0.5rem;
        padding: 1rem;
        text-align: center;
    }

    .stUploadButton:hover {
        border-color: var(--primary-color);
    }

    /* DataFrame display */
    .dataframe {
        border-radius: 0.5rem;
        overflow: hidden;
        border: 1px solid #E5E7EB;
    }

    .dataframe th {
        background-color: #F3F4F6;
        padding: 0.75rem;
    }

    .dataframe td {
        padding: 0.75rem;
        border-top: 1px solid #E5E7EB;
    }
</style>
""", unsafe_allow_html=True)

# Create a container for the main content
with st.container():
    st.title("Multi-File Python Script Generator Demo")

    # Introduction section
    st.markdown("""
    This app allows you to **manipulate multiple data files** through an intuitive Excel interface and **outputs the corresponding Python scripts** as you go. After importing your data, interact with the spreadsheet as if you're using Excel, and the app will record your transformation steps, generating the corresponding Python code.
    """)
    
    # Steps in an info box
    st.info("""
    To use the app, follow these steps:
    1. Import multiple data files into Streamlit  
    2. Use Mitosheet to manipulate and clean the data based on the prompts  
    3. Once you're done, download the cleaned data as CSV files and view the Python scripts for each step
    """)
    
    st.markdown("This app is a demo of the Mitosheet library. Learn more [here](https://trymito.io).")

@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

def load_file(uploaded_file, sep=None, selected_sheet=None):
    try:
        file_type = uploaded_file.name.split('.')[-1].lower()

        if file_type == 'csv':
            df = pd.read_csv(uploaded_file)
        elif file_type == 'txt':
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
    st.header("Code Generated")
    st.code(code, language="python")

    st.header("Final Output")
    for key, df_temp in dfs.items():
        st.subheader(f"DataFrame: {key}")
        st.dataframe(df_temp, use_container_width=True)
        
        csv = convert_df(df_temp)
        st.download_button(
            label=f"📥 Download {key} as CSV",
            data=csv,
            file_name=f'{key}.csv',
            mime='text/csv',
        )
        st.markdown("---")

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

st.header("Upload files to use MitoSheet")

# File uploader with improved styling
uploaded_files = st.file_uploader(
    "Choose files",
    accept_multiple_files=True,
    help="Supported formats: CSV, TXT, XLSX, Parquet"
)

if uploaded_files:
    dataframes = []
    for uploaded_file in uploaded_files:
        if uploaded_file.name.endswith('.xlsx'):
            xls = pd.ExcelFile(uploaded_file, engine='openpyxl')
            sheet_names = xls.sheet_names
            selected_sheet = st.selectbox(f"Select a sheet name for {uploaded_file.name}", sheet_names)
        else:
            selected_sheet = None
            
        if uploaded_file.name.endswith('.txt'):
            sep = st.text_input(f"Enter the separator for {uploaded_file.name} (e.g., ',' or '|')", ',')
        else:
            sep = None
        
        df = load_file(uploaded_file, sep=sep, selected_sheet=selected_sheet)
        
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
    st.info(
        "Awaiting file upload. Supported formats: CSV, TXT, XLSX, Parquet. Or you can import a demo file to begin."
    )
    
    try:
        # Load demo file and interact with Mitosheet
        dfs, code = spreadsheet(import_folder='./data')
        if len(dfs) != 0:
            display_mito_output(dfs, code)
    except Exception as e:
        st.error(f"Error loading demo file: {e}")