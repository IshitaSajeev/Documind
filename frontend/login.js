const API_BASE = "http://localhost:8000/api";

const usernameInput = document.getElementById("username");
const passwordInput = document.getElementById("password");
const loginBtn = document.getElementById("loginBtn");
const loginStatus = document.getElementById("loginStatus");

loginBtn.addEventListener("click", async () => {
  const username = usernameInput.value.trim();
  const password = passwordInput.value;

  if (!username || !password) {
    loginStatus.textContent = "Enter both username and password.";
    return;
  }

  loginStatus.textContent = "Logging in...";

  try {
    const response = await fetch(`${API_BASE}/token/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    const data = await response.json();

    if (!response.ok) {
      loginStatus.textContent = "Invalid username or password.";
      return;
    }

    localStorage.setItem("documind_token", data.access);
    localStorage.setItem("documind_refresh", data.refresh);
    window.location.href = "index.html";
  } catch (err) {
    loginStatus.textContent = `Login failed: ${err.message}`;
  }
});

// Allow pressing Enter to submit
passwordInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") loginBtn.click();
});