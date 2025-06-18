document.getElementById("uploadForm").addEventListener("submit", function(event) {
    const input = document.getElementById("dicoms");
    const files = input.files;

    if (files.length < 4) {
        Swal.fire({
            icon: 'warning',
            title: 'Insufficient files',
            text: 'Please select at least four DICOM files.',
            allowOutsideClick: false,
            allowEscapeKey: false,
        });
        event.preventDefault();
        return;
    }

    Swal.fire({
        title: 'Processing...',
        text: 'Please wait while predictions are being computed.',
        allowOutsideClick: false,
        allowEscapeKey: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });
});

function grabImagesFromStorage(){
    Swal.fire({
        title: 'Patient Data',
        showCancelButton: true,
        confirmButtonText: "Continue",
        showLoaderOnConfirm: true,
        allowOutsideClick: false,
        allowEscapeKey: false,
        background: 'linear-gradient(to right, #5e2ced, #a485fd)',
        color: 'white',
        html:
            '<input id="patientName" class="swal2-input" placeholder="Patient Name">' +
            '<input id="studyId" class="swal2-input" placeholder="Study ID">',
        focusConfirm: false,
        customClass:{
            confirmButton: 'select-files-confirm-button',
            cancelButton: 'select-files-cancel-button',
            input: 'select-files-input'
        },
        preConfirm: () => {
            const patientName = document.getElementById('patientName').value.trim();
            const studyId = document.getElementById('studyId').value.trim();
            if (!patientName || !studyId) {
                Swal.showValidationMessage('Both fields are required');
                return false;
            }
            return { patientName, studyId };
        }
    }).then((result) => {
        if (result.isConfirmed) 
        {
            Swal.fire({
                title: 'Processing...',
                text: 'Please wait while predictions are being computed.',
                allowOutsideClick: false,
                allowEscapeKey: false,
                didOpen: () => {
                    Swal.showLoading();
                }
            });

            document.getElementById('storage_patient_name').value = result.value.patientName;
            document.getElementById('storage_study_id').value = result.value.studyId;
            document.getElementById('uploadForm').submit();
        }
    });
}

function uploadImagesToStorage() {
    Swal.fire({
        title: 'Patient Data',
        html:
            '<input id="uploadPatientName" class="swal2-input" placeholder="Patient Name">' +
            '<input id="uploadStudyId" class="swal2-input" placeholder="Study ID">',
        background: 'linear-gradient(to right, #5e2ced, #a485fd)',
        color: 'white',
        confirmButtonText: 'Select Files',
        showCancelButton: true,
        allowOutsideClick: false,
        allowEscapeKey: false,
        customClass: {
            confirmButton: 'select-files-confirm-button',
            cancelButton: 'select-files-cancel-button'
        },
        preConfirm: () => {
            const patient = document.getElementById('uploadPatientName').value.trim().replace(/\s+/g, '_');
            const study = document.getElementById('uploadStudyId').value.trim();
            if (!patient || !study) {
                Swal.showValidationMessage('Both fields are required');
                return false;
            }
            return { patient, study };
        }
    }).then((result) => {
        if (result.isConfirmed) {
            const input = document.getElementById('localDicomFiles');
            input.onchange = () => {
                const files = input.files;
                if (!files || files.length === 0) return;

                const formData = new FormData();
                for (let file of files) {
                    formData.append("dicoms", file);
                }
                formData.append("patient_name", result.value.patient);
                formData.append("study_uid", result.value.study);

                Swal.fire({ title: 'Uploading...', allowOutsideClick: false, didOpen: () => Swal.showLoading() });

                fetch('/upload_to_storage', {
                    method: 'POST',
                    body: formData
                })
                .then(res => res.json())
                .then(data => {
                    Swal.fire(data.success ? 'Uploaded!' : 'Failed', data.message, data.success ? 'success' : 'error');
                })
                .catch(() => Swal.fire('Error', 'Upload failed.', 'error'));
            };

            input.click();
        }
    });
}
