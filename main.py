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
    page_title="Data Transformation App",
    page_icon="📊",
    layout="wide",
    menu_items={
        'Get Help': 'https://docs.trymito.io/',
        'Report a bug': "https://docs.trymito.io/",
        'About': "# This is a Streamlit - MitoSheet App that lets you manipulate multiple Pandas DataFrames with an Excel Interface"
    }
)

# Load external CSS
def load_css(css_file):
    with open(css_file, 'r') as f:
        return f'<style>{f.read()}</style>'

st.markdown(load_css('style.css'), unsafe_allow_html=True)

# Define the pages
pages = [
    st.Page("mito_app.py", title="MitoSheet", icon="📝"),
    st.Page("sample_files.py", title="Sample Files", icon="📁")
]

# Set up navigation
pg = st.navigation(pages)

# Run the selected page
pg.run()

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

# Create a centered container for the file uploader with wider middle column
col1, col2, col3 = st.columns([1.5, 2, 1.5])  # Made middle column wider
with col2:
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