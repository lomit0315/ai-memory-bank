// AI Memory Bank Frontend JavaScript
class MemoryBankFrontend {
    constructor() {
        this.apiBase = 'http://localhost:8000';
        this.uploadedFiles = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadInitialData();
    }

    setupEventListeners() {
        // File upload
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');

        uploadArea.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('dragover', this.handleDragOver.bind(this));
        uploadArea.addEventListener('dragleave', this.handleDragLeave.bind(this));
        uploadArea.addEventListener('drop', this.handleDrop.bind(this));
        fileInput.addEventListener('change', this.handleFileSelect.bind(this));

        // Search
        const searchBtn = document.getElementById('searchBtn');
        const searchInput = document.getElementById('searchInput');
        
        searchBtn.addEventListener('click', this.performSearch.bind(this));
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.performSearch();
        });

        // Header actions
        document.getElementById('statsBtn').addEventListener('click', this.showStatistics.bind(this));
        document.getElementById('clearBtn').addEventListener('click', this.clearAllData.bind(this));

        // Quick actions
        document.getElementById('addTextBtn').addEventListener('click', this.showAddTextModal.bind(this));
        document.getElementById('exportBtn').addEventListener('click', this.exportData.bind(this));
        document.getElementById('importBtn').addEventListener('click', this.importData.bind(this));
        document.getElementById('refreshBtn').addEventListener('click', this.refreshData.bind(this));

        // Modal
        document.getElementById('modalClose').addEventListener('click', this.closeModal.bind(this));
        document.getElementById('modalOverlay').addEventListener('click', (e) => {
            if (e.target.id === 'modalOverlay') this.closeModal();
        });
    }

    // File Upload Methods
    handleDragOver(e) {
        e.preventDefault();
        document.getElementById('uploadArea').classList.add('dragover');
    }

    handleDragLeave(e) {
        e.preventDefault();
        document.getElementById('uploadArea').classList.remove('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        document.getElementById('uploadArea').classList.remove('dragover');
        const files = Array.from(e.dataTransfer.files);
        this.uploadFiles(files);
    }

    handleFileSelect(e) {
        const files = Array.from(e.target.files);
        this.uploadFiles(files);
    }

    async uploadFiles(files) {
        if (files.length === 0) return;

        this.showLoading('Uploading files...');
        this.showUploadProgress();

        const totalFiles = files.length;
        let completedFiles = 0;

        for (const file of files) {
            try {
                await this.uploadSingleFile(file);
                completedFiles++;
                this.updateUploadProgress(completedFiles, totalFiles);
            } catch (error) {
                console.error('Upload failed for file:', file.name, error);
                this.addFileItem(file.name, 'error', error.message);
            }
        }

        this.hideLoading();
        this.hideUploadProgress();
        this.refreshData();
    }

    async uploadSingleFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${this.apiBase}/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }

        const result = await response.json();
        this.addFileItem(file.name, 'success', `${result.chunks_added} chunks added`);
    }

    addFileItem(fileName, status, message) {
        const uploadedFiles = document.getElementById('uploadedFiles');
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        
        const fileIcon = this.getFileIcon(fileName);
        
        fileItem.innerHTML = `
            <div class="file-info">
                <i class="file-icon ${fileIcon}"></i>
                <div class="file-details">
                    <h4>${fileName}</h4>
                    <p>${message}</p>
                </div>
            </div>
            <span class="file-status status-${status}">${status}</span>
        `;
        
        uploadedFiles.appendChild(fileItem);
    }

    getFileIcon(fileName) {
        const ext = fileName.split('.').pop().toLowerCase();
        const iconMap = {
            'pdf': 'fas fa-file-pdf',
            'md': 'fas fa-file-alt',
            'txt': 'fas fa-file-alt',
            'xlsx': 'fas fa-file-excel',
            'xls': 'fas fa-file-excel',
            'docx': 'fas fa-file-word',
            'doc': 'fas fa-file-word',
            'pptx': 'fas fa-file-powerpoint',
            'ppt': 'fas fa-file-powerpoint'
        };
        return iconMap[ext] || 'fas fa-file';
    }

    updateUploadProgress(completed, total) {
        const percentage = Math.round((completed / total) * 100);
        document.getElementById('progressText').textContent = `${percentage}%`;
        document.getElementById('progressFill').style.width = `${percentage}%`;
        document.getElementById('uploadStatus').textContent = `Processed ${completed} of ${total} files`;
    }

    showUploadProgress() {
        document.getElementById('uploadProgress').style.display = 'block';
    }

    hideUploadProgress() {
        document.getElementById('uploadProgress').style.display = 'none';
    }

    // Search Methods
    async performSearch() {
        const query = document.getElementById('searchInput').value.trim();
        if (!query) {
            this.showNotification('Please enter a search query', 'warning');
            return;
        }

        const topK = parseInt(document.getElementById('topK').value);
        const threshold = parseFloat(document.getElementById('threshold').value);

        this.showLoading('Searching...');

        try {
            const response = await fetch(`${this.apiBase}/search`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: query,
                    top_k: topK,
                    similarity_threshold: threshold
                })
            });

            if (!response.ok) {
                throw new Error('Search failed');
            }

            const result = await response.json();
            this.displaySearchResults(result);
        } catch (error) {
            console.error('Search error:', error);
            this.showNotification('Search failed: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    displaySearchResults(result) {
        const searchResults = document.getElementById('searchResults');
        
        if (result.results.length === 0) {
            searchResults.innerHTML = `
                <div class="text-center" style="padding: 40px; color: #6c757d;">
                    <i class="fas fa-search" style="font-size: 3rem; margin-bottom: 16px; opacity: 0.5;"></i>
                    <h3>No results found</h3>
                    <p>Try adjusting your search query or similarity threshold</p>
                </div>
            `;
            return;
        }

        searchResults.innerHTML = `
            <div class="mb-2">
                <h3>Found ${result.total_results} results for "${result.query}"</h3>
            </div>
        `;

        result.results.forEach((item, index) => {
            const resultItem = document.createElement('div');
            resultItem.className = 'result-item';
            
            const fileName = item.metadata.file_path.split('/').pop();
            const similarity = (item.similarity_score * 100).toFixed(1);
            
            resultItem.innerHTML = `
                <div class="result-header">
                    <div class="result-meta">
                        <span class="result-file">${fileName}</span>
                        <span class="result-type">${item.metadata.file_type}</span>
                        ${item.metadata.chunk_index !== undefined ? 
                            `<span class="result-type">Chunk ${item.metadata.chunk_index + 1}/${item.metadata.total_chunks}</span>` : 
                            ''
                        }
                    </div>
                    <span class="result-similarity">${similarity}%</span>
                </div>
                <div class="result-content">
                    ${this.highlightQuery(item.content, result.query)}
                </div>
                <div class="result-footer">
                    <span>Rank: ${item.rank}</span>
                    <span>Size: ${item.metadata.chunk_size} chars</span>
                </div>
            `;
            
            searchResults.appendChild(resultItem);
        });
    }

    highlightQuery(content, query) {
        const queryWords = query.toLowerCase().split(' ');
        let highlightedContent = content;
        
        queryWords.forEach(word => {
            if (word.length > 2) {
                const regex = new RegExp(`(${word})`, 'gi');
                highlightedContent = highlightedContent.replace(regex, '<mark>$1</mark>');
            }
        });
        
        return highlightedContent;
    }

    // Statistics Methods
    async showStatistics() {
        this.showLoading('Loading statistics...');
        
        try {
            const response = await fetch(`${this.apiBase}/statistics`);
            if (!response.ok) throw new Error('Failed to load statistics');
            
            const result = await response.json();
            this.displayStatistics(result.statistics);
        } catch (error) {
            console.error('Statistics error:', error);
            this.showNotification('Failed to load statistics', 'error');
        } finally {
            this.hideLoading();
        }
    }

    displayStatistics(stats) {
        const modalTitle = document.getElementById('modalTitle');
        const modalContent = document.getElementById('modalContent');
        
        modalTitle.textContent = 'Memory Bank Statistics';
        
        modalContent.innerHTML = `
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">${stats.total_entries || 0}</div>
                    <div class="stat-label">Total Entries</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${stats.total_vectors || 0}</div>
                    <div class="stat-label">Total Vectors</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${stats.unique_files || 0}</div>
                    <div class="stat-label">Unique Files</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${stats.total_content_length ? (stats.total_content_length / 1000).toFixed(1) + 'K' : 0}</div>
                    <div class="stat-label">Content Size (chars)</div>
                </div>
            </div>
            
            ${stats.file_types ? `
                <h4>File Types</h4>
                <div class="stats-grid">
                    ${Object.entries(stats.file_types).map(([type, count]) => `
                        <div class="stat-card">
                            <div class="stat-value">${count}</div>
                            <div class="stat-label">${type}</div>
                        </div>
                    `).join('')}
                </div>
            ` : ''}
            
            <div class="text-center mt-3">
                <button class="btn btn-primary" onclick="memoryBank.refreshData()">
                    <i class="fas fa-sync-alt"></i>
                    Refresh
                </button>
            </div>
        `;
        
        this.showModal();
    }

    // Text Input Methods
    showAddTextModal() {
        const modalTitle = document.getElementById('modalTitle');
        const modalContent = document.getElementById('modalContent');
        
        modalTitle.textContent = 'Add Text Content';
        
        modalContent.innerHTML = `
            <form id="addTextForm">
                <div class="form-group">
                    <label for="textContent">Text Content</label>
                    <textarea id="textContent" placeholder="Enter the text content you want to add to your memory bank..." required></textarea>
                </div>
                <div class="form-group">
                    <label for="textMetadata">Metadata (optional)</label>
                    <input type="text" id="textMetadata" placeholder="e.g., source, category, tags">
                </div>
                <div class="text-center">
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-plus"></i>
                        Add Text
                    </button>
                </div>
            </form>
        `;
        
        this.showModal();
        
        // Add form submit handler
        document.getElementById('addTextForm').addEventListener('submit', this.handleAddText.bind(this));
    }

    async handleAddText(e) {
        e.preventDefault();
        
        const text = document.getElementById('textContent').value.trim();
        const metadata = document.getElementById('textMetadata').value.trim();
        
        if (!text) {
            this.showNotification('Please enter some text content', 'warning');
            return;
        }
        
        this.closeModal();
        this.showLoading('Adding text content...');
        
        try {
            const response = await fetch(`${this.apiBase}/store-text`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: text,
                    metadata: metadata ? { source: metadata } : undefined
                })
            });
            
            if (!response.ok) throw new Error('Failed to add text');
            
            this.showNotification('Text content added successfully!', 'success');
            this.refreshData();
        } catch (error) {
            console.error('Add text error:', error);
            this.showNotification('Failed to add text: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    // Data Management Methods
    async clearAllData() {
        if (!confirm('Are you sure you want to clear all data? This action cannot be undone.')) {
            return;
        }
        
        this.showLoading('Clearing all data...');
        
        try {
            const response = await fetch(`${this.apiBase}/clear`, {
                method: 'POST'
            });
            
            if (!response.ok) throw new Error('Failed to clear data');
            
            this.showNotification('All data cleared successfully!', 'success');
            this.refreshData();
        } catch (error) {
            console.error('Clear data error:', error);
            this.showNotification('Failed to clear data: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    async exportData() {
        this.showLoading('Preparing export...');
        
        try {
            const response = await fetch(`${this.apiBase}/statistics`);
            if (!response.ok) throw new Error('Failed to get data');
            
            const result = await response.json();
            
            // Create a simple export (you could enhance this to get actual data)
            const exportData = {
                exported_at: new Date().toISOString(),
                statistics: result.statistics,
                note: 'This is a statistics export. For full data export, use the CLI command.'
            };
            
            const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `memory-bank-export-${new Date().toISOString().split('T')[0]}.json`;
            a.click();
            URL.revokeObjectURL(url);
            
            this.showNotification('Export completed!', 'success');
        } catch (error) {
            console.error('Export error:', error);
            this.showNotification('Export failed: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    importData() {
        this.showNotification('Import functionality is available via the CLI. Use: python app.py import <file>', 'info');
    }

    async refreshData() {
        // Clear uploaded files display
        document.getElementById('uploadedFiles').innerHTML = '';
        
        // Clear search results
        document.getElementById('searchResults').innerHTML = '';
        
        this.showNotification('Data refreshed!', 'success');
    }

    async loadInitialData() {
        // You could load initial statistics or recent files here
        console.log('Memory Bank Frontend initialized');
    }

    // UI Utility Methods
    showModal() {
        document.getElementById('modalOverlay').style.display = 'flex';
    }

    closeModal() {
        document.getElementById('modalOverlay').style.display = 'none';
    }

    showLoading(message = 'Loading...') {
        document.getElementById('loadingText').textContent = message;
        document.getElementById('loadingOverlay').style.display = 'flex';
    }

    hideLoading() {
        document.getElementById('loadingOverlay').style.display = 'none';
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas fa-${this.getNotificationIcon(type)}"></i>
            <span>${message}</span>
            <button onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        // Add styles
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${this.getNotificationColor(type)};
            color: white;
            padding: 12px 16px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 3000;
            display: flex;
            align-items: center;
            gap: 8px;
            max-width: 400px;
            animation: slideIn 0.3s ease;
        `;
        
        // Add animation styles
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
        
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    getNotificationColor(type) {
        const colors = {
            success: '#28a745',
            error: '#dc3545',
            warning: '#ffc107',
            info: '#17a2b8'
        };
        return colors[type] || '#17a2b8';
    }
}

// Initialize the frontend when the page loads
let memoryBank;
document.addEventListener('DOMContentLoaded', () => {
    memoryBank = new MemoryBankFrontend();
}); 