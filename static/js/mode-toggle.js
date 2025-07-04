// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    const modeToggle = document.getElementById('mode-toggle');
    const modeToggleLabel = document.querySelector('.mode-toggle-label-text');

    console.log('Mode toggle script loaded');
    console.log('Mode toggle element:', modeToggle);
    console.log('Mode toggle label:', modeToggleLabel);
    console.log('Mode toggle endpoint:', typeof modeToggleEndpoint !== 'undefined' ? modeToggleEndpoint : 'undefined');

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

    // Set initial state based on current mode
    const currentMode = modeToggleLabel.textContent.toLowerCase();
    console.log('Current mode:', currentMode);
    
    if (currentMode === 'teacher') {
        modeToggle.checked = true;
        modeToggleLabel.className = 'mode-toggle-label-text teacher';
    } else {
        modeToggle.checked = false;
        modeToggleLabel.className = 'mode-toggle-label-text student';
    }

    // Add event listener
    modeToggle.addEventListener('change', function() {
        console.log('Mode toggle changed');
        
        const csrfToken = document.querySelector('meta[name="csrf-token"]');
        if (!csrfToken) {
            console.error('CSRF token not found');
            return;
        }

        const newMode = modeToggle.checked ? 'teacher' : 'student';
        console.log('Switching to mode:', newMode);
        
        // Update label immediately
        if (modeToggle.checked) {
            modeToggleLabel.textContent = 'Teacher';
            modeToggleLabel.className = 'mode-toggle-label-text teacher';
        } else {
            modeToggleLabel.textContent = 'Student';
            modeToggleLabel.className = 'mode-toggle-label-text student';
        }

        // Update body class
        document.body.className = document.body.className.replace(/mode-\w+/g, '');
        document.body.classList.add(`mode-${newMode}`);

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
            console.log('Response status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Mode toggled successfully:', data);
            // Update UI context
            updateUIContext(newMode);
        })
        .catch(error => {
            console.error('Error toggling mode:', error);
            // Revert the UI if the request failed
            modeToggle.checked = !modeToggle.checked;
            const revertedMode = modeToggle.checked ? 'teacher' : 'student';
            
            if (modeToggle.checked) {
                modeToggleLabel.textContent = 'Teacher';
                modeToggleLabel.className = 'mode-toggle-label-text teacher';
            } else {
                modeToggleLabel.textContent = 'Student';
                modeToggleLabel.className = 'mode-toggle-label-text student';
            }
            
            document.body.className = document.body.className.replace(/mode-\w+/g, '');
            document.body.classList.add(`mode-${revertedMode}`);
        });
    });

    // Mode-specific UI mappings
    const modeContexts = {
        student: {
            viewLesson: 'view_lesson',
            editLesson: 'view_lesson', // Students see view instead of edit
            viewModule: 'view_module',
            editModule: 'view_module', // Students see view instead of edit
            actionText: {
                lesson: 'View Lesson',
                module: 'View Module',
                create: 'Create New',
                edit: 'View',
                delete: 'Delete'
            },
            navigation: {
                dashboard: 'Dashboard',
                modules: 'My Modules',
                lessons: 'My Lessons',
                admin: 'Settings'
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
                create: 'Create New',
                edit: 'Edit',
                delete: 'Delete'
            },
            navigation: {
                dashboard: 'Admin Dashboard',
                modules: 'Manage Modules',
                lessons: 'Manage Lessons',
                admin: 'Admin Settings'
            }
        }
    };

    // Function to update UI context based on mode
    function updateUIContext(mode) {
        console.log('Updating UI context for mode:', mode);
        const context = modeContexts[mode];
        
        // Update navigation links and text
        updateNavigationContext(context);
        
        // Update lesson and module action buttons
        updateActionButtons(context);
        
        // Update page titles and breadcrumbs
        updatePageContext(context);
        
        // Update form actions and buttons
        updateFormContext(context);
    }

    // Update navigation context
    function updateNavigationContext(context) {
        // Update sidebar navigation text
        const sidebarLinks = document.querySelectorAll('.side-menu a');
        sidebarLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href && href.includes('dashboard')) {
                link.textContent = context.navigation.dashboard;
            } else if (href && href.includes('module')) {
                link.textContent = context.navigation.modules;
            } else if (href && href.includes('lesson')) {
                link.textContent = context.navigation.lessons;
            }
        });
        
        // Update top navigation
        const topNavLinks = document.querySelectorAll('.top-nav a');
        topNavLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href && href.includes('dashboard')) {
                link.textContent = context.navigation.dashboard;
            }
        });
    }

    // Update action buttons
    function updateActionButtons(context) {
        // Update lesson action buttons
        const lessonButtons = document.querySelectorAll('a[href*="lesson"], button[data-action*="lesson"]');
        lessonButtons.forEach(button => {
            const href = button.getAttribute('href');
            if (href) {
                if (href.includes('view_lesson') && context.viewLesson !== 'view_lesson') {
                    button.href = href.replace('view_lesson', context.viewLesson);
                } else if (href.includes('edit_lesson') && context.editLesson !== 'edit_lesson') {
                    button.href = href.replace('edit_lesson', context.editLesson);
                }
            }
            
            // Update button text
            if (button.textContent.includes('View Lesson')) {
                button.textContent = context.actionText.lesson;
            } else if (button.textContent.includes('Edit Lesson')) {
                button.textContent = context.actionText.lesson;
            }
        });
        
        // Update module action buttons
        const moduleButtons = document.querySelectorAll('a[href*="module"], button[data-action*="module"]');
        moduleButtons.forEach(button => {
            const href = button.getAttribute('href');
            if (href) {
                if (href.includes('view_module') && context.viewModule !== 'view_module') {
                    button.href = href.replace('view_module', context.viewModule);
                } else if (href.includes('edit_module') && context.editModule !== 'edit_module') {
                    button.href = href.replace('edit_module', context.editModule);
                }
            }
            
            // Update button text
            if (button.textContent.includes('View Module')) {
                button.textContent = context.actionText.module;
            } else if (button.textContent.includes('Edit Module')) {
                button.textContent = context.actionText.module;
            }
        });
    }

    // Update page context
    function updatePageContext(context) {
        // Update page titles
        const pageTitle = document.querySelector('.page-title');
        if (pageTitle) {
            if (pageTitle.textContent.includes('View Lesson') && context.viewLesson === 'edit_lesson') {
                pageTitle.textContent = pageTitle.textContent.replace('View Lesson', 'Edit Lesson');
            } else if (pageTitle.textContent.includes('Edit Lesson') && context.editLesson === 'view_lesson') {
                pageTitle.textContent = pageTitle.textContent.replace('Edit Lesson', 'View Lesson');
            }
            
            if (pageTitle.textContent.includes('View Module') && context.viewModule === 'edit_module') {
                pageTitle.textContent = pageTitle.textContent.replace('View Module', 'Edit Module');
            } else if (pageTitle.textContent.includes('Edit Module') && context.editModule === 'view_module') {
                pageTitle.textContent = pageTitle.textContent.replace('Edit Module', 'View Module');
            }
        }
        
        // Update breadcrumbs
        const breadcrumbLinks = document.querySelectorAll('.breadcrumb a');
        breadcrumbLinks.forEach(link => {
            if (link.textContent.includes('View') && context.viewLesson === 'edit_lesson') {
                link.textContent = link.textContent.replace('View', 'Edit');
            } else if (link.textContent.includes('Edit') && context.editLesson === 'view_lesson') {
                link.textContent = link.textContent.replace('Edit', 'View');
            }
        });
    }

    // Update form context
    function updateFormContext(context) {
        // Update form submit buttons
        const submitButtons = document.querySelectorAll('button[type="submit"]');
        submitButtons.forEach(button => {
            if (button.textContent.includes('Save') && context.viewLesson === 'view_lesson') {
                // Hide save buttons for students
                button.style.display = 'none';
            } else if (button.textContent.includes('Save') && context.viewLesson === 'edit_lesson') {
                // Show save buttons for teachers
                button.style.display = 'inline-block';
            }
        });
        
        // Update form fields - make them read-only for students
        const formInputs = document.querySelectorAll('input, textarea, select');
        if (context.viewLesson === 'view_lesson') {
            formInputs.forEach(input => {
                if (input.type !== 'hidden' && input.type !== 'submit' && input.type !== 'button') {
                    input.readOnly = true;
                    input.disabled = true;
                }
            });
        } else {
            formInputs.forEach(input => {
                if (input.type !== 'hidden' && input.type !== 'submit' && input.type !== 'button') {
                    input.readOnly = false;
                    input.disabled = false;
                }
            });
        }
    }

    // Initialize UI context on page load
    if (currentMode) {
        updateUIContext(currentMode);
    }
});