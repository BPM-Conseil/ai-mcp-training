// English-only comments as requested
const messagesEl = document.getElementById('messages');
const sourcesEl = document.getElementById('sources');

function addMessage(role, text) {
  const div = document.createElement('div');
  div.className = `message ${role}`;
  div.textContent = text;
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

async function ask(e) {
  e.preventDefault();
  const input = document.getElementById('message');
  const text = input.value.trim();
  if (!text) return;
  addMessage('user', text);
  input.value = '';

  const res = await fetch('/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: text }) });
  const data = await res.json();
  addMessage('assistant', data.answer || 'No answer');

  sourcesEl.innerHTML = '';
  (data.sources || []).forEach((s, i) => {
    const card = document.createElement('div');
    card.className = 'message';
    card.innerHTML = `<strong>Source ${i+1}: ${s.filename}</strong><br/>${s.chunk_text}`;
    sourcesEl.appendChild(card);
  });
}

document.getElementById('chatForm').addEventListener('submit', ask);
