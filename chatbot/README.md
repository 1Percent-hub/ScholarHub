# Chatbot – how to run it

When you see **"Something went wrong"** or **"Can't reach the server"**, the chat page can't talk to the Python backend. Do this:

## 1. Start the backend

In a terminal:

```bash
cd chatbot/backend
pip install -r requirements.txt
python app.py
```

Leave this running. You should see something like: `Running on http://0.0.0.0:5000`

## 2. Open the chat page the right way

Don't double-click `index.html` (that loads it as a file and the browser may block requests to the backend).

In a **second** terminal:

```bash
cd chatbot/widget
python -m http.server 8000
```

Then in your browser go to: **http://localhost:8000**

Type in the box and press Enter. The backend will reply and the error should go away.
