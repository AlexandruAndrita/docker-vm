import os
import io
from azure.storage.blob import ContainerClient
from werkzeug.datastructures import FileStorage

def download_from_storage(storage_patient_name, storage_study_instance_uid):
    connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    storage_patient_name = storage_patient_name.lower().replace('_', '-')
    storage_study_instance_uid = storage_study_instance_uid.lower().replace('.', '-')
    container_name = f"{storage_patient_name}-{storage_study_instance_uid}"
    container_client = ContainerClient.from_connection_string(connect_str, container_name)
    blobs = container_client.list_blobs()

    file_objects = []
    for blob in blobs:
        blob_client = container_client.get_blob_client(blob.name)
        stream = io.BytesIO()
        blob_client.download_blob().readinto(stream)
        stream.seek(0)
        filename = blob.name.split('/')[-1]
        file_obj = FileStorage(stream=stream, filename=filename)
        file_objects.append(file_obj)

    return file_objects
    