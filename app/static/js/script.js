/* --- GLOBAL VARIABLES --- */
let isSoundOn = false; // Default: Sound Off

document.addEventListener("DOMContentLoaded", () => {
    const inputField = document.getElementById("user-input");
    if(inputField) inputField.focus();

    // 1. LOAD SAVED CHAT HISTORY
    loadChatHistory();

    // Listen for Enter key
    inputField.addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendMessage();
    });
});

/* --- 1. THEME & UI LOGIC --- */
function toggleTheme() {
    document.body.classList.toggle("dark-mode");
    const icon = document.getElementById("theme-icon");
    if(icon) icon.textContent = document.body.classList.contains("dark-mode") ? "light_mode" : "dark_mode";
}

function useSuggestion(text) {
    const inputField = document.getElementById("user-input");
    inputField.value = text;
    sendMessage();
}

/* --- 2. MAIN MESSAGE LOGIC --- */
function sendMessage() {
    const inputField = document.getElementById("user-input");
    const message = inputField.value.trim();
    if (!message) return;

    // Add User Message & Save
    addMessage(message, "user", false, null, true);
    inputField.value = "";

    const loadingId = showLoading();

    fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: message })
    })
    .then(res => res.json())
    .then(data => {
        removeLoading(loadingId);
        
        // Parse Markdown (Unified logic)
        let htmlContent = marked.parse(data.response);
        
        // Add Bot Message & Save
        addMessage(htmlContent, "bot", true, data.chat_id, true);

        // Speak Text (if sound is on)
        speakText(data.response);
    })
    .catch(err => {
        removeLoading(loadingId);
        addMessage("Sorry, I can't reach the server.", "bot", false, null, false);
    });
}

/**
 * Adds message to UI and optionally saves to storage.
 * @param {string} text - Message content
 * @param {string} sender - 'user' or 'bot'
 * @param {boolean} isHTML - Render as HTML?
 * @param {int} chatId - DB ID for feedback (optional)
 * @param {boolean} save - Save to LocalStorage?
 */
function addMessage(text, sender, isHTML = false, chatId = null, save = true) {
    const chatBox = document.getElementById("chat-box");
    const wrapper = document.createElement("div");
    wrapper.classList.add("message-wrapper", sender);
    
    let contentHtml = '';
    
    if (sender === "bot") {
        contentHtml += `<div class="avatar"><span class="material-icons-round">smart_toy</span></div>`;
    }
    
    // Create Bubble
    let messageHtml = isHTML ? `<div class="message">${text}` : `<div class="message">${escapeHtml(text)}`;

    // Add Feedback Buttons (Only for new bot messages that have an ID)
    if (sender === "bot" && chatId) {
        messageHtml += `
            <div class="feedback-actions">
                <button onclick="sendFeedback(${chatId}, 1, this)" title="Helpful">
                    <span class="material-icons-round" style="font-size:16px;">thumb_up</span>
                </button>
                <button onclick="sendFeedback(${chatId}, -1, this)" title="Not Helpful">
                    <span class="material-icons-round" style="font-size:16px;">thumb_down</span>
                </button>
            </div>
        `;
    }
    
    messageHtml += `</div>`; // Close bubble
    contentHtml += messageHtml;

    wrapper.innerHTML = contentHtml;
    chatBox.appendChild(wrapper);
    chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: 'smooth' });

    // Save to Storage
    if (save) {
        saveToLocalStorage(text, sender, isHTML);
    }
}

/* --- 3. PERSISTENCE (MEMORY) LOGIC --- */
function saveToLocalStorage(text, sender, isHTML) {
    let history = JSON.parse(localStorage.getItem('chatHistory')) || [];
    history.push({ text, sender, isHTML });
    localStorage.setItem('chatHistory', JSON.stringify(history));
}

function loadChatHistory() {
    let history = JSON.parse(localStorage.getItem('chatHistory')) || [];
    const chatBox = document.getElementById("chat-box");
    
    // Only clear if we have history to show
    if (history.length > 0) {
        chatBox.innerHTML = ''; 
        history.forEach(msg => {
            // pass save=false to avoid duplicating in storage
            addMessage(msg.text, msg.sender, msg.isHTML, null, false);
        });
    }
}

function clearChat() {
    if(confirm("Are you sure you want to clear the conversation?")) {
        localStorage.removeItem('chatHistory');
        location.reload();
    }
}

/* --- 4. FEEDBACK LOGIC --- */
function sendFeedback(chatId, rating, btnElement) {
    const parent = btnElement.parentElement;
    parent.innerHTML = `<span style="font-size:12px; opacity:0.7;">Thanks!</span>`;
    fetch("/api/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ chat_id: chatId, rating: rating })
    });
}

/* --- 5. TEXT TO SPEECH --- */
function toggleSound() {
    isSoundOn = !isSoundOn;
    const icon = document.getElementById("sound-icon");
    if (isSoundOn) {
        icon.textContent = "volume_up";
        icon.style.color = "#2563eb"; 
    } else {
        icon.textContent = "volume_off";
        icon.style.color = "#94a3b8";
        window.speechSynthesis.cancel();
    }
}

function speakText(text) {
    if (!isSoundOn) return;
    window.speechSynthesis.cancel();
    
    // Strip HTML/Markdown for speaking
    const cleanText = text.replace(/\*/g, "").replace(/(<([^>]+)>)/gi, "");
    
    const utterance = new SpeechSynthesisUtterance(cleanText);
    const voices = window.speechSynthesis.getVoices();
    utterance.voice = voices.find(voice => voice.name.includes('Google US English')) || voices[0];
    window.speechSynthesis.speak(utterance);
}

/* --- 6. UTILITIES --- */
function showLoading() {
    const chatBox = document.getElementById("chat-box");
    const id = "loading-" + Date.now();
    const wrapper = document.createElement("div");
    wrapper.classList.add("message-wrapper", "bot");
    wrapper.id = id;
    wrapper.innerHTML = `
        <div class="avatar"><span class="material-icons-round">smart_toy</span></div>
        <div class="message typing"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>
    `;
    chatBox.appendChild(wrapper);
    chatBox.scrollTop = chatBox.scrollHeight;
    return id;
}

function removeLoading(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

function escapeHtml(text) {
    return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

/* --- 7. VOICE INPUT --- */
function startVoiceInput() {
    if (!('webkitSpeechRecognition' in window)) {
        alert("Voice input is only supported in Chrome/Edge.");
        return;
    }
    const recognition = new webkitSpeechRecognition();
    const micBtn = document.getElementById("mic-btn");
    recognition.start();
    if(micBtn) micBtn.style.color = "#ef4444"; 
    recognition.onresult = (event) => {
        document.getElementById("user-input").value = event.results[0][0].transcript;
        sendMessage();
    };
    recognition.onend = () => { if(micBtn) micBtn.style.color = ""; };
}

/* --- 8. IMAGE UPLOAD LOGIC --- */
function handleImageUpload() {
    const fileInput = document.getElementById('image-upload');
    const file = fileInput.files[0];

    if (file) {
        // Show preview in chat
        addMessage("📂 Uploading image...", "user", false, null, true);
        
        const reader = new FileReader();
        reader.onload = function(e) {
            const base64Image = e.target.result;
            sendImageToBackend(base64Image);
        };
        reader.readAsDataURL(file);
    }
}

function sendImageToBackend(base64Image) {
    const loadingId = showLoading();

    fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
            message: "Analyze this image", // Fallback text
            image: base64Image 
        })
    })
    .then(res => res.json())
    .then(data => {
        removeLoading(loadingId);
        
        // Use Markdown Parser here too!
        let htmlContent = marked.parse(data.response);
        addMessage(htmlContent, "bot", true, data.chat_id, true);
        
        speakText(data.response);
    })
    .catch(err => {
        removeLoading(loadingId);
        addMessage("Error processing image.", "bot", false, null, false);
    });
}