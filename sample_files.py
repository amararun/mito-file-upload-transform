import streamlit as st
import pandas as pd
import io

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