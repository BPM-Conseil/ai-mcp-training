// Modern chat interface with improved UX
const messagesEl = document.getElementById('messages');
const sourcesEl = document.getElementById('sources');
const chatInput = document.getElementById('message');
const chatForm = document.getElementById('chatForm');

function addMessage(role, text) {
  const div = document.createElement('div');
  div.className = `message ${role}`;
  
  if (role === 'assistant') {
    // Format assistant messages with better typography
    div.innerHTML = formatAssistantMessage(text);
  } else {
    div.textContent = text;
  }
  
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function formatAssistantMessage(text) {
  // Convert markdown-like formatting to HTML
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\[Source (\d+)\]/g, '<span class="source-ref">📄 Source $1</span>')
    .replace(/\n/g, '<br>');
}

function showSources(sources) {
  if (!sources || sources.length === 0) {
    sourcesEl.innerHTML = '<div class="no-sources">No sources found for this query.</div>';
    return;
  }

  sourcesEl.innerHTML = '';
  sources.forEach((source, index) => {
    const sourceItem = document.createElement('div');
    sourceItem.className = 'source-item';
    
    const score = source.score ? (source.score * 100).toFixed(1) : 'N/A';
    
    sourceItem.innerHTML = `
      <div class="source-filename">📄 ${source.filename}</div>
      <div class="source-text">${source.chunk_text}</div>
      <div class="source-score">Relevance: ${score}%</div>
    `;
    
    sourcesEl.appendChild(sourceItem);
  });
}

function setLoading(isLoading) {
  const sendButton = document.querySelector('.send-button');
  const input = document.getElementById('message');
  
  if (isLoading) {
    sendButton.innerHTML = `
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"/>
        <path d="m9 12 2 2 4-4"/>
      </svg>
    `;
    sendButton.style.animation = 'spin 1s linear infinite';
    input.disabled = true;
  } else {
    sendButton.innerHTML = `
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="22" y1="2" x2="11" y2="13"></line>
        <polygon points="22,2 15,22 11,13 2,9"></polygon>
      </svg>
    `;
    sendButton.style.animation = 'none';
    input.disabled = false;
  }
}

async function ask(e) {
  e.preventDefault();
  const input = document.getElementById('message');
  const text = input.value.trim();
  if (!text) return;

  addMessage('user', text);
  input.value = '';
  setLoading(true);

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text })
    });

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    }

    const data = await res.json();
    
    if (data.error) {
      addMessage('assistant', `❌ Error: ${data.error}`);
    } else {
      addMessage('assistant', data.answer || 'No answer provided.');
    }

    showSources(data.sources || []);

  } catch (error) {
    console.error('Chat error:', error);
    addMessage('assistant', `❌ Sorry, I encountered an error: ${error.message}`);
    sourcesEl.innerHTML = '<div class="no-sources">Error loading sources.</div>';
  } finally {
    setLoading(false);
    input.focus();
  }
}

// Event listeners
chatForm.addEventListener('submit', ask);

// Auto-focus input on page load
chatInput.focus();

// Enter key handling
chatInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    ask(e);
  }
});

// Add CSS animation for loading spinner
const style = document.createElement('style');
style.textContent = `
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
  
  .source-ref {
    background: #e2e8f0;
    color: #4a5568;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.85em;
    font-weight: 500;
  }
`;
document.head.appendChild(style);
