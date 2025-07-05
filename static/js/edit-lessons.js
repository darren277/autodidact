document.addEventListener('DOMContentLoaded', function() {
    // Learning Objectives (for lessons)
    const objectivesList = document.getElementById('learning-objectives-list');
    const addObjectiveBtn = document.getElementById('add-objective');

    if (addObjectiveBtn && objectivesList) {
        addObjectiveBtn.addEventListener('click', function() {
            const newObjective = document.createElement('div');
            newObjective.className = 'objective-item';
            newObjective.innerHTML = `
                <input type="text" name="learning_objectives[]" class="form-control" placeholder="Learning objective">
                <button type="button" class="remove-objective" title="Remove objective">✕</button>
            `;
            objectivesList.appendChild(newObjective);

            // Focus on the new input
            const input = newObjective.querySelector('input');
            input.focus();
        });
    }

    // Learning Outcomes (for modules)
    const outcomesList = document.getElementById('learning-outcomes-list');
    const addOutcomeBtn = document.getElementById('add-outcome');

    if (addOutcomeBtn && outcomesList) {
        addOutcomeBtn.addEventListener('click', function() {
            const newOutcome = document.createElement('div');
            newOutcome.className = 'objective-item';
            newOutcome.innerHTML = `
                <input type="text" name="learning_outcomes[]" class="form-control" placeholder="Learning outcome">
                <button type="button" class="remove-objective" title="Remove outcome">✕</button>
            `;
            outcomesList.appendChild(newOutcome);

            // Focus on the new input
            const input = newOutcome.querySelector('input');
            input.focus();
        });
    }

    // Remove objective handlers (including existing ones)
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-objective')) {
            const objectiveItem = e.target.closest('.objective-item');
            if (objectivesList.children.length > 1) {
                objectiveItem.remove();
            } else {
                // If it's the last one, just clear the input
                const input = objectiveItem.querySelector('input');
                input.value = '';
            }
        }
    });

    // Tab switching in editor
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    if (tabButtons.length > 0) {
        tabButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Deactivate all tabs
                tabButtons.forEach(btn => btn.classList.remove('active'));
                tabContents.forEach(content => content.classList.remove('active'));

                // Activate the clicked tab
                const tabName = this.dataset.tab;
                this.classList.add('active');
                const targetTab = document.getElementById(`tab-${tabName}`);
                if (targetTab) {
                    targetTab.classList.add('active');
                }
            });
        });
    }

    // Preview toggle
    const togglePreviewBtn = document.getElementById('toggle-preview');
    const markdownPreview = document.getElementById('markdown-preview');
    const editorContainer = document.querySelector('.editor-container');

    if (togglePreviewBtn && markdownPreview && editorContainer) {
        togglePreviewBtn.addEventListener('click', function() {
            const activeTab = document.querySelector('.tab-content.active');
            if (!activeTab) return;
            
            const activeTextarea = activeTab.querySelector('textarea');
            if (!activeTextarea) return;

            if (markdownPreview.style.display === 'block') {
                // Hide preview
                markdownPreview.style.display = 'none';
                activeTab.style.display = 'block';
                togglePreviewBtn.textContent = 'Preview';
            } else {
                // Show preview
                markdownPreview.style.display = 'block';
                activeTab.style.display = 'none';
                togglePreviewBtn.textContent = 'Edit';

                // Convert markdown to HTML (simplified - you'd use a proper library)
                markdownPreview.innerHTML = convertMarkdownToHTML(activeTextarea.value);
            }
        });
    }

    // Markdown help toggle
    const toggleMarkdownHelpBtn = document.getElementById('toggle-markdown-help');
    const markdownHelpPanel = document.getElementById('markdown-help-panel');

    if (toggleMarkdownHelpBtn && markdownHelpPanel) {
        toggleMarkdownHelpBtn.addEventListener('click', function() {
            if (markdownHelpPanel.style.display === 'block') {
                markdownHelpPanel.style.display = 'none';
            } else {
                markdownHelpPanel.style.display = 'block';
            }
        });
    }

    // Hide markdown help panel when clicking outside
    if (markdownHelpPanel) {
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.markdown-help') && markdownHelpPanel.style.display === 'block') {
                markdownHelpPanel.style.display = 'none';
            }
        });
    }

    // Featured image preview
    const featuredImageInput = document.getElementById('featured_image');
    const featuredImagePreview = document.getElementById('featured-image-preview');
    const removeFeaturedImageBtn = document.getElementById('remove-featured-image');
    const removeFeaturedImageInput = document.getElementById('remove_featured_image');

    if (featuredImageInput && featuredImagePreview) {
        featuredImageInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();

                reader.onload = function(e) {
                    featuredImagePreview.innerHTML = `<img src="${e.target.result}" alt="Featured image">`;
                    featuredImagePreview.classList.add('has-image');

                    if (removeFeaturedImageInput) {
                        removeFeaturedImageInput.value = "0";
                    }
                };

                reader.readAsDataURL(this.files[0]);
            }
        });
    }

    if (removeFeaturedImageBtn && featuredImagePreview && featuredImageInput) {
        removeFeaturedImageBtn.addEventListener('click', function() {
            featuredImagePreview.innerHTML = `<div class="placeholder-text">No image selected</div>`;
            featuredImagePreview.classList.remove('has-image');
            featuredImageInput.value = '';
            if (removeFeaturedImageInput) {
                removeFeaturedImageInput.value = "1";
            }
        });
    }

    // Attachment file upload
    const attachmentFilesInput = document.getElementById('attachment_files');
    const attachmentsContainer = document.getElementById('attachments-container');

    if (attachmentFilesInput && attachmentsContainer) {
        attachmentFilesInput.addEventListener('change', function() {
            if (this.files && this.files.length > 0) {
                for (let i = 0; i < this.files.length; i++) {
                    const file = this.files[i];
                    const fileSize = formatFileSize(file.size);

                    const newAttachment = document.createElement('div');
                    newAttachment.className = 'attachment-item';
                    newAttachment.dataset.name = file.name;
                    newAttachment.innerHTML = `
                        <div class="attachment-icon">
                            <i class="icon-file"></i>
                        </div>
                        <div class="attachment-info">
                            <div class="attachment-name">${file.name}</div>
                            <div class="attachment-size">${fileSize}</div>
                        </div>
                        <div class="attachment-actions">
                            <button type="button" class="remove-new-attachment btn-text-small">
                                <i class="icon-trash-small"></i>
                            </button>
                        </div>
                    `;
                    attachmentsContainer.appendChild(newAttachment);
                }
            }
        });
    }

    // Remove attachment handlers
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-attachment') ||
            e.target.closest('.remove-attachment')) {
            const button = e.target.classList.contains('remove-attachment') ?
                  e.target : e.target.closest('.remove-attachment');
            const attachmentId = button.dataset.id;
            const attachmentItem = button.closest('.attachment-item');

            // Create a hidden input to track which attachments to remove
            const removeInput = document.createElement('input');
            removeInput.type = 'hidden';
            removeInput.name = 'remove_attachments[]';
            removeInput.value = attachmentId;
            document.getElementById('lesson-form').appendChild(removeInput);

            attachmentItem.remove();
        }

        if (e.target.classList.contains('remove-new-attachment') ||
            e.target.closest('.remove-new-attachment')) {
            const button = e.target.classList.contains('remove-new-attachment') ?
                  e.target : e.target.closest('.remove-new-attachment');
            const attachmentItem = button.closest('.attachment-item');
            attachmentItem.remove();
        }
    });

    // Helper function to format file size
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';

        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));

        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Very simplified markdown conversion (you'd use a proper library)
    function convertMarkdownToHTML(markdown) {
        if (!markdown) return '';

        // Headers
        markdown = markdown.replace(/^# (.*$)/gm, '<h1>$1</h1>');
        markdown = markdown.replace(/^## (.*$)/gm, '<h2>$1</h2>');
        markdown = markdown.replace(/^### (.*$)/gm, '<h3>$1</h3>');

        // Bold and italic
        markdown = markdown.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        markdown = markdown.replace(/\*(.*?)\*/g, '<em>$1</em>');

        // Links
        markdown = markdown.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2">$1</a>');

        // Images
        markdown = markdown.replace(/!\[(.*?)\]\((.*?)\)/g, '<img src="$2" alt="$1">');

        // Lists
        markdown = markdown.replace(/^\s*\*\s(.*$)/gm, '<li>$1</li>');
        markdown = markdown.replace(/^\s*\d\.\s(.*$)/gm, '<li>$1</li>');

        // Code blocks
        markdown = markdown.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');

        // Blockquotes
        markdown = markdown.replace(/^\>\s(.*$)/gm, '<blockquote>$1</blockquote>');

        // Paragraphs
        markdown = markdown.replace(/^(?!<[a-z])(.*$)/gm, function(m) {
            if (m.trim() === '') return '';
            return '<p>' + m + '</p>';
        });

        // Convert line breaks
        markdown = markdown.replace(/\n/g, ' ');

        return markdown;
    }

    // Fullscreen toggle
    const toggleFullscreenBtn = document.getElementById('toggle-fullscreen');
    const editorTabs = document.getElementById('editor-tabs');

    if (toggleFullscreenBtn && editorContainer && editorTabs) {
        toggleFullscreenBtn.addEventListener('click', function() {
            editorContainer.classList.toggle('fullscreen');

            if (editorContainer.classList.contains('fullscreen')) {
                editorContainer.style.position = 'fixed';
                editorContainer.style.top = '0';
                editorContainer.style.left = '0';
                editorContainer.style.width = '100%';
                editorContainer.style.height = '100%';
                editorContainer.style.zIndex = '1000';
                editorContainer.style.backgroundColor = 'white';
                editorTabs.style.position = 'sticky';
                editorTabs.style.top = '0';
                document.body.style.overflow = 'hidden';

                // Expand the active textarea
                const activeTab = document.querySelector('.tab-content.active');
                if (activeTab) {
                    const activeTextarea = activeTab.querySelector('textarea');
                    if (activeTextarea) {
                        activeTextarea.style.height = 'calc(100vh - 100px)';
                    }
                }

                // Change icon
                this.innerHTML = '<i class="icon-exit-fullscreen"></i>';
            } else {
                editorContainer.style.position = '';
                editorContainer.style.top = '';
                editorContainer.style.left = '';
                editorContainer.style.width = '';
                editorContainer.style.height = '';
                editorContainer.style.zIndex = '';
                editorContainer.style.backgroundColor = '';
                editorTabs.style.position = '';
                editorTabs.style.top = '';
                document.body.style.overflow = '';

                // Reset textarea height
                const activeTab = document.querySelector('.tab-content.active');
                if (activeTab) {
                    const activeTextarea = activeTab.querySelector('textarea');
                    if (activeTextarea) {
                        activeTextarea.style.height = '';
                    }
                }

                // Change icon back
                this.innerHTML = '<i class="icon-fullscreen"></i>';
            }
        });
    }
});