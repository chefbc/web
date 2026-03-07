document.addEventListener("DOMContentLoaded", function() {
    const forms = document.querySelectorAll('form.zensical-form');
    
    forms.forEach(form => {
        const messageDiv = document.getElementById('zensical-form-message-default');
        const submitBtn = form.querySelector('.zensical-form-submit');
        const recaptchaSiteKey = form.dataset.recaptchaSiteKey;

        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Basic Honeypot Check
            const hpField = form.querySelector('input[name="zensical_hp_field"]');
            if (hpField && hpField.value) {
                console.warn('Honeypot field filled. Blocking submission.');
                return;
            }

            // Client-side validation for files
            const fileInputs = form.querySelectorAll('input[type="file"]');
            for (const input of fileInputs) {
                const files = input.files;
                if (files.length > 0) {
                    const file = files[0];
                    const allowedExts = input.accept ? input.accept.split(',').map(ext => ext.trim().toLowerCase()) : [];
                    const maxSizeMB = parseFloat(input.dataset.maxSize) || 5;
                    
                    const ext = `.${file.name.split('.').pop().toLowerCase()}`;
                    if (allowedExts.length > 0 && !allowedExts.includes(ext)) {
                        showMessage(messageDiv, `Invalid file type: ${ext}. Allowed: ${allowedExts.join(', ')}`, 'error');
                        return;
                    }
                    
                    if (file.size > maxSizeMB * 1024 * 1024) {
                        showMessage(messageDiv, `File is too large: ${(file.size / (1024 * 1024)).toFixed(2)} MB. Max allowed: ${maxSizeMB} MB.`, 'error');
                        return;
                    }
                }
            }

            setLoading(submitBtn, true);
            
            try {
                // Execute reCAPTCHA if enabled
                let recaptchaToken = '';
                if (typeof grecaptcha !== 'undefined' && recaptchaSiteKey) {
                    recaptchaToken = await new Promise((resolve, reject) => {
                        grecaptcha.ready(function() {
                            grecaptcha.execute(recaptchaSiteKey, {action: 'submit'}).then(resolve).catch(reject);
                        });
                    });
                    form.querySelector('input[name="recaptcha_token"]').value = recaptchaToken;
                }

                const formData = new FormData(form);
                const response = await fetch(form.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'Accept': 'application/json'
                    }
                });

                if (response.ok) {
                    const config = JSON.parse(form.dataset.onSuccess);
                    if (config.type === 'redirect') {
                        window.location.href = config.value;
                    } else {
                        showMessage(messageDiv, config.value || 'Success!', 'success');
                        form.reset();
                    }
                } else {
                    const error = await response.json().catch(() => ({}));
                    showMessage(messageDiv, error.message || 'Error submitting form. Please try again.', 'error');
                }
            } catch (err) {
                console.error('Submission Error:', err);
                showMessage(messageDiv, 'An unexpected error occurred. Please try again later.', 'error');
            } finally {
                setLoading(submitBtn, false);
            }
        });
    });

    function showMessage(div, msg, type) {
        div.textContent = msg;
        div.className = `zensical-form-message ${type}`;
        div.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    function setLoading(btn, isLoading) {
        btn.disabled = isLoading;
        btn.textContent = isLoading ? 'Submitting...' : 'Submit';
        btn.style.opacity = isLoading ? '0.7' : '1';
    }
});
