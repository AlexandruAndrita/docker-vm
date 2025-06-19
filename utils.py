import pydicom
from collections import defaultdict
import textwrap

def get_patient_information(file):
    patient_information = dict()
    try:
        dicom_data = pydicom.dcmread(file.stream, stop_before_pixels=True)
        patient_name = getattr(dicom_data, "PatientName", "")
        patient_id = getattr(dicom_data, "PatientID", "")
        patient_information['PatientName'] = str(patient_name)
        patient_information['PatientID'] = str(patient_id)
        file.stream.seek(0)
    except Exception as e:
        # if exception occurs when trying to read the dicom file, it means the image is not a valid DICOM
        file.stream.seek(0)
        print(f"Error while grabbing patient information: {e}")
    
    return patient_information

def get_image_information(file):
    try:
        dcm = pydicom.dcmread(file.stream, stop_before_pixels=True)
        view_str = getattr(dcm, "ViewPosition", "")
        side_str = getattr(dcm, "ImageLaterality", "")
        study_uid = getattr(dcm, "StudyInstanceUID", None)
        dcm_permissible = side_str in ["R", "L"] and view_str in ["CC", "MLO"]
        file.stream.seek(0)
        return {
            "side": side_str,
            "view": view_str,
            "valid": dcm_permissible,
            "study_uid": study_uid,
            "file": file,
        }
    except Exception as e:
        file.stream.seek(0)
        print(f"Error while grabbing image information: {e}")
        return None

def validate_and_extract_files(files):
    images_grouped_by_study_uid = defaultdict(list)
    for file in files:
        image_info = get_image_information(file)
        if image_info and image_info['study_uid']:
            images_grouped_by_study_uid[image_info['study_uid']].append(image_info)
    
    try:
        for study_uid, images in images_grouped_by_study_uid.items():
            expected_views = {"R-CC": None, "R-MLO": None, "L-CC": None, "L-MLO": None}
            for image in images:
                key = f"{image['side']}-{image['view']}"
                if key in expected_views and expected_views[key] is None:
                    expected_views[key] = image['file']
            
            if all(expected_views.values()):
                return list(expected_views.values())
    except Exception as e:
        print(f"Error while validating and extracting files: {e}")

    return []

def prepare_plot_information(predictions, patient_information):
    xlabels_list = ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]
    predictions = [round(pred * 100, 2) for pred in predictions]
    plot_title = "Breast Cancer Risk"
    text = "This plot shows the predicted risk of breast cancer over the next 5 years based on the uploaded mammographies."
    wrapped_text = textwrap.fill(text, width=130)
    if patient_information:
        plot_title += f" - {patient_information.get('PatientName').replace('^', ' ')} (Patient ID: {patient_information.get('PatientID')})"
    return xlabels_list, predictions, plot_title, wrapped_text