document.getElementById('send-btn').addEventListener('click', () => {
    const inputBox = document.getElementById('user-input');
    const query = inputBox.value.trim();

    if (!query) {
        addMessage("System", "Please enter a query!");
        return;
    }

    addMessage("User", query);
    inputBox.value = '';

    fetch('/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
    })
        .then(response => response.json())
        .then(data => addMessage("System", data.response))
        .catch(err => addMessage("System", "An error occurred!"));
});

function addMessage(sender, message) {
    const chatBox = document.getElementById('chat-box');
    const messageDiv = document.createElement('div');
    messageDiv.className = sender.toLowerCase();
    messageDiv.textContent = `${sender}: ${message}`;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}
