// ============================================================
// Form & File Upload Client-side Validations
// ============================================================

function validateForm(formElement) {
    const inputs = formElement.querySelectorAll('[required]');
    let valid = true;

    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.style.borderColor = '#ff5252';
            valid = false;
        } else {
            input.style.borderColor = 'rgba(255, 255, 255, 0.2)';
        }
    });

    return valid;
}

function validateFileInput(inputElement) {
    const file = inputElement.files[0];
    if (file) {
        const allowed = ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'];
        const ext = file.name.split('.').pop().toLowerCase();
        
        if (!allowed.includes(ext)) {
            alert(`Invalid file extension '.${ext}'. Allowed formats: ${allowed.join(', ')}`);
            inputElement.value = '';
            return false;
        }

        // 16 MB limit check
        if (file.size > 16 * 1024 * 1024) {
            alert('File size exceeds maximum limit of 16MB.');
            inputElement.value = '';
            return false;
        }
    }
    return true;
}
