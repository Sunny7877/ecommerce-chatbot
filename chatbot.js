document.addEventListener('DOMContentLoaded', () => {
    const chatbotBtn = document.getElementById('chatbot-btn');
    const chatbotWindow = document.getElementById('chatbot-window');
    const closeChatbot = document.getElementById('close-chatbot');
    const clearChatBtn = document.getElementById('clear-chat-btn');
    const chatBody = document.getElementById('chat-body');
    const chatInput = document.getElementById('chat-input');

    if (!chatbotBtn || !chatbotWindow || !chatBody || !chatInput) return;

    const STORAGE_KEY = 'shopease_chat_history';
    const USER_KEY = 'shopease_chat_user_id';
    const OPEN_KEY = 'shopease_chat_is_open';

    const defaultWelcomeHTML = '<div class="chat-message bot-msg">Hello! Welcome to our e-commerce shopping assistant. You can ask me about products, prices, offers, cart items, orders, delivery, payments, returns, refunds, accounts, and customer support. How may I help you today?</div>';

    // Current active user ID from Flask session
    const activeUserId = String(typeof CURRENT_USER_ID !== 'undefined' ? CURRENT_USER_ID : '0');
    const shouldClearOnLoad = typeof CLEAR_CHAT_FLAG !== 'undefined' && CLEAR_CHAT_FLAG === true;

    // Helper: completely wipe stored chat
    function clearChatStorage() {
        try {
            localStorage.removeItem(STORAGE_KEY);
            localStorage.removeItem(OPEN_KEY);
        } catch(e) {}
        chatBody.innerHTML = defaultWelcomeHTML;
    }

    // 1. If server flagged a logout (e.g. redirect from /logout), clear chat
    if (shouldClearOnLoad) {
        clearChatStorage();
        localStorage.setItem(USER_KEY, activeUserId);
    } else {
        // 2. If user ID changed (e.g. user logged out or switched account), clear chat
        const savedUserId = localStorage.getItem(USER_KEY);
        if (savedUserId && savedUserId !== '0' && savedUserId !== activeUserId) {
            clearChatStorage();
        }
        localStorage.setItem(USER_KEY, activeUserId);
    }

    // 3. Restore chat history from localStorage
    function loadChatHistory() {
        try {
            const raw = localStorage.getItem(STORAGE_KEY);
            if (raw) {
                const history = JSON.parse(raw);
                if (Array.isArray(history) && history.length > 0) {
                    chatBody.innerHTML = defaultWelcomeHTML;
                    history.forEach(item => {
                        appendMessage(item.sender, item.text, '', false);
                    });
                }
            }
        } catch (e) {
            console.error('Error loading chat history:', e);
        }
    }

    loadChatHistory();

    // 4. Restore open/closed window state
    try {
        if (localStorage.getItem(OPEN_KEY) === 'true') {
            chatbotWindow.style.display = 'flex';
            chatbotBtn.style.display = 'none';
            chatBody.scrollTop = chatBody.scrollHeight;
        }
    } catch(e) {}

    // Open chatbot
    chatbotBtn.addEventListener('click', () => {
        chatbotWindow.style.display = 'flex';
        chatbotBtn.style.display = 'none';
        try {
            localStorage.setItem(OPEN_KEY, 'true');
        } catch(e) {}
        chatBody.scrollTop = chatBody.scrollHeight;
        chatInput.focus();
    });

    // Close chatbot (DO NOT ERASE CHAT)
    closeChatbot.addEventListener('click', () => {
        chatbotWindow.style.display = 'none';
        chatbotBtn.style.display = 'flex';
        try {
            localStorage.setItem(OPEN_KEY, 'false');
        } catch(e) {}
    });

    // Manual trash/clear button in chatbot header
    if (clearChatBtn) {
        clearChatBtn.addEventListener('click', () => {
            if (confirm('Do you want to clear your chat history?')) {
                clearChatStorage();
            }
        });
    }

    // 5. Intercept any logout link clicked on the page to immediately clear chat
    document.addEventListener('click', (e) => {
        const link = e.target.closest('a');
        if (link && link.getAttribute('href')) {
            const href = link.getAttribute('href').toLowerCase();
            if (href.includes('/logout') || href.endsWith('logout')) {
                clearChatStorage();
            }
        }
    });

    // Handle sending a message
    chatInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter' && this.value.trim() !== '') {
            sendMessage(this.value.trim());
            this.value = '';
        }
    });

    function saveMessageToHistory(sender, text) {
        try {
            let history = [];
            const raw = localStorage.getItem(STORAGE_KEY);
            if (raw) {
                history = JSON.parse(raw);
            }
            history.push({ sender, text });
            localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
        } catch(e) {
            console.warn('Could not save chat message to localStorage:', e);
        }
    }

    function sendMessage(text) {
        appendMessage('user', text);
        const typingId = 'typing-' + Date.now();
        appendMessage('bot', '<div class="spinner-grow spinner-grow-sm text-primary"></div> typing...', typingId);

        fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        })
        .then(res => res.json())
        .then(data => {
            const typingElem = document.getElementById(typingId);
            if (typingElem) typingElem.remove();
            
            // Convert simple markdown links to HTML: [Text](url)
            let formattedResponse = (data.response || '').replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
            appendMessage('bot', formattedResponse);
        })
        .catch(err => {
            const typingElem = document.getElementById(typingId);
            if (typingElem) typingElem.remove();
            appendMessage('bot', 'Sorry, I am having trouble connecting right now.');
        });
    }

    function appendMessage(sender, text, id = '', save = true) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'chat-message ' + (sender === 'user' ? 'user-msg' : 'bot-msg');
        if (id) msgDiv.id = id;
        msgDiv.innerHTML = text; // Allow HTML for links
        chatBody.appendChild(msgDiv);
        chatBody.scrollTop = chatBody.scrollHeight;

        if (save && !id) {
            saveMessageToHistory(sender, text);
        }
    }
});
