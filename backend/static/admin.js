// English-only comments as requested
async function fetchDocs() {
  const res = await fetch('/admin/documents');
  const data = await res.json();
  const list = document.getElementById('docList');
  list.innerHTML = '';
  (data || []).forEach(d => {
    const li = document.createElement('li');
    li.innerHTML = `<span>${d.filename} <small>(${d.id})</small></span>`;
    const del = document.createElement('button');
    del.textContent = 'Delete';
    del.onclick = async () => {
      await fetch(`/admin/documents/${d.id}`, { method: 'DELETE' });
      await fetchDocs();
    };
    li.appendChild(del);
    list.appendChild(li);
  });
}

async function handleUpload(e) {
  e.preventDefault();
  const file = document.getElementById('fileInput').files[0];
  if (!file) return;
  const fd = new FormData();
  fd.append('file', file);
  const statusEl = document.getElementById('uploadStatus');
  statusEl.textContent = 'Uploading...';
  try {
    const res = await fetch('/admin/upload', { method: 'POST', body: fd });
    const data = await res.json();
    statusEl.textContent = `Uploaded. Chunks: ${data.chunks}`;
    await fetchDocs();
  } catch (err) {
    statusEl.textContent = 'Upload failed';
  }
}

document.getElementById('uploadForm').addEventListener('submit', handleUpload);
document.getElementById('refreshBtn').addEventListener('click', fetchDocs);
fetchDocs();
