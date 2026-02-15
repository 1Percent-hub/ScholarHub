# Account System

The app uses a custom, in-house login system. All data is stored in the browser (localStorage).

## How it works

- **Create Account** – Enter email, password (min 6 chars), and optional display name. Your account and data are stored locally.
- **Sign In** – Use your email and password to sign in.
- **Cancel / Continue as guest** – Use the app without an account. Guest data stays in the browser only.
- **Data per user** – Logged-in users get their own settings and content (notepad, vocab, lab logger, etc.), separate from guest data.

## Security note

Passwords are hashed (SHA-256) before storage. This is client-side only—anyone with access to the browser can read stored data. Suitable for personal or classroom use on trusted devices.
