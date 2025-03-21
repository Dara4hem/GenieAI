```markdown
# 🤖 Genie AI Assistant – Multi-Agent RAG with LangGraph + Django UI

This project was built as a complete solution for the **AI Engineer Task** provided by Genie CRM.

It fulfills **all the required tasks**, and additionally includes a polished **full-stack assistant interface** built with Django, Bootstrap 5, LangGraph, and LangChain.

---

## ✅ Task Completion Summary

| Task | Description |
|------|-------------|
| ✔️ Task 1 | Multi-Agent Graph using LangGraph |
| ✔️ Task 2 | RAG Manager with Document + URL Handling |
| ✔️ Bonus | Full-Stack Web App with Frontend, Dark Mode, History, File/URL Upload |
| ✔️ Bonus | Built-in File Summarization + RAG Context Reuse |
| ✔️ Bonus | Prevent invalid inputs (e.g. URLs without model) |
| ✔️ Bonus | Live chat, streaming spinner, reset system, and persistent session |

---

## 🌐 Live UI Features

- Upload files (.pdf, .docx, .pptx, .txt)
- Paste URLs (auto-fetches and summarizes content)
- Ask any question (chat interface)
- Select model (GPT-4, LLaMA 3 via Groq, Mistral)
- Set prompt rules (system instructions)
- Spinner loading indicator
- View full RAG response breakdown (retrieved, summary, final answer)
- Reset app memory
- Switch between light/dark mode

---

## 🧠 Multi-Agent Graph

Using `LangGraph`, the multi-agent workflow works as:

```txt
[input_text, file_path, url_context] →
  [Retriever Agent] →
  [Summarizer Agent] →
  [QA Agent]
```

Each agent is modular and runs sequentially using `StateGraph`.

---

## 📁 Files & URL RAG System

The system supports:

| Type       | Handler                        | Notes |
|------------|--------------------------------|-------|
| PDF/TXT/DOCX/PPTX | Extracted and chunked      | LLM summarizes each chunk |
| URLs       | HTML parsed via BeautifulSoup | Summarized with LLM chunk-by-chunk |
| Session    | Stores summaries               | Saves costs and increases performance |

Uploaded files and RAG URLs are reused across user questions during the session.

---

## 💻 Tech Stack

- **Backend**: Django, LangGraph, LangChain
- **Frontend**: HTML, Bootstrap 5, Animate.css, AOS
- **LLMs Supported**:
  - GPT-4 (OpenAI)
  - LLaMA 3 via [Groq API](https://groq.com/)
  - Mistral via API

---

## 🏗️ Project Structure

```bash
Genie/
├── agents/
│   ├── views.py          # Handles logic and session
│   ├── utils.py          # File extraction, RAG, LangGraph logic
│   └── templates/        # index.html UI
├── genie_project/
│   ├── settings.py       # Django settings
├── media/                # Uploaded files stored here
├── README.md
├── requirements.txt
└── manage.py
```

---

## ⚙️ Setup & Run

```bash
# Clone the repo
git clone https://github.com/Dara4hem/GenieAI.git
cd GenieAI

# Setup env
python -m venv venv
venv\Scripts\activate  # On Windows

# Install requirements
pip install -r requirements.txt

# Run the server
python manage.py runserver
```

> Use Groq or OpenAI API key to access LLMs.

---

## 🛡️ Smart Logic & Error Handling

- ❌ Prevent adding URLs if no model or API key is set
- ✅ Session-based summaries prevent repeated API calls
- ✅ Groq rate-limiting handled safely
- ✅ Shows alerts on invalid model/API settings
- ✅ Secure file storage and deletion

---


## 📸 Screenshots

### 🌟 Home Page (Light Mode)
![Light Mode](screenshots/1.png)

### 🌙 Home Page (Dark Mode)
![Dark Mode](screenshots/2.png)

### 📂 File Uploaded and Processed
![File Processing](screenshots/3.png)

### 🔧 Model Settings and Rules
![Model Settings](screenshots/4.png)


---

## ✍️ Author

**Mostafa Darahem**  
💼 [LinkedIn](https://www.linkedin.com/in/mostafa-darahem/)  
📧 mostafasamirdarahem@gmail.com
🌐 [GitHub](https://github.com/Dara4hem/GenieAI)

---

## 📌 Note

This repository was built to fulfill the **AI Engineer Task for Genie**, as outlined in their official email communications.

I extended the basic task into a **production-ready assistant** with extra features for usability and scalability, and I plan to build further on this framework for my own projects.

```

---

لو حابب أضيف سكريبت صغير في `README` لتجربة مشروعك بواجهة سطر الأوامر أو ملف `LICENSE` كمان، قولي أظبطهم ليك!
