import os
import re
import shutil
import zipfile
import base64
import streamlit as st
import pydicom

# Function to extract a zip file
def extract_zip(zip_path, extract_dir):
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)

# Function to perform a custom operation (e.g., renaming DICOM files)
def perform_custom_operation(dcm_dir, patient_id, patient_name):
    filenames = (filename for filename in os.listdir(dcm_dir) if filename.endswith(".dcm"))

    for filename in filenames:
        filepath = os.path.join(dcm_dir, filename)
        dcm = pydicom.dcmread(filepath)
        dcm.PatientID = patient_id
        dcm.PatientName = patient_name
        dcm.save_as(filepath)

# Function to create a zip file
def create_zip(zip_dir, zip_name, source_dir):
    shutil.make_archive(os.path.join(zip_dir, zip_name), "zip", source_dir)

# Function to clean up the extraction folder
def clean_up(extract_dir):
    shutil.rmtree(extract_dir)

# Streamlit app
def main():
    st.title("Zip Operations Streamlit App")

    # Upload a zip file
    uploaded_file = st.file_uploader("Upload a zip file", type=["zip"])
    if uploaded_file is not None:
        # Specify the extraction directory
        extract_dir = os.path.join(os.getcwd(), "output")

        # Extract the uploaded zip file
        extract_zip(uploaded_file, extract_dir)

        # Perform a custom operation (e.g., renaming DICOM files)
        patient_name = st.text_input("Enter New Patient Name (format: 07_5119_001)")
        patient_id = st.text_input("Enter New Patient ID (format: 07_5119_001_20231103)")

        # Flag to determine whether the custom operation is performed
        operation_performed = False

        if not patient_name or not patient_id:
            st.warning("Please enter both Patient Name and Patient ID.")
        elif re.match(r"^\d{2}_\d{4}_\d{3}$", patient_name) and re.match(r"^\d{2}_\d{4}_\d{3}_\d{8}$", patient_id):
            # Spinner to show during the operation
            with st.spinner("Performing Operation..."):
                if st.button("Perform Operation"):
                    perform_custom_operation(extract_dir, patient_id, patient_name)
                    operation_performed = True

                    # Create a new zip file
                    zip_name = patient_id if patient_id else "default_name"
                    create_zip(extract_dir, zip_name, extract_dir)

                    # Provide a clickable and downloadable link
                    file_content = open(os.path.join(extract_dir, zip_name) + ".zip", "rb").read()
                    download_link = f'<a href="data:application/zip;base64,{base64.b64encode(file_content).decode()}" download="{zip_name}.zip">Click here to download the zip file</a>'
                    st.markdown(download_link, unsafe_allow_html=True)

                    # Clean up the extraction folder after the download
                    clean_up(extract_dir)
        else:
            st.error("Please enter a valid Name and ID in the specified format")

if __name__ == "__main__":
    main()
