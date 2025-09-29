// Modern admin interface with drag & drop and better UX
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadStatus = document.getElementById('uploadStatus');
const uploadProgress = document.getElementById('uploadProgress');
const docList = document.getElementById('docList');
const refreshBtn = document.getElementById('refreshBtn');
const docCount = document.getElementById('docCount');
const logoutBtn = document.getElementById('logoutBtn');

// File type icons mapping
const fileIcons = {
  'pdf': 'PDF',
  'txt': 'TXT',
  'md': 'MD',
  'doc': 'DOC',
  'docx': 'DOC',
  'default': '📄'
};

function getFileIcon(filename) {
  const ext = filename.split('.').pop().toLowerCase();
  return fileIcons[ext] || fileIcons.default;
}

function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
}

function showStatus(message, type = 'info') {
  uploadStatus.innerHTML = `
    <div class="status-message status-${type}">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        ${type === 'success' ? '<polyline points="20,6 9,17 4,12"></polyline>' : 
          type === 'error' ? '<circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line>' :
          '<circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line>'}
      </svg>
      ${message}
    </div>
  `;
  
  // Auto-hide after 5 seconds
  setTimeout(() => {
    uploadStatus.innerHTML = '';
  }, 5000);
}

async function fetchDocs() {
  try {
    docList.innerHTML = `
      <div class="loading-state">
        <div class="spinner"></div>
        <p>Loading documents...</p>
      </div>
    `;

    const res = await fetch('/admin/documents');
    if (res.status === 401) {
      // Redirect to login page
      window.location.href = '/admin/login';
      return;
    }
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    
    const data = await res.json();
    
    // Update document count
    docCount.textContent = `${data.length} document${data.length !== 1 ? 's' : ''}`;
    
    if (data.length === 0) {
      docList.innerHTML = `
        <div class="empty-state">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14,2 14,8 20,8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
            <polyline points="10,9 9,9 8,9"></polyline>
          </svg>
          <h3>No documents uploaded yet</h3>
          <p>Upload your first document to get started with the knowledge base.</p>
        </div>
      `;
      return;
    }

    docList.innerHTML = '';
    data.forEach(doc => {
      const card = document.createElement('div');
      card.className = 'document-card';
      
      card.innerHTML = `
        <div class="document-header">
          <div class="document-icon">${getFileIcon(doc.filename)}</div>
          <div class="document-actions">
            <button class="delete-btn" onclick="deleteDocument('${doc.id}')">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="3,6 5,6 21,6"></polyline>
                <path d="m19,6v14a2,2 0 0,1 -2,2H7a2,2 0 0,1 -2,-2V6m3,0V4a2,2 0 0,1 2,-2h4a2,2 0 0,1 2,2v2"></path>
              </svg>
              Delete
            </button>
          </div>
        </div>
        
        <div class="document-title">${doc.filename}</div>
        
        <div class="document-meta">
          <div class="document-date">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <polyline points="12,6 12,12 16,14"></polyline>
            </svg>
            ${formatDate(doc.created_at)}
          </div>
          <span class="document-type">${doc.mime_type || 'Unknown'}</span>
        </div>
      `;
      
      docList.appendChild(card);
    });

  } catch (error) {
    console.error('Error fetching documents:', error);
    docList.innerHTML = `
      <div class="empty-state">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="15" y1="9" x2="9" y2="15"></line>
          <line x1="9" y1="9" x2="15" y2="15"></line>
        </svg>
        <h3>Error loading documents</h3>
        <p>Failed to fetch documents. Please try refreshing the page.</p>
      </div>
    `;
    showStatus('Failed to load documents', 'error');
  }
}

async function deleteDocument(docId) {
  if (!confirm('Are you sure you want to delete this document? This action cannot be undone.')) {
    return;
  }

  try {
    const res = await fetch(`/admin/documents/${docId}`, { method: 'DELETE' });
    if (res.status === 401) {
      window.location.href = '/admin/login';
      return;
    }
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    
    showStatus('Document deleted successfully', 'success');
    await fetchDocs();
  } catch (error) {
    console.error('Error deleting document:', error);
    showStatus('Failed to delete document', 'error');
  }
}

async function uploadFiles(files) {
  if (!files || files.length === 0) return;

  const progressContainer = document.createElement('div');
  uploadProgress.appendChild(progressContainer);

  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    
    // Create progress item
    const progressItem = document.createElement('div');
    progressItem.className = 'upload-item';
    progressItem.innerHTML = `
      <div>
        <strong>${file.name}</strong>
        <div>${formatFileSize(file.size)}</div>
      </div>
      <div class="progress-bar">
        <div class="progress-fill" style="width: 0%"></div>
      </div>
    `;
    progressContainer.appendChild(progressItem);

    const progressBar = progressItem.querySelector('.progress-fill');

    try {
      // Simulate progress (since we can't track real upload progress with fetch)
      progressBar.style.width = '30%';
      
      const formData = new FormData();
      formData.append('file', file);
      
      progressBar.style.width = '70%';
      
      const res = await fetch('/admin/upload', {
        method: 'POST',
        body: formData
      });
      
      if (res.status === 401) {
        window.location.href = '/admin/login';
        return;
      }
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      
      const data = await res.json();
      
      progressBar.style.width = '100%';
      progressItem.classList.add('success');
      progressItem.innerHTML = `
        <div>
          <strong>${file.name}</strong>
          <div>✅ Uploaded successfully (${data.chunks} chunks)</div>
        </div>
      `;
      
    } catch (error) {
      console.error('Upload error:', error);
      progressItem.classList.add('error');
      progressItem.innerHTML = `
        <div>
          <strong>${file.name}</strong>
          <div>❌ Upload failed</div>
        </div>
      `;
    }
  }

  // Clear progress after 3 seconds
  setTimeout(() => {
    uploadProgress.innerHTML = '';
  }, 3000);

  // Refresh document list
  await fetchDocs();
}

// Drag and drop functionality
uploadArea.addEventListener('dragover', (e) => {
  e.preventDefault();
  uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', (e) => {
  e.preventDefault();
  uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
  e.preventDefault();
  uploadArea.classList.remove('dragover');
  
  const files = Array.from(e.dataTransfer.files);
  uploadFiles(files);
});

// Click to upload
uploadArea.addEventListener('click', () => {
  fileInput.click();
});

fileInput.addEventListener('change', (e) => {
  const files = Array.from(e.target.files);
  uploadFiles(files);
  // Reset input
  e.target.value = '';
});

// Logout functionality
async function handleLogout() {
  try {
    const response = await fetch('/admin/logout', {
      method: 'POST'
    });
    
    if (response.ok) {
      // Redirect to login page
      window.location.href = '/admin/login';
    } else {
      console.error('Logout failed');
      // Force redirect anyway
      window.location.href = '/admin/login';
    }
  } catch (error) {
    console.error('Logout error:', error);
    // Force redirect anyway
    window.location.href = '/admin/login';
  }
}

// Event listeners
refreshBtn.addEventListener('click', fetchDocs);
logoutBtn.addEventListener('click', handleLogout);

// Make deleteDocument globally available
window.deleteDocument = deleteDocument;

// Initial load
fetchDocs();
