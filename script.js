const API_KEY = "YOUR_API_KEY"; // Apni key yahan dalein
const PROXY_URL = "https://api.ecomagent.in/v1/messages";

async function sendMessage() {
    const input = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');
    const message = input.value.trim();

    if (!message) return;

    // User ka message screen par dikhayein
    chatBox.innerHTML += `<div class="bg-blue-900 p-3 rounded-lg self-end max-w-[80%]">${message}</div>`;
    input.value = '';

    try {
        const response = await fetch(PROXY_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "x-api-key": API_KEY,
                "anthropic-version": "2023-06-01",
                "dangerouslyAllowBrowser": "true" // Browser integration ke liye
            },
            body: JSON.stringify({
                model: "claude-opus-4.6",
                max_tokens: 1024,
                messages: [{ role: "user", content: message }]
            })
        });

        const data = await response.json();
        const aiResponse = data.content[0].text;

        // AI ka response screen par dikhayein
        chatBox.innerHTML += `<div class="bg-gray-700 p-3 rounded-lg self-start max-w-[80%]">${aiResponse}</div>`;
        
        // Auto scroll to bottom
        chatBox.scrollTop = chatBox.scrollHeight;

    } catch (error) {
        console.error("Error:", error);
        chatBox.innerHTML += `<div class="text-red-500">Error: Connection fail ho gaya.</div>`;
    }
}
