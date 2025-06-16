document.getElementById("uploadForm").addEventListener("submit", function(event) {
    const input = document.getElementById("dicoms");
    const files = input.files;

    if (files.length < 4) {
        Swal.fire({
            icon: 'warning',
            title: 'Insufficient files',
            text: 'Please select at least four DICOM files.',
            allowOutsideClick: false,
            allowEscapeKey: false
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
        title: 'Patient Information',
        showCancelButton: true,
        confirmButtonText: "Continue",
        showLoaderOnConfirm: true,
        allowOutsideClick: false,
        allowEscapeKey: false,
        background: 'linear-gradient(to right, #5e2ced, #a485fd)',
        color: 'white',
        html:
            '<input id="patientName" class="swal2-input" placeholder="Patient Name">' +
            '<input id="studyId" class="swal2-input" placeholder="Study Instance UID">',
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
        if (result.isConfirmed) {
            document.getElementById('storage_patient_name').value = result.value.patientName;
            document.getElementById('storage_study_uid').value = result.value.studyId;
            document.getElementById('uploadForm').submit();
        }
    });
}