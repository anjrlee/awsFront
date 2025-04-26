document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const sidebar = document.querySelector('.sidebar');
    const mobileSidebarToggle = document.getElementById('mobile-sidebar-toggle');
    const toggleSidebarBtn = document.getElementById('toggle-sidebar');
    const newChatBtn = document.getElementById('new-chat-btn');
    const exportChatBtn = document.getElementById('export-chat-btn');
    const settingsBtn = document.getElementById('settings-btn');
    const settingsPanel = document.getElementById('settings-panel');
    const closeSettingsBtn = document.getElementById('close-settings');
    const overlay = document.getElementById('overlay');
    const themeButtons = document.querySelectorAll('.theme-btn');
    const colorButtons = document.querySelectorAll('.color-btn');
    const chatList = document.getElementById('chat-list');
    
    // New DOM Elements
    const exportDialog = document.getElementById('export-dialog');
    const closeExportBtn = document.getElementById('close-export');
    const exportChatList = document.getElementById('export-chat-list');
    const micButton = document.getElementById('mic-button');
    const uploadButton = document.getElementById('upload-button');
    const fileInput = document.getElementById('file-input');
    const recordingIndicator = document.getElementById('recording-indicator');
    const stopRecordingBtn = document.getElementById('stop-recording');

    // Chat management
    let chats = [];
    let currentChatId = null;


    // Initialize the app
    initializeApp();

    // Function to initialize the app
    function initializeApp() {
        // Load saved chats from localStorage
        loadChats();
        
        // If no chats exist, create a new one
        if (chats.length === 0) {
            createNewChat();
        } else {
            // Load the most recent chat
            loadChat(chats[0].id);
        }
        
        // Load saved theme and color preferences
        loadThemePreferences();
    }

    // Function to load saved chats from localStorage
    function loadChats() {
        const savedChats = localStorage.getItem('bedrock-chats');
        if (savedChats) {
            chats = JSON.parse(savedChats);
            renderChatList();
        }
    }

    // Function to save chats to localStorage
    function saveChats() {
        localStorage.setItem('bedrock-chats', JSON.stringify(chats));
    }

    // Function to create a new chat
    async function createNewChat() {
        try {
            showTypingIndicator();
            
            const response = await fetch('/api/deleteVectorDB', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify("new chat created"),
            });
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const data = await response.json();
            removeTypingIndicator();
            addMessage(data.response);
        } catch (error) {
            console.error('Error:', error);
            removeTypingIndicator();
            addMessage('Sorry, there was an error processing your request. Please try again.');
        }
        // Generate a unique ID for the chat
        const chatId = Date.now().toString();
        
        // Create a new chat object
        const newChat = {
            id: chatId,
            title: `Chat ${chats.length + 1}`,
            messages: [{
                role: 'assistant',
                content: 'Hello! I\'m an AI assistant powered by Amazon Bedrock. How can I help you today?'
            }],
            createdAt: new Date().toISOString()
        };
        
        // Add to the beginning of the chats array (most recent first)
        chats.unshift(newChat);
        
        // Save to localStorage
        saveChats();
        
        // Render the chat list
        renderChatList();
        
        // Load the new chat
        loadChat(chatId);
        
    }

    // Function to render the chat list in the sidebar
    function renderChatList() {
        // Clear the current list
        chatList.innerHTML = '';
        
        // Add each chat to the list
        chats.forEach(chat => {
            const chatItem = document.createElement('div');
            chatItem.className = `chat-item ${chat.id === currentChatId ? 'active' : ''}`;
            chatItem.dataset.chatId = chat.id;
            
            // Get the first few characters of the first user message, or use default title
            let chatTitle = chat.title;
            const firstUserMessage = chat.messages.find(msg => msg.role === 'user');
            if (firstUserMessage) {
                chatTitle = firstUserMessage.content.substring(0, 20) + (firstUserMessage.content.length > 20 ? '...' : '');
            }
            
            chatItem.innerHTML = `
                <i class="fas fa-comment"></i>
                <span>${chatTitle}</span>
            `;
            
            chatItem.addEventListener('click', () => loadChat(chat.id));
            chatList.appendChild(chatItem);
        });
    }

    // Function to load a specific chat
    function loadChat(chatId) {
        // Find the chat by ID
        const chat = chats.find(c => c.id === chatId);
        if (!chat) return;
        
        // Set as current chat
        currentChatId = chatId;
        
        // Clear chat messages
        chatMessages.innerHTML = '';
        
        // Add all messages from the chat
        chat.messages.forEach(msg => {
            addMessageToUI(msg.content, msg.role === 'user');
        });
        
        // Update active state in chat list
        document.querySelectorAll('.chat-item').forEach(item => {
            item.classList.toggle('active', item.dataset.chatId === chatId);
        });
        
        // Close sidebar on mobile
        if (window.innerWidth <= 768) {
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
        }
    }

    // Function to add a message to the UI
    function addMessageToUI(content, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user' : 'assistant'}`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.textContent = content;
        
        messageDiv.appendChild(messageContent);
        chatMessages.appendChild(messageDiv);
        
        // Scroll to the bottom of the chat
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Function to add a message to the current chat
    function addMessage(content, isUser = false) {
        // Find the current chat
        const chatIndex = chats.findIndex(c => c.id === currentChatId);
        if (chatIndex === -1) return;
        
        // Add message to the chat
        chats[chatIndex].messages.push({
            role: isUser ? 'user' : 'assistant',
            content: content
        });
        
        // If this is the first user message, update the chat title
        if (isUser && chats[chatIndex].messages.filter(m => m.role === 'user').length === 1) {
            chats[chatIndex].title = content.substring(0, 20) + (content.length > 20 ? '...' : '');
            renderChatList();
        }
        
        // Save to localStorage
        saveChats();
        
        // Add to UI
        addMessageToUI(content, isUser);
    }



    function showThinkingProcess(){
        
    }
    // Function to show typing indicator
    function showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'message assistant';
        indicator.id = 'typing-indicator';
        
        const container = document.createElement('div');
        container.className = 'typing-container'; // 新增一層包住文字 + 點點
    
        const text = document.createElement('div');
        text.className = 'typing-text';
        text.textContent = '打字中...';
    
        const indicatorContent = document.createElement('div');
        indicatorContent.className = 'typing-indicator';
        
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('span');
            indicatorContent.appendChild(dot);
        }
        
        container.appendChild(text);             // 文字在上
        container.appendChild(indicatorContent); // 點點在下
        indicator.appendChild(container);
        chatMessages.appendChild(indicator);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        thinkgProcess=["Input Validation","Embedding Generation","Vector Database Search","Re-ranking","Response Generation","Output Verification"]
        thinkginTime=[2,4,6,4,4]
        // 創建 sleep 函數
        const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

        // 使用 async 函數來實現動畫
        async function animateText(text) {
            
            for(let i=0;i<thinkgProcess.length;i++){
                text.textContent = thinkgProcess[i] ;
                for (let j = 0; j < thinkginTime[i]; j++) {
                    text.classList.add('hidden');
                    await sleep(500);
                    text.classList.remove('hidden');
                    text.classList.add('flex');
                    await sleep(1500);
                }
            }
        }

        // 調用函數
        //const text = document.querySelector('.your-text-element'); // 替換成你的元素選擇器
        animateText(text);

      


    }
    

    // Function to remove typing indicator
    function removeTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    // Function to send message to backend
    async function sendMessage(message) {
        let finished = false;
    
        showTypingIndicator();
    
        const sendPromise = fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message }),
        })
        .then(async (response) => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const data = await response.json();
            addMessage(data.response);
        })
        .catch((error) => {
            console.error('Error:', error);
            addMessage('Sorry, there was an error processing your request. Please try again.');
        })
        .finally(() => {
            finished = true;
            removeTypingIndicator();
        });
       
    }
    
    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    function doSomethingWhileWaiting() {
        console.log('Waiting for response...');
        // 這裡可以加你想要等待時做的事情，例如小動畫
    }
    

    // Function to start a new chat
    function startNewChat() {
        createNewChat();
    }

    // Function to export current chat
    function exportChat() {
        // Show the export dialog
        exportDialog.classList.add('active');
        overlay.classList.add('active');
        
        // Populate the export chat list
        renderExportChatList();
    }
    
    // Function to render the export chat list
    function renderExportChatList() {
        // Clear the current list
        exportChatList.innerHTML = '';
        
        // Add each chat to the list
        chats.forEach(chat => {
            const chatItem = document.createElement('div');
            chatItem.className = 'export-chat-item';
            chatItem.dataset.chatId = chat.id;
            
            // Get the first few characters of the first user message, or use default title
            let chatTitle = chat.title;
            const firstUserMessage = chat.messages.find(msg => msg.role === 'user');
            if (firstUserMessage) {
                chatTitle = firstUserMessage.content.substring(0, 30) + (firstUserMessage.content.length > 30 ? '...' : '');
            }
            
            // Add date information
            const date = new Date(chat.createdAt);
            const formattedDate = date.toLocaleDateString();
            
            chatItem.innerHTML = `
                <i class="fas fa-comment"></i>
                <div>
                    <div>${chatTitle}</div>
                    <div class="chat-date">${formattedDate}</div>
                </div>
            `;
            
            chatItem.addEventListener('click', () => downloadChat(chat.id));
            exportChatList.appendChild(chatItem);
        });
    }
    
    // Function to download a specific chat
    function downloadChat(chatId) {
        // Find the chat by ID
        const chat = chats.find(c => c.id === chatId);
        if (!chat) return;
        
        // Create formatted text from chat messages
        let exportText = '';
        chat.messages.forEach(msg => {
            const role = msg.role === 'user' ? 'You' : 'Assistant';
            exportText += `${role}: ${msg.content}\n\n`;
        });
        
        // Create a blob and download link
        const blob = new Blob([exportText], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        
        // Get current date and time for filename
        const date = new Date();
        const formattedDate = date.toISOString().replace(/[:.]/g, '-').slice(0, 19);
        
        a.href = url;
        a.download = `chat-export-${formattedDate}.txt`;
        a.click();
        
        // Clean up
        URL.revokeObjectURL(url);
        
        // Close the export dialog
        exportDialog.classList.remove('active');
        overlay.classList.remove('active');
    }

    // Speech recognition variables
    let recognition = null;
    let isRecording = false;
    
    // Initialize speech recognition
    function initSpeechRecognition() {
        // Check if browser supports speech recognition
        if ('webkitSpeechRecognition' in window) {
            recognition = new webkitSpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = true;
            
            recognition.onstart = () => {
                isRecording = true;
                recordingIndicator.classList.add('active');
                console.log("start")
            };
            
            recognition.onend = () => {
                isRecording = false;
                recordingIndicator.classList.remove('active');
                console.log("end")
            };
            
            recognition.onresult = (event) => {
                let interimTranscript = '';
                let finalTranscript = '';
                console.log("result")
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const transcript = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {
                        finalTranscript += transcript;
                    } else {
                        interimTranscript += transcript;
                    }
                }
                
                // Update the input field with the transcription
                if (finalTranscript !== '') {
                    userInput.value = finalTranscript;
                } else {
                    userInput.value = interimTranscript;
                }
                
            };
            
            recognition.onerror = (event) => {
                console.error('Speech recognition error', event.error);
                isRecording = false;
                recordingIndicator.classList.remove('active');
            };
        } else {
            micButton.style.display = 'none';
            console.warn('Speech recognition not supported in this browser');
        }
    }
    
    // Function to toggle speech recognition
    function toggleSpeechRecognition() {
        if (!recognition) {
            initSpeechRecognition();
        }
        
        if (isRecording) {
            recognition.stop();
        } else {
            recognition.start();
        }
    }

    // Function to toggle settings panel
    function toggleSettings() {
        settingsPanel.classList.toggle('active');
        overlay.classList.toggle('active');
        
        // Close sidebar on mobile when settings is opened
        if (window.innerWidth <= 768 && settingsPanel.classList.contains('active')) {
            sidebar.classList.remove('active');
        }
    }
    
    // Function to handle file uploads
    async function handleFileUpload(file) {
        if (!file) return;
        const formData = new FormData();
        formData.append('file', file);
        sendButton.disabled = true;
        try {
            await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
        } catch (error) {
            console.error('Failed to upload file:', error);
        }
        sendButton.disabled = false;
        // Check file extension
        const fileName = file.name;
        const fileExtension = fileName.split('.').pop().toLowerCase();
        
        // Validate file type
        const allowedImageTypes = ['jpg', 'jpeg', 'png', 'gif'];
        const allowedDocTypes = ['pdf', 'md', 'markdown'];
        
        if ([...allowedImageTypes, ...allowedDocTypes].includes(fileExtension)) {
            // Create a message with the file
            const reader = new FileReader();
            
            reader.onload = (e) => {
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message user';
                
                const messageContent = document.createElement('div');
                messageContent.className = 'message-content';
                
                const fileMessage = document.createElement('div');
                fileMessage.className = 'file-message';
                
                // Handle different file types
                if (allowedImageTypes.includes(fileExtension)) {
                    // For images, show a preview
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    img.className = 'file-preview';
                    fileMessage.appendChild(img);
                }
                
                // Add file info
                const fileInfo = document.createElement('div');
                fileInfo.className = 'file-info';
                
                // Choose icon based on file type
                let iconClass = 'fa-file';
                if (allowedImageTypes.includes(fileExtension)) {
                    iconClass = 'fa-file-image';
                } else if (fileExtension === 'pdf') {
                    iconClass = 'fa-file-pdf';
                } else if (['md', 'markdown'].includes(fileExtension)) {
                    iconClass = 'fa-file-alt';
                }
                
                fileInfo.innerHTML = `
                    <i class="fas ${iconClass} file-icon"></i>
                    <span>${fileName}</span>
                `;
                
                fileMessage.appendChild(fileInfo);
                messageContent.appendChild(fileMessage);
                messageDiv.appendChild(messageContent);
                chatMessages.appendChild(messageDiv);
                
                // Scroll to the bottom of the chat
                chatMessages.scrollTop = chatMessages.scrollHeight;
                
                // Add to chat history
                const chatIndex = chats.findIndex(c => c.id === currentChatId);
                if (chatIndex !== -1) {
                    const fileContent = `[File: ${fileName}]`;
                    chats[chatIndex].messages.push({
                        role: 'user',
                        content: fileContent,
                        fileType: fileExtension,
                        fileName: fileName
                    });
                    
                    // If this is the first user message, update the chat title
                    if (chats[chatIndex].messages.filter(m => m.role === 'user').length === 1) {
                        chats[chatIndex].title = `File: ${fileName}`;
                        renderChatList();
                    }
                    
                    // Save to localStorage
                    saveChats();
                    
                    // Send a message to the AI about the uploaded file
                    sendMessage(`I've uploaded a ${fileExtension.toUpperCase()} file named "${fileName}". Please acknowledge.`);
                  
                    //if backend show message
                    // sendButton.disabled = false;

                }
            };
            
            // Read the file
            if (allowedImageTypes.includes(fileExtension)) {
                reader.readAsDataURL(file);
            } else {
                reader.readAsText(file);
            }
        } else {
            alert(`File type not supported. Please upload an image (JPG, PNG, GIF), PDF, or Markdown file.`);
        }
    }

    // Function to apply theme
    function applyTheme(theme) {
        // Remove all theme classes
        document.body.classList.remove('light-theme', 'dark-theme', 'blue-theme');
        
        // Add selected theme class
        if (theme !== 'light') {
            document.body.classList.add(`${theme}-theme`);
        }
        
        // Update active state on buttons
        themeButtons.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.theme === theme);
        });
        
        // Save preference
        localStorage.setItem('preferred-theme', theme);
    }
    
    // Function to apply accent color
    function applyAccentColor(color) {
        // Remove all color classes
        document.body.classList.remove('accent-blue', 'accent-green', 'accent-purple', 'accent-orange');
        
        // Add selected color class if not default blue
        if (color !== 'blue') {
            document.body.classList.add(`accent-${color}`);
        }
        
        // Update active state on buttons
        colorButtons.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.color === color);
        });
        
        // Save preference
        localStorage.setItem('preferred-color', color);
    }

    // Function to load saved theme preferences
    function loadThemePreferences() {
        const savedTheme = localStorage.getItem('preferred-theme') || 'light';
        const savedColor = localStorage.getItem('preferred-color') || 'blue';
        
        applyTheme(savedTheme);
        applyAccentColor(savedColor);
    }

    // Event listener for send button
    sendButton.addEventListener('click', () => {
        const message = userInput.value.trim();
        if (message) {
            addMessage(message, true);
            userInput.value = '';
            sendMessage(message);
        }
    });

    // Event listener for Enter key (with Shift+Enter for new line)
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendButton.click();
        }
    });

    // Event listeners for sidebar functionality
    mobileSidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('active');
        overlay.classList.toggle('active');
    });

    toggleSidebarBtn.addEventListener('click', () => {
        sidebar.classList.toggle('active');
        overlay.classList.toggle('active');
    });

    // Event listener for overlay click (closes sidebar and settings)
    overlay.addEventListener('click', () => {
        sidebar.classList.remove('active');
        settingsPanel.classList.remove('active');
        overlay.classList.remove('active');
    });

    // Event listeners for sidebar buttons
    newChatBtn.addEventListener('click', startNewChat);
    exportChatBtn.addEventListener('click', exportChat);
    settingsBtn.addEventListener('click', toggleSettings);
    closeSettingsBtn.addEventListener('click', toggleSettings);

    // Event listeners for theme buttons
    themeButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const theme = btn.dataset.theme;
            applyTheme(theme);
        });
    });

    // Event listeners for color buttons
    colorButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const color = btn.dataset.color;
            applyAccentColor(color);
        });
    });
    
    // Event listener for export dialog close button
    closeExportBtn.addEventListener('click', () => {
        exportDialog.classList.remove('active');
        overlay.classList.remove('active');
    });
    
    // Event listener for microphone button
    micButton.addEventListener('click', toggleSpeechRecognition);
    
    // Event listener for stop recording button
    stopRecordingBtn.addEventListener('click', () => {
        if (recognition && isRecording) {
            recognition.stop();
        }
    });
    
    // Event listener for upload button
    uploadButton.addEventListener('click', () => {
        fileInput.click();
    });
    
    // Event listener for file input change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
            // Reset the file input so the same file can be uploaded again
            fileInput.value = '';
        }
    });
});






