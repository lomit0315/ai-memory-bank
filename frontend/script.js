/**
 * AI Memory Bank - Enhanced Frontend JavaScript
 * Modern, feature-rich interface with improved UX and functionality
 */

class AIMemoryBank {
    constructor() {
        this.currentPanel = 'dashboard';
        this.config = {
            local: {
                model: '',
                temperature: 0.7,
                maxTokens: 2048
            },
            online: {
                provider: 'openai',
                apiKey: '',
                model: 'gpt-3.5-turbo'
            }
        };
        this.chatHistory = [];
        this.documents = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadStatistics();
        this.loadLocalModels();
        this.checkOllamaStatus();
        this.loadDocuments();
        this.showPanel('dashboard');
        this.updatePageTitle('Dashboard');
    }

    setupEventListeners() {
        // Sidebar navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const panel = e.currentTarget.dataset.panel;
                this.switchToPanel(panel);
            });
        });

        // Mobile menu
        const mobileMenuBtn = document.getElementById('mobile-menu-btn');
        const sidebar = document.getElementById('sidebar');
        
        if (mobileMenuBtn && sidebar) {
            mobileMenuBtn.addEventListener('click', () => {
                sidebar.classList.toggle('open');
            });
        }

        // Quick search
        const quickSearch = document.getElementById('quick-search');
        if (quickSearch) {
            quickSearch.addEventListener('input', this.debounce(() => {
                this.performQuickSearch(quickSearch.value);
            }, 300));
        }

        // Quick action buttons
        document.querySelectorAll('.quick-action-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.currentTarget.dataset.action;
                this.switchToPanel(action);
            });
        });

        // File upload
        const fileInput = document.getElementById('file-input');
        const uploadZone = document.getElementById('upload-zone');
        
        if (fileInput && uploadZone) {
            fileInput.addEventListener('change', (e) => this.handleFileUpload(e.target.files));
            uploadZone.addEventListener('click', () => fileInput.click());
            this.setupDragAndDrop(uploadZone, fileInput);
        }

        // Text input
        const textInput = document.getElementById('text-input');
        const submitText = document.getElementById('submit-text');
        
        if (textInput && submitText) {
            textInput.addEventListener('input', () => this.updateTextStats(textInput.value));
            submitText.addEventListener('click', () => this.submitText());
        }

        // Search
        const searchBtn = document.getElementById('search-btn');
        const searchInput = document.getElementById('search-input');
        
        if (searchBtn && searchInput) {
            searchBtn.addEventListener('click', () => this.performSearch());
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.performSearch();
            });
        }

        // Chat
        const sendBtn = document.getElementById('send-btn');
        const chatInput = document.getElementById('chat-input');
        const clearChatBtn = document.getElementById('clear-chat-btn');
        
        if (sendBtn && chatInput) {
            sendBtn.addEventListener('click', () => this.sendMessage());
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
            chatInput.addEventListener('input', () => this.autoResizeTextarea(chatInput));
        }

        if (clearChatBtn) {
            clearChatBtn.addEventListener('click', () => this.clearChat());
        }

        // Suggested questions
        document.querySelectorAll('.suggestion').forEach(suggestion => {
            suggestion.addEventListener('click', (e) => {
                const question = e.target.dataset.question;
                this.askQuestion(question);
            });
        });

        // Documents
        const documentsSearch = document.getElementById('documents-search');
        const documentTypeFilter = document.getElementById('document-type-filter');
        const refreshDocuments = document.getElementById('refresh-documents');
        
        if (documentsSearch) {
            documentsSearch.addEventListener('input', this.debounce(() => {
                this.filterDocuments();
            }, 300));
        }

        if (documentTypeFilter) {
            documentTypeFilter.addEventListener('change', () => this.filterDocuments());
        }

        if (refreshDocuments) {
            refreshDocuments.addEventListener('click', () => this.loadDocuments());
        }

        // Settings
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tab = e.target.dataset.tab;
                this.switchTab(tab);
            });
        });

        // Settings controls
        const localModel = document.getElementById('local-model');
        const temperature = document.getElementById('temperature');
        const apiProvider = document.getElementById('api-provider');
        const apiKey = document.getElementById('api-key');
        const clearDataBtn = document.getElementById('clear-data-btn');

        if (localModel) localModel.addEventListener('change', () => this.updateLocalModel());
        if (temperature) temperature.addEventListener('input', () => this.updateTemperature());
        if (apiProvider) apiProvider.addEventListener('change', () => this.updateApiProvider());
        if (apiKey) apiKey.addEventListener('input', () => this.updateApiKey());
        if (clearDataBtn) clearDataBtn.addEventListener('click', () => this.confirmClearData());

        // Modal
        const modalClose = document.getElementById('modal-close');
        const modalOverlay = document.getElementById('modal-overlay');
        
        if (modalClose) {
            modalClose.addEventListener('click', () => this.closeModal());
        }
        
        if (modalOverlay) {
            modalOverlay.addEventListener('click', (e) => {
                if (e.target === modalOverlay) this.closeModal();
            });
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch (e.key) {
                    case 'k':
                        e.preventDefault();
                        this.switchToPanel('search');
                        break;
                    case 'u':
                        e.preventDefault();
                        this.switchToPanel('upload');
                        break;
                    case 'c':
                        e.preventDefault();
                        this.switchToPanel('chat');
                        break;
                }
            }
        });
    }

    switchToPanel(panelName) {
        // Update active navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-panel="${panelName}"]`).classList.add('active');

        // Show panel
        this.showPanel(panelName);
        this.currentPanel = panelName;
        this.updatePageTitle(this.getPanelTitle(panelName));

        // Close mobile sidebar
        const sidebar = document.getElementById('sidebar');
        if (sidebar) {
            sidebar.classList.remove('open');
        }
    }

    showPanel(panelName) {
        // Hide all panels
        document.querySelectorAll('.panel').forEach(panel => {
            panel.classList.remove('active');
        });

        // Show target panel
        const targetPanel = document.getElementById(`${panelName}-panel`);
        if (targetPanel) {
            targetPanel.classList.add('active');
        }
    }

    updatePageTitle(title) {
        const pageTitle = document.getElementById('page-title');
        if (pageTitle) {
            pageTitle.textContent = title;
        }
    }

    getPanelTitle(panelName) {
        const titles = {
            'dashboard': 'Dashboard',
            'upload': 'Add Documents',
            'search': 'Search',
            'chat': 'AI Assistant',
            'documents': 'Documents',
            'settings': 'Settings'
        };
        return titles[panelName] || 'Dashboard';
    }

    setupDragAndDrop(uploadZone, fileInput) {
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('dragover');
        });

        uploadZone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('dragover');
        });

        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('dragover');
            this.handleFileUpload(e.dataTransfer.files);
        });
    }

    async handleFileUpload(files) {
        if (!files || files.length === 0) return;

        this.showLoading('Uploading files...', `Processing ${files.length} file(s)`);

        try {
            const uploadProgress = document.getElementById('upload-progress');
            const progressFill = document.getElementById('progress-fill');
            const progressText = document.getElementById('progress-text');
            const progressFiles = document.getElementById('progress-files');

            if (uploadProgress) {
                uploadProgress.classList.remove('hidden');
            }

            let successCount = 0;
            for (let i = 0; i < files.length; i++) {
                const file = files[i];
                const progress = ((i + 1) / files.length) * 100;

                if (progressFill) progressFill.style.width = `${progress}%`;
                if (progressText) progressText.textContent = `${Math.round(progress)}%`;
                if (progressFiles) progressFiles.textContent = `Processing: ${file.name}`;

                const formData = new FormData();
                formData.append('file', file);

                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    throw new Error(`Failed to upload ${file.name}`);
                }

                successCount++;
            }

            this.showToast(`Successfully uploaded ${successCount} file(s)!`, 'success');
            this.loadStatistics();
            this.loadDocuments();
        } catch (error) {
            this.showToast(`Upload failed: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
            const uploadProgress = document.getElementById('upload-progress');
            if (uploadProgress) {
                uploadProgress.classList.add('hidden');
            }
        }
    }

    updateTextStats(text) {
        const charCount = document.getElementById('text-char-count');
        const wordCount = document.getElementById('text-word-count');
        
        if (charCount) {
            charCount.textContent = `${text.length} characters`;
        }
        
        if (wordCount) {
            const words = text.trim() ? text.trim().split(/\s+/).length : 0;
            wordCount.textContent = `${words} words`;
        }
    }

    async submitText() {
        const textInput = document.getElementById('text-input');
        const text = textInput.value.trim();

        if (!text) {
            this.showToast('Please enter some text', 'warning');
            return;
        }

        this.showLoading('Saving text...', 'Adding to knowledge base');

        try {
            const response = await fetch('/store-text', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });

            if (!response.ok) {
                throw new Error('Failed to save text');
            }

            textInput.value = '';
            this.updateTextStats('');
            this.showToast('Text saved successfully!', 'success');
            this.loadStatistics();
            this.loadDocuments();
        } catch (error) {
            this.showToast(`Save failed: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }

    async performSearch() {
        const searchInput = document.getElementById('search-input');
        const query = searchInput.value.trim();

        if (!query) {
            this.showToast('Please enter a search query', 'warning');
            return;
        }

        const limit = parseInt(document.getElementById('search-limit').value) || 5;
        
        this.showLoading('Searching...', 'Finding relevant content');

        try {
            const response = await fetch('/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query, top_k: limit })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Search failed');
            }

            this.displaySearchResults(data.results, query);
        } catch (error) {
            this.showToast(`Search failed: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }

    async performQuickSearch(query) {
        if (!query.trim()) return;

        try {
            const response = await fetch('/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query, top_k: 3 })
            });

            const data = await response.json();

            if (response.ok && data.results.length > 0) {
                this.showQuickSearchResults(data.results, query);
            }
        } catch (error) {
            console.error('Quick search failed:', error);
        }
    }

    showQuickSearchResults(results, query) {
        // Create a dropdown or tooltip with quick results
        // This could be enhanced with a proper dropdown component
        console.log('Quick search results:', results);
    }

    displaySearchResults(results, query) {
        const searchResults = document.getElementById('search-results');
        const searchResultsHeader = document.getElementById('search-results-header');
        const resultsCount = document.getElementById('results-count');
        const noResults = document.getElementById('no-results');
        
        if (results.length === 0) {
            if (searchResults) searchResults.classList.remove('visible');
            if (searchResultsHeader) searchResultsHeader.classList.add('hidden');
            if (noResults) noResults.classList.remove('hidden');
        } else {
            if (searchResultsHeader) {
                searchResultsHeader.classList.remove('hidden');
                if (resultsCount) resultsCount.textContent = `${results.length} result(s) found`;
            }
            
            if (noResults) noResults.classList.add('hidden');
            
            if (searchResults) {
                const resultsHtml = results.map(result => `
                    <div class="result-item">
                        <div class="result-header">
                            <span class="result-score">Score: ${result.score.toFixed(3)}</span>
                        </div>
                        <div class="result-file">
                            <i class="fas fa-file"></i> ${result.document_info.file_path}
                        </div>
                        <div class="result-text">${this.highlightQuery(result.text, query)}</div>
                    </div>
                `).join('');

                searchResults.innerHTML = resultsHtml;
                searchResults.classList.add('visible');
            }
        }
    }

    highlightQuery(text, query) {
        if (!query) return text;
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }

    async sendMessage() {
        const chatInput = document.getElementById('chat-input');
        const message = chatInput.value.trim();

        if (!message) return;

        this.addMessageToChat(message, 'user');
        chatInput.value = '';
        this.autoResizeTextarea(chatInput);

        await this.askQuestion(message);
    }

    async askQuestion(question) {
        this.addMessageToChat('', 'bot', true); // Add loading message

        try {
            const useAI = document.getElementById('use-ai').checked;
            const useLocal = document.getElementById('use-local').checked;

            const response = await fetch('/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    question,
                    use_ollama: useAI && useLocal,
                    model: this.config.local.model
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Question failed');
            }

            this.updateLastBotMessage(data.answer, data.sources);
            this.chatHistory.push({
                question,
                answer: data.answer,
                sources: data.sources,
                timestamp: new Date()
            });
        } catch (error) {
            this.updateLastBotMessage(`Sorry, I encountered an error: ${error.message}`);
        }
    }

    addMessageToChat(message, sender, isLoading = false) {
        const chatMessages = document.getElementById('chat-messages');
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        if (isLoading) messageDiv.classList.add('loading');

        if (sender === 'user') {
            messageDiv.innerHTML = `
                <div class="message-content">
                    <p>${message}</p>
                </div>
            `;
        } else {
            messageDiv.innerHTML = `
                <div class="bot-avatar">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="message-content">
                    ${isLoading ? '<p>Thinking...</p>' : `<p>${message}</p>`}
                </div>
            `;
        }

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    updateLastBotMessage(answer, sources = []) {
        const chatMessages = document.getElementById('chat-messages');
        const lastMessage = chatMessages.lastElementChild;
        
        if (lastMessage && lastMessage.classList.contains('bot-message')) {
            lastMessage.classList.remove('loading');
            const content = lastMessage.querySelector('.message-content');
            let html = `<p>${answer}</p>`;
            
            if (sources && sources.length > 0) {
                const uniqueSources = [...new Set(sources)];
                html += `
                    <div class="message-sources">
                        <small>Sources: ${uniqueSources.join(', ')}</small>
                    </div>
                `;
            }
            
            content.innerHTML = html;
        }
    }

    clearChat() {
        const chatMessages = document.getElementById('chat-messages');
        if (chatMessages) {
            chatMessages.innerHTML = `
                <div class="welcome-message">
                    <div class="bot-avatar">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="message-content">
                        <h4>Hello! I'm your AI assistant</h4>
                        <p>I can help you find information in your documents and answer questions based on your knowledge base. Ask me anything!</p>
                        <div class="suggested-questions">
                            <span class="suggestion" data-question="What documents do I have?">What documents do I have?</span>
                            <span class="suggestion" data-question="Summarize my recent research">Summarize my recent research</span>
                            <span class="suggestion" data-question="Find programming tutorials">Find programming tutorials</span>
                            <span class="suggestion" data-question="What are the key concepts in my documents?">Key concepts in my documents</span>
                        </div>
                    </div>
                </div>
            `;
        }
        this.chatHistory = [];
    }

    autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }

    async loadDocuments() {
        try {
            const response = await fetch('/statistics');
            const stats = await response.json();

            // For now, we'll create mock document data
            // In a real implementation, you'd have an endpoint to get document details
            this.documents = [
                {
                    id: 1,
                    name: 'Sample Document.pdf',
                    type: 'pdf',
                    size: '2.5 MB',
                    added: '2024-01-15'
                }
            ];

            this.renderDocuments();
        } catch (error) {
            console.error('Error loading documents:', error);
        }
    }

    renderDocuments() {
        const documentsGrid = document.getElementById('documents-grid');
        const documentsEmpty = document.getElementById('documents-empty');

        if (this.documents.length === 0) {
            if (documentsGrid) documentsGrid.innerHTML = '';
            if (documentsEmpty) documentsEmpty.classList.remove('hidden');
        } else {
            if (documentsEmpty) documentsEmpty.classList.add('hidden');
            
            if (documentsGrid) {
                const documentsHtml = this.documents.map(doc => `
                    <div class="document-card" data-document-id="${doc.id}">
                        <div class="document-header">
                            <div class="document-icon">
                                <i class="fas fa-${this.getFileIcon(doc.type)}"></i>
                            </div>
                            <div class="document-info">
                                <h4>${doc.name}</h4>
                                <p>${doc.type.toUpperCase()} • ${doc.size}</p>
                            </div>
                        </div>
                        <div class="document-meta">
                            <span>Added: ${doc.added}</span>
                        </div>
                    </div>
                `).join('');

                documentsGrid.innerHTML = documentsHtml;
            }
        }
    }

    getFileIcon(type) {
        const icons = {
            'pdf': 'file-pdf',
            'docx': 'file-word',
            'xlsx': 'file-excel',
            'pptx': 'file-powerpoint',
            'md': 'file-alt',
            'txt': 'file-alt'
        };
        return icons[type] || 'file';
    }

    filterDocuments() {
        const searchTerm = document.getElementById('documents-search')?.value.toLowerCase() || '';
        const typeFilter = document.getElementById('document-type-filter')?.value || '';

        const filtered = this.documents.filter(doc => {
            const matchesSearch = doc.name.toLowerCase().includes(searchTerm);
            const matchesType = !typeFilter || doc.type === typeFilter;
            return matchesSearch && matchesType;
        });

        this.renderFilteredDocuments(filtered);
    }

    renderFilteredDocuments(documents) {
        const documentsGrid = document.getElementById('documents-grid');
        const documentsEmpty = document.getElementById('documents-empty');

        if (documents.length === 0) {
            if (documentsGrid) documentsGrid.innerHTML = '';
            if (documentsEmpty) {
                documentsEmpty.classList.remove('hidden');
                documentsEmpty.querySelector('h3').textContent = 'No documents found';
                documentsEmpty.querySelector('p').textContent = 'Try adjusting your search or filter criteria.';
            }
        } else {
            if (documentsEmpty) documentsEmpty.classList.add('hidden');
            
            if (documentsGrid) {
                const documentsHtml = documents.map(doc => `
                    <div class="document-card" data-document-id="${doc.id}">
                        <div class="document-header">
                            <div class="document-icon">
                                <i class="fas fa-${this.getFileIcon(doc.type)}"></i>
                            </div>
                            <div class="document-info">
                                <h4>${doc.name}</h4>
                                <p>${doc.type.toUpperCase()} • ${doc.size}</p>
                            </div>
                        </div>
                        <div class="document-meta">
                            <span>Added: ${doc.added}</span>
                        </div>
                    </div>
                `).join('');

                documentsGrid.innerHTML = documentsHtml;
            }
        }
    }

    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');
    }

    async loadLocalModels() {
        try {
            const response = await fetch('/ollama/models');
            const data = await response.json();

            const modelSelect = document.getElementById('local-model');
            const chatModel = document.getElementById('chat-model');
            
            if (modelSelect && data.models) {
                modelSelect.innerHTML = '<option value="">Select Model...</option>';
                data.models.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model;
                    option.textContent = model;
                    modelSelect.appendChild(option);
                });

                if (data.models.length > 0) {
                    this.config.local.model = data.models[0];
                    modelSelect.value = data.models[0];
                }
            }

            if (chatModel && data.models) {
                chatModel.innerHTML = '<option value="">Auto-select</option>';
                data.models.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model;
                    option.textContent = model;
                    chatModel.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Error loading local models:', error);
        }
    }

    async checkOllamaStatus() {
        try {
            const response = await fetch('/ollama/status');
            const status = await response.json();

            const statusIcon = document.getElementById('ollama-status');
            const statusText = document.getElementById('ollama-status-text');
            const aiStatusDot = document.getElementById('ai-status-dot');
            const aiStatusText = document.getElementById('ai-status-text');
            const chatStatusDot = document.getElementById('chat-status-dot');
            const chatStatusText = document.getElementById('chat-status-text');

            if (status.available) {
                if (statusIcon) statusIcon.classList.remove('offline');
                if (statusText) statusText.textContent = `Connected • ${status.available_models?.length || 0} models`;
                if (aiStatusDot) aiStatusDot.classList.remove('offline');
                if (aiStatusText) aiStatusText.textContent = 'AI Ready';
                if (chatStatusDot) chatStatusDot.classList.remove('offline');
                if (chatStatusText) chatStatusText.textContent = 'Ready';
            } else {
                if (statusIcon) statusIcon.classList.add('offline');
                if (statusText) statusText.textContent = 'Ollama not available';
                if (aiStatusDot) aiStatusDot.classList.add('offline');
                if (aiStatusText) aiStatusText.textContent = 'AI Offline';
                if (chatStatusDot) chatStatusDot.classList.add('offline');
                if (chatStatusText) chatStatusText.textContent = 'Offline';
            }
        } catch (error) {
            const statusIcon = document.getElementById('ollama-status');
            const statusText = document.getElementById('ollama-status-text');
            const aiStatusDot = document.getElementById('ai-status-dot');
            const aiStatusText = document.getElementById('ai-status-text');
            
            if (statusIcon) statusIcon.classList.add('offline');
            if (statusText) statusText.textContent = 'Connection error';
            if (aiStatusDot) aiStatusDot.classList.add('offline');
            if (aiStatusText) aiStatusText.textContent = 'Connection Error';
        }
    }

    updateLocalModel() {
        const modelSelect = document.getElementById('local-model');
        this.config.local.model = modelSelect.value;
    }

    updateTemperature() {
        const tempInput = document.getElementById('temperature');
        const tempValue = document.querySelector('.temp-value');
        
        this.config.local.temperature = parseFloat(tempInput.value);
        if (tempValue) {
            tempValue.textContent = tempInput.value;
        }
    }

    updateApiProvider() {
        const provider = document.getElementById('api-provider').value;
        const modelSelect = document.getElementById('online-model');
        
        this.config.online.provider = provider;
        
        // Update model options based on provider
        const modelOptions = {
            'openai': [
                { value: 'gpt-3.5-turbo', text: 'GPT-3.5 Turbo' },
                { value: 'gpt-4', text: 'GPT-4' }
            ],
            'anthropic': [
                { value: 'claude-3-sonnet', text: 'Claude 3 Sonnet' },
                { value: 'claude-3-opus', text: 'Claude 3 Opus' }
            ],
            'gemini': [
                { value: 'gemini-pro', text: 'Gemini Pro' }
            ]
        };
        
        if (modelSelect && modelOptions[provider]) {
            modelSelect.innerHTML = '';
            modelOptions[provider].forEach(option => {
                const optionElement = document.createElement('option');
                optionElement.value = option.value;
                optionElement.textContent = option.text;
                modelSelect.appendChild(optionElement);
            });
            
            this.config.online.model = modelOptions[provider][0].value;
        }
    }

    updateApiKey() {
        this.config.online.apiKey = document.getElementById('api-key').value;
        this.updateApiStatus();
    }

    updateApiStatus() {
        const statusIcon = document.getElementById('api-status');
        const statusText = document.getElementById('api-status-text');
        
        if (statusIcon && statusText) {
            if (this.config.online.apiKey) {
                statusIcon.classList.remove('offline');
                statusText.textContent = `${this.config.online.provider.toUpperCase()} configured`;
            } else {
                statusIcon.classList.add('offline');
                statusText.textContent = 'Enter API key';
            }
        }
    }

    async loadStatistics() {
        try {
            const response = await fetch('/statistics');
            const stats = await response.json();

            const elements = {
                'total-docs': stats.total_documents || 0,
                'total-chunks': stats.total_chunks || 0,
                'db-size': `${(stats.database_size_mb || 0).toFixed(1)} MB`,
                'last-updated': stats.last_updated ? 
                    new Date(stats.last_updated).toLocaleDateString() : 'Never',
                'settings-db-size': `${(stats.database_size_mb || 0).toFixed(1)} MB`,
                'settings-total-docs': stats.total_documents || 0,
                'settings-last-updated': stats.last_updated ? 
                    new Date(stats.last_updated).toLocaleDateString() : 'Never'
            };

            Object.entries(elements).forEach(([id, value]) => {
                const element = document.getElementById(id);
                if (element) element.textContent = value;
            });
        } catch (error) {
            console.error('Error loading statistics:', error);
        }
    }

    showLoading(title = 'Processing...', message = 'Please wait') {
        const overlay = document.getElementById('loading-overlay');
        const titleEl = document.getElementById('loading-title');
        const messageEl = document.getElementById('loading-message');
        
        if (titleEl) titleEl.textContent = title;
        if (messageEl) messageEl.textContent = message;
        if (overlay) overlay.classList.remove('hidden');
    }

    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) overlay.classList.add('hidden');
    }

    showModal(title, content) {
        const modalTitle = document.getElementById('modal-title');
        const modalContent = document.getElementById('modal-content');
        const modalOverlay = document.getElementById('modal-overlay');
        
        if (modalTitle) modalTitle.textContent = title;
        if (modalContent) modalContent.innerHTML = content;
        if (modalOverlay) modalOverlay.classList.remove('hidden');
    }

    closeModal() {
        const modalOverlay = document.getElementById('modal-overlay');
        if (modalOverlay) modalOverlay.classList.add('hidden');
    }

    confirmClearData() {
        this.showModal(
            'Clear All Data',
            `
            <p>Are you sure you want to clear all data from your AI Memory Bank?</p>
            <p><strong>This action cannot be undone.</strong></p>
            <div style="display: flex; gap: 1rem; margin-top: 1.5rem;">
                <button class="danger-btn" onclick="app.clearData()">
                    <i class="fas fa-trash"></i>
                    Clear All Data
                </button>
                <button class="action-btn" onclick="app.closeModal()">
                    Cancel
                </button>
            </div>
            `
        );
    }

    async clearData() {
        try {
            const response = await fetch('/clear', {
                method: 'POST'
            });

            if (response.ok) {
                this.showToast('All data cleared successfully!', 'success');
                this.loadStatistics();
                this.loadDocuments();
                this.closeModal();
            } else {
                throw new Error('Failed to clear data');
            }
        } catch (error) {
            this.showToast(`Failed to clear data: ${error.message}`, 'error');
        }
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };

        toast.innerHTML = `
            <i class="toast-icon ${icons[type]}"></i>
            <span class="toast-message">${message}</span>
            <button class="toast-close" onclick="this.parentElement.remove()">&times;</button>
        `;

        container.appendChild(toast);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 5000);
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Initialize when DOM is loaded
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new AIMemoryBank();
}); 