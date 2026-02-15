(function () {
  var API_URL = (typeof window.CHATBOT_API_URL !== "undefined" && window.CHATBOT_API_URL)
    ? window.CHATBOT_API_URL
    : "/api/chat";

  function getOrCreateSessionId() {
    try {
      var id = localStorage.getItem("josiah_session_id");
      if (id && id.length >= 10) return id;
      id = "sess_" + Math.random().toString(36).slice(2) + "_" + Date.now().toString(36);
      localStorage.setItem("josiah_session_id", id);
      return id;
    } catch (e) {
      return "default";
    }
  }

  var messagesEl = document.getElementById("chat-messages");
  var inputEl = document.getElementById("chat-input");
  var sendBtn = document.getElementById("chat-send");
  var clearBtn = document.getElementById("chat-clear");

  if (!messagesEl || !inputEl || !sendBtn) return;

  if (clearBtn) {
    clearBtn.addEventListener("click", function () {
      while (messagesEl.firstChild) messagesEl.removeChild(messagesEl.firstChild);
      inputEl.value = "";
      inputEl.focus();
      appendMessage("Hey I'm The Creater, what can I do for you?", "bot");
    });
  }

  function appendMessage(text, type) {
    type = type || "bot";
    var wrap = document.createElement("div");
    wrap.className = "chat-msg chat-msg--" + type;
    var label = type === "user" ? "You" : "The Creater";
    wrap.innerHTML =
      '<div class="chat-msg-label">' + escapeHtml(label) + "</div>" +
      '<div class="chat-msg-content">' + escapeHtml(text) + "</div>";
    messagesEl.appendChild(wrap);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    return wrap;
  }

  function appendThinking() {
    var wrap = document.createElement("div");
    wrap.className = "chat-msg chat-msg--thinking";
    wrap.setAttribute("data-thinking", "1");
    wrap.innerHTML =
      '<div class="chat-msg-label">The Creater</div>' +
      '<div class="chat-msg-content chat-thinking"><span class="chat-thinking-dot"></span><span class="chat-thinking-dot"></span><span class="chat-thinking-dot"></span></div>';
    messagesEl.appendChild(wrap);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    return wrap;
  }

  function replaceThinkingWithReply(thinkingEl, text, isError, suggested, memoryHint) {
    thinkingEl.classList.remove("chat-msg--thinking");
    thinkingEl.classList.add(isError ? "chat-msg--error" : "chat-msg--bot");
    thinkingEl.removeAttribute("data-thinking");
    var content = thinkingEl.querySelector(".chat-msg-content");
    content.className = "chat-msg-content";
    content.textContent = "";

    var useTyping = !isError && text.length > 80;
    if (useTyping) {
      typeIntoElement(content, text, function () {
        appendMemoryHint(thinkingEl, memoryHint);
        appendSuggestedToMessage(thinkingEl, suggested);
        messagesEl.scrollTop = messagesEl.scrollHeight;
      });
    } else {
      content.textContent = text;
      appendMemoryHint(thinkingEl, memoryHint);
      appendSuggestedToMessage(thinkingEl, suggested);
    }
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function appendMemoryHint(msgWrap, hint) {
    if (!hint || typeof hint !== "string" || !msgWrap) return;
    var existing = msgWrap.querySelector(".chat-memory-hint");
    if (existing) existing.remove();
    var div = document.createElement("div");
    div.className = "chat-memory-hint";
    div.textContent = hint;
    msgWrap.appendChild(div);
  }

  function typeIntoElement(el, fullText, onDone) {
    var index = 0;
    var chunk = 3;
    var interval = setInterval(function () {
      index += chunk;
      if (index >= fullText.length) {
        el.textContent = fullText;
        clearInterval(interval);
        if (onDone) onDone();
        return;
      }
      el.textContent = fullText.slice(0, index);
      messagesEl.scrollTop = messagesEl.scrollHeight;
    }, 16);
  }

  function appendSuggestedToMessage(msgWrap, suggested) {
    if (!suggested || !Array.isArray(suggested) || suggested.length === 0) return;
    var row = document.createElement("div");
    row.className = "chat-suggested";
    row.setAttribute("aria-label", "Suggested questions");
    for (var i = 0; i < suggested.length; i++) {
      var q = suggested[i];
      if (!q || typeof q !== "string") continue;
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "chat-suggestion-chip";
      btn.textContent = q;
      btn.addEventListener("click", function (ev) {
        var t = (ev.target && ev.target.textContent) || "";
        if (t) {
          inputEl.value = t;
          inputEl.focus();
          sendMessage();
        }
      });
      row.appendChild(btn);
    }
    msgWrap.appendChild(row);
  }

  function escapeHtml(s) {
    var div = document.createElement("div");
    div.textContent = s;
    return div.innerHTML;
  }

  function setSendEnabled(enabled) {
    sendBtn.disabled = !enabled;
  }

  function sendMessage() {
    var text = (inputEl.value || "").trim();
    if (!text) return;

    inputEl.value = "";
    if (inputEl.rows > 1) inputEl.rows = 1;
    appendMessage(text, "user");
    setSendEnabled(false);
    var thinkingEl = appendThinking();

    fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, session_id: getOrCreateSessionId() })
    })
      .then(function (res) {
        if (!res.ok) throw new Error("Request failed");
        return res.json();
      })
      .then(function (data) {
        var suggested = data.suggested;
        var memoryHint = data.memory_hint || null;
        replaceThinkingWithReply(thinkingEl, data.reply || "No response.", false, suggested, memoryHint);
      })
      .catch(function () {
        replaceThinkingWithReply(thinkingEl, "Can't reach the server. 1) Make sure the server is still running. 2) Open chat from the same server URL (e.g. http://localhost:5000 or your deployed URL). 3) If needed, restart the backend.", true, null, null);
      })
      .finally(function () {
        setSendEnabled(true);
      });
  }

  sendBtn.addEventListener("click", sendMessage);
  inputEl.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  inputEl.addEventListener("input", function () {
    var lines = (inputEl.value || "").split("\n").length;
    inputEl.rows = Math.min(Math.max(1, lines), 8);
  });

  function getStoredApiUrl() {
    try {
      return localStorage.getItem("chatbot_api_url") || "";
    } catch (e) {
      return "";
    }
  }

  function setStoredApiUrl(url) {
    try {
      if (url) localStorage.setItem("chatbot_api_url", url);
      else localStorage.removeItem("chatbot_api_url");
    } catch (e) {}
  }

  function copyLastBotReply() {
    var botMsgs = messagesEl.querySelectorAll(".chat-msg--bot .chat-msg-content");
    if (botMsgs.length === 0) return false;
    var last = botMsgs[botMsgs.length - 1];
    var text = last.textContent || "";
    if (!text) return false;
    try {
      navigator.clipboard.writeText(text);
      return true;
    } catch (e) {
      return false;
    }
  }

  function scrollToBottom() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function isNearBottom(threshold) {
    var el = messagesEl;
    threshold = threshold || 80;
    return el.scrollHeight - el.scrollTop - el.clientHeight < threshold;
  }

  messagesEl.addEventListener("scroll", function () {
    if (!scrollToBottomBtn) return;
    scrollToBottomBtn.style.opacity = isNearBottom() ? "0" : "1";
  });

  var scrollToBottomBtn = null;
  (function addScrollButton() {
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "chat-scroll-down";
    btn.setAttribute("aria-label", "Scroll to bottom");
    btn.innerHTML = "<span>↓</span>";
    btn.style.opacity = "0";
    btn.addEventListener("click", function () {
      scrollToBottom();
      btn.style.opacity = "0";
    });
    var main = document.getElementById("chat-main");
    if (main) main.appendChild(btn);
    scrollToBottomBtn = btn;
  })();

  document.addEventListener("keydown", function (e) {
    if (e.ctrlKey && e.key === "Enter") {
      e.preventDefault();
      sendMessage();
    }
    if (e.key === "Escape") {
      inputEl.blur();
    }
  });

  appendMessage("Hey I'm The Creater, what can I do for you?", "bot");

  (function checkOrigin() {
    // Only warn when opened directly as file://.
    // Hosting from localhost or LAN IP is fine because API_URL is same-origin (/api/chat).
    if (window.location.protocol !== "file:") return;
    var banner = document.createElement("div");
    banner.style.cssText = "background:#3d2a00;color:#ffc;padding:8px 12px;font-size:13px;text-align:center;";
    banner.textContent = "Open from http://localhost:5000 (run START_CHATBOT.bat) instead of opening index.html directly.";
    document.body.insertBefore(banner, document.body.firstChild);
  })();
})();
