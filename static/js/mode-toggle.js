console.log('🚀 Mode toggle script loaded');

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('📄 DOM loaded, initializing mode toggle');
    const modeToggle = document.getElementById('mode-toggle');
    const modeToggleLabel = document.querySelector('.mode-toggle-label-text');

    // Check if elements exist
    if (!modeToggle) {
        console.error('Mode toggle checkbox not found');
        return;
    }

    if (!modeToggleLabel) {
        console.error('Mode toggle label not found');
        return;
    }

    if (typeof modeToggleEndpoint === 'undefined') {
        console.error('Mode toggle endpoint not defined');
        return;
    }

    // Set initial state based on current mode from server
    const currentMode = modeToggleLabel.textContent.toLowerCase();
    
    if (currentMode === 'teacher') {
        modeToggle.checked = true;
        modeToggleLabel.className = 'mode-toggle-label-text teacher';
    } else {
        modeToggle.checked = false;
        modeToggleLabel.className = 'mode-toggle-label-text student';
    }

    // Add click event listener to the label
    const modeToggleLabelElement = document.querySelector('.mode-toggle-label');
    if (modeToggleLabelElement) {
        modeToggleLabelElement.addEventListener('click', function(e) {
            e.stopPropagation();
            // Manually toggle the checkbox
            modeToggle.checked = !modeToggle.checked;
            // Trigger the change event manually
            modeToggle.dispatchEvent(new Event('change'));
        });
    }
    
    // Add event listener for the change event
    let isProcessing = false; // Prevent multiple simultaneous requests
    
    modeToggle.addEventListener('change', function() {
        if (isProcessing) {
            console.log('⚠️ Request already in progress, ignoring click');
            return;
        }
        
        console.log('🔄 Mode toggle clicked - checkbox checked:', modeToggle.checked);
        isProcessing = true;
        
        const csrfToken = document.querySelector('meta[name="csrf-token"]');
        if (!csrfToken) {
            console.error('CSRF token not found');
            isProcessing = false;
            return;
        }

        const newMode = modeToggle.checked ? 'teacher' : 'student';
        console.log('🔄 Sending request to switch to mode:', newMode);

        // Send request to server
        fetch(modeToggleEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken.getAttribute('content')
            },
            body: JSON.stringify({ mode: newMode })
        })
        .then(response => {
            console.log('📡 Response status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('✅ Server response:', data);
            console.log('🔄 Refreshing page in 200ms...');
            // Add a longer delay to ensure session is saved before refreshing
            setTimeout(() => {
                window.location.reload();
            }, 200);
        })
        .catch(error => {
            console.error('❌ Error toggling mode:', error);
            // Revert the checkbox if the request failed
            modeToggle.checked = !modeToggle.checked;
            isProcessing = false;
        });
    });






});