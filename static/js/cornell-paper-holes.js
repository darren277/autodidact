// Add paper-hole elements to the document
document.addEventListener('DOMContentLoaded', function() {
    const article = document.querySelector('article');

    // Create left margin holes
    for(let i = 0; i < 3; i++) {
        const hole = document.createElement('div');
        hole.className = 'paper-hole';
        hole.style.left = '10px';
        hole.style.top = (100 + i * 200) + 'px';
        article.appendChild(hole);
    }

    // Add editable functionality to date/topic/class fields
    const rightheader = document.querySelector('.rightheader');
    const originalText = rightheader.textContent;

    // Replace underscores with editable spans
    let newText = originalText.replace(/_+/g, function(match) {
        return '<span class="editable" contenteditable="true" style="border-bottom: 1px solid #333; min-width: 60px; display: inline-block;">&nbsp;</span>';
    });

    rightheader.innerHTML = newText;
});