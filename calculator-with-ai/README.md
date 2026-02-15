# School Resource with AI Widget

This folder is a copy of the **School Resource** app (Math, English, and Science materials) with an optional **AI (Josiah) chat widget** on the side.

- **Original app**: The unchanged version lives in the `calculator` folder. Use that if you want to work without the AI or if something in this copy breaks.
- **This copy**: Same app plus a floating “Ask Josiah” tab. Click it to open a small chat panel you can drag around the screen. The panel talks to the same Josiah chatbot (memory, knowledge, etc.) as the standalone chat page.

## For a website (others use it, no terminal)

To put this on a real site so **visitors just open a link** and use the AI with no terminal or local server, see **[DEPLOY.md](DEPLOY.md)**. You deploy the backend once (e.g. to Render), set the URL in **config.js**, then host this folder on Netlify, Vercel, GitHub Pages, or your own server.

## Local use (your computer)

**Double-click `START_WITH_AI.bat`** in this folder. It will:

1. Start the AI server (a “Josiah Server” window will open—keep it open).
2. Open your browser to School Resource with the AI already connected.

You only run that one file; no need to run the chatbot separately or open `index.html` by hand. Click “Ask Josiah” on the right to use the AI.

- **Open `index.html` directly**: The AI widget will try `http://localhost:5000/api/chat`. If the server isn’t running, you’ll see “Can’t reach the server.” Use `START_WITH_AI.bat` instead.
