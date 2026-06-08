const chat = document.getElementById("chat");
const form = document.getElementById("ask-form");
const input = document.getElementById("question-input");
const sendBtn = document.getElementById("send-btn");
const fileInput = document.getElementById("file-input");
const uploadBtn = document.getElementById("upload-btn");
const uploadStatus = document.getElementById("upload-status");
const docsBtn = document.getElementById("docs-btn");
const docCount = document.getElementById("doc-count");

// Ask a question — stream the response
form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const question = input.value.trim();
    if (!question) return;

    // Show user message
    appendMessage(question, "user");
    input.value = "";
    sendBtn.disabled = true;

    // Create assistant message placeholder
    const msgEl = appendMessage("", "assistant");

    try {
        const response = await fetch("/api/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question }),
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let fullText = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split("\n");

            for (const line of lines) {
                if (line.startsWith("data: ")) {
                    const data = line.slice(6);
                    if (data === "[DONE]") break;

                    try {
                        const parsed = JSON.parse(data);
                        fullText += parsed.token;
                        msgEl.querySelector("p").textContent = fullText;
                    } catch {}
                }
            }
        }
    } catch (err) {
        msgEl.querySelector("p").textContent = "Error: Could not get a response.";
    }

    sendBtn.disabled = false;
    chat.scrollTop = chat.scrollHeight;
});

// Upload documents
uploadBtn.addEventListener("click", async () => {
    const files = fileInput.files;
    if (!files.length) return;

    uploadStatus.textContent = "Uploading...";
    uploadBtn.disabled = true;

    const formData = new FormData();
    for (const file of files) {
        formData.append("files", file);
    }

    try {
        const response = await fetch("/api/ingest", {
            method: "POST",
            body: formData,
        });
        const result = await response.json();
        uploadStatus.textContent = result.message;
        fileInput.value = "";
        loadDocCount();
    } catch {
        uploadStatus.textContent = "Upload failed.";
    }

    uploadBtn.disabled = false;
});

// View document count
docsBtn.addEventListener("click", loadDocCount);

async function loadDocCount() {
    try {
        const response = await fetch("/api/documents");
        const data = await response.json();
        docCount.textContent = `${data.documents.length} document(s), ${data.total_chunks} chunks`;
    } catch {
        docCount.textContent = "Could not load documents.";
    }
}

function appendMessage(text, role) {
    const div = document.createElement("div");
    div.className = `message ${role}`;
    div.innerHTML = `<p>${text}</p>`;
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
    return div;
}

// Load count on startup
loadDocCount();
