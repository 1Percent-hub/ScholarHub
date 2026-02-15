# Deploy So Others Can Use It (No Terminal)

To put School Resource + AI on a real website so **visitors just open a link** (no terminal, no local server):

## 1. Deploy the AI backend (one-time)

The widget needs the Josiah API on the internet. Use a free host like **Render**.

1. Go to [render.com](https://render.com) and sign up (free).
2. **New → Web Service**.
3. Connect your GitHub (or upload the `chatbot/backend` folder).
4. Set **Root Directory** to `chatbot/backend` (if your repo is the whole Apps folder) or the folder that contains `app.py` and `requirements.txt`.
5. Render will detect Python and use:
   - **Build:** `pip install -r requirements.txt`
   - **Start:** `gunicorn --bind 0.0.0.0:$PORT app:app`
6. Click **Create Web Service**. Wait for the first deploy to finish.
7. Copy your service URL, e.g. `https://josiah-api-xxxx.onrender.com`. The API is at `https://josiah-api-xxxx.onrender.com/api/chat`.

Note: On the free tier the service may sleep after 15 minutes of no use; the first visit after that can take ~30 seconds to wake up.

## 2. Point the site at your backend

In the **calculator-with-ai** folder, edit **config.js**:

```js
window.CHATBOT_API_URL = "https://YOUR-SERVICE-URL.onrender.com/api/chat";
```

Replace `YOUR-SERVICE-URL` with the URL Render gave you (no trailing slash before `/api/chat`).

## 3. Host the website

Upload or deploy the **calculator-with-ai** folder (all files: `index.html`, `config.js`, `ai-widget.js`, `styles.css`, `app.js`, etc.) to any host:

- **Netlify:** Drag the folder into [app.netlify.com/drop](https://app.netlify.com/drop), or connect a repo and set publish directory to `calculator-with-ai`.
- **Vercel:** Import the project, set root to `calculator-with-ai`.
- **GitHub Pages:** Push the folder to a repo and enable Pages (publish from that folder or branch).
- **Your own server:** Copy the folder to the web root (e.g. `public_html` or `www`).

Visitors open the site URL; no terminal or local setup needed. The “Ask Josiah” widget will use the backend URL you set in **config.js**.

## Quick checklist

- [ ] Backend deployed on Render (or similar) and URL copied.
- [ ] **config.js** updated with `window.CHATBOT_API_URL = "https://.../api/chat";`
- [ ] **calculator-with-ai** folder deployed to your website host.
- [ ] Open the live site and click “Ask Josiah” to confirm the AI responds.
