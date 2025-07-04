const modeToggle = document.getElementById('mode-toggle');
const modeToggleLabel = document.querySelector('.mode-toggle-label-text');

// Set initial state based on current mode
if (modeToggleLabel && modeToggle) {
    const currentMode = modeToggleLabel.textContent.toLowerCase();
    if (currentMode === 'teacher') {
        modeToggle.checked = true;
        modeToggleLabel.className = 'mode-toggle-label-text teacher';
    } else {
        modeToggle.checked = false;
        modeToggleLabel.className = 'mode-toggle-label-text student';
    }
}

if (modeToggle) {
    modeToggle.addEventListener('change', () => {
        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
        
        if (modeToggle.checked) {
            modeToggleLabel.textContent = 'Teacher';
            modeToggleLabel.className = 'mode-toggle-label-text teacher';
        } else {
            modeToggleLabel.textContent = 'Student';
            modeToggleLabel.className = 'mode-toggle-label-text student';
        }

        fetch(modeToggleEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ mode: modeToggle.checked ? 'teacher' : 'student' })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Mode toggled successfully:', data);
        })
        .catch(error => {
            console.error('Error toggling mode:', error);
            // Revert the UI if the request failed
            modeToggle.checked = !modeToggle.checked;
            if (modeToggle.checked) {
                modeToggleLabel.textContent = 'Teacher';
                modeToggleLabel.className = 'mode-toggle-label-text teacher';
            } else {
                modeToggleLabel.textContent = 'Student';
                modeToggleLabel.className = 'mode-toggle-label-text student';
            }
        });
    });
}