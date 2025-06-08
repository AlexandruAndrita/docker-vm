import time
import requests
import paramiko
import json
import matplotlib.pyplot as plt

VM_IP = "<vm_ip>"
SSH_USER = "azureuser"
SSH_KEY_PATH = "<local_path_to_ssh_key>"


def connect_ssh(ip, username, key_path):
    """Establish SSH connection and return client."""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    retries = 5
    for attempt in range(retries):
        try:
            print(f"Attempt {attempt + 1} to connect to VM...")
            private_key = paramiko.RSAKey.from_private_key_file(key_path)
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
    docker run ...
    """
    stdin, stdout, stderr = ssh_client.exec_command(docker_cmd)
    print("Docker output:", stdout.read().decode())
    print("Docker errors:", stderr.read().decode())
    # time.sleep(60)

def send_curl_request():
    """Send curl POST request via SSH."""
    files = [
        ('mrn', (None, 'a11111111')),
        ('accession', (None, 'a2222222')),
        ('dicom', open(r"<image_path>", 'rb')),
        ('dicom', open(r"<image_path>", 'rb')),
        ('dicom', open(r"<image_path>", 'rb')),
        ('dicom', open(r"<image_path>", 'rb')),
    ]

    try:
        response = requests.post(f'http://{VM_IP}:<port>/serve', files=files)
        json_bytes = response.content
        json_str = json_bytes.decode('utf-8')
        data = json.loads(json_str)
        predictions = data.get("prediction", [])

    except Exception as e:
        print(f"Error at curl request: {e}")

    return predictions

def main():
    ssh = None
    predictions = None
    try:
        ssh = connect_ssh(VM_IP, SSH_USER, SSH_KEY_PATH)
        run_docker_container(ssh)
        predictions = send_curl_request()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if ssh:
            ssh.close()
            print("SSH connection closed")

    plt.figure(figsize=(10, 6))
    plt.plot(["Year 1", "Year 2", "Year 3", "Year 4", "Year 5"], predictions)
    plt.title('Mirai Predictions')
    plt.xlabel('Year')
    plt.ylabel('Prediction value')
    plt.grid()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()