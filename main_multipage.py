import streamlit as st

# Configure the app
st.set_page_config(
    page_title="Data Transformation App",
    page_icon="📊",
    layout="wide"
)

# Define the pages
pages = [
    st.Page("mito_app.py", title="MitoSheet", icon="📝"),
    st.Page("sample_files.py", title="Sample Files", icon="📁")
]

# Set up navigation
pg = st.navigation(pages)

# Run the selected page
pg.run() 