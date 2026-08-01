const API_BASE = "http://localhost:8000/api";
// Redirect to login if no token is present
if (!localStorage.getItem("documind_token")) {
  window.location.href = "login.html";
}

document.getElementById("logoutBtn").addEventListener("click", () => {
  localStorage.removeItem("documind_token");
  localStorage.removeItem("documind_refresh");
  window.location.href = "login.html";
});

// NOTE: In a real deployment, get this token from a login flow.
// This demo assumes the token is stored after a prior login request.
let accessToken = localStorage.getItem("documind_token") || "";

let currentDocumentId = null;

const fileInput = document.getElementById("fileInput");
const uploadBtn = document.getElementById("uploadBtn");
const uploadStatus = document.getElementById("uploadStatus");
const summaryOutput = document.getElementById("summaryOutput");
const questionInput = document.getElementById("questionInput");
const askBtn = document.getElementById("askBtn");
const answerOutput = document.getElementById("answerOutput");

uploadBtn.addEventListener("click", async () => {
  const file = fileInput.files[0];
  if (!file) {
    uploadStatus.textContent = "Please choose a file first.";
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  uploadStatus.textContent = "Uploading and processing...";

  try {
    const response = await fetch(`${API_BASE}/documents/upload/`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      uploadStatus.textContent = `Error: ${data.error || "Upload failed"}`;
      return;
    }

    currentDocumentId = data.id;
    uploadStatus.textContent = `Uploaded "${data.title}" successfully.`;
    summaryOutput.textContent = data.summary || "Processing...";
  } catch (err) {
    uploadStatus.textContent = `Request failed: ${err.message}`;
  }
});

askBtn.addEventListener("click", async () => {
  if (!currentDocumentId) {
    answerOutput.textContent = "Upload a document first.";
    return;
  }

  const question = questionInput.value.trim();
  if (!question) {
    answerOutput.textContent = "Type a question first.";
    return;
  }

  answerOutput.textContent = "Thinking...";

  try {
    const response = await fetch(
      `${API_BASE}/documents/${currentDocumentId}/ask/`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ question }),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      answerOutput.textContent = `Error: ${data.error || "Failed to get answer"}`;
      return;
    }

    answerOutput.textContent = data.answer;
  } catch (err) {
    answerOutput.textContent = `Request failed: ${err.message}`;
  }
});
