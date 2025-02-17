import streamlit as st
from mitosheet.streamlit.v1 import spreadsheet
import pandas as pd
import openpyxl
import io
import os
import re
import keyword
import time

# Configure the app
st.set_page_config(
    page_title="MitoSheet Data Transformer",
    page_icon="images/FXLOGO.png",
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

        /* Footer styles */
        footer a:hover {
            color: rgb(67, 56, 202) !important;
            text-decoration: underline !important;
        }

        footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            z-index: 999;
            backdrop-filter: blur(8px);
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

# Mito Team Acknowledgment
st.markdown("""
    <div style='background: linear-gradient(135deg, rgba(79, 70, 229, 0.05), rgba(79, 70, 229, 0.08)); 
               padding: 0.75rem 1rem; 
               border-radius: 0.5rem; 
               border: 1px solid rgba(79, 70, 229, 0.15);
               margin: 0.5rem 0 1rem 0;
               font-size: 0.9rem;'>
        <div style='color: rgba(30, 27, 75, 0.8); line-height: 1.5;'>
            🔍 Transform data with a spreadsheet interface + natural language AI 
            <span style='margin: 0 0.25rem; color: rgba(79, 70, 229, 0.3)'>•</span>
            ⚡ Powered by Mitosheet & Mito AI 
            <span style='margin: 0 0.25rem; color: rgba(79, 70, 229, 0.3)'>•</span>
            <a href='https://www.trymito.io' target='_blank' style='color: rgb(79, 70, 229); text-decoration: none;'>
                Visit trymito.io
            </a>
        </div>
        <div style='color: rgba(30, 27, 75, 0.8); line-height: 1.5; margin-top: 0.4rem;'>
            <a href='https://mito-script-generator-demo.streamlit.app' target='_blank' style='color: rgb(79, 70, 229); text-decoration: none;'>
                Original Demo & Code
            </a>
            <span style='margin: 0 0.25rem; color: rgba(79, 70, 229, 0.3)'>•</span>
            <a href='https://github.com/amararun/mito-file-upload-transform' target='_blank' style='color: rgb(79, 70, 229); text-decoration: none;'>
                This App's Repo
            </a>
            <span style='margin: 0 0.25rem; color: rgba(79, 70, 229, 0.3)'>•</span>
            💡 This app is based on the original open-source demo and code with a few formatting changes
        </div>
    </div>
    """, unsafe_allow_html=True)

# Create tabs
mito_tab, samples_tab = st.tabs(["📝 MitoSheet", "📁 Sample Files"])

# MitoSheet Tab Content
with mito_tab:
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
        try:
            # Load demo file and interact with Mitosheet
            dfs, code = spreadsheet(import_folder='./data')
            if len(dfs) != 0:
                display_mito_output(dfs, code)
        except Exception as e:
            st.error(f"Error loading demo file: {e}")

    # Add Footer
    st.markdown("""
        <footer style="background-color: rgba(255, 255, 255, 0.5); border-top: 1px solid rgba(79, 70, 229, 0.1); padding: 0.5rem 0; margin-top: 2rem; text-align: center; font-size: 0.875rem; color: rgba(30, 27, 75, 0.7);">
            <div style="max-width: 80rem; margin: 0 auto; padding: 0 1rem;">
                Amar Harolikar <span style="margin: 0 0.375rem; color: rgba(79, 70, 229, 0.3)">•</span> 
                Specialist - Decision Sciences & Applied Generative AI <span style="margin: 0 0.375rem; color: rgba(79, 70, 229, 0.3)">•</span>
                <a href="https://www.linkedin.com/in/amarharolikar" target="_blank" rel="noopener noreferrer" 
                   style="color: rgb(79, 70, 229); text-decoration: none; transition: all 0.2s;">LinkedIn</a> 
                <span style="margin: 0 0.375rem; color: rgba(79, 70, 229, 0.3)">•</span>
                <a href="https://rex.tigzig.com" target="_blank" rel="noopener noreferrer"
                   style="color: rgb(79, 70, 229); text-decoration: none; transition: all 0.2s;">rex.tigzig.com</a> 
                <span style="margin: 0 0.375rem; color: rgba(79, 70, 229, 0.3)">•</span>
                <a href="https://tigzig.com" target="_blank" rel="noopener noreferrer"
                   style="color: rgb(79, 70, 229); text-decoration: none; transition: all 0.2s;">tigzig.com</a>
            </div>
        </footer>
    """, unsafe_allow_html=True)

# Sample Files Tab Content
with samples_tab:
    st.title("Sample Files")
    
    # Add delimiter info with styling
    st.markdown("""
        <div style='background: linear-gradient(135deg, rgba(255, 171, 0, 0.1), rgba(255, 171, 0, 0.05));
                 padding: 0.75rem 1rem;
                 border-radius: 0.5rem;
                 border: 1px solid rgba(255, 171, 0, 0.2);
                 margin: 0.5rem 0 1.5rem 0;
                 font-size: 0.95rem;'>
            ℹ️ All sample files use pipe ( <code>|</code> ) as delimiter. When importing, enter <code>|</code> in the delimiter field.
        </div>
    """, unsafe_allow_html=True)
    
    def count_file_rows(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return sum(1 for _ in f)
        except Exception as e:
            return "Unable to count rows"
    
    # Sample file metadata
    sample_files = [
        {
            "name": "ICICI Bluechip Fund (Sep-Dec 2024)",
            "description": """Mutual fund performance data for ICICI Bluechip Fund comparing two quarters (September and December 2024). 
Contains NAV values and fund metrics.""",
            "file_path": "sample_files/ICICI_BLUECHIP_SEP_DEC_2024.txt",
            "size": "7.0 KB",
            "rows": count_file_rows('sample_files/ICICI_BLUECHIP_SEP_DEC_2024.txt'),
            "preview_rows": 5
        },
        {
            "name": "RBI Cards Data (December 2024)",
            "description": """Monthly RBI data on credit/debit card transactions and ATM/POS usage for December 2024. 
Includes transaction volumes and values across different channels.""",
            "file_path": "sample_files/RBI_CARDS_ATM_POS_DEC2024.txt",
            "size": "14 KB",
            "rows": count_file_rows('sample_files/RBI_CARDS_ATM_POS_DEC2024.txt'),
            "preview_rows": 5
        },
        {
            "name": "RBI Cards Data (Full Year 2024)",
            "description": """Comprehensive yearly RBI data on credit/debit card transactions and ATM/POS usage for the entire year 2024. 
Monthly breakdown of transaction metrics.""",
            "file_path": "sample_files/RBI_CARDS_ATM_POS_2024_FULL_YEAR_MONTHLY.txt",
            "size": "157 KB",
            "rows": count_file_rows('sample_files/RBI_CARDS_ATM_POS_2024_FULL_YEAR_MONTHLY.txt'),
            "preview_rows": 5
        }
    ]

    # Display sample files catalog with enhanced styling
    for file in sample_files:
        with st.expander(f"{file['name']} ({file['size']} • {file['rows']:,} rows)"):
            st.markdown(f"""
            <div style='background-color: rgba(79, 70, 229, 0.05); padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;'>
                {file['description']}
            </div>
            """, unsafe_allow_html=True)
            
            # Read and display preview with enhanced styling
            try:
                with open(file['file_path'], 'r', encoding='utf-8') as f:
                    preview_data = ''.join([next(f) for _ in range(file['preview_rows'])])
                st.markdown("**📄 Preview (First 5 rows):**")
                st.code(preview_data, language='text')
            except Exception as e:
                st.warning(f"Preview not available: {str(e)}")
            
            # Download button with enhanced styling and spinner
            try:
                with open(file['file_path'], 'rb') as f:
                    file_data = f.read()
                    
                col1, col2, col3 = st.columns([1,2,1])
                with col2:
                    if st.download_button(
                        label=f"📥 Download {file['name']}",
                        data=file_data,
                        file_name=file['file_path'].split('/')[-1],
                        mime='text/plain',
                        use_container_width=True,
                    ):
                        with st.spinner(f'Preparing download for {file["name"]}...'):
                            # Add a small delay to show the spinner (especially for small files)
                            time.sleep(1)
                        st.success(f'✅ {file["name"]} is ready for download!')
            except Exception as e:
                st.error(f"Error setting up download: {str(e)}")

    # Additional Files Section
    st.markdown("---")
    st.subheader("📦 Additional Sample Files")
    
    st.markdown("""
    <div style='background: linear-gradient(135deg, rgba(79, 70, 229, 0.1), rgba(79, 70, 229, 0.05)); padding: 1.5rem; border-radius: 0.75rem; border: 1px solid rgba(79, 70, 229, 0.2);'>
        <h4 style='color: rgb(79, 70, 229); margin-bottom: 1rem; font-size: 1.1rem;'>More Sample Files Available on Google Drive 🔗</h4>
        <p style='margin-bottom: 1rem;'>Access our extended collection of sample files for testing and analysis:</p>
        <ol style='margin-left: 1.5rem; margin-bottom: 1rem;'>
            <li style='margin-bottom: 0.5rem;'><strong>Live RBI Monthly Card JDMP Statistics</strong> - Current and historical card transaction data</li>
            <li style='margin-bottom: 0.5rem;'><strong>Mock Bank Credit Card Data</strong> - Simulated customer profiles and transaction patterns</li>
            <li style='margin-bottom: 0.5rem;'><strong>ODI Cricket Dataset (180 MB)</strong> - Comprehensive cricket statistics from 2002-2024 with 1.5 million records</li>
            <li style='margin-bottom: 0.5rem;'><strong>Bank Transaction Analytics</strong> - Detailed financial transaction datasets</li>
        </ol>
        <a href="https://drive.google.com/drive/folders/1QlE8tJDKAX9XaHUCabfflPgRnNiOXigV?usp=drive_link" 
           target="_blank" 
           style='display: inline-block; background-color: rgb(79, 70, 229); color: white; padding: 0.5rem 1rem; border-radius: 0.375rem; text-decoration: none; font-weight: 500; margin-top: 0.5rem; transition: all 0.2s;'>
           🔗 Access Files on Google Drive
        </a>
    </div>
    """, unsafe_allow_html=True)