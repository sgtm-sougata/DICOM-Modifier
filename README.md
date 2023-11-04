# DICOM Modifier

DICOM Modifier is an open-source application designed to modify the patient name and patient ID in DICOM images. This tool offers a user-friendly interface to update these critical patient identification details while preserving the integrity of the medical image data.

## Features

- **Patient Name Modification**: Allows changing the patient's name associated with DICOM images.
- **Patient ID Modification**: Enables editing the patient's ID linked to the DICOM files.
- **Streamlined Interface**: User-friendly interface for easy navigation and efficient data modification.

## Installation

To use the DICOM Modifier:

1. Clone this repository:
    ```bash
    git clone https://github.com/tmckol/dicom-modifier.git
    cd dicom-modifier
    ```

2. Install the necessary dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Run the application:
    ```bash
    streamlit run app.py
    ```

## Usage

- Launch the application by executing `streamlit run app.py`.
- Upload a ZIP file containing DICOM images.
- Enter the new patient name and/or patient ID in the provided fields.
- Submit the changes to modify the DICOM file attributes.
- Download the modified ZIP file containing the updated DICOM images.

## Contributing

Contributions are welcome! If you'd like to contribute to this project, please fork the repository and create a pull request with your changes.

## License

This project is licensed under the [MIT License](LICENSE).
