/**
   * Gathers the page content in a hierarchical structure.
   * You can adapt this to suit your own HTML structure and naming conventions.
*/
function gatherPageContent() {
    const headerCues = document.querySelector('.leftheader')?.innerText || '';
    const headerMeta = document.querySelector('.rightheader')?.innerText || '';

    const leftmargins = [...document.querySelectorAll('.leftmargin')].map(el => el.innerText);
    const mains = [...document.querySelectorAll('.main')].map(el => el.innerText);

    const summaryBox = document.querySelector('footer .summary-box')?.innerText || '';

    // Build a structured object. Feel free to add more fields or rearrange as needed.
    const structuredNotes = {
        header: {cues: headerCues, metadata: headerMeta},
        sections: leftmargins.map((cue, idx) => ({cue, content: mains[idx] || ''})),
        overallSummary: summaryBox
    };

    return structuredNotes;
}

document.getElementById('summarizeBtn').addEventListener('click', async () => {
    // 1. System prompt for LLM
    const systemPrompt = `
You are a helpful AI assistant.
Given the user's study notes, please:
1) Provide an overall summary.
2) Highlight key points.
3) Offer metacognition tips for effective memory retention.
4) Suggest any relevant mnemonics.
    `;

    // 2. Gather the page content in a structured form
    const notesData = gatherPageContent();

    // 3. Structure payload object
    const payload = {systemPrompt, userNotes: notesData};

    try {
        // 4. Send the request to LLM endpoint
        const response = await fetch('/summarize', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });

        // 5. Parse the server's response (assumed to be in JSON)
        const data = await response.json();

        // 6. Populate the new div (#aiSummary) with the returned text
        const aiSummaryDiv = document.getElementById('aiSummary');
        aiSummaryDiv.textContent = data.summary || 'No summary returned.';

        // If you return multiple fields (e.g., key points, mnemonics, etc.),
        // you could also structure them in HTML here:
        //
        // aiSummaryDiv.innerHTML = `
        //   <h3>Overall Summary</h3>
        //   <p>${data.overallSummary}</p>
        //   <h3>Key Points</h3>
        //   <ul>${data.keyPoints.map(point => `<li>${point}</li>`).join('')}</ul>
        //   <h3>Metacognition Tips</h3>
        //   <p>${data.metacognitionTips}</p>
        //   <h3>Mnemonics</h3>
        //   <p>${data.mnemonics}</p>
        // `;

    } catch (error) {
        console.error('Error fetching AI summary:', error);
        document.getElementById('aiSummary').textContent = 'Error fetching AI summary.';
    }
});
