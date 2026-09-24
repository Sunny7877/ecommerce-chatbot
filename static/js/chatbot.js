document.addEventListener('DOMContentLoaded', () => {
    const chatbotBtn = document.getElementById('chatbot-btn');
    const chatbotWindow = document.getElementById('chatbot-window');
    const closeChatbot = document.getElementById('close-chatbot');
    const chatBody = document.getElementById('chat-body');
    const chatInput = document.getElementById('chat-input');

    if(!chatbotBtn) return;

    chatbotBtn.addEventListener('click', () => {
        chatbotWindow.style.display = 'flex';
        chatbotBtn.style.display = 'none';
    });

    closeChatbot.addEventListener('click', () => {
        chatbotWindow.style.display = 'none';
        chatbotBtn.style.display = 'flex';
    });

    chatInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter' && this.value.trim() !== '') {
            sendMessage(this.value.trim());
            this.value = '';
        }
    });

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
            document.getElementById(typingId).remove();
            // Convert simple markdown links to HTML: [Text](url)
            let formattedResponse = data.response.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
            appendMessage('bot', formattedResponse);
        })
        .catch(err => {
            document.getElementById(typingId).remove();
            appendMessage('bot', 'Sorry, I am having trouble connecting right now.');
        });
    }

    function appendMessage(sender, text, id = '') {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'chat-message ' + (sender === 'user' ? 'user-msg' : 'bot-msg');
        if(id) msgDiv.id = id;
        msgDiv.innerHTML = text; // Allow HTML for links
        chatBody.appendChild(msgDiv);
        chatBody.scrollTop = chatBody.scrollHeight;
    }
});
