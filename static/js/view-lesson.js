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

    // Initialize save button state
    saveNotesBtn.disabled = true;

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
        fetch('/api/save_notes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
            },
            body: JSON.stringify({
                lesson_id: lessonData.id,
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
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
                },
                body: JSON.stringify({
                    lesson_id: lessonData.id
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

    // Chat functionality
    const questionForm = document.getElementById('question-form');
    const chatMessages = document.getElementById('chat-messages');
    const chatLoading = document.getElementById('chat-loading');
    const clearChatBtn = document.getElementById('clear-chat');
    let currentEventSource = null;
    let currentAssistantMessageElement = null;

    // Clear chat functionality
    if (clearChatBtn) {
        clearChatBtn.addEventListener('click', function() {
            chatMessages.innerHTML = '';
        });
    }

    // Submit a question
    if (questionForm) {
        questionForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const questionText = document.getElementById('question-text').value;

            if (!questionText.trim()) {
                return;
            }

            const submitBtn = document.getElementById('submit-question');
            const originalBtnText = submitBtn.innerHTML;

            // Add user message to chat
            addChatMessage('user', questionText);

            // Clear input and show loading
            document.getElementById('question-text').value = '';
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="icon-spinner"></i> Asking...';
            chatLoading.style.display = 'block';

            // Close previous event source if exists
            if (currentEventSource) {
                currentEventSource.close();
            }

            // Send the question to server
            fetch('/api/submit_question', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
                },
                body: JSON.stringify({
                    lesson_id: lessonData.id,
                    question: questionText
                })
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(data => {
                        throw new Error(data.error || 'Failed to submit question');
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.thread_id) {
                    // Start listening for SSE events
                    startEventSource(data.thread_id);
                } else {
                    console.error('No thread_id received');
                    chatLoading.style.display = 'none';
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalBtnText;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                chatLoading.style.display = 'none';
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
                
                // Check if it's an API key error
                if (error.message && error.message.includes('API key')) {
                    addChatMessage('assistant', `Error: ${error.message}. Please configure your OpenAI API key in Settings.`);
                    
                    // Add a button to go to settings
                    const settingsBtn = document.createElement('button');
                    settingsBtn.className = 'btn btn-primary btn-small';
                    settingsBtn.textContent = 'Go to Settings';
                    settingsBtn.style.marginTop = '10px';
                    settingsBtn.onclick = () => window.location.href = '/settings';
                    
                    const lastMessage = chatMessages.lastElementChild;
                    if (lastMessage) {
                        lastMessage.appendChild(settingsBtn);
                    }
                } else {
                    // Show generic error message
                    addChatMessage('assistant', 'Sorry, there was an error processing your question. Please try again.');
                }
            });
        });
    }

    function addChatMessage(type, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${type}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        if (type === 'assistant' && content) {
            // Use zero-md for markdown rendering
            const zeroMd = document.createElement('zero-md');
            const scriptTag = document.createElement('script');
            scriptTag.type = 'text/markdown';
            scriptTag.textContent = content;
            zeroMd.appendChild(scriptTag);
            contentDiv.appendChild(zeroMd);
        } else {
            contentDiv.textContent = content;
        }
        
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = new Date().toLocaleTimeString();
        
        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(timeDiv);
        
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        return messageDiv;
    }

    function startEventSource(threadId) {
        let assistantResponse = "";

        // Create a new EventSource
        currentEventSource = new EventSource(`/stream?channel=${threadId}`);

        // Start assistant message
        currentAssistantMessageElement = addChatMessage('assistant', '');

        currentEventSource.addEventListener('message', function(event) {
            const data = event.data;
            console.log('Raw SSE data:', data);

            if (data && currentAssistantMessageElement) {
                // Append to the assistant's message
                assistantResponse += data;

                // Update the message content with markdown rendering
                updateAssistantMessage(assistantResponse);

                // Scroll to bottom
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        });

        currentEventSource.addEventListener('error', function(event) {
            console.error('EventSource error:', event);
            currentEventSource.close();
            chatLoading.style.display = 'none';
            document.getElementById('submit-question').disabled = false;
            document.getElementById('submit-question').innerHTML = '<i class="icon-send"></i> Ask';
        });

        currentEventSource.addEventListener('complete', function(event) {
            console.log('COMPLETE event:', event);
            try {
                const parsedData = JSON.parse(event.data);
                if (parsedData.full_message) {
                    // Update with final message
                    updateAssistantMessage(parsedData.full_message);
                }
            } catch (err) {
                console.error('Error parsing complete event data:', err);
            }

            // Finish up
            currentEventSource.close();
            chatLoading.style.display = 'none';
            document.getElementById('submit-question').disabled = false;
            document.getElementById('submit-question').innerHTML = '<i class="icon-send"></i> Ask';
        });
    }

    function updateAssistantMessage(content) {
        const contentDiv = currentAssistantMessageElement.querySelector('.message-content');
        
        // Clear existing content
        contentDiv.innerHTML = '';
        
        // Create new zero-md element
        const zeroMd = document.createElement('zero-md');
        const scriptTag = document.createElement('script');
        scriptTag.type = 'text/markdown';
        scriptTag.textContent = content;
        zeroMd.appendChild(scriptTag);
        contentDiv.appendChild(zeroMd);
    }
});