/* ==========================================================================
   AI College Assistant - chat frontend logic
   Talks to the Flask backend via fetch(); no full page reloads.
   ========================================================================== */

(function () {
  "use strict";

  const chatWindow = document.getElementById("chatWindow");
  const chatForm = document.getElementById("chatForm");
  const chatInput = document.getElementById("chatInput");
  const sendBtn = document.getElementById("sendBtn");
  const clearChatBtn = document.getElementById("clearChatBtn");
  const typingIndicator = document.getElementById("typingIndicator");
  const suggestedRow = document.getElementById("suggestedRow");
  const sidebar = document.getElementById("sidebar");
  const sidebarToggle = document.getElementById("sidebarToggle");
  const popularList = document.getElementById("popularList");
  const noticesList = document.getElementById("noticesList");

  const DEFAULT_SUGGESTIONS = [
    "What is the admission process?",
    "What is the fee structure?",
    "What are the college timings?",
    "Where is the library?",
    "Tell me about placements",
  ];

  // ---------------------------------------------------------------------
  // Helpers
  // ---------------------------------------------------------------------

  function formatTime(date) {
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }

  function scrollToBottom() {
    chatWindow.scrollTop = chatWindow.scrollHeight;
  }

  function appendUserMessage(text) {
    const wrapper = document.createElement("div");
    wrapper.className = "message user-message";
    wrapper.innerHTML = `
      <div class="avatar user-avatar">You</div>
      <div class="message-content">
        <div class="bubble"></div>
        <div class="msg-time"></div>
      </div>
    `;
    wrapper.querySelector(".bubble").textContent = text;
    wrapper.querySelector(".msg-time").textContent = formatTime(new Date());
    chatWindow.appendChild(wrapper);
    scrollToBottom();
  }

  function appendBotMessage(answer, { isFallback = false, isError = false, confidence = null } = {}) {
    const wrapper = document.createElement("div");
    wrapper.className = "message bot-message";

    let bubbleClass = "bubble";
    if (isError) bubbleClass += " error";
    else if (isFallback) bubbleClass += " fallback";

    wrapper.innerHTML = `
      <div class="avatar bot-avatar">AI</div>
      <div class="message-content">
        <div class="${bubbleClass}"></div>
        <div class="msg-time"></div>
      </div>
    `;
    wrapper.querySelector(".bubble").textContent = answer;
    wrapper.querySelector(".msg-time").textContent = formatTime(new Date());
    chatWindow.appendChild(wrapper);
    scrollToBottom();
  }

  function showTyping() {
    typingIndicator.hidden = false;
    scrollToBottom();
  }

  function hideTyping() {
    typingIndicator.hidden = true;
  }

  function renderSuggestions(list) {
    suggestedRow.innerHTML = "";
    list.slice(0, 5).forEach((q) => {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "suggested-chip";
      chip.textContent = q;
      chip.addEventListener("click", () => {
        chatInput.value = q;
        chatForm.dispatchEvent(new Event("submit"));
      });
      suggestedRow.appendChild(chip);
    });
  }

  // ---------------------------------------------------------------------
  // Sending a message
  // ---------------------------------------------------------------------

  async function sendMessage(text) {
    const trimmed = text.trim();
    if (!trimmed) return;

    appendUserMessage(trimmed);
    chatInput.value = "";
    sendBtn.disabled = true;
    showTyping();

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: trimmed }),
      });

      const payload = await response.json();
      hideTyping();

      if (!response.ok || !payload.success) {
        appendBotMessage(
          payload.error || "Something went wrong. Please try again.",
          { isError: true }
        );
        return;
      }

      const data = payload.data;
      appendBotMessage(data.answer, {
        isFallback: data.is_fallback,
        confidence: data.confidence,
      });
    } catch (err) {
      hideTyping();
      appendBotMessage(
        "I couldn't reach the server. Please check your connection and try again.",
        { isError: true }
      );
    } finally {
      sendBtn.disabled = false;
      chatInput.focus();
    }
  }

  chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    sendMessage(chatInput.value);
  });

  chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      chatForm.dispatchEvent(new Event("submit"));
    }
  });

  // ---------------------------------------------------------------------
  // Clear chat
  // ---------------------------------------------------------------------

  clearChatBtn.addEventListener("click", () => {
    chatWindow.innerHTML = "";
    appendBotMessage(
      "Chat cleared. Ask me anything about admissions, courses, fees, exams, hostel, library, placements, and more."
    );
  });

  // ---------------------------------------------------------------------
  // Sidebar category buttons
  // ---------------------------------------------------------------------

  document.querySelectorAll(".nav-item").forEach((item) => {
    item.addEventListener("click", () => {
      document.querySelectorAll(".nav-item").forEach((i) => i.classList.remove("active"));
      item.classList.add("active");

      const category = item.getAttribute("data-category");
      if (category) {
        sendMessage(`Tell me about ${category}`);
      }
      if (window.innerWidth <= 820) {
        sidebar.classList.remove("open");
      }
    });
  });

  sidebarToggle.addEventListener("click", () => {
    sidebar.classList.toggle("open");
  });

  // ---------------------------------------------------------------------
  // Popular queries (right panel)
  // ---------------------------------------------------------------------

  popularList.querySelectorAll("li").forEach((li) => {
    li.addEventListener("click", () => {
      chatInput.value = li.textContent;
      chatForm.dispatchEvent(new Event("submit"));
    });
  });

  // ---------------------------------------------------------------------
  // Load notices for the right panel
  // ---------------------------------------------------------------------

  async function loadNotices() {
    try {
      const response = await fetch("/api/notices");
      const payload = await response.json();

      if (!payload.success || !payload.data.length) {
        noticesList.innerHTML = '<li class="notice-loading">No active notices.</li>';
        return;
      }

      noticesList.innerHTML = "";
      payload.data.slice(0, 5).forEach((notice) => {
        const li = document.createElement("li");
        li.innerHTML = `<span class="notice-title"></span>`;
        li.querySelector(".notice-title").textContent = notice.title;
        li.title = notice.content;
        noticesList.appendChild(li);
      });
    } catch (err) {
      noticesList.innerHTML = '<li class="notice-loading">Could not load notices.</li>';
    }
  }

  // ---------------------------------------------------------------------
  // Init
  // ---------------------------------------------------------------------

  renderSuggestions(DEFAULT_SUGGESTIONS);
  loadNotices();

  document.querySelectorAll("[data-time]").forEach((el) => {
    el.textContent = formatTime(new Date());
  });

  chatInput.focus();
})();
