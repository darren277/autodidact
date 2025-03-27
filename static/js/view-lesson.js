document.addEventListener('DOMContentLoaded', function() {
    // Tab switching
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabName = this.dataset.tab;

            // Deactivate all tabs
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // Activate selected tab
            this.classList.add('active');
            document.getElementById(`tab-${tabName}`).classList.add('active');
        });
    });

    // Table of Contents generation
    const tocContainer = document.getElementById('toc-content');
    const lessonContent = document.querySelector('.lesson-content');

    if (lessonContent) {
        // Find all headings in the content
        const headings = lessonContent.querySelectorAll('h2, h3, h4');

        if (headings.length > 0) {
            const tocList = document.createElement('ul');

            headings.forEach((heading, index) => {
                // Add ID to the heading if it doesn't have one
                if (!heading.id) {
                    heading.id = `heading-${index}`;
                }

                const listItem = document.createElement('li');
                const link = document.createElement('a');
                link.href = `#${heading.id}`;
                link.textContent = heading.textContent;
                link.className = `toc-${heading.tagName.toLowerCase()}`;
                link.dataset.target = heading.id;

                listItem.appendChild(link);
                tocList.appendChild(listItem);
            });

            tocContainer.innerHTML = '';
            tocContainer.appendChild(tocList);

            // Scroll spy for TOC
            const tocLinks = tocContainer.querySelectorAll('a');

            function highlightToc() {
                const scrollPosition = window.scrollY;

                // Find the current heading
                for (let i = headings.length - 1; i >= 0; i--) {
                    const heading = headings[i];

                    if (scrollPosition >= heading.offsetTop - 100) {
                        // Remove active class from all links
                        tocLinks.forEach(link => link.classList.remove('active'));

                        // Add active class to current link
                        const currentLink = tocContainer.querySelector(`a[data-target="${heading.id}"]`);
                        if (currentLink) {
                            currentLink.classList.add('active');
                        }
                        break;
                    }
                }
            }

            // Smooth scroll for TOC links
            tocLinks.forEach(link => {
                link.addEventListener('click', function(e) {
                    e.preventDefault();

                    const targetId = this.getAttribute('href').substring(1);
                    const targetElement = document.getElementById(targetId);

                    if (targetElement) {
                        window.scrollTo({
                            top: targetElement.offsetTop - 80,
                            behavior: 'smooth'
                        });
                    }
                });
            });

            window.addEventListener('scroll', highlightToc);
            highlightToc(); // Initial highlight
        } else {
            tocContainer.innerHTML = '<p>No table of contents available for this lesson.</p>';
        }
    }

    // Notes functionality
    const notesTextarea = document.getElementById('user-notes');
    const saveNotesBtn = document.getElementById('save-notes');
    const notesStatus = document.getElementById('notes-status');
    let originalNotes = notesTextarea.value;

    notesTextarea.addEventListener('input', function() {
        // Enable save button if content has changed
        saveNotesBtn.disabled = notesTextarea.value === originalNotes;
    });

    // Save notes
    saveNotesBtn.addEventListener('click', function() {
        const noteContent = notesTextarea.value;

        // Display saving status
        notesStatus.className = '';
        notesStatus.textContent = 'Saving...';

        // Send to server
        fetch('/api/save-notes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                lesson_id: '{{ lesson.id }}',
                content: noteContent
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to save notes');
            }
            return response.json();
        })
        .then(data => {
            notesStatus.className = 'success';
            notesStatus.textContent = 'Notes saved!';
            originalNotes = noteContent;
            saveNotesBtn.disabled = true;

            // Clear status after 3 seconds
            setTimeout(() => {
                notesStatus.textContent = '';
                notesStatus.className = '';
            }, 3000);
        })
        .catch(error => {
            notesStatus.className = 'error';
            notesStatus.textContent = 'Error saving notes';
            console.error('Error saving notes:', error);

            // Clear status after 3 seconds
            setTimeout(() => {
                notesStatus.textContent = '';
                notesStatus.className = '';
            }, 3000);
        });
    });

    // Mark lesson as complete
    const completeBtn = document.querySelector('.btn-progress[data-action="mark-complete"]');

    if (completeBtn && !completeBtn.disabled) {
        completeBtn.addEventListener('click', function() {
            completeBtn.disabled = true;
            completeBtn.innerHTML = '<i class="icon-spinner"></i> Updating...';

            fetch('/api/mark-lesson-complete', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    lesson_id: '{{ lesson.id }}'
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to mark lesson as complete');
                }
                return response.json();
            })
            .then(data => {
                completeBtn.innerHTML = '<i class="icon-check"></i> Completed';

                // Update progress indicator
                const progressIndicator = document.querySelector('.progress-indicator');
                progressIndicator.style.width = data.new_percentage + '%';
                progressIndicator.querySelector('.progress-text').textContent = data.new_percentage + '% Complete';
            })
            .catch(error => {
                completeBtn.disabled = false;
                completeBtn.textContent = 'Mark as Complete';
                console.error('Error marking lesson complete:', error);
                alert('There was an error updating your progress. Please try again.');
            });
        });
    }

    // Submit a question
    const questionForm = document.getElementById('question-form');

    if (questionForm) {
        questionForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const questionText = document.getElementById('question-text').value;

            if (!questionText.trim()) {
                return;
            }

            const submitBtn = questionForm.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.textContent;

            submitBtn.disabled = true;
            submitBtn.textContent = 'Submitting...';

            fetch('/api/submit-question', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    lesson_id: '{{ lesson.id }}',
                    question: questionText
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to submit question');
                }
                return response.json();
            })
            .then(data => {
                document.getElementById('question-text').value = '';

                // Show success message
                const successDiv = document.createElement('div');
                successDiv.className = 'success-message';
                successDiv.textContent = 'Your question has been submitted successfully. An instructor will respond soon.';

                questionForm.appendChild(successDiv);

                // Reset button
                submitBtn.disabled = false;
                submitBtn.textContent = originalBtnText;

                // Remove success message after 5 seconds
                setTimeout(() => {
                    successDiv.remove();
                }, 5000);
            })
            .catch(error => {
                console.error('Error submitting question:', error);

                // Show error message
                const errorDiv = document.createElement('div');
                errorDiv.className = 'error-message';
                errorDiv.textContent = 'There was an error submitting your question. Please try again.';

                questionForm.appendChild(errorDiv);

                // Reset button
                submitBtn.disabled = false;
                submitBtn.textContent = originalBtnText;

                // Remove error message after 5 seconds
                setTimeout(() => {
                    errorDiv.remove();
                }, 5000);
            });
        });
    }
});