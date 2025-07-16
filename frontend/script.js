/**
 * AI Memory Bank - Frontend JavaScript
 * Handles user interactions, API calls, and UI updates
 */

class AIMemoryBank {
    constructor() {
        this.apiBase = '';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadStatistics();
        this.setupDragAndDrop();
    }

    setupEventListeners() {
        // Search functionality
        const searchBtn = document.getElementById('searchBtn');
        const searchInput = document.getElementById('searchInput');
        
        searchBtn.addEventListener('click', () => this.performSearch());
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.performSearch();
            }
        });

        // File upload
        const fileInput = document.getElementById('fileInput');
        const uploadArea = document.getElementById('uploadArea');
        
        fileInput.addEventListener('change', (e) => this.handleFileUpload(e.target.files));
        uploadArea.addEventListener('click', () => fileInput.click());

        // Text storage
        const storeTextBtn = document.getElementById('storeTextBtn');
        storeTextBtn.addEventListener('click', () => this.storeText());

        // Notification close
        const notificationClose = document.querySelector('.notification-close');
        if (notificationClose) {
            notificationClose.addEventListener('click', () => this.hideNotification());
        }
    }

    setupDragAndDrop() {
        const uploadArea = document.getElementById('uploadArea');
        
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
            this.handleFileUpload(files);
        });
    }

    async performSearch() {
        const query = document.getElementById('searchInput').value.trim();
        const topK = parseInt(document.getElementById('topK').value) || 5;
        
        if (!query) {
            this.showNotification('Please enter a search query', 'warning', 'fas fa-exclamation-triangle');
            return;
        }

        this.showLoading();
        
        try {
            const response = await fetch('/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    top_k: topK
                })
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'Search failed');
            }

            this.displaySearchResults(data.results, query);
            
            if (data.results.length === 0) {
                this.showNotification('No results found for your query', 'warning', 'fas fa-search');
            }

        } catch (error) {
            console.error('Search error:', error);
            this.showNotification(`Search failed: ${error.message}`, 'error', 'fas fa-exclamation-circle');
        } finally {
            this.hideLoading();
        }
    }

    displaySearchResults(results, query) {
        const resultsContainer = document.getElementById('searchResults');
        
        if (results.length === 0) {
            resultsContainer.innerHTML = `
                <div class="no-results">
                    <i class="fas fa-search fa-3x"></i>
                    <h3>No results found</h3>
                    <p>Try different keywords or check your spelling</p>
                </div>
            `;
            resultsContainer.classList.add('visible');
            return;
        }

        const resultsHTML = results.map((result, index) => `
            <div class="result-card">
                <div class="result-header">
                    <div class="result-score">Score: ${result.score.toFixed(3)}</div>
                </div>
                <div class="result-file">
                    <i class="fas fa-file"></i> ${result.document_info.file_path}
                </div>
                <div class="result-text">
                    ${this.highlightText(result.text, query)}
                </div>
            </div>
        `).join('');

        resultsContainer.innerHTML = `
            <div class="results-header">
                <h3><i class="fas fa-search"></i> Search Results for "${query}" (${results.length} found)</h3>
            </div>
            ${resultsHTML}
        `;
        
        resultsContainer.classList.add('visible');
        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    highlightText(text, query) {
        if (!query) return text;
        
        const words = query.toLowerCase().split(' ').filter(word => word.length > 2);
        let highlightedText = text;
        
        words.forEach(word => {
            const regex = new RegExp(`(${word})`, 'gi');
            highlightedText = highlightedText.replace(regex, '<mark>$1</mark>');
        });
        
        return highlightedText;
    }

    async handleFileUpload(files) {
        if (!files || files.length === 0) return;

        const supportedTypes = ['.pdf', '.md', '.markdown', '.txt', '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt'];
        const validFiles = Array.from(files).filter(file => {
            const extension = '.' + file.name.split('.').pop().toLowerCase();
            return supportedTypes.includes(extension);
        });

        if (validFiles.length === 0) {
            this.showNotification('No supported files selected', 'warning', 'fas fa-file-exclamation');
            return;
        }

        if (validFiles.length < files.length) {
            this.showNotification(`${files.length - validFiles.length} unsupported files skipped`, 'warning', 'fas fa-exclamation-triangle');
        }

        this.showUploadProgress();
        
        let successCount = 0;
        
        for (let i = 0; i < validFiles.length; i++) {
            const file = validFiles[i];
            
            try {
                await this.uploadSingleFile(file);
                successCount++;
                
                // Update progress
                const progress = ((i + 1) / validFiles.length) * 100;
                this.updateUploadProgress(progress, `Processing ${file.name}...`);
                
            } catch (error) {
                console.error(`Error uploading ${file.name}:`, error);
                this.showNotification(`Failed to upload ${file.name}: ${error.message}`, 'error', 'fas fa-exclamation-circle');
            }
        }

        this.hideUploadProgress();
        
        if (successCount > 0) {
            this.showNotification(`Successfully uploaded ${successCount} file(s)`, 'success', 'fas fa-check-circle');
            this.loadStatistics(); // Refresh stats
        }

        // Clear file input
        document.getElementById('fileInput').value = '';
    }

    async uploadSingleFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Upload failed');
        }

        return data;
    }

    async storeText() {
        const text = document.getElementById('textInput').value.trim();
        
        if (!text) {
            this.showNotification('Please enter some text', 'warning', 'fas fa-exclamation-triangle');
            return;
        }

        this.showLoading();
        
        try {
            const response = await fetch('/store-text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: text })
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'Failed to store text');
            }

            this.showNotification('Text stored successfully!', 'success', 'fas fa-check-circle');
            document.getElementById('textInput').value = '';
            this.loadStatistics(); // Refresh stats

        } catch (error) {
            console.error('Store text error:', error);
            this.showNotification(`Failed to store text: ${error.message}`, 'error', 'fas fa-exclamation-circle');
        } finally {
            this.hideLoading();
        }
    }

    async loadStatistics() {
        try {
            const response = await fetch('/statistics');
            const stats = await response.json();
            
            if (!response.ok) {
                throw new Error('Failed to load statistics');
            }

            this.updateStatistics(stats);

        } catch (error) {
            console.error('Statistics error:', error);
            // Don't show notification for stats error, just log it
        }
    }

    updateStatistics(stats) {
        document.getElementById('totalDocs').textContent = stats.total_documents || 0;
        document.getElementById('totalChunks').textContent = stats.total_chunks || 0;
        document.getElementById('dbSize').textContent = `${(stats.database_size_mb || 0).toFixed(1)} MB`;
        
        // Format last updated date
        if (stats.last_updated) {
            const date = new Date(stats.last_updated);
            document.getElementById('lastUpdated').textContent = date.toLocaleDateString();
        } else {
            document.getElementById('lastUpdated').textContent = 'Never';
        }
    }

    showUploadProgress() {
        const progressContainer = document.getElementById('uploadProgress');
        progressContainer.classList.remove('hidden');
        this.updateUploadProgress(0, 'Starting upload...');
    }

    updateUploadProgress(percentage, message) {
        const progressFill = document.querySelector('.progress-fill');
        const progressText = document.querySelector('.progress-text');
        
        progressFill.style.width = `${percentage}%`;
        progressText.textContent = message;
    }

    hideUploadProgress() {
        setTimeout(() => {
            document.getElementById('uploadProgress').classList.add('hidden');
        }, 1000);
    }

    showLoading() {
        document.getElementById('loadingOverlay').classList.remove('hidden');
    }

    hideLoading() {
        document.getElementById('loadingOverlay').classList.add('hidden');
    }

    showNotification(message, type = 'info', icon = 'fas fa-info-circle') {
        const notification = document.getElementById('notification');
        const notificationIcon = notification.querySelector('.notification-icon');
        const notificationMessage = notification.querySelector('.notification-message');
        
        // Set icon and message
        notificationIcon.className = `notification-icon ${icon}`;
        notificationMessage.textContent = message;
        
        // Set type class
        notification.className = `notification ${type}`;
        
        // Show notification
        notification.classList.remove('hidden');
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            this.hideNotification();
        }, 5000);
    }

    hideNotification() {
        document.getElementById('notification').classList.add('hidden');
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new AIMemoryBank();
});

// Add some helpful CSS for highlighted search terms
const style = document.createElement('style');
style.textContent = `
    mark {
        background-color: #ffeb3b;
        padding: 1px 3px;
        border-radius: 3px;
        font-weight: bold;
    }
    
    .no-results {
        text-align: center;
        padding: 40px;
        color: #6c757d;
    }
    
    .no-results i {
        margin-bottom: 20px;
        color: #dee2e6;
    }
    
    .results-header {
        margin-bottom: 20px;
        padding-bottom: 15px;
        border-bottom: 2px solid #e9ecef;
    }
    
    .results-header h3 {
        color: #495057;
        font-size: 1.2rem;
    }
`;
document.head.appendChild(style); 