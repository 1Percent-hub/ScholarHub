(function () {
  const MAX_DISPLAY_LEN = 24;
  const displayEl = document.getElementById('display');
  const keysEl = document.getElementById('keys');
  const modeButtons = document.querySelectorAll('.mode-button');
  const panels = document.querySelectorAll('.panel');
  const notepadInput = document.getElementById('notepad-input');
  const notepadOutput = document.getElementById('notepad-output');
  const diagramBlocksEl = document.getElementById('diagram-blocks');
  const diagramAddBtn = document.getElementById('diagram-add');
  const diagramLinksEl = document.getElementById('diagram-links');
  const tutorialStepTitleEl = document.getElementById('tutorial-step-title');
  const tutorialStepDescEl = document.getElementById('tutorial-step-desc');
  const tutorialStepActionsEl = document.getElementById('tutorial-step-actions');
  const tutorialPrevBtn = document.getElementById('tutorial-prev');
  const tutorialNextBtn = document.getElementById('tutorial-next');
  const tutorialProgressEl = document.getElementById('tutorial-progress');
  const tutorialMenuEl = document.getElementById('tutorial-menu');
  const launchScreenEl = document.getElementById('launch-screen');
  const launchEnterCalculatorBtn = document.getElementById('launch-enter-calculator');
  const launchEnterEnglishBtn = document.getElementById('launch-enter-english');
  const launchEnterScienceBtn = document.getElementById('launch-enter-science');
  const themeButtons = document.querySelectorAll('.theme-btn');
  const mainMenuBtn = document.getElementById('main-menu-btn');
  const appRootEl = document.getElementById('app-root');
  const modeToggleEl = document.getElementById('mode-toggle');
  const appHeaderTitleEl = document.getElementById('app-header-title');
  const graphSeriesListEl = document.getElementById('graph-series-list');
  const graphAddSeriesBtn = document.getElementById('graph-add-series');
  const graphCanvasEl = document.getElementById('graph-canvas');
  const lottieTapContainer = document.getElementById('lottie-tap-container');
  const lottieTransitionOverlay = document.getElementById('lottie-transition-overlay');

  let display = '0';
  let pendingOp = null;
  let pendingValue = null;
  let mode = 'calculator';
  let tutorialStepIndex = 0;
  let activeTheme = 'theme-professional';
  let appContext = 'calculator';

  const DEFAULT_GRAPH_COLORS = ['#4ce5ff', '#a9ff6a', '#b292ff', '#ff8ea1', '#ffd86a', '#7febff'];
  let graphSeries = [];
  let graphSeriesId = 0;

  (function initAuth() {
    const authScreen = document.getElementById('auth-screen');
    const launchScreenEl = document.getElementById('launch-screen');
    const headerProfile = document.getElementById('header-profile');
    const headerProfileName = document.getElementById('header-profile-name');
    const headerSignoutBtn = document.getElementById('header-signout-btn');
    const headerSigninWrap = document.getElementById('header-signin-wrap');
    const headerSigninBtn = document.getElementById('header-signin-btn');
    const authTabBtns = document.querySelectorAll('.auth-tab');
    const authFormSignin = document.getElementById('auth-form-signin');
    const authFormSignup = document.getElementById('auth-form-signup');
    const authEmail = document.getElementById('auth-email');
    const authPassword = document.getElementById('auth-password');
    const authEmailUp = document.getElementById('auth-email-up');
    const authPasswordUp = document.getElementById('auth-password-up');
    const authDisplayName = document.getElementById('auth-display-name');
    const authErrorSignin = document.getElementById('auth-error-signin');
    const authErrorSignup = document.getElementById('auth-error-signup');
    const authGuestBtn = document.getElementById('auth-guest-btn');

    function showAuthScreen() {
      if (authScreen) authScreen.classList.remove('auth-hidden');
      if (launchScreenEl) launchScreenEl.classList.add('launch-hidden');
      if (headerProfile) headerProfile.classList.remove('visible');
      if (headerSigninWrap) headerSigninWrap.classList.remove('visible');
    }

    function showLaunchScreen() {
      if (authScreen) authScreen.classList.add('auth-hidden');
      if (launchScreenEl) launchScreenEl.classList.remove('launch-hidden');
    }

    function updateProfileUI(session) {
      if (!headerProfile || !headerSignoutBtn || !headerSigninWrap) return;
      if (session && session.user) {
        headerProfile.classList.add('visible');
        headerSigninWrap.classList.remove('visible');
        const auth = window.SchoolResourceAuth;
        if (auth) {
          auth.getProfile(session.user.id).then(function (p) {
            if (headerProfileName && p) {
              headerProfileName.textContent = p.display_name || session.user.email || 'Signed in';
            } else if (headerProfileName) {
              headerProfileName.textContent = session.user.email || 'Signed in';
            }
          }).catch(function () {
            if (headerProfileName) headerProfileName.textContent = session.user.email || 'Signed in';
          });
        }
      } else {
        headerProfile.classList.remove('visible');
        if (launchScreenEl && launchScreenEl.classList.contains('launch-hidden')) {
          headerSigninWrap.classList.add('visible');
        }
      }
    }

    function onAuthReady(session) {
      if (session) {
        showLaunchScreen();
        updateProfileUI(session);
        window.dispatchEvent(new CustomEvent('school-resource:user-logged-in', { detail: { session } }));
      } else {
        showAuthScreen();
        updateProfileUI(null);
      }
    }

    (async function bootstrap() {
      const auth = window.SchoolResourceAuth;
      if (auth) {
        const { data } = await auth.getSession();
        const session = data && data.session ? data.session : null;
        if (session) {
          showLaunchScreen();
          updateProfileUI(session);
          window.dispatchEvent(new CustomEvent('school-resource:user-logged-in', { detail: { session } }));
          return;
        }
      }
      showAuthScreen();
    })();

    authTabBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        const tab = btn.getAttribute('data-auth-tab');
        authTabBtns.forEach(function (b) { b.classList.toggle('active', b === btn); });
        if (tab === 'signin') {
          authFormSignin.classList.remove('hidden');
          authFormSignup.classList.add('hidden');
          if (authErrorSignin) authErrorSignin.textContent = '';
          if (authErrorSignup) authErrorSignup.textContent = '';
        } else {
          authFormSignin.classList.add('hidden');
          authFormSignup.classList.remove('hidden');
          if (authErrorSignin) authErrorSignin.textContent = '';
          if (authErrorSignup) authErrorSignup.textContent = '';
        }
      });
    });

    if (authFormSignin) {
      authFormSignin.addEventListener('submit', async function (e) {
        e.preventDefault();
        if (!authEmail || !authPassword) return;
        if (authErrorSignin) authErrorSignin.textContent = '';
        const auth = window.SchoolResourceAuth;
        if (!auth) return;
        const { data, error } = await auth.signIn(authEmail.value.trim(), authPassword.value);
        if (error) {
          if (authErrorSignin) authErrorSignin.textContent = error.message || 'Sign in failed';
          return;
        }
        if (data && data.session) {
          showLaunchScreen();
          updateProfileUI(data.session);
          authFormSignin.reset();
          window.dispatchEvent(new CustomEvent('school-resource:user-logged-in', { detail: { session: data.session } }));
        }
      });
    }

    if (authFormSignup) {
      authFormSignup.addEventListener('submit', async function (e) {
        e.preventDefault();
        if (!authEmailUp || !authPasswordUp) return;
        if (authErrorSignup) authErrorSignup.textContent = '';
        const auth = window.SchoolResourceAuth;
        if (!auth) return;
        const displayName = authDisplayName ? authDisplayName.value.trim() : '';
        const { data, error } = await auth.signUp(authEmailUp.value.trim(), authPasswordUp.value, displayName || undefined);
        if (error) {
          if (authErrorSignup) authErrorSignup.textContent = error.message || 'Sign up failed';
          return;
        }
        if (data && data.session) {
          showLaunchScreen();
          updateProfileUI(data.session);
          authFormSignup.reset();
          if (window.SchoolResourceData && window.SchoolResourceData.copyLocalDataToAccount) {
            window.SchoolResourceData.copyLocalDataToAccount();
          }
          window.dispatchEvent(new CustomEvent('school-resource:user-logged-in', { detail: { session: data.session } }));
        } else if (data && data.user && !data.session) {
          if (authErrorSignup) authErrorSignup.textContent = 'Check your email to confirm your account.';
        }
      });
    }

    if (authGuestBtn) {
      authGuestBtn.addEventListener('click', function () {
        showLaunchScreen();
      });
    }

    if (headerSigninBtn) {
      headerSigninBtn.addEventListener('click', function () {
        showAuthScreen();
      });
    }

    if (headerSignoutBtn) {
      headerSignoutBtn.addEventListener('click', async function () {
        const auth = window.SchoolResourceAuth;
        if (auth) await auth.signOut();
        updateProfileUI(null);
        showAuthScreen();
      });
    }

    window.SchoolResourceAuthShowAuth = showAuthScreen;
    window.SchoolResourceAuthShowLaunch = showLaunchScreen;
    window.SchoolResourceAuthUpdateProfile = updateProfileUI;
  })();

  function updateDisplay(value) {
    display = String(value);
    if (display.length > MAX_DISPLAY_LEN) {
      display = display.slice(0, MAX_DISPLAY_LEN);
    }
    displayEl.textContent = display;
  }

  function tokenize(str) {
    const tokens = [];
    let i = 0;
    const ops = new Set(['+', '-', '*', '/']);
    while (i < str.length) {
      if (ops.has(str[i])) {
        tokens.push({ type: 'op', value: str[i] });
        i++;
      } else if (/\d|\./.test(str[i])) {
        let num = '';
        while (i < str.length && (/\d/.test(str[i]) || str[i] === '.')) {
          num += str[i];
          i++;
        }
        const n = parseFloat(num);
        if (Number.isNaN(n)) return null;
        let isPercent = false;
        if (str[i] === '%') {
          isPercent = true;
          i++;
        }
        tokens.push({ type: 'num', value: n, isPercent: isPercent });
      } else {
        i++;
      }
    }
    return tokens;
  }

  function evaluate(expr) {
    const tokens = tokenize(expr);
    if (!tokens || tokens.length === 0 || tokens[0].type !== 'num') return null;
    if (tokens.length === 1) {
      const only = tokens[0];
      return only.isPercent ? only.value / 100 : only.value;
    }

    let nums = tokens.filter(t => t.type === 'num').map(t => ({
      value: t.value,
      isPercent: Boolean(t.isPercent),
    }));
    let ops = tokens.filter(t => t.type === 'op').map(t => t.value);
    if (ops.length !== nums.length - 1) return null;

    for (let pass = 0; pass < 2; pass++) {
      const priority = pass === 0 ? ['*', '/'] : ['+', '-'];
      while (ops.some(o => priority.includes(o))) {
        const idx = ops.findIndex(o => priority.includes(o));
        const a = nums[idx];
        const b = nums[idx + 1];
        const op = ops[idx];
        let result;
        const aVal = a.isPercent ? a.value / 100 : a.value;
        const bVal = b.isPercent ? b.value / 100 : b.value;
        if (op === '*') result = aVal * bVal;
        else if (op === '/') {
          if (bVal === 0) return 'Error';
          result = aVal / bVal;
        } else if (op === '+') {
          const right = b.isPercent ? aVal * (b.value / 100) : bVal;
          result = aVal + right;
        } else if (op === '-') {
          const right = b.isPercent ? aVal * (b.value / 100) : bVal;
          result = aVal - right;
        }
        nums.splice(idx, 2, { value: result, isPercent: false });
        ops.splice(idx, 1);
      }
    }
    const result = nums[0].isPercent ? nums[0].value / 100 : nums[0].value;
    if (result === Infinity || result === -Infinity || Number.isNaN(result)) return 'Error';
    return Math.round(result * 1e10) / 1e10;
  }

  function handleInput(value) {
    if (value === 'C') {
      display = '0';
      pendingOp = null;
      pendingValue = null;
      updateDisplay(display);
      return;
    }

    if (display === 'Error' && value !== 'C') {
      display = '0';
      pendingOp = null;
      pendingValue = null;
    }

    if (value === '=') {
      if (pendingOp !== null && pendingValue !== null && display !== '') {
        const expr = pendingValue + pendingOp + display;
        const result = evaluate(expr);
        if (result === null) return;
        display = String(result);
        pendingOp = null;
        pendingValue = null;
      } else {
        const result = evaluate(display);
        if (result !== null) {
          display = String(result);
        }
      }
      updateDisplay(display);
      return;
    }

    if (value === '%') {
      const current = parseFloat(display);
      if (Number.isNaN(current)) return;
      let next;
      if (pendingValue !== null && pendingOp !== null) {
        const base = parseFloat(pendingValue);
        if (Number.isNaN(base)) return;
        if (pendingOp === '+' || pendingOp === '-') {
          next = (base * current) / 100;
        } else {
          next = current / 100;
        }
      } else {
        next = current / 100;
      }
      updateDisplay(Math.round(next * 1e10) / 1e10);
      return;
    }

    if (['+', '-', '*', '/'].includes(value)) {
      if (pendingOp !== null && pendingValue !== null && display !== '' && display !== '0') {
        const expr = pendingValue + pendingOp + display;
        const result = evaluate(expr);
        if (result !== null && result !== 'Error') {
          pendingValue = String(result);
          pendingOp = value;
          display = '0';
          updateDisplay(display);
          return;
        }
      }
      pendingValue = display === '0' && !display.includes('.') ? '0' : display;
      pendingOp = value;
      display = '0';
      updateDisplay(display);
      return;
    }

    if (value === '.') {
      const lastNum = display.split(/[\+\-\*\/]/).pop();
      if (lastNum && lastNum.includes('.')) return;
      if (display === '0' || /[\+\-\*\/]$/.test(display)) {
        display = display === '0' ? '0.' : display + '0.';
      } else {
        display = display + '.';
      }
      if (display.length <= MAX_DISPLAY_LEN) updateDisplay(display);
      return;
    }

    if (/\d/.test(value)) {
      if (display === '0' && value !== '0') display = value;
      else if (display !== '0') display = display + value;
      else if (value === '0') display = '0';
      if (display.length <= MAX_DISPLAY_LEN) updateDisplay(display);
    }
  }

  keysEl.addEventListener('click', function (e) {
    const btn = e.target.closest('.key');
    if (!btn) return;
    if (mode !== 'calculator' && appContext !== 'calculator') return;
    playTapLottie(e);
    const value = btn.getAttribute('data-value');
    if (value) handleInput(value);
  });

  function setMode(next) {
    if (mode === next) return;
    mode = next;
    modeButtons.forEach((btn) => {
      const btnMode = btn.getAttribute('data-mode');
      if (btnMode === mode) {
        btn.classList.add('mode-button-active');
      } else {
        btn.classList.remove('mode-button-active');
      }
    });
    panels.forEach((panel) => {
      const panelMode = panel.getAttribute('data-panel');
      if (panelMode === mode) {
        panel.classList.remove('panel-hidden');
        if (panelMode === 'diagram') {
          requestAnimationFrame(() => {
            requestAnimationFrame(drawDiagramLinks);
          });
        }
        if (panelMode === 'graph') {
          requestAnimationFrame(drawGraph);
        }
      } else {
        panel.classList.add('panel-hidden');
      }
    });
    playTransitionLottie();
  }

  modeButtons.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      playTapLottie(e);
      const next = btn.getAttribute('data-mode');
      if (next) setMode(next);
    });
  });

  document.querySelectorAll('.math-materials-link-btn').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      playTapLottie(e);
      const goto = btn.getAttribute('data-goto');
      if (goto) setMode(goto);
    });
  });

  (function initMathMaterials() {
    const mathCategoryTabs = document.querySelectorAll('.math-category-tab');
    const mathCategoryContents = document.querySelectorAll('.math-category-content');
    const mathNavBtns = document.querySelectorAll('.math-nav-btn');

    mathCategoryTabs.forEach((tab) => {
      tab.addEventListener('click', () => {
        const cat = tab.getAttribute('data-math-category');
        mathCategoryTabs.forEach((t) => t.classList.remove('active'));
        tab.classList.add('active');
        mathCategoryContents.forEach((c) => {
          c.classList.toggle('hidden', c.id !== 'math-category-' + cat);
        });
      });
    });

    mathNavBtns.forEach((btn) => {
      btn.addEventListener('click', () => {
        const tool = btn.getAttribute('data-math-tool');
        if (!tool) return;
        const category = btn.closest('.math-category-content');
        if (!category) return;
        category.querySelectorAll('.math-nav-btn').forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');
        category.querySelectorAll('.math-tool-content').forEach((card) => {
          card.classList.toggle('hidden', card.id !== 'math-tool-' + tool);
        });
        if (tool === 'diagram') {
          requestAnimationFrame(() => {
            requestAnimationFrame(drawDiagramLinks);
          });
        }
        if (tool === 'graph') {
          requestAnimationFrame(drawGraph);
        }
      });
    });
  })();

  function showMathTool(category, tool) {
    const mathCategoryTabs = document.querySelectorAll('.math-category-tab');
    const mathCategoryContents = document.querySelectorAll('.math-category-content');
    mathCategoryTabs.forEach((t) => {
      const cat = t.getAttribute('data-math-category');
      t.classList.toggle('active', cat === category);
    });
    mathCategoryContents.forEach((c) => {
      c.classList.toggle('hidden', c.id !== 'math-category-' + category);
    });
    const content = document.getElementById('math-category-' + category);
    if (content && tool) {
      content.querySelectorAll('.math-nav-btn').forEach((b) => {
        b.classList.toggle('active', b.getAttribute('data-math-tool') === tool);
      });
      content.querySelectorAll('.math-tool-content').forEach((card) => {
        card.classList.toggle('hidden', card.id !== 'math-tool-' + tool);
      });
      if (tool === 'diagram') {
        requestAnimationFrame(() => requestAnimationFrame(drawDiagramLinks));
      }
      if (tool === 'graph') {
        requestAnimationFrame(drawGraph);
      }
    }
  }

  function renderNotepad() {
    if (!notepadInput || !notepadOutput) return;
    const text = notepadInput.value || '';
    const lines = text.split(/\r?\n/);
    const rendered = lines
      .map((line) => {
        if (!line.trim()) return '';
        if (!line.includes('=')) return line;
        const [beforeEq] = line.split('=');
        const exprRaw = beforeEq.trim();
        if (!exprRaw) return line;

        const expr = exprRaw.replace(/[^0-9+\-*/.%]/g, '');
        if (!expr || !/[0-9]/.test(expr)) return line;

        const result = evaluate(expr);
        if (result === null) return line;
        if (result === 'Error') {
          return line + '  →  ' + '[Error]';
        }
        return line + '  →  ' + result;
      })
      .join('\n');

    notepadOutput.textContent = rendered;
  }

  if (notepadInput) {
    notepadInput.addEventListener('input', function () {
      renderNotepad();
      const ds = window.SchoolResourceData;
      if (ds) ds.debouncedSaveContent('notepad', { text: notepadInput.value }, 500);
    });
    (function loadNotepad() {
      const ds = window.SchoolResourceData;
      if (!ds) { renderNotepad(); return; }
      ds.getContent('notepad').then(function (o) {
        if (o && o.text != null && notepadInput) notepadInput.value = o.text;
        renderNotepad();
      }).catch(function () { renderNotepad(); });
    })();
  }

  let diagramBlockId = 0;
  let diagramBlocks = [];

  function resolveDiagramValue(str, results) {
    if (!str || typeof str !== 'string') return null;
    const t = str.trim();
    const refMatch = t.match(/^#(\d+)$/);
    if (refMatch) {
      const idx = parseInt(refMatch[1], 10) - 1;
      if (idx >= 0 && results[idx] !== undefined && results[idx] !== null) return results[idx];
      return null;
    }
    const num = parseFloat(t.replace(/[^0-9.\-%]/g, ''));
    if (Number.isNaN(num)) return null;
    return t.endsWith('%') ? num / 100 : num;
  }

  function computeDiagramBlock(block, results) {
    const left = resolveDiagramValue(block.left, results);
    const right = resolveDiagramValue(block.right, results);
    if (left === null || right === null) return null;
    const op = (block.op || '+').trim();
    if (op === '*') return left * right;
    if (op === '/') {
      if (right === 0) return 'Error';
      return left / right;
    }
    if (op === '+') return left + right;
    if (op === '-') return left - right;
    return null;
  }

  function getDiagramResults() {
    const results = [];
    for (let i = 0; i < diagramBlocks.length; i++) {
      const block = diagramBlocks[i];
      const value = computeDiagramBlock(block, results);
      if (value !== null && value !== 'Error') {
        results.push(typeof value === 'number' ? Math.round(value * 1e10) / 1e10 : value);
      } else {
        results.push(value);
      }
    }
    return results;
  }

  function renderDiagramBlocks() {
    if (!diagramBlocksEl) return;
    diagramBlocksEl.innerHTML = '';
    const results = getDiagramResults();
    diagramBlocks.forEach((block, index) => {
      const result = results[index];
      const card = document.createElement('div');
      card.className = 'diagram-block';
      card.dataset.blockId = String(block.id);

      const leftSlot = document.createElement('input');
      leftSlot.type = 'text';
      leftSlot.className = 'diagram-block-slot diagram-slot-left';
      leftSlot.setAttribute('aria-label', 'Left operand');
      leftSlot.dataset.slot = 'left';
      leftSlot.value = block.left;
      leftSlot.placeholder = '# or num';

      const opSlot = document.createElement('input');
      opSlot.type = 'text';
      opSlot.className = 'diagram-block-slot diagram-slot-op';
      opSlot.setAttribute('aria-label', 'Operator');
      opSlot.dataset.slot = 'op';
      opSlot.value = block.op;
      opSlot.placeholder = '+';

      const rightSlot = document.createElement('input');
      rightSlot.type = 'text';
      rightSlot.className = 'diagram-block-slot diagram-slot-right';
      rightSlot.setAttribute('aria-label', 'Right operand');
      rightSlot.dataset.slot = 'right';
      rightSlot.value = block.right;
      rightSlot.placeholder = '# or num';

      const equalsSpan = document.createElement('span');
      equalsSpan.className = 'diagram-block-equals';
      equalsSpan.textContent = ' = ';

      const resultEl = document.createElement('span');
      resultEl.className = 'diagram-block-result' + (result === 'Error' || result === null ? ' error' : '');
      resultEl.textContent = result === null ? '?' : (result === 'Error' ? 'Error' : String(result));

      const removeBtn = document.createElement('button');
      removeBtn.type = 'button';
      removeBtn.className = 'diagram-block-remove';
      removeBtn.textContent = 'Remove';

      const blockLabel = document.createElement('span');
      blockLabel.className = 'diagram-block-num';
      blockLabel.textContent = (index + 1) + '.';
      card.appendChild(blockLabel);
      card.appendChild(leftSlot);
      card.appendChild(opSlot);
      card.appendChild(rightSlot);
      card.appendChild(equalsSpan);
      card.appendChild(resultEl);
      card.appendChild(removeBtn);

      function syncBlock() {
        block.left = leftSlot.value;
        block.op = opSlot.value.trim() || '+';
        block.right = rightSlot.value;
        renderDiagramBlocks();
        requestAnimationFrame(drawDiagramLinks);
      }

      [leftSlot, opSlot, rightSlot].forEach((input) => {
        input.addEventListener('input', syncBlock);
        input.addEventListener('change', syncBlock);
      });

      removeBtn.addEventListener('click', () => {
        diagramBlocks = diagramBlocks.filter((b) => b.id !== block.id);
        renderDiagramBlocks();
        requestAnimationFrame(drawDiagramLinks);
      });

      diagramBlocksEl.appendChild(card);
    });
    requestAnimationFrame(drawDiagramLinks);
  }

  function drawDiagramLinks() {
    if (!diagramLinksEl || !diagramBlocksEl) return;
    const workspace = diagramLinksEl.parentElement;
    if (!workspace) return;
    const blocks = diagramBlocksEl.querySelectorAll('.diagram-block');
    const workspaceRect = workspace.getBoundingClientRect();
    const svgNs = 'http://www.w3.org/2000/svg';
    diagramLinksEl.innerHTML = '';
    diagramLinksEl.setAttribute('viewBox', `0 0 ${workspaceRect.width} ${workspaceRect.height}`);
    diagramLinksEl.setAttribute('width', workspaceRect.width);
    diagramLinksEl.setAttribute('height', workspaceRect.height);

    blocks.forEach((targetBlockEl, targetIndex) => {
      const targetBlock = diagramBlocks[targetIndex];
      if (!targetBlock) return;
      const leftSlot = targetBlockEl.querySelector('.diagram-slot-left');
      const rightSlot = targetBlockEl.querySelector('.diagram-slot-right');
      const leftVal = (targetBlock.left || '').trim();
      const rightVal = (targetBlock.right || '').trim();
      const leftRef = leftVal.match(/^#(\d+)$/);
      const rightRef = rightVal.match(/^#(\d+)$/);

      [leftRef, rightRef].forEach((ref, side) => {
        if (!ref) return;
        const srcIndex = parseInt(ref[1], 10) - 1;
        if (srcIndex < 0 || srcIndex >= blocks.length || srcIndex >= targetIndex) return;
        const srcBlock = blocks[srcIndex];
        const resultEl = srcBlock.querySelector('.diagram-block-result');
        const slotEl = side === 0 ? leftSlot : rightSlot;
        if (!resultEl || !slotEl) return;
        const from = resultEl.getBoundingClientRect();
        const to = slotEl.getBoundingClientRect();
        const x1 = from.left - workspaceRect.left + from.width / 2;
        const y1 = from.bottom - workspaceRect.top;
        const x2 = to.left - workspaceRect.left + to.width / 2;
        const y2 = to.top - workspaceRect.top;
        const midY = (y1 + y2) / 2;
        const path = document.createElementNS(svgNs, 'path');
        path.setAttribute('d', `M ${x1} ${y1} C ${x1} ${midY}, ${x2} ${midY}, ${x2} ${y2}`);
        path.setAttribute('fill', 'none');
        path.setAttribute('stroke', '#3a5a7a');
        path.setAttribute('stroke-width', '1.5');
        diagramLinksEl.appendChild(path);
      });
    });
  }

  function addDiagramBlock() {
    diagramBlocks.push({
      id: ++diagramBlockId,
      left: diagramBlocks.length === 0 ? '5' : '#1',
      op: '*',
      right: diagramBlocks.length === 0 ? '20' : '10',
    });
    renderDiagramBlocks();
  }

  if (diagramAddBtn) {
    diagramAddBtn.addEventListener('click', (e) => {
      playTapLottie(e);
      addDiagramBlock();
    });
  }

  function evaluateWithX(expr, x) {
    if (!expr || typeof expr !== 'string') return null;
    let cleaned = expr.trim().replace(/\s/g, '');
    const xStr = String(x);
    cleaned = cleaned.replace(/(\d)x/gi, '$1*' + xStr).replace(/x(\d)/gi, xStr + '*$1');
    cleaned = cleaned.replace(/x/gi, xStr);
    const safe = cleaned.replace(/[^0-9+\-*/.%]/g, '');
    if (!safe || !/[0-9]/.test(safe)) return null;
    const result = evaluate(safe);
    return result === 'Error' ? null : result;
  }

  function drawGraph() {
    if (!graphCanvasEl || !graphSeries.length) {
      if (graphCanvasEl) {
        const ctx = graphCanvasEl.getContext('2d');
        const dpr = window.devicePixelRatio || 1;
        const w = graphCanvasEl.width;
        const h = graphCanvasEl.height;
        graphCanvasEl.style.width = w + 'px';
        graphCanvasEl.style.height = h + 'px';
        graphCanvasEl.width = w * dpr;
        graphCanvasEl.height = h * dpr;
        ctx.scale(dpr, dpr);
        ctx.fillStyle = '#0a0a0a';
        ctx.fillRect(0, 0, w, h);
        ctx.fillStyle = '#555';
        ctx.font = '12px system-ui, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('Add a line above', w / 2, h / 2);
      }
      return;
    }
    const ctx = graphCanvasEl.getContext('2d');
    const dpr = window.devicePixelRatio || 1;
    const w = graphCanvasEl.width;
    const h = graphCanvasEl.height;
    const cssW = 640;
    const cssH = 320;
    graphCanvasEl.style.width = cssW + 'px';
    graphCanvasEl.style.height = cssH + 'px';
    graphCanvasEl.width = cssW * dpr;
    graphCanvasEl.height = cssH * dpr;
    ctx.scale(dpr, dpr);
    const padding = { top: 20, right: 20, bottom: 28, left: 38 };
    const plotW = cssW - padding.left - padding.right;
    const plotH = cssH - padding.top - padding.bottom;
    const xMin = -10;
    const xMax = 10;
    const xStep = (xMax - xMin) / 500;
    let yMin = -10;
    let yMax = 10;
    const allPoints = graphSeries.map((s) => {
      const pts = [];
      for (let x = xMin; x <= xMax; x += xStep) {
        const y = evaluateWithX(s.expr, x);
        if (y !== null && Number.isFinite(y)) {
          pts.push({ x, y });
          if (y < yMin) yMin = y;
          if (y > yMax) yMax = y;
        }
      }
      return { series: s, points: pts };
    });
    if (allPoints.some((p) => p.points.length > 0)) {
      const yPadding = (yMax - yMin) * 0.05 || 1;
      yMin -= yPadding;
      yMax += yPadding;
    }
    ctx.fillStyle = '#0a0a0a';
    ctx.fillRect(0, 0, cssW, cssH);
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(padding.left, padding.top);
    ctx.lineTo(padding.left, cssH - padding.bottom);
    ctx.lineTo(cssW - padding.right, cssH - padding.bottom);
    ctx.stroke();
    ctx.strokeStyle = '#2a2a2a';
    for (let i = 1; i < 5; i++) {
      const x = padding.left + (plotW * i) / 5;
      ctx.beginPath();
      ctx.moveTo(x, padding.top);
      ctx.lineTo(x, cssH - padding.bottom);
      ctx.stroke();
    }
    for (let i = 1; i < 5; i++) {
      const y = cssH - padding.bottom - (plotH * i) / 5;
      ctx.beginPath();
      ctx.moveTo(padding.left, y);
      ctx.lineTo(cssW - padding.right, y);
      ctx.stroke();
    }
    const toScreenX = (x) => padding.left + ((x - xMin) / (xMax - xMin)) * plotW;
    const toScreenY = (y) => cssH - padding.bottom - ((y - yMin) / (yMax - yMin)) * plotH;
    allPoints.forEach(({ series, points }) => {
      if (points.length < 2) return;
      ctx.strokeStyle = series.color;
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      ctx.moveTo(toScreenX(points[0].x), toScreenY(points[0].y));
      for (let i = 1; i < points.length; i++) {
        ctx.lineTo(toScreenX(points[i].x), toScreenY(points[i].y));
      }
      ctx.stroke();
    });
  }

  function renderGraphSeriesList() {
    if (!graphSeriesListEl) return;
    graphSeriesListEl.innerHTML = '';
    graphSeries.forEach((s) => {
      const row = document.createElement('div');
      row.className = 'graph-series-row';
      const exprInput = document.createElement('input');
      exprInput.type = 'text';
      exprInput.className = 'graph-series-expr';
      exprInput.setAttribute('aria-label', 'Expression in x');
      exprInput.placeholder = 'e.g. x*2 or x*x';
      exprInput.value = s.expr;
      const colorInput = document.createElement('input');
      colorInput.type = 'color';
      colorInput.className = 'graph-series-color';
      colorInput.setAttribute('aria-label', 'Line color');
      colorInput.value = s.color;
      const colorWrap = document.createElement('div');
      colorWrap.className = 'graph-series-color-wrap';
      const colorLabel = document.createElement('label');
      colorLabel.textContent = 'Color';
      colorWrap.appendChild(colorLabel);
      colorWrap.appendChild(colorInput);
      const removeBtn = document.createElement('button');
      removeBtn.type = 'button';
      removeBtn.className = 'graph-series-remove';
      removeBtn.textContent = 'Remove';
      const rowLabel = document.createElement('label');
      rowLabel.textContent = 'y =';
      row.appendChild(rowLabel);
      row.appendChild(exprInput);
      row.appendChild(colorWrap);
      row.appendChild(removeBtn);
      function sync() {
        s.expr = exprInput.value.trim();
        s.color = colorInput.value;
        drawGraph();
      }
      exprInput.addEventListener('input', sync);
      exprInput.addEventListener('change', sync);
      colorInput.addEventListener('input', sync);
      colorInput.addEventListener('change', sync);
      removeBtn.addEventListener('click', () => {
        graphSeries = graphSeries.filter((x) => x.id !== s.id);
        renderGraphSeriesList();
        drawGraph();
      });
      graphSeriesListEl.appendChild(row);
    });
  }

  function addGraphSeries() {
    graphSeries.push({
      id: ++graphSeriesId,
      expr: 'x*2',
      color: DEFAULT_GRAPH_COLORS[graphSeries.length % DEFAULT_GRAPH_COLORS.length],
    });
    renderGraphSeriesList();
    drawGraph();
  }

  if (graphAddSeriesBtn) {
    graphAddSeriesBtn.addEventListener('click', (e) => {
      playTapLottie(e);
      addGraphSeries();
    });
  }

  function runCalculatorWalkthrough() {
    display = '12';
    pendingValue = '12';
    pendingOp = '+';
    const result = evaluate('12+8');
    display = String(result === null ? '20' : result);
    pendingValue = null;
    pendingOp = null;
    updateDisplay(display);
    showMathTool('calculations', 'calculator');
  }

  function runNotepadWalkthrough() {
    if (!notepadInput) return;
    notepadInput.value = 'Trip budget: 45*3 =\nTax: 135*0.07 =\nFinal: 135+9.45 =';
    renderNotepad();
    showMathTool('calculations', 'notepad');
  }

  function runDiagramWalkthrough() {
    if (!diagramBlocksEl) return;
    diagramBlocks = [
      { id: ++diagramBlockId, left: '5', op: '*', right: '20' },
      { id: ++diagramBlockId, left: '#1', op: '+', right: '30' },
      { id: ++diagramBlockId, left: '#2', op: '-', right: '15' },
    ];
    renderDiagramBlocks();
    showMathTool('visualization', 'diagram');
  }

  function runModeTour() {
    showMathTool('calculations', 'calculator');
    setTimeout(() => showMathTool('calculations', 'notepad'), 350);
    setTimeout(() => showMathTool('visualization', 'diagram'), 700);
    setTimeout(() => showMathTool('visualization', 'graph'), 1050);
    setTimeout(() => showMathTool('learning', 'tutorial'), 1400);
  }

  const tutorialSteps = [
    {
      title: 'Welcome',
      description: 'Use this tutorial to learn Math Materials, Notepad, and Diagram modes with interactive examples.',
      actions: [
        { label: 'Run quick mode tour', onClick: runModeTour },
      ],
    },
    {
      title: 'Math Materials Basics',
      description: 'Use the keypad for quick arithmetic. Try the guided example to auto-run 12 + 8.',
      actions: [
        { label: 'Try math example', onClick: runCalculatorWalkthrough },
        { label: 'Go to Calculator', onClick: () => showMathTool('calculations', 'calculator') },
      ],
    },
    {
      title: 'Notepad Mode',
      description: 'Write text and expressions together. Lines with "=" are solved live in the results panel.',
      actions: [
        { label: 'Load Notepad example', onClick: runNotepadWalkthrough },
        { label: 'Go to Notepad', onClick: () => showMathTool('calculations', 'notepad') },
      ],
    },
    {
      title: 'Diagram Linking',
      description: 'Build a flow of calculations. Use #1, #2, etc. to reference earlier results and visualize dependencies.',
      actions: [
        { label: 'Load Diagram example', onClick: runDiagramWalkthrough },
        { label: 'Go to Diagram', onClick: () => showMathTool('visualization', 'diagram') },
      ],
    },
    {
      title: 'Graphing',
      description: 'Plot expressions in x (e.g. x*2, x*x). Change line colors per transformation to keep complex charts readable.',
      actions: [
        { label: 'Go to Graph', onClick: () => showMathTool('visualization', 'graph') },
        { label: 'Add a line', onClick: () => { showMathTool('visualization', 'graph'); addGraphSeries(); } },
      ],
    },
    {
      title: 'Pro Tips',
      description: 'Use Calculator for quick checks, Notepad for mixed notes + math, Diagram for linked totals, and Graph for visualizing functions.',
      actions: [
        { label: 'Go to Calculator', onClick: () => showMathTool('calculations', 'calculator') },
        { label: 'Go to Notepad', onClick: () => showMathTool('calculations', 'notepad') },
        { label: 'Go to Diagram', onClick: () => showMathTool('visualization', 'diagram') },
        { label: 'Go to Graph', onClick: () => showMathTool('visualization', 'graph') },
      ],
    },
  ];

  function renderTutorialMenu() {
    if (!tutorialMenuEl) return;
    tutorialMenuEl.innerHTML = '';
    tutorialSteps.forEach((step, idx) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'tutorial-menu-item' + (idx === tutorialStepIndex ? ' active' : '');
      btn.textContent = (idx + 1) + '. ' + step.title;
      btn.addEventListener('click', () => {
        tutorialStepIndex = idx;
        renderTutorialStep();
      });
      tutorialMenuEl.appendChild(btn);
    });
  }

  function renderTutorialStep() {
    const step = tutorialSteps[tutorialStepIndex];
    if (!step || !tutorialStepTitleEl || !tutorialStepDescEl || !tutorialStepActionsEl) return;
    tutorialStepTitleEl.textContent = step.title;
    tutorialStepDescEl.textContent = step.description;
    tutorialStepActionsEl.innerHTML = '';
    step.actions.forEach((action) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'tutorial-btn';
      btn.textContent = action.label;
      btn.addEventListener('click', action.onClick);
      tutorialStepActionsEl.appendChild(btn);
    });
    if (tutorialProgressEl) {
      tutorialProgressEl.textContent = 'Step ' + (tutorialStepIndex + 1) + ' of ' + tutorialSteps.length;
    }
    renderTutorialMenu();
    if (tutorialPrevBtn) tutorialPrevBtn.disabled = tutorialStepIndex === 0;
    if (tutorialNextBtn) tutorialNextBtn.disabled = tutorialStepIndex === tutorialSteps.length - 1;
  }

  if (tutorialPrevBtn) {
    tutorialPrevBtn.addEventListener('click', () => {
      if (tutorialStepIndex > 0) {
        tutorialStepIndex -= 1;
        renderTutorialStep();
      }
    });
  }

  if (tutorialNextBtn) {
    tutorialNextBtn.addEventListener('click', () => {
      if (tutorialStepIndex < tutorialSteps.length - 1) {
        tutorialStepIndex += 1;
        renderTutorialStep();
      }
    });
  }

  renderTutorialStep();

  function applyTheme(themeClass) {
    const themes = ['theme-professional', 'theme-galaxy', 'theme-cyan', 'theme-violet', 'theme-lime', 'theme-crimson'];
    const next = themes.includes(themeClass) ? themeClass : 'theme-professional';
    document.body.classList.remove(...themes);
    document.body.classList.add(next);
    activeTheme = next;
    const ds = window.SchoolResourceData;
    if (ds) {
      ds.getSettings().then(function (s) {
        return ds.saveSettings({ theme: next, soundEffects: s.soundEffects, speakOnHover: s.speakOnHover });
      }).catch(function () {});
    }
  }

  function showMainMenu() {
    if (launchScreenEl) launchScreenEl.classList.remove('launch-hidden');
    if (appRootEl) appRootEl.classList.add('app-locked');
  }

  if (themeButtons.length > 0) {
    themeButtons.forEach((btn) => {
      btn.addEventListener('click', (e) => {
        playTapLottie(e);
        const theme = btn.getAttribute('data-theme');
        if (!theme) return;
        applyTheme(theme);
        themeButtons.forEach((other) => {
          other.classList.toggle('theme-btn-active', other === btn);
        });
      });
    });
  }

  if (mainMenuBtn) {
    mainMenuBtn.addEventListener('click', (e) => {
      playTapLottie(e);
      showMainMenu();
    });
  }

  function enterCalculatorContext() {
    appContext = 'calculator';
    if (appRootEl) {
      appRootEl.classList.remove('app-context-english', 'app-context-science');
      appRootEl.classList.add('app-context-calculator');
    }
    if (appHeaderTitleEl) appHeaderTitleEl.textContent = 'Math Materials';
    mode = 'math-materials';
    panels.forEach((panel) => {
      const panelMode = panel.getAttribute('data-panel');
      if (panelMode === 'math-materials') {
        panel.classList.remove('panel-hidden');
      } else {
        panel.classList.add('panel-hidden');
      }
    });
    playTransitionLottie();
  }

  function enterEnglishContext() {
    appContext = 'english';
    if (appRootEl) {
      appRootEl.classList.remove('app-context-calculator');
      appRootEl.classList.add('app-context-english');
      appRootEl.classList.remove('app-context-science');
    }
    if (appHeaderTitleEl) appHeaderTitleEl.textContent = 'English Materials';
    mode = 'english';
    panels.forEach((panel) => {
      const panelMode = panel.getAttribute('data-panel');
      if (panelMode === 'english') {
        panel.classList.remove('panel-hidden');
      } else {
        panel.classList.add('panel-hidden');
      }
    });
    playTransitionLottie();
  }

  function enterScienceContext() {
    appContext = 'science';
    if (appRootEl) {
      appRootEl.classList.remove('app-context-calculator');
      appRootEl.classList.remove('app-context-english');
      appRootEl.classList.add('app-context-science');
    }
    if (appHeaderTitleEl) appHeaderTitleEl.textContent = 'Science Materials';
    mode = 'science';
    panels.forEach((panel) => {
      const panelMode = panel.getAttribute('data-panel');
      if (panelMode === 'science') {
        panel.classList.remove('panel-hidden');
      } else {
        panel.classList.add('panel-hidden');
      }
    });
    playTransitionLottie();
  }

  function startAppMusic() {
    const appMusic = document.getElementById('app-music');
    if (appMusic) appMusic.play().catch(function () {});
  }

  function stopAppMusic() {
    const appMusic = document.getElementById('app-music');
    if (appMusic) {
      appMusic.pause();
      appMusic.currentTime = 0;
    }
  }

  function onEnterApp() {
    const auth = window.SchoolResourceAuth;
    const updateProfile = window.SchoolResourceAuthUpdateProfile;
    if (auth && updateProfile) {
      auth.getSession().then(function (r) {
        updateProfile(r.data && r.data.session ? r.data.session : null);
      });
    }
    window.dispatchEvent(new CustomEvent('school-resource:app-entered'));
  }

  if (launchEnterCalculatorBtn) {
    launchEnterCalculatorBtn.addEventListener('click', (e) => {
      playTapLottie(e);
      if (launchScreenEl) launchScreenEl.classList.add('launch-hidden');
      if (appRootEl) appRootEl.classList.remove('app-locked');
      enterCalculatorContext();
      startAppMusic();
      onEnterApp();
    });
  }

  if (launchEnterEnglishBtn) {
    launchEnterEnglishBtn.addEventListener('click', (e) => {
      playTapLottie(e);
      if (launchScreenEl) launchScreenEl.classList.add('launch-hidden');
      if (appRootEl) appRootEl.classList.remove('app-locked');
      enterEnglishContext();
      startAppMusic();
      onEnterApp();
    });
  }

  if (launchEnterScienceBtn) {
    launchEnterScienceBtn.addEventListener('click', (e) => {
      playTapLottie(e);
      if (launchScreenEl) launchScreenEl.classList.add('launch-hidden');
      if (appRootEl) appRootEl.classList.remove('app-locked');
      enterScienceContext();
      startAppMusic();
      onEnterApp();
    });
  }

  (function initScienceTools() {
    const scienceCategoryTabs = document.querySelectorAll('.science-category-tab');
    const scienceCategoryContents = document.querySelectorAll('.science-category-content');
    const scienceNavBtns = document.querySelectorAll('.science-nav-btn');

    scienceCategoryTabs.forEach((tab) => {
      tab.addEventListener('click', () => {
        const cat = tab.getAttribute('data-science-category');
        scienceCategoryTabs.forEach((t) => t.classList.remove('active'));
        tab.classList.add('active');
        scienceCategoryContents.forEach((c) => {
          c.classList.toggle('hidden', c.id !== 'science-category-' + cat);
        });
      });
    });

    scienceNavBtns.forEach((btn) => {
      btn.addEventListener('click', () => {
        const tool = btn.getAttribute('data-science-tool');
        if (!tool) return;
        const category = btn.closest('.science-category-content');
        if (!category) return;
        category.querySelectorAll('.science-nav-btn').forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');
        category.querySelectorAll('.science-tool').forEach((t) => {
          t.classList.toggle('hidden', t.id !== 'science-' + tool);
        });
      });
    });
  })();

  (function initScienceTutorial() {
    const titleEl = document.getElementById('science-tutorial-title');
    const descEl = document.getElementById('science-tutorial-desc');
    const actionsEl = document.getElementById('science-tutorial-actions');
    const progressEl = document.getElementById('science-tutorial-progress');
    const prevBtn = document.getElementById('science-tutorial-prev');
    const nextBtn = document.getElementById('science-tutorial-next');

    function switchScienceCategory(cat, tool) {
      const catTab = document.querySelector('.science-category-tab[data-science-category="' + cat + '"]');
      if (catTab) {
        document.querySelectorAll('.science-category-tab').forEach((t) => t.classList.remove('active'));
        catTab.classList.add('active');
      }
      document.querySelectorAll('.science-category-content').forEach((c) => {
        c.classList.toggle('hidden', c.id !== 'science-category-' + cat);
      });
      if (tool) {
        const btn = document.querySelector('#science-category-' + cat + ' .science-nav-btn[data-science-tool="' + tool + '"]');
        if (btn) btn.click();
      }
    }

    const scienceTutorialSteps = [
      {
        title: 'Welcome to Science Materials',
        description: 'Use the category tabs above to switch between Simulators, Reference, Lab Tools, Study Aids, and this Learning tab. In each category, use the smaller tabs to pick a specific tool.',
        actions: [],
      },
      {
        title: 'The "What If" Lab (Simulators)',
        description: 'Try the Stoichiometry Solver for balanced equations and molar calculations, the Genetic Square Generator for Punnett squares, and the Circuit Sandbox to build simple circuits.',
        actions: [
          { label: 'Open Simulators', onClick: () => switchScienceCategory('simulators', null) },
          { label: 'Open Stoichiometry', onClick: () => switchScienceCategory('simulators', 'stoichiometry') },
        ],
      },
      {
        title: 'Interactive Data & Reference',
        description: 'Use the Dynamic Periodic Table to filter and sort elements, the Unit Converter for energy and units, and the Constants Library for quick lookup of physical constants.',
        actions: [
          { label: 'Open Reference', onClick: () => switchScienceCategory('reference', null) },
          { label: 'Open Periodic Table', onClick: () => switchScienceCategory('reference', 'periodictable') },
        ],
      },
      {
        title: 'Lab Management Tools',
        description: 'Smart Lab Timer runs multiple timers with labels; Observation Logger helps you record hypothesis, variables, and procedure; Graphing Engine plots data and exports images.',
        actions: [
          { label: 'Open Lab Tools', onClick: () => switchScienceCategory('lab', null) },
          { label: 'Open Graphing Engine', onClick: () => switchScienceCategory('lab', 'graphing') },
        ],
      },
      {
        title: 'Study Aids',
        description: 'Root Word Dictionary explains Greek and Latin roots and has a Science Decoder. Safety Quiz Mode tests your knowledge of lab safety symbols.',
        actions: [
          { label: 'Open Study Aids', onClick: () => switchScienceCategory('study', null) },
          { label: 'Open Safety Quiz', onClick: () => switchScienceCategory('study', 'safety') },
        ],
      },
      {
        title: 'You\'re all set',
        description: 'Explore each category and tool at your own pace. Come back to Learning anytime for a quick reminder of what each section offers.',
        actions: [
          { label: 'Back to Learning', onClick: () => switchScienceCategory('learning', 'learning') },
        ],
      },
    ];

    let scienceTutorialStepIndex = 0;

    function renderScienceTutorialStep() {
      const step = scienceTutorialSteps[scienceTutorialStepIndex];
      if (!step) return;
      if (titleEl) titleEl.textContent = step.title;
      if (descEl) descEl.textContent = step.description;
      if (actionsEl) {
        actionsEl.innerHTML = '';
        (step.actions || []).forEach((a) => {
          const btn = document.createElement('button');
          btn.type = 'button';
          btn.className = 'english-tutorial-btn';
          btn.textContent = a.label;
          btn.addEventListener('click', a.onClick);
          actionsEl.appendChild(btn);
        });
      }
      if (progressEl) progressEl.textContent = (scienceTutorialStepIndex + 1) + ' / ' + scienceTutorialSteps.length;
      if (prevBtn) prevBtn.disabled = scienceTutorialStepIndex === 0;
      if (nextBtn) nextBtn.disabled = scienceTutorialStepIndex === scienceTutorialSteps.length - 1;
    }

    if (prevBtn) prevBtn.addEventListener('click', () => {
      if (scienceTutorialStepIndex > 0) {
        scienceTutorialStepIndex--;
        renderScienceTutorialStep();
      }
    });
    if (nextBtn) nextBtn.addEventListener('click', () => {
      if (scienceTutorialStepIndex < scienceTutorialSteps.length - 1) {
        scienceTutorialStepIndex++;
        renderScienceTutorialStep();
      }
    });

    renderScienceTutorialStep();
  })();

  (function initSimulators() {
    const MOLAR_MASS = { H: 1, C: 12, N: 14, O: 16, S: 32, P: 31, Cl: 35.5, F: 19, Br: 80, I: 127, Na: 23, K: 39, Ca: 40, Mg: 24, Fe: 56, Cu: 64, Zn: 65, Al: 27, Si: 28 };
    function parseFormula(f) {
      f = f.trim();
      let mass = 0;
      const regex = /([A-Z][a-z]?)(\d*)/g;
      let m;
      while ((m = regex.exec(f)) !== null) {
        const el = m[1];
        const n = m[2] ? parseInt(m[2], 10) : 1;
        mass += (MOLAR_MASS[el] || 0) * n;
      }
      return mass;
    }
    function parseEquation(str) {
      str = str.replace(/→|=>|=/g, '=').trim();
      const [left, right] = str.split('=').map(s => s.trim());
      const parseSide = (s) => s.split('+').map(x => {
        x = x.trim();
        const match = x.match(/^(\d*)\s*(.+)$/);
        const coef = match && match[1] ? parseInt(match[1], 10) : 1;
        const formula = (match && match[2]) || x;
        return { coef, formula: formula.trim(), mass: parseFormula(formula) };
      });
      return { reactants: parseSide(left), products: parseSide(right) };
    }
    const stoichSolve = document.getElementById('stoich-solve');
    const stoichEquation = document.getElementById('stoich-equation');
    const stoichGiven = document.getElementById('stoich-given');
    const stoichOutput = document.getElementById('stoich-output');
    if (stoichSolve && stoichEquation && stoichGiven && stoichOutput) {
      stoichSolve.addEventListener('click', () => {
        const eqStr = stoichEquation.value.trim();
        const givenStr = stoichGiven.value.trim();
        if (!eqStr || !givenStr) {
          stoichOutput.innerHTML = '<p class="stoich-err">Enter equation and given amount.</p>';
          return;
        }
        const givenMatch = givenStr.match(/^([\d.]+)\s*(g|mol)?\s*(.+)$/i);
        if (!givenMatch) {
          stoichOutput.innerHTML = '<p class="stoich-err">Format: amount unit formula (e.g., 4 g H2)</p>';
          return;
        }
        const amount = parseFloat(givenMatch[1]);
        const unit = (givenMatch[2] || 'g').toLowerCase();
        const targetFormula = givenMatch[3].trim();
        let eq;
        try {
          eq = parseEquation(eqStr);
        } catch (e) {
          stoichOutput.innerHTML = '<p class="stoich-err">Could not parse equation.</p>';
          return;
        }
        const all = [...eq.reactants, ...eq.products];
        const target = all.find(x => x.formula.replace(/\s/g, '') === targetFormula.replace(/\s/g, ''));
        if (!target) {
          stoichOutput.innerHTML = '<p class="stoich-err">Formula not found in equation.</p>';
          return;
        }
        let moles = unit === 'mol' ? amount : amount / target.mass;
        let html = '<div class="stoich-table"><p><strong>Molar masses & amounts:</strong></p><table><tr><th>Substance</th><th>Molar mass (g/mol)</th><th>Amount</th></tr>';
        const ratio = moles / target.coef;
        all.forEach(x => {
          const m = ratio * x.coef * x.mass;
          const n = ratio * x.coef;
          html += `<tr><td>${x.formula}</td><td>${x.mass.toFixed(1)}</td><td>${m.toFixed(2)} g (${n.toFixed(3)} mol)</td></tr>`;
        });
        html += '</table></div>';
        stoichOutput.innerHTML = html;
      });
    }

    const geneticBuild = document.getElementById('genetic-build');
    const geneticP1 = document.getElementById('genetic-p1');
    const geneticP2 = document.getElementById('genetic-p2');
    const punnettWrap = document.getElementById('punnett-wrap');
    const geneticResults = document.getElementById('genetic-results');
    function validateGenotype(s) {
      s = s.trim().toUpperCase();
      if (s.length !== 2) return null;
      const a = s[0], b = s[1];
      if (a === b) return [a, b];
      if (a < b) return [a, b];
      return [b, a];
    }
    function gametes(geno) {
      return [geno[0], geno[1]];
    }
    if (geneticBuild && geneticP1 && geneticP2 && punnettWrap && geneticResults) {
      geneticBuild.addEventListener('click', () => {
        const p1 = validateGenotype(geneticP1.value);
        const p2 = validateGenotype(geneticP2.value);
        if (!p1 || !p2) {
          punnettWrap.innerHTML = '';
          geneticResults.innerHTML = '<p class="genetic-err">Enter 2 letters per parent (e.g., Bb, AA, bb).</p>';
          return;
        }
        const g1 = gametes(p1);
        const g2 = gametes(p2);
        const square = [];
        const counts = {};
        for (const a of g1) {
          for (const b of g2) {
            const geno = (a + b).split('').sort().join('');
            square.push(geno);
            counts[geno] = (counts[geno] || 0) + 1;
          }
        }
        const total = 4;
        let html = '<table class="punnett-table"><tr><td></td><td>' + g2[0] + '</td><td>' + g2[1] + '</td></tr>';
        html += '<tr><td>' + g1[0] + '</td><td>' + square[0] + '</td><td>' + square[1] + '</td></tr>';
        html += '<tr><td>' + g1[1] + '</td><td>' + square[2] + '</td><td>' + square[3] + '</td></tr></table>';
        punnettWrap.innerHTML = html;
        const dominant = Object.entries(counts).filter(([g]) => /[A-Z]/.test(g)).reduce((sum, [, v]) => sum + v, 0);
        const recessive = total - dominant;
        let res = '<p><strong>Genotype:</strong> ';
        res += Object.entries(counts).map(([k, v]) => k + ': ' + ((v / total) * 100) + '%').join(', ');
        res += '</p><p><strong>Phenotype:</strong> Dominant: ' + ((dominant / total) * 100) + '%, Recessive: ' + ((recessive / total) * 100) + '%</p>';
        geneticResults.innerHTML = res;
      });
    }

    const CIRCUIT_SIZE = 6;
    const circuitGrid = document.getElementById('circuit-grid');
    const circuitSimulate = document.getElementById('circuit-simulate');
    const circuitResult = document.getElementById('circuit-result');
    const paletteBtns = document.querySelectorAll('.circuit-palette-btn');
    let selectedType = null;
    let circuitCells = [];
    function initCircuitGrid() {
      if (!circuitGrid) return;
      circuitGrid.innerHTML = '';
      circuitCells = [];
      for (let r = 0; r < CIRCUIT_SIZE; r++) {
        const row = [];
        for (let c = 0; c < CIRCUIT_SIZE; c++) {
          const cell = document.createElement('div');
          cell.className = 'circuit-cell';
          cell.dataset.r = r;
          cell.dataset.c = c;
          cell.dataset.type = '';
          circuitGrid.appendChild(cell);
          row.push(cell);
        }
        circuitCells.push(row);
      }
    }
    if (circuitGrid) {
      initCircuitGrid();
      paletteBtns.forEach(btn => {
        btn.addEventListener('click', () => {
          selectedType = btn.getAttribute('data-circuit-type');
          if (selectedType === 'erase') selectedType = 'erase';
          paletteBtns.forEach(b => b.classList.toggle('active', b === btn));
        });
      });
      circuitGrid.addEventListener('click', (e) => {
        const cell = e.target.closest('.circuit-cell');
        if (!cell || !selectedType) return;
        if (selectedType === 'erase') {
          cell.dataset.type = '';
          cell.textContent = '';
          cell.className = 'circuit-cell';
        } else {
          const symbols = { battery: '🔋', resistor: 'Ω', bulb: '💡', wire: '─' };
          cell.dataset.type = selectedType;
          cell.textContent = symbols[selectedType] || '';
          cell.className = 'circuit-cell circuit-' + selectedType;
        }
      });
    }
    function getCellType(r, c) {
      if (r < 0 || r >= CIRCUIT_SIZE || c < 0 || c >= CIRCUIT_SIZE) return '';
      return circuitCells[r] && circuitCells[r][c] ? circuitCells[r][c].dataset.type : '';
    }
    function hasPathFromBatteryToBulb(batteryPos, bulbPos) {
      const visited = new Set();
      const stack = [batteryPos];
      const key = (r, c) => r + ',' + c;
      while (stack.length) {
        const { r, c } = stack.pop();
        if (r === bulbPos.r && c === bulbPos.c) return true;
        if (visited.has(key(r, c))) continue;
        visited.add(key(r, c));
        const type = getCellType(r, c);
        if (!type || type === 'erase') continue;
        [[r-1,c],[r+1,c],[r,c-1],[r,c+1]].forEach(([nr, nc]) => {
          if (nr < 0 || nr >= CIRCUIT_SIZE || nc < 0 || nc >= CIRCUIT_SIZE) return;
          const ntype = getCellType(nr, nc);
          if (ntype && ntype !== 'erase' && !visited.has(key(nr, nc))) stack.push({ r: nr, c: nc });
        });
      }
      return false;
    }
    if (circuitSimulate && circuitResult && circuitGrid) {
      circuitSimulate.addEventListener('click', () => {
        let batteryPos = null;
        let bulbPos = null;
        for (let r = 0; r < CIRCUIT_SIZE; r++) {
          for (let c = 0; c < CIRCUIT_SIZE; c++) {
            const type = getCellType(r, c);
            if (type === 'battery') batteryPos = { r, c };
            if (type === 'bulb') bulbPos = { r, c };
          }
        }
        if (!batteryPos) {
          circuitResult.textContent = 'Place a battery on the grid.';
          return;
        }
        if (!bulbPos) {
          circuitResult.textContent = 'Place a bulb on the grid.';
          return;
        }
        const connected = hasPathFromBatteryToBulb(batteryPos, bulbPos);
        if (connected) {
          circuitResult.innerHTML = '\uD83D\uDCA1 <strong>Circuit closed!</strong> The bulb lights up. Current flows from battery through the circuit.';
        } else {
          circuitResult.innerHTML = 'The bulb does not light. Connect battery to bulb with wires (adjacent cells form the path).';
        }
      });
    }
  })();

  (function initReferenceTools() {
    const PERIODIC_DATA = [
      { n:1,s:'H',name:'Hydrogen',x:1,y:1,melt:14,boil:20.3,en:2.2,ar:53 },
      { n:2,s:'He',name:'Helium',x:18,y:1,melt:0.95,boil:4.22,en:null,ar:31 },
      { n:3,s:'Li',name:'Lithium',x:1,y:2,melt:453.7,boil:1603,en:0.98,ar:167 },
      { n:4,s:'Be',name:'Beryllium',x:2,y:2,melt:1560,boil:2742,en:1.57,ar:112 },
      { n:5,s:'B',name:'Boron',x:13,y:2,melt:2349,boil:4200,en:2.04,ar:87 },
      { n:6,s:'C',name:'Carbon',x:14,y:2,melt:3823,boil:4300,en:2.55,ar:67 },
      { n:7,s:'N',name:'Nitrogen',x:15,y:2,melt:63.2,boil:77.4,en:3.04,ar:56 },
      { n:8,s:'O',name:'Oxygen',x:16,y:2,melt:54.4,boil:90.2,en:3.44,ar:48 },
      { n:9,s:'F',name:'Fluorine',x:17,y:2,melt:53.5,boil:85,en:3.98,ar:42 },
      { n:10,s:'Ne',name:'Neon',x:18,y:2,melt:24.6,boil:27.1,en:null,ar:38 },
      { n:11,s:'Na',name:'Sodium',x:1,y:3,melt:371,boil:1156,en:0.93,ar:190 },
      { n:12,s:'Mg',name:'Magnesium',x:2,y:3,melt:923,boil:1363,en:1.31,ar:145 },
      { n:13,s:'Al',name:'Aluminium',x:13,y:3,melt:933,boil:2743,en:1.61,ar:118 },
      { n:14,s:'Si',name:'Silicon',x:14,y:3,melt:1687,boil:3538,en:1.9,ar:111 },
      { n:15,s:'P',name:'Phosphorus',x:15,y:3,melt:317,boil:554,en:2.19,ar:98 },
      { n:16,s:'S',name:'Sulfur',x:16,y:3,melt:388,boil:718,en:2.58,ar:88 },
      { n:17,s:'Cl',name:'Chlorine',x:17,y:3,melt:171.6,boil:239.1,en:3.16,ar:79 },
      { n:18,s:'Ar',name:'Argon',x:18,y:3,melt:83.8,boil:87.3,en:null,ar:71 },
      { n:19,s:'K',name:'Potassium',x:1,y:4,melt:336.5,boil:1032,en:0.82,ar:243 },
      { n:20,s:'Ca',name:'Calcium',x:2,y:4,melt:1115,boil:1757,en:1,ar:194 },
      { n:21,s:'Sc',name:'Scandium',x:3,y:4,melt:1814,boil:3109,en:1.36,ar:184 },
      { n:22,s:'Ti',name:'Titanium',x:4,y:4,melt:1941,boil:3560,en:1.54,ar:176 },
      { n:23,s:'V',name:'Vanadium',x:5,y:4,melt:2183,boil:3680,en:1.63,ar:171 },
      { n:24,s:'Cr',name:'Chromium',x:6,y:4,melt:2180,boil:2944,en:1.66,ar:166 },
      { n:25,s:'Mn',name:'Manganese',x:7,y:4,melt:1519,boil:2334,en:1.55,ar:161 },
      { n:26,s:'Fe',name:'Iron',x:8,y:4,melt:1811,boil:3134,en:1.83,ar:156 },
      { n:27,s:'Co',name:'Cobalt',x:9,y:4,melt:1768,boil:3200,en:1.88,ar:152 },
      { n:28,s:'Ni',name:'Nickel',x:10,y:4,melt:1728,boil:3186,en:1.91,ar:149 },
      { n:29,s:'Cu',name:'Copper',x:11,y:4,melt:1357.8,boil:2835,en:1.9,ar:145 },
      { n:30,s:'Zn',name:'Zinc',x:12,y:4,melt:692.7,boil:1180,en:1.65,ar:142 },
      { n:31,s:'Ga',name:'Gallium',x:13,y:4,melt:302.9,boil:2673,en:1.81,ar:136 },
      { n:32,s:'Ge',name:'Germanium',x:14,y:4,melt:1211,boil:3106,en:2.01,ar:125 },
      { n:33,s:'As',name:'Arsenic',x:15,y:4,melt:1090,boil:887,en:2.18,ar:114 },
      { n:34,s:'Se',name:'Selenium',x:16,y:4,melt:494,boil:958,en:2.55,ar:103 },
      { n:35,s:'Br',name:'Bromine',x:17,y:4,melt:265.8,boil:332,en:2.96,ar:94 },
      { n:36,s:'Kr',name:'Krypton',x:18,y:4,melt:115.8,boil:119.9,en:3,ar:88 },
      { n:37,s:'Rb',name:'Rubidium',x:1,y:5,melt:312.5,boil:961,en:0.82,ar:265 },
      { n:38,s:'Sr',name:'Strontium',x:2,y:5,melt:1050,boil:1655,en:0.95,ar:219 },
      { n:39,s:'Y',name:'Yttrium',x:3,y:5,melt:1799,boil:3609,en:1.22,ar:212 },
      { n:40,s:'Zr',name:'Zirconium',x:4,y:5,melt:2128,boil:4682,en:1.33,ar:206 },
      { n:41,s:'Nb',name:'Niobium',x:5,y:5,melt:2750,boil:5017,en:1.6,ar:198 },
      { n:42,s:'Mo',name:'Molybdenum',x:6,y:5,melt:2896,boil:4912,en:2.16,ar:190 },
      { n:43,s:'Tc',name:'Technetium',x:7,y:5,melt:2430,boil:4538,en:1.9,ar:183 },
      { n:44,s:'Ru',name:'Ruthenium',x:8,y:5,melt:2607,boil:4423,en:2.2,ar:178 },
      { n:45,s:'Rh',name:'Rhodium',x:9,y:5,melt:2237,boil:3968,en:2.28,ar:173 },
      { n:46,s:'Pd',name:'Palladium',x:10,y:5,melt:1828,boil:3236,en:2.2,ar:169 },
      { n:47,s:'Ag',name:'Silver',x:11,y:5,melt:1234.9,boil:2435,en:1.93,ar:165 },
      { n:48,s:'Cd',name:'Cadmium',x:12,y:5,melt:594.2,boil:1040,en:1.69,ar:161 },
      { n:49,s:'In',name:'Indium',x:13,y:5,melt:429.7,boil:2345,en:1.78,ar:156 },
      { n:50,s:'Sn',name:'Tin',x:14,y:5,melt:505.1,boil:2875,en:1.96,ar:145 },
      { n:51,s:'Sb',name:'Antimony',x:15,y:5,melt:903.8,boil:1860,en:2.05,ar:133 },
      { n:52,s:'Te',name:'Tellurium',x:16,y:5,melt:722.7,boil:1261,en:2.1,ar:123 },
      { n:53,s:'I',name:'Iodine',x:17,y:5,melt:386.9,boil:457.5,en:2.66,ar:115 },
      { n:54,s:'Xe',name:'Xenon',x:18,y:5,melt:161.4,boil:165.1,en:2.6,ar:108 },
      { n:55,s:'Cs',name:'Cesium',x:1,y:6,melt:301.6,boil:944,en:0.79,ar:298 },
      { n:56,s:'Ba',name:'Barium',x:2,y:6,melt:1000,boil:2118,en:0.89,ar:253 },
      { n:57,s:'La',name:'Lanthanum',x:3,y:6,melt:1193,boil:3737,en:1.1,ar:195 },
      { n:72,s:'Hf',name:'Hafnium',x:4,y:6,melt:2506,boil:4876,en:1.3,ar:208 },
      { n:73,s:'Ta',name:'Tantalum',x:5,y:6,melt:3290,boil:5731,en:1.5,ar:200 },
      { n:74,s:'W',name:'Tungsten',x:6,y:6,melt:3695,boil:6203,en:2.36,ar:193 },
      { n:75,s:'Re',name:'Rhenium',x:7,y:6,melt:3459,boil:5869,en:1.9,ar:188 },
      { n:76,s:'Os',name:'Osmium',x:8,y:6,melt:3306,boil:5285,en:2.2,ar:185 },
      { n:77,s:'Ir',name:'Iridium',x:9,y:6,melt:2719,boil:4701,en:2.2,ar:180 },
      { n:78,s:'Pt',name:'Platinum',x:10,y:6,melt:2041.4,boil:4098,en:2.28,ar:177 },
      { n:79,s:'Au',name:'Gold',x:11,y:6,melt:1337.3,boil:3129,en:2.54,ar:174 },
      { n:80,s:'Hg',name:'Mercury',x:12,y:6,melt:234.3,boil:629.9,en:2,ar:171 },
      { n:81,s:'Tl',name:'Thallium',x:13,y:6,melt:577,boil:1746,en:1.62,ar:156 },
      { n:82,s:'Pb',name:'Lead',x:14,y:6,melt:600.6,boil:2022,en:2.33,ar:154 },
      { n:83,s:'Bi',name:'Bismuth',x:15,y:6,melt:544.4,boil:1837,en:2.02,ar:143 },
      { n:84,s:'Po',name:'Polonium',x:16,y:6,melt:527,boil:1235,en:2,ar:135 },
      { n:85,s:'At',name:'Astatine',x:17,y:6,melt:575,boil:610,en:2.2,ar:127 },
      { n:86,s:'Rn',name:'Radon',x:18,y:6,melt:202,boil:211.5,en:null,ar:120 }
    ];
    function getStateAtTemp(el, tempK) {
      if (el.melt == null || el.boil == null) return el.n <= 86 ? 'solid' : null;
      if (tempK < el.melt) return 'solid';
      if (tempK < el.boil) return 'liquid';
      return 'gas';
    }
    const periodicWrap = document.getElementById('periodic-table-wrap');
    const periodicDetail = document.getElementById('periodic-detail');
    const periodicTemp = document.getElementById('periodic-temp');
    const periodicStateFilter = document.getElementById('periodic-state-filter');
    const periodicSort = document.getElementById('periodic-sort');
    function renderPeriodicTable() {
      if (!periodicWrap) return;
      const tempK = parseFloat(periodicTemp?.value) || 298;
      const stateFilter = periodicStateFilter?.value || '';
      const sortBy = periodicSort?.value || 'default';
      let elements = PERIODIC_DATA.map(el => ({
        ...el,
        state: getStateAtTemp(el, tempK)
      }));
      if (stateFilter) elements = elements.filter(el => el.state === stateFilter);
      if (sortBy === 'electronegativity') {
        elements = [...elements].sort((a, b) => (b.en ?? -1) - (a.en ?? -1));
      } else if (sortBy === 'atomic-radius') {
        elements = [...elements].sort((a, b) => (b.ar ?? 0) - (a.ar ?? 0));
      } else if (sortBy === 'number') {
        elements = [...elements].sort((a, b) => a.n - b.n);
      }
      if (sortBy === 'default') {
        periodicWrap.innerHTML = '<div class="periodic-grid">' + PERIODIC_DATA.map(el => {
          const state = getStateAtTemp(el, tempK);
          const show = !stateFilter || state === stateFilter;
          return '<div class="periodic-cell' + (show ? '' : ' periodic-cell-hidden') + ' periodic-state-' + (state || '') + '" style="grid-column:' + el.x + ';grid-row:' + el.y + '" data-n="' + el.n + '" data-state="' + (state || '') + '" title="' + el.name + '">' +
            '<span class="periodic-num">' + el.n + '</span><span class="periodic-sym">' + el.s + '</span>' +
            (el.en != null ? '<span class="periodic-en">' + el.en + '</span>' : '') + '</div>';
        }).join('') + '</div>';
      } else {
        periodicWrap.innerHTML = '<div class="periodic-list">' + elements.map(el =>
          '<div class="periodic-list-item" data-n="' + el.n + '"><span class="periodic-sym">' + el.s + '</span> ' + el.name +
          ' — #' + el.n + (el.en != null ? ', EN: ' + el.en : '') + (el.ar ? ', radius: ' + el.ar + ' pm' : '') + ', ' + (el.state || '—') + '</div>'
        ).join('') + '</div>';
      }
      periodicWrap.querySelectorAll('.periodic-cell, .periodic-list-item').forEach(cell => {
        cell.addEventListener('click', () => {
          const n = parseInt(cell.dataset.n, 10);
          const el = PERIODIC_DATA.find(e => e.n === n);
          if (!el) return;
          const state = getStateAtTemp(el, tempK);
          periodicDetail.innerHTML = '<div class="periodic-detail-card"><strong>' + el.name + ' (' + el.s + ')</strong> — #' + el.n +
            '<br>State at ' + tempK + ' K: ' + (state || '—') +
            (el.melt != null ? '<br>M.P.: ' + el.melt + ' K' : '') +
            (el.boil != null ? ', B.P.: ' + el.boil + ' K' : '') +
            (el.en != null ? '<br>Electronegativity: ' + el.en : '') +
            (el.ar ? '<br>Atomic radius: ' + el.ar + ' pm' : '') + '</div>';
        });
      });
    }
    if (periodicWrap) {
      [periodicTemp, periodicStateFilter, periodicSort].forEach(el => {
        if (el) el.addEventListener('input', renderPeriodicTable);
        if (el) el.addEventListener('change', renderPeriodicTable);
      });
      renderPeriodicTable();
    }

    const CONVERTER_UNITS = {
      energy: [
        { id: 'J', name: 'Joules (J)', toBase: 1 },
        { id: 'cal', name: 'Calories (cal)', toBase: 4.184 },
        { id: 'kcal', name: 'Kilocalories (kcal)', toBase: 4184 },
        { id: 'eV', name: 'Electron-volts (eV)', toBase: 1.602176634e-19 },
        { id: 'kWh', name: 'Kilowatt-hours (kWh)', toBase: 3.6e6 },
        { id: 'Btu', name: 'British thermal units (Btu)', toBase: 1055.06 }
      ],
      distance: [
        { id: 'm', name: 'Meters (m)', toBase: 1 },
        { id: 'ly', name: 'Light years (ly)', toBase: 9.46073e15 },
        { id: 'pc', name: 'Parsecs (pc)', toBase: 3.08568e16 },
        { id: 'km', name: 'Kilometers (km)', toBase: 1000 },
        { id: 'AU', name: 'Astronomical units (AU)', toBase: 1.496e11 },
        { id: 'nm', name: 'Nanometers (nm)', toBase: 1e-9 }
      ],
      temperature: [
        { id: 'K', name: 'Kelvin (K)', toBase: 1, offset: 0 },
        { id: 'C', name: 'Celsius (°C)', toBase: 1, offset: 273.15 },
        { id: 'F', name: 'Fahrenheit (°F)', toBase: 5/9, offset: 459.67 }
      ],
      pressure: [
        { id: 'Pa', name: 'Pascals (Pa)', toBase: 1 },
        { id: 'atm', name: 'Atmospheres (atm)', toBase: 101325 },
        { id: 'bar', name: 'Bar', toBase: 100000 },
        { id: 'mmHg', name: 'mmHg (torr)', toBase: 133.322 },
        { id: 'psi', name: 'psi', toBase: 6894.76 }
      ],
      other: [
        { id: 'mol', name: 'Moles (mol)', toBase: 1 },
        { id: 'particles', name: 'Particles (×N_A)', toBase: 6.02214076e23 },
        { id: 'Hz', name: 'Hertz (Hz)', toBase: 1 },
        { id: 's', name: 'Seconds (s)', toBase: 1 },
        { id: 'min', name: 'Minutes', toBase: 60 },
        { id: 'h', name: 'Hours', toBase: 3600 }
      ]
    };
    const converterValue = document.getElementById('converter-value');
    const converterFrom = document.getElementById('converter-from');
    const converterTo = document.getElementById('converter-to');
    const converterResult = document.getElementById('converter-result');
    const converterCatBtns = document.querySelectorAll('.converter-cat-btn');
    let currentCat = 'energy';
    function toBase(val, unit) {
      if (currentCat === 'temperature') {
        return (val + (unit.offset || 0)) * (unit.toBase || 1);
      }
      return val * (unit.toBase || 1);
    }
    function fromBase(base, unit) {
      if (currentCat === 'temperature') {
        return base / (unit.toBase || 1) - (unit.offset || 0);
      }
      return base / (unit.toBase || 1);
    }
    function updateConverterUnits() {
      const units = CONVERTER_UNITS[currentCat] || [];
      if (converterFrom && converterTo) {
        converterFrom.innerHTML = units.map(u => '<option value="' + u.id + '">' + u.name + '</option>').join('');
        converterTo.innerHTML = units.map(u => '<option value="' + u.id + '">' + u.name + '</option>').join('');
        if (units.length > 1) {
          converterTo.value = units[1].id;
        }
      }
      doConvert();
    }
    function doConvert() {
      const val = parseFloat(converterValue?.value);
      if (Number.isNaN(val) || !converterFrom || !converterResult) return;
      const units = CONVERTER_UNITS[currentCat] || [];
      const fromU = units.find(u => u.id === converterFrom.value);
      const toU = units.find(u => u.id === converterTo.value);
      if (!fromU || !toU) return;
      const base = toBase(val, fromU);
      const result = fromBase(base, toU);
      converterResult.textContent = String(Math.round(result * 1e10) / 1e10);
    }
    converterCatBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        currentCat = btn.getAttribute('data-cat') || 'energy';
        converterCatBtns.forEach(b => b.classList.toggle('active', b === btn));
        updateConverterUnits();
      });
    });
    if (converterValue) converterValue.addEventListener('input', doConvert);
    if (converterFrom) converterFrom.addEventListener('change', doConvert);
    if (converterTo) converterTo.addEventListener('change', doConvert);
    updateConverterUnits();

    const CONSTANTS = [
      { name: 'Speed of light', symbol: 'c', value: '2.998×10⁸', unit: 'm/s' },
      { name: 'Planck constant', symbol: 'h', value: '6.626×10⁻³⁴', unit: 'J⋅s' },
      { name: 'Reduced Planck constant', symbol: 'ℏ', value: '1.055×10⁻³⁴', unit: 'J⋅s' },
      { name: 'Gravitational constant', symbol: 'G', value: '6.674×10⁻¹¹', unit: 'm³/(kg⋅s²)' },
      { name: 'Elementary charge', symbol: 'e', value: '1.602×10⁻¹⁹', unit: 'C' },
      { name: 'Boltzmann constant', symbol: 'k_B', value: '1.381×10⁻²³', unit: 'J/K' },
      { name: 'Avogadro constant', symbol: 'N_A', value: '6.022×10²³', unit: 'mol⁻¹' },
      { name: 'Gas constant', symbol: 'R', value: '8.314', unit: 'J/(mol⋅K)' },
      { name: 'Stefan–Boltzmann constant', symbol: 'σ', value: '5.670×10⁻⁸', unit: 'W/(m²⋅K⁴)' },
      { name: 'Fine structure constant', symbol: 'α', value: '1/137', unit: '≈0.00730' },
      { name: 'Vacuum permittivity', symbol: 'ε₀', value: '8.854×10⁻¹²', unit: 'F/m' },
      { name: 'Vacuum permeability', symbol: 'μ₀', value: '4π×10⁻⁷', unit: 'H/m' },
      { name: 'Electron mass', symbol: 'm_e', value: '9.109×10⁻³¹', unit: 'kg' },
      { name: 'Proton mass', symbol: 'm_p', value: '1.673×10⁻²⁷', unit: 'kg' },
      { name: 'Neutron mass', symbol: 'm_n', value: '1.675×10⁻²⁷', unit: 'kg' },
      { name: 'Faraday constant', symbol: 'F', value: '96485', unit: 'C/mol' },
      { name: 'Standard gravity', symbol: 'g', value: '9.807', unit: 'm/s²' }
    ];
    const constantsSearch = document.getElementById('constants-search');
    const constantsList = document.getElementById('constants-list');
    function renderConstants(filter) {
      if (!constantsList) return;
      const q = (filter || '').toLowerCase().trim();
      const list = q ? CONSTANTS.filter(c =>
        c.name.toLowerCase().includes(q) || c.symbol.toLowerCase().includes(q)
      ) : CONSTANTS;
      constantsList.innerHTML = list.map(c =>
        '<div class="constant-item"><span class="constant-symbol">' + c.symbol + '</span> ' + c.name +
        ' = <strong>' + c.value + '</strong> ' + c.unit + '</div>'
      ).join('');
    }
    if (constantsSearch) constantsSearch.addEventListener('input', () => renderConstants(constantsSearch.value));
    renderConstants();
  })();

  (function initLabTools() {
    const timerSlots = document.querySelectorAll('.lab-timer-slot');
    const timerIntervals = {};
    const timerRemaining = {};
    function formatTime(sec) {
      const m = Math.floor(sec / 60);
      const s = Math.floor(sec % 60);
      return m + ':' + (s < 10 ? '0' : '') + s;
    }
    function tick(id) {
      if (timerRemaining[id] == null) return;
      timerRemaining[id]--;
      const slot = document.querySelector('.lab-timer-slot[data-timer-id="' + id + '"]');
      if (slot) {
        const display = slot.querySelector('.lab-timer-display');
        if (display) display.textContent = formatTime(Math.max(0, timerRemaining[id]));
      }
      if (timerRemaining[id] <= 0) {
        clearInterval(timerIntervals[id]);
        delete timerIntervals[id];
        const slot = document.querySelector('.lab-timer-slot[data-timer-id="' + id + '"]');
        if (slot) {
          slot.querySelector('.lab-timer-start')?.classList.remove('hidden');
          slot.querySelector('.lab-timer-pause')?.classList.add('hidden');
        }
      }
    }
    timerSlots.forEach(slot => {
      const id = parseInt(slot.dataset.timerId, 10);
      const minInput = slot.querySelector('.lab-timer-min');
      const secInput = slot.querySelector('.lab-timer-sec');
      const display = slot.querySelector('.lab-timer-display');
      const startBtn = slot.querySelector('.lab-timer-start');
      const pauseBtn = slot.querySelector('.lab-timer-pause');
      const resetBtn = slot.querySelector('.lab-timer-reset');
      function updateDisplayFromInputs() {
        const m = parseInt(minInput?.value, 10) || 0;
        const s = parseInt(secInput?.value, 10) || 0;
        if (display) display.textContent = formatTime(m * 60 + s);
      }
      minInput?.addEventListener('input', updateDisplayFromInputs);
      secInput?.addEventListener('input', updateDisplayFromInputs);
      startBtn?.addEventListener('click', () => {
        if (timerIntervals[id]) return;
        let total = timerRemaining[id] != null ? timerRemaining[id] : (parseInt(minInput?.value, 10) || 0) * 60 + (parseInt(secInput?.value, 10) || 0);
        if (total <= 0) total = (parseInt(minInput?.value, 10) || 0) * 60 + (parseInt(secInput?.value, 10) || 0);
        if (total <= 0) return;
        timerRemaining[id] = total;
        if (display) display.textContent = formatTime(total);
        startBtn.classList.add('hidden');
        pauseBtn?.classList.remove('hidden');
        timerIntervals[id] = setInterval(() => tick(id), 1000);
      });
      pauseBtn?.addEventListener('click', () => {
        if (!timerIntervals[id]) return;
        clearInterval(timerIntervals[id]);
        delete timerIntervals[id];
        startBtn?.classList.remove('hidden');
        pauseBtn?.classList.add('hidden');
      });
      resetBtn?.addEventListener('click', () => {
        if (timerIntervals[id]) {
          clearInterval(timerIntervals[id]);
          delete timerIntervals[id];
        }
        delete timerRemaining[id];
        const m = parseInt(minInput?.value, 10) || 0;
        const s = parseInt(secInput?.value, 10) || 0;
        if (display) display.textContent = formatTime(m * 60 + s);
        startBtn?.classList.remove('hidden');
        pauseBtn?.classList.add('hidden');
      });
    });

    const loggerHypothesis = document.getElementById('logger-hypothesis');
    const loggerVariable = document.getElementById('logger-variable');
    const loggerProcedure = document.getElementById('logger-procedure');
    const loggerConclusion = document.getElementById('logger-conclusion');
    const loggerSave = document.getElementById('logger-save');
    const loggerClear = document.getElementById('logger-clear');
    async function loadLogger() {
      const ds = window.SchoolResourceData;
      if (!ds) return;
      try {
        const o = await ds.getContent('lab_logger');
        if (o && typeof o === 'object') {
          if (loggerHypothesis) loggerHypothesis.value = o.hypothesis || '';
          if (loggerVariable) loggerVariable.value = o.variable || '';
          if (loggerProcedure) loggerProcedure.value = o.procedure || '';
          if (loggerConclusion) loggerConclusion.value = o.conclusion || '';
        }
      } catch (e) {}
    }
    function saveLogger() {
      const o = {
        hypothesis: loggerHypothesis?.value || '',
        variable: loggerVariable?.value || '',
        procedure: loggerProcedure?.value || '',
        conclusion: loggerConclusion?.value || ''
      };
      const ds = window.SchoolResourceData;
      if (ds) ds.saveContent('lab_logger', o).catch(function () {});
    }
    if (loggerSave) loggerSave.addEventListener('click', () => { saveLogger(); });
    if (loggerClear) loggerClear.addEventListener('click', () => {
      if (loggerHypothesis) loggerHypothesis.value = '';
      if (loggerVariable) loggerVariable.value = '';
      if (loggerProcedure) loggerProcedure.value = '';
      if (loggerConclusion) loggerConclusion.value = '';
      saveLogger();
    });
    loadLogger();

    const labGraphData = document.getElementById('lab-graph-data');
    const labGraphXlabel = document.getElementById('lab-graph-xlabel');
    const labGraphYlabel = document.getElementById('lab-graph-ylabel');
    const labGraphType = document.getElementById('lab-graph-type');
    const labGraphDraw = document.getElementById('lab-graph-draw');
    const labGraphExport = document.getElementById('lab-graph-export');
    const labGraphCanvas = document.getElementById('lab-graph-canvas');
    function parseLabData(text) {
      const rows = text.trim().split(/\r?\n/).filter(Boolean);
      const points = [];
      for (let i = 0; i < rows.length; i++) {
        const parts = rows[i].split(/[\t,]/).map(s => s.trim());
        const x = parseFloat(parts[0]);
        const y = parseFloat(parts[1]);
        if (Number.isFinite(x) && Number.isFinite(y)) points.push({ x, y });
      }
      return points;
    }
    function drawLabGraph() {
      if (!labGraphCanvas) return;
      const points = parseLabData(labGraphData?.value || '');
      const type = labGraphType?.value || 'line';
      const xLabel = labGraphXlabel?.value?.trim() || 'X';
      const yLabel = labGraphYlabel?.value?.trim() || 'Y';
      const dpr = window.devicePixelRatio || 1;
      const cssW = 640;
      const cssH = 320;
      labGraphCanvas.style.width = cssW + 'px';
      labGraphCanvas.style.height = cssH + 'px';
      labGraphCanvas.width = cssW * dpr;
      labGraphCanvas.height = cssH * dpr;
      const ctx = labGraphCanvas.getContext('2d');
      ctx.scale(dpr, dpr);
      ctx.fillStyle = '#0a0a0a';
      ctx.fillRect(0, 0, cssW, cssH);
      if (points.length === 0) {
        ctx.fillStyle = '#666';
        ctx.font = '14px system-ui, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('Enter data above and click Draw graph', cssW / 2, cssH / 2);
        return;
      }
      const padding = { top: 24, right: 24, bottom: 36, left: 44 };
      const plotW = cssW - padding.left - padding.right;
      const plotH = cssH - padding.top - padding.bottom;
      let xMin = points[0].x, xMax = points[0].x, yMin = points[0].y, yMax = points[0].y;
      points.forEach(p => {
        if (p.x < xMin) xMin = p.x;
        if (p.x > xMax) xMax = p.x;
        if (p.y < yMin) yMin = p.y;
        if (p.y > yMax) yMax = p.y;
      });
      const xRange = xMax - xMin || 1;
      const yRange = yMax - yMin || 1;
      const xPad = xRange * 0.05;
      const yPad = yRange * 0.05;
      xMin -= xPad;
      xMax += xPad;
      yMin -= yPad;
      yMax += yPad;
      const toX = (x) => padding.left + ((x - xMin) / (xMax - xMin)) * plotW;
      const toY = (y) => cssH - padding.bottom - ((y - yMin) / (yMax - yMin)) * plotH;
      ctx.strokeStyle = '#333';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(padding.left, padding.top);
      ctx.lineTo(padding.left, cssH - padding.bottom);
      ctx.lineTo(cssW - padding.right, cssH - padding.bottom);
      ctx.stroke();
      ctx.fillStyle = '#888';
      ctx.font = '11px system-ui, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(xLabel, padding.left + plotW / 2, cssH - 10);
      ctx.save();
      ctx.translate(18, padding.top + plotH / 2);
      ctx.rotate(-Math.PI / 2);
      ctx.fillText(yLabel, 0, 0);
      ctx.restore();
      ctx.strokeStyle = '#4ce5ff';
      ctx.fillStyle = 'rgba(76, 229, 255, 0.3)';
      if (type === 'line' && points.length >= 2) {
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(toX(points[0].x), toY(points[0].y));
        for (let i = 1; i < points.length; i++) {
          ctx.lineTo(toX(points[i].x), toY(points[i].y));
        }
        ctx.stroke();
      } else if (type === 'bar' && points.length >= 1) {
        const barW = Math.max(4, plotW / points.length * 0.6);
        const baseline = toY(yMin);
        points.forEach((p) => {
          const left = toX(p.x) - barW / 2;
          const top = toY(p.y);
          const h = baseline - top;
          ctx.fillRect(left, top, barW, h);
          ctx.strokeRect(left, top, barW, h);
        });
      }
    }
    if (labGraphDraw) labGraphDraw.addEventListener('click', drawLabGraph);
    if (labGraphExport) labGraphExport.addEventListener('click', () => {
      drawLabGraph();
      if (!labGraphCanvas) return;
      try {
        const link = document.createElement('a');
        link.download = 'lab-graph.png';
        link.href = labGraphCanvas.toDataURL('image/png');
        link.click();
      } catch (e) {}
    });
  })();

  (function initStudyAids() {
    const ROOT_WORDS = [
      { root: 'bio-', meaning: 'life', example: 'biology = study of life' },
      { root: '-ology', meaning: 'study of', example: 'biology, geology' },
      { root: 'therm-', meaning: 'heat', example: 'thermometer, thermal' },
      { root: 'hydro-', meaning: 'water', example: 'hydroelectric, hydrate' },
      { root: 'photo-', meaning: 'light', example: 'photosynthesis, photon' },
      { root: '-synthesis', meaning: 'putting together', example: 'photosynthesis' },
      { root: 'geo-', meaning: 'earth', example: 'geology, geography' },
      { root: '-graphy', meaning: 'writing / description', example: 'geography' },
      { root: 'chem-', meaning: 'chemical', example: 'chemistry' },
      { root: 'astr-', meaning: 'star', example: 'astronomy, astronaut' },
      { root: '-nomy', meaning: 'law / system', example: 'astronomy' },
      { root: 'micro-', meaning: 'small', example: 'microscope, microbe' },
      { root: 'macro-', meaning: 'large', example: 'macromolecule' },
      { root: 'scope', meaning: 'see / look', example: 'microscope, telescope' },
      { root: 'tele-', meaning: 'far', example: 'telescope, telephone' },
      { root: 'chron-', meaning: 'time', example: 'chronology, synchronize' },
      { root: 'cardio-', meaning: 'heart', example: 'cardiovascular' },
      { root: 'neuro-', meaning: 'nerve', example: 'neuron, neurology' },
      { root: 'hemo-', meaning: 'blood', example: 'hemoglobin' },
      { root: 'derm-', meaning: 'skin', example: 'dermatology' },
      { root: 'oste-', meaning: 'bone', example: 'osteoporosis' },
      { root: 'eco-', meaning: 'house / environment', example: 'ecology, ecosystem' },
      { root: 'cyto-', meaning: 'cell', example: 'cytology, cytoplasm' },
      { root: '-pod', meaning: 'foot', example: 'arthropod, cephalopod' },
      { root: 'arthro-', meaning: 'joint', example: 'arthropod' },
      { root: 'cephal-', meaning: 'head', example: 'cephalopod' },
      { root: 'phil-', meaning: 'love', example: 'philosophy' },
      { root: '-phobia', meaning: 'fear of', example: 'hydrophobia' },
      { root: 'a- / an-', meaning: 'not, without', example: 'asexual, anaerobic' },
      { root: 'hyper-', meaning: 'over, above', example: 'hyperactive' },
      { root: 'hypo-', meaning: 'under, below', example: 'hypothesis, hypodermic' },
      { root: 'endo-', meaning: 'inside', example: 'endothermic' },
      { root: 'exo-', meaning: 'outside', example: 'exoskeleton' },
      { root: 'iso-', meaning: 'same, equal', example: 'isotope' },
      { root: 'poly-', meaning: 'many', example: 'polymer, polygon' },
      { root: 'mono-', meaning: 'one', example: 'monomer, monopoly' },
      { root: 'di-', meaning: 'two', example: 'dioxide, dioxide' },
      { root: 'tri-', meaning: 'three', example: 'triangle, tricycle' },
      { root: '-meter', meaning: 'measure', example: 'thermometer, kilometer' },
      { root: '-sphere', meaning: 'ball, layer', example: 'atmosphere, biosphere' }
    ];
    const rootDecoderInput = document.getElementById('root-decoder-input');
    const rootDecoderResult = document.getElementById('root-decoder-result');
    const rootSearch = document.getElementById('root-search');
    const rootList = document.getElementById('root-list');
    function decodeWord(word) {
      if (!word || !word.trim()) return [];
      const w = word.trim().toLowerCase();
      const found = [];
      ROOT_WORDS.forEach(r => {
        const raw = r.root.toLowerCase().replace(/\s/g, '');
        const normalized = raw.replace(/-/g, '');
        if (normalized.length < 2) return;
        if (w.indexOf(normalized) !== -1) found.push(r);
      });
      return found;
    }
    function renderRootList(filter) {
      if (!rootList) return;
      const q = (filter || '').toLowerCase().trim();
      const list = q ? ROOT_WORDS.filter(r =>
        r.root.toLowerCase().includes(q) || r.meaning.toLowerCase().includes(q) || (r.example && r.example.toLowerCase().includes(q))
      ) : ROOT_WORDS;
      rootList.innerHTML = list.map(r =>
        '<div class="root-item"><span class="root-root">' + r.root + '</span> → ' + r.meaning +
        (r.example ? ' <span class="root-example">(' + r.example + ')</span>' : '') + '</div>'
      ).join('');
    }
    if (rootDecoderInput) {
      rootDecoderInput.addEventListener('input', () => {
        const word = rootDecoderInput.value.trim();
        if (!rootDecoderResult) return;
        if (!word) {
          rootDecoderResult.innerHTML = '';
          return;
        }
        const matches = decodeWord(word);
        if (matches.length === 0) {
          rootDecoderResult.innerHTML = '<p class="root-decoder-empty">No roots found for this word. Try searching in the list below.</p>';
          return;
        }
        rootDecoderResult.innerHTML = '<p class="root-decoder-title">Possible roots in "' + word + '":</p>' +
          matches.map(r => '<div class="root-item"><span class="root-root">' + r.root + '</span> → ' + r.meaning +
            (r.example ? ' <span class="root-example">' + r.example + '</span>' : '') + '</div>').join('');
      });
    }
    if (rootSearch) rootSearch.addEventListener('input', () => renderRootList(rootSearch.value));
    renderRootList();

    const SAFETY_SYMBOLS = [
      { symbol: 'Flammable', meaning: 'Catches fire easily. Keep away from flames and sparks.' },
      { symbol: 'Corrosive', meaning: 'Can burn skin or damage materials. Wear gloves; avoid contact.' },
      { symbol: 'Toxic / Poison', meaning: 'Harmful if swallowed or inhaled. Do not taste or breathe fumes.' },
      { symbol: 'Irritant', meaning: 'Can cause skin or eye irritation. Handle with care; wash after use.' },
      { symbol: 'Health Hazard', meaning: 'May cause serious or long-term health effects (e.g. carcinogen).' },
      { symbol: 'Oxidizer', meaning: 'Releases oxygen; can make fires worse. Keep away from flammables.' },
      { symbol: 'Explosive', meaning: 'Can explode if shocked or heated. Handle with extreme care.' },
      { symbol: 'Compressed Gas', meaning: 'Gas under pressure. Can explode if heated or damaged.' },
      { symbol: 'Environment', meaning: 'Harmful to the environment. Dispose of properly.' },
      { symbol: 'Biohazard', meaning: 'Infectious or biological hazard. Use proper containment.' },
      { symbol: 'Radioactive', meaning: 'Emits radiation. Follow safety procedures and shielding.' },
      { symbol: 'Eye Protection', meaning: 'Wear safety goggles or face shield in this area.' },
      { symbol: 'Sharp Object', meaning: 'Risk of cuts. Handle with care; dispose in sharps container.' },
      { symbol: 'Electrical Hazard', meaning: 'Risk of electric shock. Do not use near water.' },
      { symbol: 'Hot Surface', meaning: 'Surface is hot. Do not touch without protection.' }
    ];
    const safetyQuizStart = document.getElementById('safety-quiz-start');
    const safetyQuizGame = document.getElementById('safety-quiz-game');
    const safetyQuizDone = document.getElementById('safety-quiz-done');
    const safetyQuizBegin = document.getElementById('safety-quiz-begin');
    const safetyQuizScoreEl = document.getElementById('safety-quiz-score');
    const safetyQuizTotalEl = document.getElementById('safety-quiz-total');
    const safetyQuizPrompt = document.getElementById('safety-quiz-prompt');
    const safetyQuizChoices = document.getElementById('safety-quiz-choices');
    const safetyQuizFinal = document.getElementById('safety-quiz-final');
    const safetyQuizAgain = document.getElementById('safety-quiz-again');
    let safetyQuizIndex = 0;
    let safetyQuizCorrect = 0;
    let safetyQuizOrder = [];
    function shuffle(arr) {
      const a = [...arr];
      for (let i = a.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [a[i], a[j]] = [a[j], a[i]];
      }
      return a;
    }
    function startSafetyQuiz() {
      safetyQuizOrder = shuffle(SAFETY_SYMBOLS.map((_, i) => i));
      safetyQuizIndex = 0;
      safetyQuizCorrect = 0;
      if (safetyQuizStart) safetyQuizStart.classList.add('hidden');
      if (safetyQuizDone) safetyQuizDone.classList.add('hidden');
      if (safetyQuizGame) safetyQuizGame.classList.remove('hidden');
      showSafetyQuestion();
    }
    function showSafetyQuestion() {
      if (safetyQuizIndex >= safetyQuizOrder.length) {
        endSafetyQuiz();
        return;
      }
      const idx = safetyQuizOrder[safetyQuizIndex];
      const item = SAFETY_SYMBOLS[idx];
      if (safetyQuizTotalEl) safetyQuizTotalEl.textContent = safetyQuizOrder.length;
      if (safetyQuizScoreEl) safetyQuizScoreEl.textContent = safetyQuizCorrect;
      if (safetyQuizPrompt) safetyQuizPrompt.textContent = 'What does "' + item.symbol + '" mean?';
      const wrong = SAFETY_SYMBOLS.filter((_, i) => i !== idx).map(s => s.meaning);
      const choices = shuffle([item.meaning, ...shuffle(wrong).slice(0, 3)]);
      if (safetyQuizChoices) {
        safetyQuizChoices.innerHTML = choices.map(meaning =>
          '<button type="button" class="safety-choice-btn" data-correct="' + (meaning === item.meaning) + '">' + meaning + '</button>'
        ).join('');
        safetyQuizChoices.querySelectorAll('.safety-choice-btn').forEach(btn => {
          btn.addEventListener('click', () => {
            const correct = btn.dataset.correct === 'true';
            if (correct) safetyQuizCorrect++;
            safetyQuizIndex++;
            showSafetyQuestion();
          });
        });
      }
    }
    function endSafetyQuiz() {
      if (safetyQuizGame) safetyQuizGame.classList.add('hidden');
      if (safetyQuizDone) safetyQuizDone.classList.remove('hidden');
      if (safetyQuizFinal) {
        const pct = Math.round((safetyQuizCorrect / safetyQuizOrder.length) * 100);
        safetyQuizFinal.textContent = 'You got ' + safetyQuizCorrect + ' out of ' + safetyQuizOrder.length + ' (' + pct + '%). ' +
          (pct >= 80 ? 'Great job — you\'re ready for the lab!' : 'Review the symbols and try again.');
      }
    }
    if (safetyQuizBegin) safetyQuizBegin.addEventListener('click', startSafetyQuiz);
    if (safetyQuizAgain) safetyQuizAgain.addEventListener('click', () => {
      if (safetyQuizStart) safetyQuizStart.classList.remove('hidden');
      if (safetyQuizDone) safetyQuizDone.classList.add('hidden');
      startSafetyQuiz();
    });
  })();

  (function initCredits() {
    const creditsOverlay = document.getElementById('credits-overlay');
    const creditsAudio = document.getElementById('credits-audio');
    const appMusic = document.getElementById('app-music');
    const appCreditsBtn = document.getElementById('app-credits-btn');
    const launchCreditsBtn = document.getElementById('launch-credits-btn');
    const creditsClose = document.getElementById('credits-close');
    const creditsCrawl = document.getElementById('credits-crawl');

    let creditsMusicTimeout = null;

    function openCredits() {
      if (!creditsOverlay) return;
      if (creditsMusicTimeout) {
        clearTimeout(creditsMusicTimeout);
        creditsMusicTimeout = null;
      }
      if (appMusic) {
        appMusic.pause();
      }
      creditsOverlay.classList.add('credits-open');
      creditsOverlay.setAttribute('aria-hidden', 'false');
      if (creditsAudio) {
        creditsAudio.currentTime = 0;
        creditsMusicTimeout = setTimeout(function () {
          creditsMusicTimeout = null;
          creditsAudio.play().catch(function () {});
        }, 1500);
      }
      if (creditsCrawl) {
        creditsCrawl.style.animation = 'none';
        creditsCrawl.offsetHeight;
        creditsCrawl.style.animation = '';
      }
    }

    function closeCredits() {
      if (!creditsOverlay) return;
      if (creditsMusicTimeout) {
        clearTimeout(creditsMusicTimeout);
        creditsMusicTimeout = null;
      }
      creditsOverlay.classList.remove('credits-open');
      creditsOverlay.setAttribute('aria-hidden', 'true');
      if (creditsAudio) {
        creditsAudio.pause();
        creditsAudio.currentTime = 0;
      }
      if (appMusic && launchScreenEl && launchScreenEl.classList.contains('launch-hidden')) {
        appMusic.play().catch(function () {});
      }
    }

    if (appCreditsBtn) appCreditsBtn.addEventListener('click', openCredits);
    if (launchCreditsBtn) launchCreditsBtn.addEventListener('click', openCredits);
    if (creditsClose) creditsClose.addEventListener('click', closeCredits);
    if (creditsOverlay) {
      creditsOverlay.addEventListener('click', (e) => {
        if (e.target === creditsOverlay) closeCredits();
      });
    }
  })();

  (function initSettingsAndSound() {
    let soundEffectsEnabled = true;
    let speakOnHoverEnabled = false;
    let audioContext = null;
    let speakHoverTimeout = null;
    let lastSpokenEl = null;

    async function loadSettings() {
      const ds = window.SchoolResourceData;
      if (!ds) return;
      const s = await ds.getSettings();
      soundEffectsEnabled = s.soundEffects !== false;
      speakOnHoverEnabled = s.speakOnHover === true;
    }

    async function saveSettings() {
      const ds = window.SchoolResourceData;
      if (!ds) return;
      await ds.saveSettings({
        theme: document.body.className.match(/theme-\w+/) ? document.body.className.match(/theme-\w+/)[0] : 'theme-professional',
        soundEffects: soundEffectsEnabled,
        speakOnHover: speakOnHoverEnabled,
      });
    }

    function playClickSound() {
      if (!soundEffectsEnabled) return;
      try {
        if (!audioContext) audioContext = new (window.AudioContext || window.webkitAudioContext)();
        if (audioContext.state === 'suspended') audioContext.resume();
        const osc = audioContext.createOscillator();
        const gain = audioContext.createGain();
        osc.connect(gain);
        gain.connect(audioContext.destination);
        osc.frequency.value = 520;
        osc.type = 'sine';
        gain.gain.setValueAtTime(0.12, audioContext.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + 0.06);
        osc.start(audioContext.currentTime);
        osc.stop(audioContext.currentTime + 0.06);
      } catch (_) {}
    }

    document.addEventListener('click', function (e) {
      if (e.target.closest('button') || e.target.closest('[role="button"]')) {
        playClickSound();
      }
    }, true);

    loadSettings().then(function () {
      const settingSoundEl = document.getElementById('setting-sound-effects');
      const settingSpeakEl = document.getElementById('setting-speak-on-hover');
      if (settingSoundEl) settingSoundEl.checked = soundEffectsEnabled;
      if (settingSpeakEl) settingSpeakEl.checked = speakOnHoverEnabled;
      const ds = window.SchoolResourceData;
      if (ds) ds.getSettings().then(function (s) {
        if (s.theme && typeof applyTheme === 'function') applyTheme(s.theme);
      }).catch(function () {});
    });

    const settingsOverlay = document.getElementById('settings-overlay');
    const settingsPanel = document.getElementById('settings-panel');
    const settingsBtn = document.getElementById('settings-btn');
    const settingsCloseBtn = document.getElementById('settings-close-btn');
    const settingSoundEl = document.getElementById('setting-sound-effects');
    const settingSpeakEl = document.getElementById('setting-speak-on-hover');

    if (settingSoundEl) {
      settingSoundEl.addEventListener('change', function () {
        soundEffectsEnabled = settingSoundEl.checked;
        saveSettings();
      });
    }
    if (settingSpeakEl) {
      settingSpeakEl.addEventListener('change', function () {
        speakOnHoverEnabled = settingSpeakEl.checked;
        saveSettings();
      });
    }

    function openSettings() {
      if (settingsOverlay) {
        settingsOverlay.classList.add('settings-open');
        settingsOverlay.setAttribute('aria-hidden', 'false');
      }
    }
    function closeSettings() {
      if (settingsOverlay) {
        settingsOverlay.classList.remove('settings-open');
        settingsOverlay.setAttribute('aria-hidden', 'true');
      }
    }

    if (settingsBtn) settingsBtn.addEventListener('click', openSettings);
    if (settingsCloseBtn) settingsCloseBtn.addEventListener('click', closeSettings);
    if (settingsOverlay) {
      settingsOverlay.addEventListener('click', function (e) {
        if (e.target === settingsOverlay) closeSettings();
      });
    }
    if (settingsPanel) {
      settingsPanel.addEventListener('click', function (e) { e.stopPropagation(); });
    }

    function getButtonLabel(el) {
      const target = el.closest('button') || (el.getAttribute('role') === 'button' ? el : null) || (el.tagName === 'LABEL' ? el : null);
      if (!target) return '';
      const aria = target.getAttribute('aria-label');
      if (aria && aria.trim()) return aria.trim();
      const text = (target.textContent || '').trim().replace(/\s+/g, ' ');
      if (text && text.length < 120) return text;
      return '';
    }

    document.addEventListener('mouseover', function (e) {
      if (!speakOnHoverEnabled) return;
      const el = e.target.closest('button') || e.target.closest('[role="button"]') || (e.target.tagName === 'LABEL' ? e.target : null);
      if (!el) return;
      const label = getButtonLabel(el);
      if (!label) return;
      if (speakHoverTimeout) clearTimeout(speakHoverTimeout);
      speakHoverTimeout = setTimeout(function () {
        speakHoverTimeout = null;
        if (!window.speechSynthesis) return;
        window.speechSynthesis.cancel();
        const u = new SpeechSynthesisUtterance(label);
        u.rate = 0.95;
        u.volume = 1;
        window.speechSynthesis.speak(u);
        lastSpokenEl = el;
      }, 400);
    }, true);

    document.addEventListener('mouseout', function (e) {
      if (!speakOnHoverEnabled) return;
      const el = e.target.closest('button') || e.target.closest('[role="button"]') || (e.target.tagName === 'LABEL' ? e.target : null);
      if (el) {
        if (speakHoverTimeout) {
          clearTimeout(speakHoverTimeout);
          speakHoverTimeout = null;
        }
        if (window.speechSynthesis) window.speechSynthesis.cancel();
      }
    }, true);
  })();

  (function initEnglishTools() {
    const englishPanel = document.querySelector('.panel-english');
    const categoryTabs = englishPanel ? englishPanel.querySelectorAll('.english-category-tab') : [];
    const categoryContents = englishPanel ? englishPanel.querySelectorAll('.english-category-content') : [];
    const englishNavBtns = document.querySelectorAll('#english-category-reading .english-nav-btn');
    const readingTools = document.querySelectorAll('#english-category-reading .english-tool');
    const ereaderPaste = document.getElementById('ereader-paste');
    const ereaderFile = document.getElementById('ereader-file');
    const ereaderLoad = document.getElementById('ereader-load');
    const ereaderHighlight = document.getElementById('ereader-highlight');
    const ereaderNote = document.getElementById('ereader-note');
    const ereaderView = document.getElementById('ereader-view');
    const ereaderNotes = document.getElementById('ereader-notes');
    const trackerForm = document.getElementById('tracker-form');
    const trackerList = document.getElementById('tracker-list');
    const trackerFilter = document.getElementById('tracker-filter');
    const summaryInput = document.getElementById('summary-input');
    const summaryGenerate = document.getElementById('summary-generate');
    const summaryConnections = document.getElementById('summary-connections');
    const summaryOutput = document.getElementById('summary-output');
    const connectionsOutput = document.getElementById('connections-output');
    const accessibilityDyslexic = document.getElementById('accessibility-dyslexic');
    const accessibilityGuide = document.getElementById('accessibility-guide');

    let literaryDevices = [];
    let stickyNotes = [];

    categoryTabs.forEach((tab) => {
      tab.addEventListener('click', () => {
        const cat = tab.getAttribute('data-english-category');
        categoryTabs.forEach((t) => t.classList.remove('active'));
        tab.classList.add('active');
        categoryContents.forEach((c) => {
          c.classList.toggle('hidden', c.id !== 'english-category-' + cat);
        });
      });
    });

    englishNavBtns.forEach((btn) => {
      btn.addEventListener('click', () => {
        const tool = btn.getAttribute('data-english-tool');
        if (!tool) return;
        englishNavBtns.forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');
        readingTools.forEach((t) => {
          t.classList.toggle('hidden', t.id !== 'english-' + tool);
        });
      });
    });

    function loadEreaderText() {
      const text = ereaderPaste ? ereaderPaste.value.trim() : '';
      if (ereaderView) {
        ereaderView.textContent = text || '(Paste or upload text, then click Load Text)';
        ereaderView.contentEditable = text ? 'true' : 'false';
      }
    }

    if (ereaderFile) {
      ereaderFile.addEventListener('change', (e) => {
        const f = e.target.files[0];
        if (!f) return;
        const r = new FileReader();
        r.onload = () => {
          if (ereaderPaste) ereaderPaste.value = r.result;
          loadEreaderText();
        };
        r.readAsText(f);
      });
    }

    if (ereaderLoad) ereaderLoad.addEventListener('click', loadEreaderText);

    if (ereaderHighlight && ereaderView) {
      ereaderHighlight.addEventListener('click', () => {
        const sel = window.getSelection();
        if (!sel.rangeCount) return;
        const range = sel.getRangeAt(0);
        if (!ereaderView.contains(range.commonAncestorContainer)) return;
        const mark = document.createElement('mark');
        try {
          range.surroundContents(mark);
        } catch (_) {
          const frag = range.extractContents();
          mark.appendChild(frag);
          range.insertNode(mark);
        }
        sel.removeAllRanges();
      });
    }

    if (ereaderNote && ereaderView) {
      ereaderNote.addEventListener('click', () => {
        const noteText = prompt('Sticky note:');
        if (!noteText) return;
        stickyNotes.push({ text: noteText });
        const el = document.createElement('div');
        el.className = 'ereader-sticky-note';
        el.textContent = noteText;
        if (ereaderNotes) ereaderNotes.appendChild(el);
      });
    }

    if (trackerForm) {
      trackerForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const device = document.getElementById('tracker-device').value;
        const quote = document.getElementById('tracker-quote').value.trim();
        const source = document.getElementById('tracker-source').value.trim();
        const notes = document.getElementById('tracker-notes').value.trim();
        if (!quote) return;
        literaryDevices.push({ device, quote, source, notes });
        document.getElementById('tracker-quote').value = '';
        document.getElementById('tracker-source').value = '';
        document.getElementById('tracker-notes').value = '';
        renderTrackerList();
      });
    }

    if (trackerFilter) {
      trackerFilter.addEventListener('change', renderTrackerList);
    }

    function renderTrackerList() {
      if (!trackerList) return;
      const filter = trackerFilter ? trackerFilter.value : '';
      const filtered = filter ? literaryDevices.filter((d) => d.device === filter) : literaryDevices;
      trackerList.innerHTML = filtered
        .map(
          (d) =>
            `<li class="tracker-item">
              <div class="tracker-item-type">${d.device}</div>
              <div class="tracker-item-quote">"${d.quote}"</div>
              ${d.source ? `<div class="tracker-item-source">${d.source}</div>` : ''}
              ${d.notes ? `<div class="tracker-item-notes">${d.notes}</div>` : ''}
            </li>`
        )
        .join('');
    }

    function extractiveSummary(text, maxSentences = 5) {
      const sentences = text.match(/[^.!?]+[.!?]+/g) || [text];
      if (sentences.length <= maxSentences) return text.trim();
      const step = Math.floor(sentences.length / maxSentences);
      const picked = [];
      for (let i = 0; i < maxSentences && i * step < sentences.length; i++) {
        picked.push(sentences[i * step].trim());
      }
      return picked.join(' ');
    }

    function findThemes(text) {
      const words = text.toLowerCase().replace(/[^\w\s]/g, ' ').split(/\s+/).filter((w) => w.length > 4);
      const stop = new Set(['which', 'their', 'would', 'could', 'about', 'there', 'these', 'those', 'where', 'while', 'after', 'before', 'other', 'having', 'being']);
      const freq = {};
      words.forEach((w) => {
        if (!stop.has(w)) freq[w] = (freq[w] || 0) + 1;
      });
      return Object.entries(freq)
        .filter(([, c]) => c >= 2)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 15)
        .map(([w, c]) => `${w} (${c})`)
        .join(', ');
    }

    if (summaryGenerate && summaryInput && summaryOutput) {
      summaryGenerate.addEventListener('click', () => {
        const text = summaryInput.value.trim();
        summaryOutput.textContent = text ? extractiveSummary(text) : 'Paste text first, then click Generate Summary.';
      });
    }

    if (summaryConnections && summaryInput && connectionsOutput) {
      summaryConnections.addEventListener('click', () => {
        const text = summaryInput.value.trim();
        connectionsOutput.textContent = text ? (findThemes(text) || 'No recurring themes found (need words 5+ chars, 2+ occurrences).') : 'Paste text first, then click Find Themes.';
      });
    }

    if (accessibilityDyslexic) {
      accessibilityDyslexic.addEventListener('change', () => {
        document.body.classList.toggle('font-dyslexic', accessibilityDyslexic.checked);
      });
    }

    if (accessibilityGuide) {
      accessibilityGuide.addEventListener('change', () => {
        document.body.classList.toggle('reading-guide-active', accessibilityGuide.checked);
      });
    }

    (function initWritingTools() {
      const writingNavBtns = document.querySelectorAll('.english-nav-writing .english-nav-btn');
      const writingToolIds = ['english-plot', 'english-style', 'english-audio', 'english-citation'];
      writingNavBtns.forEach((btn) => {
        btn.addEventListener('click', () => {
          const tool = btn.getAttribute('data-english-tool-w');
          if (!tool) return;
          writingNavBtns.forEach((b) => b.classList.remove('active'));
          btn.classList.add('active');
          writingToolIds.forEach((id, i) => {
            const el = document.getElementById(id);
            if (el) el.classList.toggle('hidden', id !== 'english-' + tool);
          });
        });
      });

      const plotTabBtns = document.querySelectorAll('.plot-tab-btn');
      const plotTimelineWrap = document.getElementById('plot-timeline-wrap');
      const plotCharacterWrap = document.getElementById('plot-character-wrap');
      plotTabBtns.forEach((btn) => {
        btn.addEventListener('click', () => {
          const tab = btn.getAttribute('data-plot-tab');
          plotTabBtns.forEach((b) => b.classList.remove('active'));
          btn.classList.add('active');
          if (plotTimelineWrap) plotTimelineWrap.classList.toggle('hidden', tab !== 'timeline');
          if (plotCharacterWrap) plotCharacterWrap.classList.toggle('hidden', tab !== 'character');
        });
      });

      let timelineEvents = [];
      const timelineList = document.getElementById('plot-timeline-list');
      const timelineInput = document.getElementById('plot-timeline-input');
      const timelineAddBtn = document.getElementById('plot-timeline-add-btn');
      if (timelineAddBtn && timelineInput && timelineList) {
        timelineAddBtn.addEventListener('click', () => {
          const text = timelineInput.value.trim();
          if (!text) return;
          timelineEvents.push(text);
          const li = document.createElement('li');
          li.textContent = timelineEvents.length + '. ' + text;
          timelineList.appendChild(li);
          timelineInput.value = '';
        });
      }

      let characterProfiles = [];
      const characterForm = document.getElementById('plot-character-form');
      const characterList = document.getElementById('plot-character-list');
      if (characterForm && characterList) {
        characterForm.addEventListener('submit', (e) => {
          e.preventDefault();
          const name = document.getElementById('plot-char-name').value.trim();
          const role = document.getElementById('plot-char-role').value.trim();
          const appearance = document.getElementById('plot-char-appearance').value.trim();
          const backstory = document.getElementById('plot-char-backstory').value.trim();
          const motivation = document.getElementById('plot-char-motivation').value.trim();
          if (!name) return;
          characterProfiles.push({ name, role, appearance, backstory, motivation });
          const li = document.createElement('li');
          li.innerHTML = '<strong>' + name + '</strong>' + (role ? ' — ' + role : '') + (appearance ? '<br>Appearance: ' + appearance : '') + (motivation ? '<br>Motivation: ' + motivation : '');
          characterList.appendChild(li);
          characterForm.reset();
        });
      }

      const styleInput = document.getElementById('style-checker-input');
      const styleRun = document.getElementById('style-checker-run');
      const styleOutput = document.getElementById('style-checker-output');
      if (styleRun && styleInput && styleOutput) {
        styleRun.addEventListener('click', () => {
          const text = styleInput.value.trim();
          if (!text) { styleOutput.innerHTML = 'Paste text first.'; return; }
          const sentences = text.match(/[^.!?]+[.!?]+/g) || [text];
          const passiveRe = /\b(was|were|is|are|be|been|being)\s+[\w]+ed\b/i;
          let html = '';
          sentences.forEach((s) => {
            s = s.trim();
            const wordCount = s.split(/\s+/).length;
            const long = wordCount > 25;
            const passive = passiveRe.test(s);
            let cls = '';
            if (long && passive) cls = 'sentence-long sentence-passive';
            else if (long) cls = 'sentence-long';
            else if (passive) cls = 'sentence-passive';
            html += '<span class="' + cls + '">' + s + ' </span>';
          });
          styleOutput.innerHTML = html || 'No sentences found.';
          if (html) styleOutput.innerHTML += '<br><br><small>Yellow = long sentence (25+ words). Red tint = passive voice.</small>';
        });
      }

      const audioInput = document.getElementById('audio-proofreader-input');
      const audioPlay = document.getElementById('audio-proofreader-play');
      const audioStop = document.getElementById('audio-proofreader-stop');
      if (audioPlay && audioInput) {
        audioPlay.addEventListener('click', () => {
          const u = window.speechSynthesis;
          if (!u) { alert('Text-to-speech not supported in this browser.'); return; }
          u.cancel();
          const msg = new SpeechSynthesisUtterance(audioInput.value.trim() || 'Nothing to read.');
          u.speak(msg);
        });
      }
      if (audioStop) {
        audioStop.addEventListener('click', () => {
          if (window.speechSynthesis) window.speechSynthesis.cancel();
        });
      }

      const citationUrlWrap = document.getElementById('citation-url-wrap');
      const citationBookWrap = document.getElementById('citation-book-wrap');
      document.querySelectorAll('input[name="citation-mode"]').forEach((radio) => {
        radio.addEventListener('change', () => {
          const isBook = radio.value === 'book';
          if (citationUrlWrap) citationUrlWrap.classList.toggle('hidden', isBook);
          if (citationBookWrap) citationBookWrap.classList.toggle('hidden', !isBook);
        });
      });
      const citationGenerate = document.getElementById('citation-generate');
      const citationOutput = document.getElementById('citation-output');
      if (citationGenerate && citationOutput) {
        citationGenerate.addEventListener('click', () => {
          const format = (document.getElementById('citation-format') || {}).value || 'mla';
          const isBook = document.querySelector('input[name="citation-mode"]:checked')?.value === 'book';
          let out = '';
          if (isBook) {
            const author = (document.getElementById('citation-author') || {}).value.trim();
            const title = (document.getElementById('citation-title') || {}).value.trim();
            const year = (document.getElementById('citation-year') || {}).value.trim();
            const publisher = (document.getElementById('citation-publisher') || {}).value.trim();
            if (!author || !title) { citationOutput.textContent = 'Enter at least author and title.'; return; }
            if (format === 'mla') out = author + '. ' + title + (publisher ? '. ' + publisher : '') + (year ? ', ' + year + '.' : '.');
            else out = author + ' (' + (year || 'n.d.') + '). ' + title + (publisher ? '. ' + publisher : '') + '.';
          } else {
            const url = (document.getElementById('citation-url') || {}).value.trim();
            if (!url) { citationOutput.textContent = 'Enter a URL.'; return; }
            const title = url.replace(/^https?:\/\//, '').split('/')[0];
            if (format === 'mla') out = '"' + title + '." Web. Accessed ' + new Date().toLocaleDateString() + '. ' + url;
            else out = title + '. (n.d.). Retrieved ' + new Date().toLocaleDateString() + ', from ' + url;
          }
          citationOutput.textContent = out;
        });
      }
    })();

    (function initEngagementTools() {
      const engagementNavBtns = document.querySelectorAll('.english-nav-engagement .english-nav-btn');
      const engagementToolIds = ['english-cards', 'english-daily', 'english-vocab'];
      engagementNavBtns.forEach((btn) => {
        btn.addEventListener('click', () => {
          const tool = btn.getAttribute('data-english-tool-e');
          if (!tool) return;
          engagementNavBtns.forEach((b) => b.classList.remove('active'));
          btn.classList.add('active');
          engagementToolIds.forEach((id) => {
            const el = document.getElementById(id);
            if (el) el.classList.toggle('hidden', id !== 'english-' + tool);
          });
        });
      });

      const dailyPrompts = [
        'Write about a place that feels like home.',
        'Describe a character who has a secret.',
        'Start with: "The last time I saw them..."',
        'Write a letter to your future self.',
        'What would you do with one extra hour every day?',
      ];
      const dailyPromptEl = document.getElementById('daily-prompt');
      if (dailyPromptEl) {
        const day = Math.floor(Date.now() / 86400000) % dailyPrompts.length;
        dailyPromptEl.textContent = 'Today\'s prompt: ' + dailyPrompts[day];
      }
      let dailyTimerInterval = null;
      const dailyTimerEl = document.getElementById('daily-timer');
      const dailyStart = document.getElementById('daily-timer-start');
      const dailyReset = document.getElementById('daily-timer-reset');
      let dailySeconds = 15 * 60;
      function updateDailyTimer() {
        if (!dailyTimerEl) return;
        const m = Math.floor(dailySeconds / 60);
        const s = dailySeconds % 60;
        dailyTimerEl.textContent = (m < 10 ? '0' : '') + m + ':' + (s < 10 ? '0' : '') + s;
      }
      if (dailyStart && dailyTimerEl) {
        dailyStart.addEventListener('click', () => {
          if (dailyTimerInterval) return;
          dailyTimerInterval = setInterval(() => {
            dailySeconds--;
            updateDailyTimer();
            if (dailySeconds <= 0) clearInterval(dailyTimerInterval);
          }, 1000);
        });
      }
      if (dailyReset && dailyTimerEl) {
        dailyReset.addEventListener('click', () => {
          if (dailyTimerInterval) clearInterval(dailyTimerInterval);
          dailyTimerInterval = null;
          dailySeconds = 15 * 60;
          updateDailyTimer();
        });
      }
      updateDailyTimer();

      const cardForm = document.getElementById('card-form');
      const cardsGrid = document.getElementById('cards-grid');
      let cards = [];
      if (cardForm && cardsGrid) {
        cardForm.addEventListener('submit', (e) => {
          e.preventDefault();
          const name = document.getElementById('card-name').value.trim();
          const type = (document.getElementById('card-type') || {}).value;
          const image = (document.getElementById('card-image') || {}).value.trim();
          const archetype = (document.getElementById('card-archetype') || {}).value.trim();
          const motivation = (document.getElementById('card-motivation') || {}).value.trim();
          if (!name) return;
          cards.push({ name, type, image, archetype, motivation });
          const div = document.createElement('div');
          div.className = 'card-item';
          div.innerHTML = (image ? '<img src="' + image + '" alt="">' : '<div style="height:100px;background:#1a1a1a;display:flex;align-items:center;justify-content:center;color:#555;">No image</div>') +
            '<div class="card-item-body"><div class="card-item-name">' + name + '</div><div class="card-item-meta">' + (archetype ? archetype : '') + (motivation ? ' — ' + motivation : '') + '</div></div>';
          cardsGrid.appendChild(div);
          cardForm.reset();
        });
      }

      let vocabList = [];
      const vocabWord = document.getElementById('vocab-word');
      const vocabDef = document.getElementById('vocab-def');
      const vocabAddBtn = document.getElementById('vocab-add-btn');
      const vocabListEl = document.getElementById('vocab-list');
      const vocabCardWord = document.getElementById('vocab-card-word');
      const vocabFlip = document.getElementById('vocab-flip');
      const vocabPrev = document.getElementById('vocab-prev');
      const vocabNext = document.getElementById('vocab-next');
      const vocabIndexEl = document.getElementById('vocab-index');
      let vocabCurrentIndex = 0;
      let vocabShowingDef = false;
      function renderVocabCard() {
        const v = vocabList[vocabCurrentIndex];
        if (!vocabCardWord) return;
        if (!v) { vocabCardWord.textContent = 'Add words above.'; if (vocabFlip) vocabFlip.textContent = 'Show definition'; return; }
        vocabShowingDef = false;
        vocabCardWord.textContent = v.word;
        if (vocabFlip) vocabFlip.textContent = 'Show definition';
        if (vocabIndexEl) vocabIndexEl.textContent = (vocabCurrentIndex + 1) + ' / ' + vocabList.length;
      }
      function saveVocab() {
        const ds = window.SchoolResourceData;
        if (ds) ds.saveContent('vocab', vocabList).catch(function () {});
      }
      (function loadVocab() {
        const ds = window.SchoolResourceData;
        if (!ds) { renderVocabCard(); return; }
        ds.getContent('vocab').then(function (arr) {
          if (Array.isArray(arr) && arr.length) {
            vocabList.length = 0;
            vocabList.push.apply(vocabList, arr);
            if (vocabListEl) {
              vocabListEl.innerHTML = '';
              vocabList.forEach(function (v) {
                const li = document.createElement('li');
                li.textContent = v.word + ' — ' + (v.def || '');
                vocabListEl.appendChild(li);
              });
            }
            vocabCurrentIndex = Math.min(vocabCurrentIndex, vocabList.length - 1);
          }
          renderVocabCard();
        }).catch(function () { renderVocabCard(); });
      })();
      if (vocabAddBtn && vocabWord && vocabDef && vocabListEl) {
        vocabAddBtn.addEventListener('click', () => {
          const word = vocabWord.value.trim();
          const def = vocabDef.value.trim();
          if (!word || !def) return;
          vocabList.push({ word, def });
          const li = document.createElement('li');
          li.textContent = word + ' — ' + def;
          vocabListEl.appendChild(li);
          vocabWord.value = '';
          vocabDef.value = '';
          vocabCurrentIndex = vocabList.length - 1;
          renderVocabCard();
          saveVocab();
        });
      }
      if (vocabFlip && vocabCardWord) {
        vocabFlip.addEventListener('click', () => {
          const v = vocabList[vocabCurrentIndex];
          if (!v) return;
          vocabShowingDef = !vocabShowingDef;
          vocabCardWord.textContent = vocabShowingDef ? v.def : v.word;
          vocabFlip.textContent = vocabShowingDef ? 'Show word' : 'Show definition';
        });
      }
      if (vocabPrev) vocabPrev.addEventListener('click', () => { vocabCurrentIndex = Math.max(0, vocabCurrentIndex - 1); renderVocabCard(); });
      if (vocabNext) vocabNext.addEventListener('click', () => { vocabCurrentIndex = Math.min(vocabList.length - 1, vocabCurrentIndex + 1); renderVocabCard(); });
      renderVocabCard();
    })();

    (function initEnglishTutorial() {
      const stepTitleEl = document.getElementById('english-tutorial-step-title');
      const stepDescEl = document.getElementById('english-tutorial-step-desc');
      const stepActionsEl = document.getElementById('english-tutorial-actions');
      const progressEl = document.getElementById('english-tutorial-progress');
      const prevBtn = document.getElementById('english-tutorial-prev');
      const nextBtn = document.getElementById('english-tutorial-next');
      const menuEl = document.getElementById('english-tutorial-menu');

      let englishTutorialStepIndex = 0;

      function switchEnglishTool(tool) {
        let category = 'reading';
        if (tool === 'tutorial') category = 'learning';
        else if (['plot', 'style', 'audio', 'citation'].includes(tool)) category = 'writing';
        else if (['cards', 'daily', 'vocab'].includes(tool)) category = 'engagement';
        const categoryEl = document.getElementById('english-category-' + category);
        if (categoryEl) categoryEl.classList.remove('hidden');
        const catTab = englishPanel ? englishPanel.querySelector('.english-category-tab[data-english-category="' + category + '"]') : null;
        if (catTab) { catTab.classList.add('active'); englishPanel.querySelectorAll('.english-category-tab').forEach((t) => { if (t !== catTab) t.classList.remove('active'); }); }
        if (englishPanel) englishPanel.querySelectorAll('.english-category-content').forEach((c) => { c.classList.toggle('hidden', c.id !== 'english-category-' + category); });
        if (tool !== 'tutorial') {
          let btn = null;
          if (category === 'reading') btn = document.querySelector('#english-category-reading .english-nav-btn[data-english-tool="' + tool + '"]');
          else if (category === 'writing') btn = document.querySelector('#english-category-writing .english-nav-btn[data-english-tool-w="' + tool + '"]');
          else if (category === 'engagement') btn = document.querySelector('#english-category-engagement .english-nav-btn[data-english-tool-e="' + tool + '"]');
          if (btn) btn.click();
        }
      }

      const englishTutorialSteps = [
        {
          title: 'Welcome',
          description: 'Learn how to use Reading tools, Writing assistants, Engagement features, and more.',
          actions: [
            { label: 'Run quick tour', onClick: runEnglishTour },
          ],
        },
        {
          title: 'E-Reader',
          description: 'Upload a text file or paste text, then click Load Text. Select text and click "Highlight selected" to mark passages, or "Add sticky note" for notes.',
          actions: [
            { label: 'Open E-Reader', onClick: () => switchEnglishTool('ereader') },
            { label: 'Load sample text', onClick: () => {
              switchEnglishTool('ereader');
              if (ereaderPaste) {
                ereaderPaste.value = 'The old man stood at the shore. The waves crashed like thunder. His heart was a stone.';
                loadEreaderText();
              }
            } },
          ],
        },
        {
          title: 'Literary Device Tracker',
          description: 'As you read, add examples of metaphors, similes, irony, and other devices. Include the quote, source, and your analysis. Use the filter to view by type.',
          actions: [
            { label: 'Open Device Tracker', onClick: () => switchEnglishTool('tracker') },
            { label: 'Add sample entry', onClick: () => {
              switchEnglishTool('tracker');
              literaryDevices.push({
                device: 'metaphor',
                quote: 'Her smile was the sun',
                source: 'Sample',
                notes: 'Describes warmth and brightness of character',
              });
              renderTrackerList();
            } },
          ],
        },
        {
          title: 'Summary & Connections',
          description: 'Paste longer text and click "Generate Summary" for an extractive summary, or "Find Themes" to see recurring words and ideas.',
          actions: [
            { label: 'Open Summary tool', onClick: () => switchEnglishTool('summary') },
            { label: 'Try with sample', onClick: () => {
              switchEnglishTool('summary');
              if (summaryInput) {
                summaryInput.value = 'The theme of isolation appears throughout the novel. The main character feels isolated from society. Isolation leads to loneliness.';
                if (summaryGenerate) summaryGenerate.click();
                if (summaryConnections) summaryConnections.click();
              }
            } },
          ],
        },
        {
          title: 'Reading Accessibility',
          description: 'Enable OpenDyslexic font for easier reading, or the reading line guide for a subtle visual aid that helps keep your eyes on the right line.',
          actions: [
            { label: 'Open Accessibility', onClick: () => switchEnglishTool('accessibility') },
            { label: 'Try OpenDyslexic', onClick: () => {
              switchEnglishTool('accessibility');
              if (accessibilityDyslexic) accessibilityDyslexic.checked = true;
              document.body.classList.add('font-dyslexic');
            } },
          ],
        },
        {
          title: 'Plot Builders',
          description: 'Build your story arc with a timeline of events, and keep character details consistent with profiles. Add events in order and save character traits for reference.',
          actions: [
            { label: 'Open Plot Builders', onClick: () => switchEnglishTool('plot') },
            { label: 'Add sample event', onClick: () => {
              switchEnglishTool('plot');
              const input = document.getElementById('plot-timeline-input');
              const addBtn = document.getElementById('plot-timeline-add-btn');
              if (input) input.value = 'Inciting incident';
              if (addBtn) addBtn.click();
            } },
          ],
        },
        {
          title: 'Style Checker',
          description: 'Paste your draft to highlight long or complex sentences and passive voice. Helps you tighten and vary your prose.',
          actions: [
            { label: 'Open Style Checker', onClick: () => switchEnglishTool('style') },
          ],
        },
        {
          title: 'Audio Proofreader',
          description: 'Listen back to your writing with text-to-speech to catch awkward phrasing, missing words, and rhythm issues.',
          actions: [
            { label: 'Open Audio Proofreader', onClick: () => switchEnglishTool('audio') },
          ],
        },
        {
          title: 'Citation Automator',
          description: 'Generate MLA or APA citations from a URL or book details. Enter the source and pick your format.',
          actions: [
            { label: 'Open Citation tool', onClick: () => switchEnglishTool('citation') },
          ],
        },
        {
          title: 'Trading Cards',
          description: 'Create cards for characters or vocabulary with image, archetype, motivation, and more. Great for studying or planning stories.',
          actions: [
            { label: 'Open Trading Cards', onClick: () => switchEnglishTool('cards') },
          ],
        },
        {
          title: 'Daily Writing Challenge',
          description: 'Get a daily prompt and use the focus timer for distraction-free writing. Set a goal and start the timer.',
          actions: [
            { label: 'Open Daily Challenge', onClick: () => switchEnglishTool('daily') },
          ],
        },
        {
          title: 'Vocabulary Games',
          description: 'Add words and definitions, then practice with flashcards or a quick quiz. Build your vocabulary as you read.',
          actions: [
            { label: 'Open Vocabulary Games', onClick: () => switchEnglishTool('vocab') },
          ],
        },
        {
          title: 'You\'re all set',
          description: 'Use Reading tools for close reading, Writing for drafting and citations, Engagement for practice and creativity, and Accessibility when you need support.',
          actions: [
            { label: 'Go to E-Reader', onClick: () => switchEnglishTool('ereader') },
            { label: 'Go to Plot Builders', onClick: () => switchEnglishTool('plot') },
            { label: 'Go to Trading Cards', onClick: () => switchEnglishTool('cards') },
          ],
        },
      ];

      function runEnglishTour() {
        switchEnglishTool('tutorial');
        englishTutorialStepIndex = 0;
        renderEnglishTutorialStep();
        let i = 0;
        const tools = ['ereader', 'tracker', 'summary', 'accessibility', 'plot', 'style', 'audio', 'citation', 'cards', 'daily', 'vocab', 'tutorial'];
        const interval = setInterval(() => {
          if (i < tools.length) {
            switchEnglishTool(tools[i]);
            i++;
          } else {
            clearInterval(interval);
            switchEnglishTool('tutorial');
            englishTutorialStepIndex = 0;
            renderEnglishTutorialStep();
          }
        }, 600);
      }

      function renderEnglishTutorialStep() {
        const step = englishTutorialSteps[englishTutorialStepIndex];
        if (!step) return;
        if (stepTitleEl) stepTitleEl.textContent = step.title;
        if (stepDescEl) stepDescEl.textContent = step.description;
        if (stepActionsEl) {
          stepActionsEl.innerHTML = '';
          step.actions.forEach((a) => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'english-tutorial-btn';
            btn.textContent = a.label;
            btn.addEventListener('click', a.onClick);
            stepActionsEl.appendChild(btn);
          });
        }
        if (progressEl) {
          progressEl.textContent = 'Step ' + (englishTutorialStepIndex + 1) + ' of ' + englishTutorialSteps.length;
        }
        if (menuEl) {
          menuEl.innerHTML = '';
          englishTutorialSteps.forEach((s, idx) => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'english-tutorial-menu-item' + (idx === englishTutorialStepIndex ? ' active' : '');
            btn.textContent = (idx + 1) + '. ' + s.title;
            btn.addEventListener('click', () => {
              englishTutorialStepIndex = idx;
              renderEnglishTutorialStep();
            });
            menuEl.appendChild(btn);
          });
        }
        if (prevBtn) prevBtn.disabled = englishTutorialStepIndex === 0;
        if (nextBtn) nextBtn.disabled = englishTutorialStepIndex === englishTutorialSteps.length - 1;
      }

      if (prevBtn) {
        prevBtn.addEventListener('click', () => {
          if (englishTutorialStepIndex > 0) {
            englishTutorialStepIndex--;
            renderEnglishTutorialStep();
          }
        });
      }

      if (nextBtn) {
        nextBtn.addEventListener('click', () => {
          if (englishTutorialStepIndex < englishTutorialSteps.length - 1) {
            englishTutorialStepIndex++;
            renderEnglishTutorialStep();
          }
        });
      }

      renderEnglishTutorialStep();
    })();
  })();

  function playTapLottie(e) {
    try {
      if (typeof lottie === 'undefined') return;
      if (!lottieTapContainer) return;
      const rect = (e && e.target && e.target.getBoundingClientRect) ? e.target.getBoundingClientRect() : null;
      if (rect) {
        lottieTapContainer.style.left = (rect.left + rect.width / 2) + 'px';
        lottieTapContainer.style.top = (rect.top + rect.height / 2) + 'px';
      }
      lottieTapContainer.classList.add('playing');
      lottieTapContainer.innerHTML = '';
      const anim = lottie.loadAnimation({
        container: lottieTapContainer,
        renderer: 'svg',
        loop: false,
        autoplay: true,
        animationData: getTapLottieData(),
      });
      anim.setSpeed(1.8);
      anim.addEventListener('complete', () => {
        lottieTapContainer.classList.remove('playing');
        anim.destroy();
      });
    } catch (_) {}
  }

  function getTapLottieData() {
    return {
      v: '5.7.2',
      fr: 60,
      ip: 0,
      op: 20,
      w: 100,
      h: 100,
      layers: [{
        ddd: 0,
        ind: 1,
        ty: 4,
        nm: 'Tap',
        sr: 1,
        ks: {
          o: { a: 1, k: [{ i: { x: [0.4], y: 1 }, o: { x: [0.6], y: 0 }, t: 0, s: [80] }, { t: 20, s: [0] }] },
          r: { a: 0, k: 0 },
          p: { a: 0, k: [50, 50, 0] },
          a: { a: 0, k: [0, 0, 0] },
          s: { a: 1, k: [{ i: { x: [0.4], y: 1 }, o: { x: [0.6], y: 0 }, t: 0, s: [0, 0, 100] }, { t: 20, s: [120, 120, 100] }] },
        },
        ao: 0,
        shapes: [
          { ty: 'el', d: { a: 0, k: [50, 50] } },
          { ty: 'st', c: { a: 0, k: [0.3, 0.9, 1, 1] }, o: { a: 0, k: 70 } },
          { ty: 'fl', c: { a: 0, k: [0.3, 0.9, 1, 0.25] }, o: { a: 0, k: 70 } },
          { ty: 'tr', p: { a: 0, k: [0, 0] }, a: { a: 0, k: [0, 0] }, s: { a: 0, k: [100, 100] }, r: { a: 0, k: 0 }, o: { a: 0, k: 100 } },
        ],
        ip: 0,
        op: 20,
      }],
    };
  }

  function playTransitionLottie() {
    try {
      if (typeof lottie === 'undefined' || !lottieTransitionOverlay) return;
      const wrap = document.createElement('div');
      wrap.className = 'lottie-inner';
      wrap.style.width = '120px';
      wrap.style.height = '120px';
      lottieTransitionOverlay.appendChild(wrap);
      lottieTransitionOverlay.classList.add('playing');
      const anim = lottie.loadAnimation({
        container: wrap,
        renderer: 'svg',
        loop: false,
        autoplay: true,
        animationData: getTransitionLottieData(),
      });
      anim.setSpeed(2);
      anim.addEventListener('complete', () => {
        lottieTransitionOverlay.classList.remove('playing');
        if (wrap.parentNode) wrap.remove();
        anim.destroy();
      });
    } catch (_) {}
  }

  function getTransitionLottieData() {
    return {
      v: '5.7.2',
      fr: 60,
      ip: 0,
      op: 24,
      w: 120,
      h: 120,
      layers: [{
        ddd: 0,
        ind: 1,
        ty: 4,
        nm: 'Transition',
        sr: 1,
        ks: {
          o: { a: 1, k: [{ i: { x: [0.4], y: 1 }, o: { x: [0.6], y: 0 }, t: 0, s: [60] }, { t: 24, s: [0] }] },
          r: { a: 0, k: 0 },
          p: { a: 0, k: [60, 60, 0] },
          a: { a: 0, k: [0, 0, 0] },
          s: { a: 1, k: [{ i: { x: [0.33], y: 1 }, o: { x: [0.66], y: 0 }, t: 0, s: [40, 40, 100] }, { t: 24, s: [100, 100, 100] }] },
        },
        ao: 0,
        shapes: [
          { ty: 'el', d: { a: 0, k: [50, 50] } },
          { ty: 'st', c: { a: 0, k: [0.3, 0.85, 1, 1] }, o: { a: 0, k: 50 } },
          { ty: 'fl', c: { a: 0, k: [0.3, 0.85, 1, 0.15] }, o: { a: 0, k: 50 } },
          { ty: 'tr', p: { a: 0, k: [0, 0] }, a: { a: 0, k: [0, 0] }, s: { a: 0, k: [100, 100] }, r: { a: 0, k: 0 }, o: { a: 0, k: 100 } },
        ],
        ip: 0,
        op: 24,
      }],
    };
  }

  window.addEventListener('resize', () => {
    if (mode === 'diagram') requestAnimationFrame(drawDiagramLinks);
    if (mode === 'graph') requestAnimationFrame(drawGraph);
  });

  applyTheme(activeTheme);
  setMode('math-materials');
  startAppMusic();
})();
