document.addEventListener("DOMContentLoaded", () => {
    const inputField = document.getElementById("user-input");

    // Allow pressing "Enter" to send message
    inputField.addEventListener("keypress", function (e) {
        if (e.key === "Enter") {
            sendMessage();
        }
    });
});

function sendMessage() {
    const inputField = document.getElementById("user-input");
    const chatBox = document.getElementById("chat-box");
    const message = inputField.value.trim();

    if (message === "") return;

    // 1. Add User Message to Chat
    appendMessage(message, "user-message");
    inputField.value = ""; // Clear input

    // 2. Show a temporary "Typing..." indicator (Optional UI enhancement)
    const loadingId = "loading-" + Date.now();
    appendMessage("Typing...", "bot-message", loadingId);

    // 3. Send to Backend
    fetch("/api/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        // Remove "Typing..."
        const loadingMsg = document.getElementById(loadingId);
        if (loadingMsg) loadingMsg.remove();

        // Add Bot Response
        if (data.error) {
            appendMessage("Error: " + data.error, "bot-message");
        } else {
            appendMessage(data.response, "bot-message");
        }
    })
    .catch(error => {
        console.error("Error:", error);
        const loadingMsg = document.getElementById(loadingId);
        if (loadingMsg) loadingMsg.remove();
        appendMessage("Sorry, I couldn't reach the server.", "bot-message");
    });
}

function appendMessage(text, className, id = null) {
    const chatBox = document.getElementById("chat-box");
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", className);
    messageDiv.textContent = text;
    
    if (id) messageDiv.id = id;

    chatBox.appendChild(messageDiv);
    
    // Auto-scroll to the bottom
    chatBox.scrollTop = chatBox.scrollHeight;
}