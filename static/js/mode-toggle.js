console.log('🚀 Mode toggle script loaded');

// Mode-specific routing contexts
const modeContexts = {
    student: {
        viewLesson: 'view_lesson',
        editLesson: 'view_lesson', // Students see view instead of edit
        viewModule: 'view_module',
        editModule: 'view_module', // Students see view instead of edit
        actionText: {
            lesson: 'View Lesson',
            module: 'View Module',
            course: 'View Course'
        },
        navigation: {
            dashboard: 'Dashboard',
            modules: 'My Modules',
            lessons: 'My Lessons',
            courses: 'My Courses'
        }
    },
    teacher: {
        viewLesson: 'edit_lesson',
        editLesson: 'edit_lesson',
        viewModule: 'edit_module',
        editModule: 'edit_module',
        actionText: {
            lesson: 'Edit Lesson',
            module: 'Edit Module',
            course: 'Edit Course'
        },
        navigation: {
            dashboard: 'Admin Dashboard',
            modules: 'Manage Modules',
            lessons: 'Manage Lessons',
            courses: 'Manage Courses'
        }
    }
};

// Function to get current page context
function getCurrentPageContext() {
    const path = window.location.pathname;
    const urlParams = new URLSearchParams(window.location.search);
    
    // Extract lesson ID from URL patterns
    const lessonMatch = path.match(/\/view_lesson\/(\d+)/);
    if (lessonMatch) {
        return { type: 'lesson', id: lessonMatch[1], action: 'view' };
    }
    
    const editLessonMatch = path.match(/\/edit_lesson\/(\d+)/);
    if (editLessonMatch) {
        return { type: 'lesson', id: editLessonMatch[1], action: 'edit' };
    }
    
    const moduleMatch = path.match(/\/module\/(\d+)/);
    if (moduleMatch) {
        return { type: 'module', id: moduleMatch[1], action: 'view' };
    }
    
    const editModuleMatch = path.match(/\/edit_module\/(\d+)/);
    if (editModuleMatch) {
        return { type: 'module', id: editModuleMatch[1], action: 'edit' };
    }
    
    const courseMatch = path.match(/\/view_course\/(\d+)/);
    if (courseMatch) {
        return { type: 'course', id: courseMatch[1], action: 'view' };
    }
    
    const editCourseMatch = path.match(/\/edit_course\/(\d+)/);
    if (editCourseMatch) {
        return { type: 'course', id: editCourseMatch[1], action: 'edit' };
    }
    
    return null;
}

// Function to get appropriate URL for mode switch
function getModeAppropriateUrl(currentContext, newMode) {
    if (!currentContext) return null;
    
    const { type, id, action } = currentContext;
    const context = modeContexts[newMode];
    
    if (type === 'lesson') {
        if (newMode === 'teacher') {
            return `/edit_lesson/${id}`;
        } else {
            return `/view_lesson/${id}`;
        }
    }
    
    if (type === 'module') {
        if (newMode === 'teacher') {
            return `/edit_module/${id}`;
        } else {
            return `/module/${id}`;
        }
    }
    
    if (type === 'course') {
        if (newMode === 'teacher') {
            return `/edit_course/${id}`;
        } else {
            return `/view_course/${id}`;
        }
    }
    
    return null;
}

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

        // Get current page context for intelligent routing
        const currentContext = getCurrentPageContext();
        const targetUrl = getModeAppropriateUrl(currentContext, newMode);
        
        console.log('📍 Current context:', currentContext);
        console.log('🎯 Target URL:', targetUrl);

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
            
            // Use intelligent routing if available, otherwise refresh
            if (targetUrl && targetUrl !== window.location.pathname) {
                console.log('🔄 Redirecting to:', targetUrl);
                window.location.href = targetUrl;
            } else {
                console.log('🔄 Refreshing page in 200ms...');
                setTimeout(() => {
                    window.location.reload();
                }, 200);
            }
        })
        .catch(error => {
            console.error('❌ Error toggling mode:', error);
            // Revert the checkbox if the request failed
            modeToggle.checked = !modeToggle.checked;
            isProcessing = false;
        });
    });
});