
import streamlit as st
import zipfile
import os
import pydicom
import base64
import tempfile
from io import BytesIO
import re


st.set_page_config(page_title="DICOM Modifier", page_icon="https://img.icons8.com/fluency/48/edit-link.png")

# Function to modify DICOM data
def modify_dicom_data(file, new_name, new_id):
    dicom_data = pydicom.dcmread(file)
    
    # Modify Patient Name and Patient ID if input matches the format
    if re.match(r'^\d{2}_\d{4}_\d{3}$', new_name) and re.match(r'^\d{2}_\d{4}_\d{3}_\d{8}$', new_id):
        dicom_data.PatientName = new_name
        dicom_data.PatientID = new_id
    else:
        st.error("Invalid input format. Expected format: 07_5119_001 for name and 07_5119_001_20231103 for ID")
        return None

    modified_file = tempfile.NamedTemporaryFile(delete=False)
    dicom_data.save_as(modified_file.name)
    return modified_file

# Function to create a modified zip file with modified DICOMs
def create_modified_zip(zip_file, new_name, new_id):
    with zipfile.ZipFile(zip_file, 'r') as original_zip:
        num_files = sum(1 for name in original_zip.namelist() if name.lower().endswith('.dcm'))
        progress_bar = st.progress(0)

        modified_zip = tempfile.NamedTemporaryFile(delete=False)
        with zipfile.ZipFile(modified_zip, 'a', zipfile.ZIP_DEFLATED, False) as zf:
            count = 0
            for filename in original_zip.namelist():
                file_data = original_zip.read(filename)
                if filename.lower().endswith('.dcm'):
                    modified_file = modify_dicom_data(BytesIO(file_data), new_name, new_id)
                    if modified_file:
                        zf.writestr(filename, open(modified_file.name, 'rb').read())
                        modified_file.close()
                        count += 1
                        progress = count / num_files
                        progress_bar.progress(progress)
                    else:
                        return None
                else:
                    zf.writestr(filename, file_data)

    return modified_zip

# Streamlit app
st.markdown("""
    <div style='display: flex; align-items: center;'>
        <img src='https://img.icons8.com/fluency/48/edit-link.png' style='width:48px;height:48px;'>
        <h1 style='font-family: Arial; font-size: 24px;'>KORTUC Study DICOM Modifier</h1>
    </div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload a ZIP file", type="zip")
if uploaded_file:
    st.write("File uploaded successfully.")
    
    new_name = st.text_input("Enter New Patient Name (format: 07_5119_001)")
    new_id = st.text_input("Enter New Patient ID (format: 07_5119_001_20231103)")

    if st.button("Submit"):
        if new_name and new_id:
            modified_zip = create_modified_zip(BytesIO(uploaded_file.read()), new_name, new_id)
            if modified_zip:
                st.write("Preprocessing completed. You can download the processed file below:")
                with open(modified_zip.name, 'rb') as f:
                    bytes = f.read()
                    b64 = base64.b64encode(bytes).decode()
                    href = f'<a href="data:file/zip;base64,{b64}" download="{new_id}.zip">Download Modified ZIP File</a>'
                    st.markdown(href, unsafe_allow_html=True)
                modified_zip.close()
