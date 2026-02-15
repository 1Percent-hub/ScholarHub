(function () {
  var API_URL = (typeof window.CHATBOT_API_URL !== "undefined" && window.CHATBOT_API_URL)
    ? window.CHATBOT_API_URL
    : (window.location.hostname === "localhost" && window.location.port === "5000")
      ? "/api/chat"
      : "http://localhost:5000/api/chat";

  var STORAGE_KEY_POS = "ai_widget_panel_position";

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

  function loadPosition() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY_POS);
      if (raw) {
        var p = JSON.parse(raw);
        if (typeof p.left === "number" && typeof p.top === "number") return p;
      }
    } catch (e) {}
    return null;
  }

  function savePosition(left, top) {
    try {
      localStorage.setItem(STORAGE_KEY_POS, JSON.stringify({ left: left, top: top }));
    } catch (e) {}
  }

  var tabEl = document.getElementById("ai-widget-tab");
  var panelEl = document.getElementById("ai-widget-panel");
  var headerEl = document.getElementById("ai-widget-header");
  var messagesEl = document.getElementById("ai-widget-messages");
  var inputEl = document.getElementById("ai-widget-input");
  var sendBtn = document.getElementById("ai-widget-send");
  var closeBtn = document.getElementById("ai-widget-close");

  if (!tabEl || !panelEl || !messagesEl || !inputEl || !sendBtn) return;

  function setPanelPosition(left, top) {
    panelEl.style.right = "";
    panelEl.style.top = top + "px";
    panelEl.style.left = left + "px";
    panelEl.style.transform = "none";
  }

  function openPanel() {
    panelEl.classList.remove("ai-widget-panel--hidden");
    var pos = loadPosition();
    if (pos) setPanelPosition(pos.left, pos.top);
  }

  function closePanel() {
    panelEl.classList.add("ai-widget-panel--hidden");
  }

  function togglePanel() {
    if (panelEl.classList.contains("ai-widget-panel--hidden")) openPanel();
    else closePanel();
  }

  tabEl.addEventListener("click", togglePanel);
  if (closeBtn) closeBtn.addEventListener("click", closePanel);

  (function initDrag() {
    var pos = loadPosition();
    if (pos) {
      setPanelPosition(pos.left, pos.top);
    }

    var dragging = false;
    var startX = 0, startY = 0, startLeft = 0, startTop = 0;

    function getPanelRect() {
      var r = panelEl.getBoundingClientRect();
      return { left: r.left, top: r.top };
    }

    function onMouseMove(e) {
      if (!dragging) return;
      var dx = e.clientX - startX;
      var dy = e.clientY - startY;
      var left = Math.max(0, Math.min(window.innerWidth - panelEl.offsetWidth, startLeft + dx));
      var top = Math.max(0, Math.min(window.innerHeight - panelEl.offsetHeight, startTop + dy));
      setPanelPosition(left, top);
      savePosition(left, top);
    }

    function onMouseUp() {
      if (!dragging) return;
      dragging = false;
      document.removeEventListener("mousemove", onMouseMove);
      document.removeEventListener("mouseup", onMouseUp);
    }

    headerEl.addEventListener("mousedown", function (e) {
      if (e.button !== 0) return;
      var r = getPanelRect();
      startLeft = r.left;
      startTop = r.top;
      startX = e.clientX;
      startY = e.clientY;
      dragging = true;
      document.addEventListener("mousemove", onMouseMove);
      document.addEventListener("mouseup", onMouseUp);
      e.preventDefault();
    });
  })();

  function escapeHtml(s) {
    var div = document.createElement("div");
    div.textContent = s;
    return div.innerHTML;
  }

  function appendMessage(text, type) {
    type = type || "bot";
    var wrap = document.createElement("div");
    wrap.className = "ai-widget-msg ai-widget-msg--" + type;
    var label = type === "user" ? "You" : "Josiah";
    wrap.innerHTML =
      '<div class="ai-widget-msg-label">' + escapeHtml(label) + "</div>" +
      '<div class="ai-widget-msg-content">' + escapeHtml(text) + "</div>";
    messagesEl.appendChild(wrap);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    return wrap;
  }

  function appendThinking() {
    var wrap = document.createElement("div");
    wrap.className = "ai-widget-msg ai-widget-msg--thinking";
    wrap.setAttribute("data-thinking", "1");
    wrap.innerHTML =
      '<div class="ai-widget-msg-label">Josiah</div>' +
      '<div class="ai-widget-msg-content ai-widget-thinking">' +
      '<span class="ai-widget-thinking-dot"></span><span class="ai-widget-thinking-dot"></span><span class="ai-widget-thinking-dot"></span>' +
      '</div>';
    messagesEl.appendChild(wrap);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    return wrap;
  }

  function appendMemoryHint(msgWrap, hint) {
    if (!hint || typeof hint !== "string" || !msgWrap) return;
    var existing = msgWrap.querySelector(".ai-widget-memory-hint");
    if (existing) existing.remove();
    var div = document.createElement("div");
    div.className = "ai-widget-memory-hint";
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
    row.className = "ai-widget-suggested";
    for (var i = 0; i < suggested.length; i++) {
      var q = suggested[i];
      if (!q || typeof q !== "string") continue;
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "ai-widget-chip";
      btn.textContent = q;
      (function (txt) {
        btn.addEventListener("click", function () {
          inputEl.value = txt;
          inputEl.focus();
          sendMessage();
        });
      })(q);
      row.appendChild(btn);
    }
    msgWrap.appendChild(row);
  }

  function replaceThinkingWithReply(thinkingEl, text, isError, suggested, memoryHint) {
    thinkingEl.classList.remove("ai-widget-msg--thinking");
    thinkingEl.classList.add(isError ? "ai-widget-msg--error" : "ai-widget-msg--bot");
    thinkingEl.removeAttribute("data-thinking");
    var content = thinkingEl.querySelector(".ai-widget-msg-content");
    content.className = "ai-widget-msg-content";
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
        replaceThinkingWithReply(thinkingEl, "Can't reach the server. Run the Josiah chatbot (e.g. START_CHATBOT.bat) so the widget can connect.", true, null, null);
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
    inputEl.rows = Math.min(Math.max(1, lines), 6);
  });

  appendMessage("Hey I'm Josiah, what can I do for you?", "bot");
})();
