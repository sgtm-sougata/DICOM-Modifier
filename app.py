import os
import pathlib
import re
import shutil
import zipfile
import base64
import streamlit as st
import pydicom
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="DICOM Modifier",
    page_icon="https://img.icons8.com/fluency/48/edit-link.png",
)


extract_dir_main = os.path.join(os.getcwd(), "dicom")
if "dicom" in os.listdir(os.getcwd()):
    shutil.rmtree(extract_dir_main, ignore_errors=False)

os.mkdir(extract_dir_main)


# Function to extract a zip file
def extract_zip(zip_path, extract_dir, progress_bar_extract, progress_text_extract):
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        dcm_files = [file for file in zip_ref.namelist() if os.path.splitext(file)[1] == ".dcm"]
        total_files = len(dcm_files)
        
        for i, file in enumerate(dcm_files):
            zip_ref.extract(file, extract_dir)
            progress_bar_extract.progress((i + 1) / total_files)
            progress_text_extract.text(f"Extracted: {i + 1}/{total_files} files")


# Function to move all DICOM files to a second folder
def move_dicom_files(source_dir, destination_dir):
    os.makedirs(destination_dir, exist_ok=True)
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            shutil.move(os.path.join(root, file), destination_dir)


# Function to perform a custom operation (e.g., renaming DICOM files)
def perform_custom_operation(
    dcm_dir, patient_id, patient_name, progress_bar, progress_text
):
    filenames = [
        os.path.join(dp, f)
        for dp, dn, filenames in os.walk(dcm_dir)
        for f in filenames
        if f.endswith(".dcm")
    ]

    save_file = os.path.join(extract_dir_main, "save_file")
    os.makedirs(save_file, exist_ok=True)

    total_files = len(filenames)

    for i, filepath in enumerate(filenames):
        dcm = pydicom.dcmread(filepath)
        dcm.PatientID = patient_id
        dcm.PatientName = patient_name
        dcm.save_as(filepath)

        # Get the file name without the extension
        file_name = os.path.splitext(os.path.basename(filepath))[0]

        # Define the new file name with patient ID and patient name
        new_file_name = f"{patient_id}_{patient_name}.dcm"

        # Check if the destination file exists and rename if necessary
        dest_path = os.path.join(save_file, new_file_name)
        count = 1
        while os.path.exists(dest_path):
            new_file_name = f"{patient_id}_{patient_name}_{count}.dcm"
            dest_path = os.path.join(save_file, new_file_name)
            count += 1

        # Move the file to the destination
        shutil.move(filepath, dest_path)

        # Update progress bar
        progress_bar.progress((i + 1) / total_files)
        # Update progress text
        progress_text.text(f"Processed: {i + 1}/{total_files} files")


# Function to create a zip file
def create_zip(zip_dir, zip_name, source_dir):
    shutil.make_archive(os.path.join(zip_dir, zip_name), "zip", source_dir)


# Function to clean up the extraction folder
def clean_up(extract_dir):
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)


# Streamlit app
def main():
    # Local authentication using environment variables
    username = os.getenv("APP_USERNAME")
    password = os.getenv("APP_PASSWORD")
    
    if not username or not password:
        st.error("Please set APP_USERNAME and APP_PASSWORD in your .env file")
        st.stop()
    
    # Check if authenticated
    if not st.session_state.get("authenticated", False):
        # Create login form
        st.title("Login")
        login_username = st.text_input("Username", type="default")
        login_password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if login_username == username and login_password == password:
                st.session_state.authenticated = True
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")
        st.stop()
    
    st.markdown(
        """
    <div style='display: flex; align-items: center;'>
        <h1 style='font-family: Arial; font-size: 34px;'>KMS</h1>
    </div><br>
    """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"Welcome {username}")
    with col2:
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()

    extract_dir_main = os.path.join(os.getcwd(), "dicom")

    # Create a form for user input
    uploaded_file = st.file_uploader("Upload a zip file", type=["zip"])
    patient_name = st.text_input("Enter New Patient Name (format: 07_5119_001)")
    patient_id = st.text_input(
        "Enter New Patient ID (format: 07_5119_001_20231103)"
    )

    # Check and display messages for patient name and ID format
    if patient_name and not re.match(r"^\d{2}_\d{4}_\d{3}$", patient_name):
        st.warning("Please enter a valid Patient Name in the specified format.")
    if patient_id and not re.match(r"^\d{2}_\d{4}_\d{3}_\d{8}$", patient_id):
        st.warning("Please enter a valid Patient ID in the specified format.")

    # Progress bars

    # Process button to trigger operations (enabled only if name and ID are valid)
    if st.button(
        "Process",
        disabled=(
            uploaded_file is None
            or not re.match(r"^\d{2}_\d{4}_\d{3}$", patient_name)
            or not re.match(r"^\d{2}_\d{4}_\d{3}_\d{8}$", patient_id)
        ),
    ):
        progress_bar_extract = st.progress(0.0)
        progress_text_extract = st.empty()  # Empty element for updating text
        progress_bar_process = st.progress(0.0)
        progress_text_process = st.empty()  # Empty element for updating text

        if (
            uploaded_file is not None
            and re.match(r"^\d{2}_\d{4}_\d{3}$", patient_name)
            and re.match(r"^\d{2}_\d{4}_\d{3}_\d{8}$", patient_id)
        ):
            # Specify the extraction directory
            extract_dir = os.path.join(extract_dir_main, "upload")

            # Extract the uploaded zip file with progress bar
            extract_zip(
                uploaded_file,
                extract_dir,
                progress_bar_extract,
                progress_text_extract,
            )

            # Move all DICOM files to a second folder
            move_dir = os.path.join(extract_dir_main, "move")
            move_dicom_files(extract_dir, move_dir)

            # Perform custom operation with progress bar
            progress_bar_process.progress(0.0)
            progress_text_process.text("Processed: 0/0 files")
            perform_custom_operation(
                move_dir,
                patient_id,
                patient_name,
                progress_bar_process,
                progress_text_process,
            )

            # Create a new zip file

            # Provide a clickable and downloadable link

        else:
            st.warning(
                "Please upload a zip file and enter both valid Patient Name and Patient ID."
            )

        # Clean up the extraction folders after the download

        # Provide a clickable and downloadable link
        zip_name = patient_id if patient_id else "default_name"
        extract_dir_output = os.path.join(extract_dir_main, "output")

        with st.spinner("Creating Archive..."):
            create_zip(
                extract_dir_output,
                zip_name,
                os.path.join(extract_dir_main, "save_file"),
            )

        zip_file_path = os.path.join(extract_dir_output, f"{zip_name}.zip")
        with open(zip_file_path, "rb") as file:
            btn = st.download_button(
                label="Download Zip",
                data=file,
                file_name=f"{zip_name}.zip",
                mime="zip",
            )


if __name__ == "__main__":
    main()
