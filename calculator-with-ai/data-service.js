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
          };
        }
      } catch (_) {}
      return { theme: 'theme-professional', soundEffects: true, speakOnHover: false };
    },

    async saveSettings(settings) {
      const uid = await getUserId();
      const k = uid ? CONTENT_PREFIX + uid + '-settings' : SETTINGS_KEY;
      const payload = {
        theme: settings.theme || 'theme-professional',
        soundEffects: settings.soundEffects !== false,
        speakOnHover: settings.speakOnHover === true,
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
  };
})();
