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
