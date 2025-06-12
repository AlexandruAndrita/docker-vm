import time
import requests
import paramiko
import json
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from flask import Flask, request, render_template
import io
import base64
import os

from utils import get_patient_information, validate_and_extract_files

app = Flask(__name__)

VM_IP = os.getenv("VM_IP")
PORT = os.getenv("PORT")
SSH_USER = os.getenv("SSH_USER")

def connect_ssh(ip, username):
    """Establish SSH connection and return client."""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    retries = 5
    for attempt in range(retries):
        try:
            print(f"Attempt {attempt + 1} to connect to VM...")
            key_data = os.getenv("SSH_PRIVATE_KEY")
            if not key_data:
                raise Exception("Missing SSH_PRIVATE_KEY environmental variable")
            key_data = key_data.replace("\\n", "\n")
            key_file = io.StringIO(key_data)
            private_key = paramiko.RSAKey.from_private_key(key_file)
            ssh.connect(hostname=ip, username=username, pkey=private_key, timeout=20, banner_timeout=30)
            print("SSH connected")
            return ssh
        except Exception as e:
            print(f"SSH error: {e}")
            time.sleep(5)
    raise Exception(f"Failed to connect to VM after {retries} attempts")

def run_docker_container(ssh_client):
    """Run Docker container via SSH."""
    docker_cmd = r"""
        docker run -d -p 5000:5000 \
            -v /home/azureuser/oncodata_wrapper.py:/root/oncoserve/oncodata_wrapper.py \
            -v /home/azureuser/dicom_to_png.py:/root/OncoData/oncodata/dicom_to_png/dicom_to_png.py \
            --shm-size 32G \
            learn2cure/oncoserve_mirai:0.5.0
        """
    if not docker_cmd:
        raise Exception("Missing DOCKER_RUN_COMMAND environmental variable")
    try:
        _, stdout, stderr = ssh_client.exec_command(docker_cmd)
        print("Docker output:", stdout.read().decode())
        print("Docker errors:", stderr.read().decode())
    except Exception as e:
        print(f"Error running Docker container: {e}")
        raise

def send_curl_request(files):
    """Send curl POST request via SSH."""
    form = {
        'mrn': 'a11111111',
        'accession': 'a2222222'
    }
    file_data = [('dicom', (f.filename, f.stream, f.mimetype)) for f in files]
    predictions = None

    try:
        response = requests.post(f'http://{VM_IP}:{PORT}/serve', data=form, files=file_data)
        json_bytes = response.content
        json_str = json_bytes.decode('utf-8')
        data = json.loads(json_str)
        predictions = data.get("prediction", [])

    except Exception as e:
        print(f"Error at curl request: {e}")

    return predictions

@app.route('/', methods=['GET', 'POST'])
def upload_and_predict():
    predictions, plot_url, patient_information, usable_files, error_message = None, None, None, None, None
    if request.method == 'POST':
        files = request.files.getlist('dicoms')
        if not files or len(files) < 4:
            error_message = "No files uploaded"
        
        # need to validate files and extract relevant information about the patient
        usable_files = validate_and_extract_files(files)
        if len(usable_files) < 4:
            error_message = "Not enough valid files uploaded"
        
        if not error_message:
            try:
                patient_information = get_patient_information(usable_files[0])
                ssh = connect_ssh(VM_IP, SSH_USER)
                run_docker_container(ssh)
                time.sleep(15)
                predictions = send_curl_request(files)
                
                if not predictions:
                    error_message = "No predictions computed"
                plot_url = create_plot(predictions, patient_information)
            except Exception as e:
                error_message = "Error occurred while computing the predictions"
                print(f"Exception occurred while grabbing predictions: {e}")

    return render_template("index.html", plot_url=plot_url, error_message=error_message)

def create_plot(predictions, patient_information):
    xlabels_list = ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]
    plot_title = "Breast Cancer Risk"
    if patient_information:
        plot_title += f" - {patient_information.get('PatientName').replace('^', ' ')} (Patient ID: {patient_information.get('PatientID')})"
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(xlabels_list, predictions, marker='o')
    ax.set_title(plot_title)
    ax.set_xlabel('Year')
    ax.set_ylabel('Prediction value')
    ax.grid()
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close(fig)
    return img_base64

if __name__ == "__main__":
    app.run()