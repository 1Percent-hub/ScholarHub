(function () {
  const USERS_KEY = 'school-resource-users';
  const SESSION_KEY = 'school-resource-session';
  const SALT = 'school-resource-v1';

  async function hashPassword(password, email) {
    const str = SALT + email.toLowerCase() + password;
    const encoder = new TextEncoder();
    const data = encoder.encode(str);
    const hash = await crypto.subtle.digest('SHA-256', data);
    return Array.from(new Uint8Array(hash)).map(b => b.toString(16).padStart(2, '0')).join('');
  }

  function getUsers() {
    try {
      const raw = localStorage.getItem(USERS_KEY);
      return raw ? JSON.parse(raw) : {};
    } catch (_) { return {}; }
  }

  function setUsers(users) {
    try {
      localStorage.setItem(USERS_KEY, JSON.stringify(users));
    } catch (_) {}
  }

  function getSession() {
    try {
      const raw = localStorage.getItem(SESSION_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (_) { return null; }
  }

  function setSession(email, displayName) {
    try {
      localStorage.setItem(SESSION_KEY, JSON.stringify({ email, displayName: displayName || email.split('@')[0] }));
    } catch (_) {}
  }

  function clearSession() {
    try { localStorage.removeItem(SESSION_KEY); } catch (_) {}
  }

  window.SchoolResourceAuth = {
    async signUp(email, password, displayName) {
      const em = (email || '').trim().toLowerCase();
      const pw = password || '';
      if (!em || !pw || pw.length < 6) {
        return { error: { message: 'Email and password (min 6 chars) required' } };
      }
      const users = getUsers();
      if (users[em]) {
        return { error: { message: 'An account with this email already exists' } };
      }
      const passwordHash = await hashPassword(pw, em);
      const name = (displayName || '').trim() || em.split('@')[0];
      users[em] = { passwordHash, displayName: name };
      setUsers(users);
      setSession(em, name);
      const session = {
        user: {
          id: em,
          email: em,
          user_metadata: { display_name: name },
        },
      };
      return { data: { session, user: session.user } };
    },

    async signIn(email, password) {
      const em = (email || '').trim().toLowerCase();
      const pw = password || '';
      if (!em || !pw) {
        return { error: { message: 'Email and password required' } };
      }
      const users = getUsers();
      const u = users[em];
      if (!u) {
        return { error: { message: 'No account found with this email' } };
      }
      const passwordHash = await hashPassword(pw, em);
      if (passwordHash !== u.passwordHash) {
        return { error: { message: 'Incorrect password' } };
      }
      setSession(em, u.displayName);
      const session = {
        user: {
          id: em,
          email: em,
          user_metadata: { display_name: u.displayName },
        },
      };
      return { data: { session, user: session.user } };
    },

    async signOut() {
      clearSession();
    },

    async getSession() {
      const s = getSession();
      if (!s || !s.email) return { data: { session: null } };
      const users = getUsers();
      const u = users[s.email];
      if (!u) {
        clearSession();
        return { data: { session: null } };
      }
      const session = {
        user: {
          id: s.email,
          email: s.email,
          user_metadata: { display_name: s.displayName || u.displayName },
        },
      };
      return { data: { session } };
    },

    onAuthStateChange(callback) {
      return function () {};
    },

    async getProfile(userId) {
      const s = getSession();
      const em = userId || (s && s.email);
      if (!em) return null;
      const users = getUsers();
      const u = users[em];
      if (!u) return null;
      return { display_name: u.displayName, avatar_url: null };
    },

    async updateProfile(userId, updates) {
      const em = (userId || '').trim().toLowerCase();
      if (!em) return { error: { message: 'User required' } };
      const users = getUsers();
      const u = users[em];
      if (!u) return { error: { message: 'User not found' } };
      if (updates.display_name != null) u.displayName = String(updates.display_name);
      if (updates.avatar_url != null) u.avatar_url = updates.avatar_url;
      setUsers(users);
      const s = getSession();
      if (s && s.email === em && updates.display_name != null) {
        setSession(em, updates.display_name);
      }
      return { data: u };
    },
  };
})();
