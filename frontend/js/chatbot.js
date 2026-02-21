// Chatbot JavaScript
// Functionality will be implemented later

const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');

// Send message on button click
sendBtn.addEventListener('click', sendMessage);

// Send message on Enter key
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

async function sendMessage() {
    const message = userInput.value.trim();
    
    if (!message) {
        return;
    }
    
    // Clear input
    userInput.value = '';
    
    // Add user message to chat
    addMessage(message, 'user');
    
    // Disable input while processing
    userInput.disabled = true;
    sendBtn.disabled = true;
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        // Call backend API
        const response = await fetch('/api/chatbot/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question: message })
        });
        
        const data = await response.json();
        
        hideTypingIndicator();
        
        if (response.ok) {
            // Display answer
            addMessage(data.answer, 'bot');
            
            // Display recommendations if available
            if (data.recommendations && data.recommendations.length > 0) {
                const recommendationsText = '💡 Recommendations:\n\n' + 
                    data.recommendations.map((rec, idx) => `${idx + 1}. ${rec}`).join('\n');
                addMessage(recommendationsText, 'bot');
            }
        } else {
            addMessage('Sorry, I encountered an error. Please try again.', 'bot');
        }
    } catch (error) {
        hideTypingIndicator();
        addMessage('Network error. Please check your connection and try again.', 'bot');
        console.error('Chatbot error:', error);
    } finally {
        // Re-enable input
        userInput.disabled = false;
        sendBtn.disabled = false;
        userInput.focus();
    }
}

function addMessage(text, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = type === 'bot' ? '🤖' : '👤';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    
    const messageText = document.createElement('div');
    messageText.className = 'message-text';
    
    // Handle multi-line text and preserve line breaks
    const lines = text.split('\n');
    lines.forEach((line, index) => {
        if (line.trim()) {
            const lineElement = document.createElement('div');
            lineElement.textContent = line;
            if (index > 0) {
                lineElement.style.marginTop = '8px';
            }
            messageText.appendChild(lineElement);
        } else if (index < lines.length - 1) {
            // Add spacing for empty lines
            const br = document.createElement('br');
            messageText.appendChild(br);
        }
    });
    
    const messageTime = document.createElement('div');
    messageTime.className = 'message-time';
    messageTime.textContent = getCurrentTime();
    
    content.appendChild(messageText);
    content.appendChild(messageTime);
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    scrollToBottom();
}

function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot-message';
    typingDiv.id = 'typingIndicator';
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = '🤖';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'message-text typing-indicator';
    typingIndicator.innerHTML = '<span></span><span></span><span></span>';
    
    content.appendChild(typingIndicator);
    typingDiv.appendChild(avatar);
    typingDiv.appendChild(content);
    
    chatMessages.appendChild(typingDiv);
    scrollToBottom();
}

function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

function getCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString('en-US', { 
        hour: 'numeric', 
        minute: '2-digit',
        hour12: true 
    });
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Auto-focus input on page load
window.addEventListener('load', () => {
    userInput.focus();
});
