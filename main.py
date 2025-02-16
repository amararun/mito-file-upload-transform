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

# Create tabs
mito_tab, samples_tab = st.tabs(["📝 MitoSheet", "📁 Sample Files"])

# MitoSheet Tab Content
with mito_tab:
    col1, col2 = st.columns([0.8, 1.2])
    with col1:
        st.info("""Upload files -> Click AI button - for natural language-based spreadsheet editing.
Press Win+H (Windows) or Cmd+H (Mac) to use your device's native voice dictation.""")
    with col2:
        # Add a container with custom styling
        with st.container():
            uploaded_files = st.file_uploader(
                "📂 Choose files to transform",
                accept_multiple_files=True,
                help="Supported formats: CSV, TXT, XLSX, Parquet",
                label_visibility="visible",
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
        try:
            # Load demo file and interact with Mitosheet
            dfs, code = spreadsheet(import_folder='./data')
            if len(dfs) != 0:
                display_mito_output(dfs, code)
        except Exception as e:
            st.error(f"Error loading demo file: {e}")

# Sample Files Tab Content
with samples_tab:
    st.title("Sample Files")

    # Create some sample data
    def create_sample_csv():
        data = {
            'Name': ['John', 'Jane', 'Bob', 'Alice'],
            'Age': [25, 30, 35, 28],
            'City': ['New York', 'London', 'Paris', 'Tokyo']
        }
        return pd.DataFrame(data)

    def create_sample_excel():
        data = {
            'Product': ['Laptop', 'Phone', 'Tablet', 'Watch'],
            'Price': [1200, 800, 500, 300],
            'Stock': [50, 100, 75, 150]
        }
        return pd.DataFrame(data)

    # Display sample files section
    st.header("Available Sample Files")

    with st.expander("Sample CSV File"):
        df_csv = create_sample_csv()
        st.dataframe(df_csv)
        csv = df_csv.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Sample CSV",
            data=csv,
            file_name='sample_data.csv',
            mime='text/csv',
        )

    with st.expander("Sample Excel File"):
        df_excel = create_sample_excel()
        st.dataframe(df_excel)
        # Convert to Excel
        excel_buffer = io.BytesIO()
        df_excel.to_excel(excel_buffer, index=False, engine='openpyxl')
        excel_data = excel_buffer.getvalue()
        st.download_button(
            label="📥 Download Sample Excel",
            data=excel_data,
            file_name='sample_data.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )