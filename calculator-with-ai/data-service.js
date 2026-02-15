(function () {
  const SETTINGS_KEY = 'school-resource-settings';
  const CONTENT_PREFIX = 'school-resource-content-';
  const GUEST_PREFIX = 'school-resource-guest-';
  const debounceTimers = {};

  async function getUserId() {
    const auth = window.SchoolResourceAuth;
    if (!auth) return null;
    const { data } = await auth.getSession();
    return data && data.session && data.session.user ? data.session.user.id : null;
  }

  function contentKey(key, uid) {
    return uid ? CONTENT_PREFIX + uid + '-' + key : GUEST_PREFIX + key;
  }

  window.SchoolResourceData = {
    async getSettings() {
      const uid = await getUserId();
      const k = uid ? CONTENT_PREFIX + uid + '-settings' : SETTINGS_KEY;
      try {
        const raw = localStorage.getItem(k);
        if (raw) {
          const s = JSON.parse(raw);
          return {
            theme: s.theme || 'theme-professional',
            soundEffects: s.soundEffects !== false,
            speakOnHover: s.speakOnHover === true,
            volume: typeof s.volume === 'number' ? Math.min(100, Math.max(0, s.volume)) : 100,
          };
        }
      } catch (_) {}
      return { theme: 'theme-professional', soundEffects: true, speakOnHover: false, volume: 100 };
    },

    async saveSettings(settings) {
      const uid = await getUserId();
      const k = uid ? CONTENT_PREFIX + uid + '-settings' : SETTINGS_KEY;
      const payload = {
        theme: settings.theme || 'theme-professional',
        soundEffects: settings.soundEffects !== false,
        speakOnHover: settings.speakOnHover === true,
        volume: typeof settings.volume === 'number' ? Math.min(100, Math.max(0, settings.volume)) : 100,
      };
      try {
        localStorage.setItem(k, JSON.stringify(payload));
      } catch (_) {}
    },

    async getContent(key) {
      const uid = await getUserId();
      const k = contentKey(key, uid);
      try {
        const raw = localStorage.getItem(k);
        if (raw) return JSON.parse(raw);
      } catch (_) {}
      if (!uid) {
        try {
          const raw = localStorage.getItem(CONTENT_PREFIX + key);
          if (raw) return JSON.parse(raw);
        } catch (_) {}
      }
      return null;
    },

    async saveContent(key, value) {
      const uid = await getUserId();
      const k = contentKey(key, uid);
      try {
        localStorage.setItem(k, JSON.stringify(value));
      } catch (_) {}
    },

    debouncedSaveContent(key, value, delayMs) {
      delayMs = delayMs || 500;
      if (debounceTimers[key]) clearTimeout(debounceTimers[key]);
      debounceTimers[key] = setTimeout(function () {
        debounceTimers[key] = null;
        window.SchoolResourceData.saveContent(key, value);
      }, delayMs);
    },

    async copyLocalDataToAccount() {
      const uid = await getUserId();
      if (!uid) return;
      try {
        const rawSettings = localStorage.getItem(SETTINGS_KEY);
        if (rawSettings) {
          const s = JSON.parse(rawSettings);
          await window.SchoolResourceData.saveSettings({
            theme: s.theme || 'theme-professional',
            soundEffects: s.soundEffects !== false,
            speakOnHover: s.speakOnHover === true,
            volume: typeof s.volume === 'number' ? Math.min(100, Math.max(0, s.volume)) : 100,
          });
        }
        const labRaw = localStorage.getItem('school-resource-lab-logger');
        if (labRaw) {
          try {
            const val = JSON.parse(labRaw);
            await window.SchoolResourceData.saveContent('lab_logger', val);
          } catch (_) {}
        }
        const contentKeys = ['notepad', 'vocab', 'literary_devices', 'sticky_notes', 'graph_series', 'diagram_blocks', 'plot_timeline', 'plot_characters'];
        for (let i = 0; i < contentKeys.length; i++) {
          const k = contentKeys[i];
          const raw = localStorage.getItem(CONTENT_PREFIX + k);
          if (raw) {
            try {
              const val = JSON.parse(raw);
              await window.SchoolResourceData.saveContent(k, val);
            } catch (_) {}
          }
        }
      } catch (_) {}
    },

    async exportUserData() {
      const uid = await getUserId();
      if (!uid) return null;
      const out = { exportedAt: new Date().toISOString(), userId: uid, version: 1, settings: null, content: {} };
      try {
        out.settings = await window.SchoolResourceData.getSettings();
        const prefix = CONTENT_PREFIX + uid + '-';
        const settingsKey = prefix + 'settings';
        for (let i = 0; i < localStorage.length; i++) {
          const key = localStorage.key(i);
          if (!key || key === settingsKey) continue;
          if (key.startsWith(prefix)) {
            const contentKey = key.slice(prefix.length);
            try {
              const raw = localStorage.getItem(key);
              if (raw) out.content[contentKey] = JSON.parse(raw);
            } catch (_) {}
          }
        }
      } catch (_) {}
      return JSON.stringify(out, null, 2);
    },

    async listUserContentKeys() {
      const uid = await getUserId();
      if (!uid) return [];
      const prefix = CONTENT_PREFIX + uid + '-';
      const keys = [];
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith(prefix) && key !== prefix + 'settings') {
          keys.push(key.slice(prefix.length));
        }
      }
      return keys;
    },
  };
})();
