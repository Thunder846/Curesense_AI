// =====================================
// CureSense AI Frontend
// Compatible with FastAPI Backend
// =====================================

let currentMode = "";
let sessionId = "";
let isConversationStarted = false;

// -----------------------------
// Scroll to Chat Section
// -----------------------------
function scrollToModes() {
  document.getElementById("modes").scrollIntoView({
    behavior: "smooth",
  });
}

// -----------------------------
// Generate Session ID
// -----------------------------
function generateSessionId() {
  return (
    "session_" + Date.now() + "_" + Math.random().toString(36).substring(2, 10)
  );
}

// -----------------------------
// Select Mode
// -----------------------------
function chooseMode(mode) {
  currentMode = mode;
  sessionId = generateSessionId();
  isConversationStarted = false;

  document.getElementById("mode-cards").style.display = "none";
  document.getElementById("chat-panel").hidden = false;

  document.getElementById("chat-mode-icon").textContent =
    mode === "symptom" ? "🌿" : "💊";

  document.getElementById("chat-mode-label").textContent =
    mode === "symptom" ? "Symptom Advisor" : "Medicine Info";

  const messages = document.getElementById("messages");
  messages.innerHTML = "";

  if (mode === "symptom") {
    addAIMessage(
      `Hello 👋

Describe your symptoms in detail.

Example:
"I have fever and headache since yesterday."`,
    );
  } else {
    addAIMessage(
      `Hello 👋

Enter a medicine name.

Example:
"Paracetamol"`,
    );
  }

  document.getElementById("user-input").focus();
}

// -----------------------------
// Back Button
// -----------------------------
function goBack() {
  currentMode = "";
  sessionId = "";
  isConversationStarted = false;

  document.getElementById("chat-panel").hidden = true;
  document.getElementById("mode-cards").style.display = "grid";
}

// -----------------------------
// Enter Key
// -----------------------------
document
  .getElementById("user-input")
  .addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
      sendMessage();
    }
  });

// -----------------------------
// Send Message
// -----------------------------
async function sendMessage() {
  const input = document.getElementById("user-input");

  const text = input.value.trim();

  if (!text) return;

  addUserMessage(text);

  input.value = "";

  showTyping();

  try {
    let endpoint = "";
    let body = {};

    // FIRST MESSAGE
    if (!isConversationStarted) {
      endpoint = "/start";

      body = {
        session_id: sessionId,
        mode: currentMode,
        text: text,
      };
    }

    // FOLLOW UP
    else {
      endpoint = "/followup";

      body = {
        session_id: sessionId,
        mode: currentMode,
        question: text,
      };
    }

    const response = await fetch(endpoint, {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify(body),
    });

    removeTyping();

    if (!response.ok) {
      addAIMessage("❌ Server Error");

      return;
    }

    const data = await response.json();

    isConversationStarted = true;

    addAIMessage(data.reply);
  } catch (err) {
    console.error(err);

    removeTyping();

    addAIMessage("Unable to connect to the backend.");
  }
}

// -----------------------------
// User Message
// -----------------------------
function addUserMessage(text) {
  const div = document.createElement("div");

  div.className = "msg-user";

  div.textContent = text;

  document.getElementById("messages").appendChild(div);

  scrollBottom();
}

// -----------------------------
// AI Message
// -----------------------------
function addAIMessage(text) {
  const div = document.createElement("div");

  div.className = "msg-ai";

  let html = text;

  html = html.replace(
    /Severity:\s*mild/gi,
    "Severity: <span class='tag tag-mild'>MILD</span>",
  );

  html = html.replace(
    /Severity:\s*moderate/gi,
    "Severity: <span class='tag tag-moderate'>MODERATE</span>",
  );

  html = html.replace(
    /Severity:\s*severe/gi,
    "Severity: <span class='tag tag-severe'>SEVERE</span>",
  );

  html = html.replace(/\n/g, "<br>");

  div.innerHTML = html;

  document.getElementById("messages").appendChild(div);

  scrollBottom();
}

// -----------------------------
// Typing Animation
// -----------------------------
function showTyping() {
  const div = document.createElement("div");

  div.className = "msg-ai";

  div.id = "typing";

  div.innerHTML = `
        <div class="bubble-typing">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;

  document.getElementById("messages").appendChild(div);

  scrollBottom();
}

// -----------------------------
// Remove Typing
// -----------------------------
function removeTyping() {
  const typing = document.getElementById("typing");

  if (typing) {
    typing.remove();
  }
}

// -----------------------------
// Auto Scroll
// -----------------------------
function scrollBottom() {
  const messages = document.getElementById("messages");

  messages.scrollTop = messages.scrollHeight;
}
