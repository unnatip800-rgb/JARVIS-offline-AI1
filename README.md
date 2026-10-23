# JARVIS — Offline AI Assistant

JARVIS is a privacy-focused AI assistant designed to run locally on a Windows computer using Ollama and the Llama 3.2 3B language model. It provides AI chat, PDF question answering, persistent memory, study assistance, coding support, and local utility tools.

## Features

- **Offline AI chat:** Chat locally with Llama 3.2 3B through Ollama.
- **PDF question answering:** Ask questions about supported PDF documents.
- **Persistent memory:** Save and manage selected memories using SQLite.
- **Study tools:** Use AI-assisted study features.
- **Coding assistant:** Get coding help.
- **Local utilities:** Access supported calculator, date/time, system information, and file information tools.
- **Local web interface:** Use the assistant through a browser on your own computer.

## Technology Stack

- Python
- Ollama
- Llama 3.2 3B
- Streamlit
- SQLite
- Requests
- PDF-processing and retrieval libraries listed in `requirements.txt`

## Prerequisites

- Windows
- A compatible Python installation
- Ollama installed
- The `llama3.2:3b` model downloaded through Ollama
- Dependencies listed in `requirements.txt`

## Installation

### 1. Install Ollama

Install Ollama from https://ollama.com/.

### 2. Download the model

Open Command Prompt and run:

```bash
ollama pull llama3.2:3b
```

Ensure Ollama is running before starting JARVIS.

### 3. Install Python dependencies

Open Command Prompt in the project directory and run:

```bash
python -m pip install -r requirements.txt
```

### 4. Start JARVIS

**Windows quick start:** Double-click `jarvis.bat`.

**Alternative — run from Command Prompt:**

```bash
python -m streamlit run app.py --server.address=127.0.0.1 --server.port=8501
```

Open http://127.0.0.1:8501 in your browser if it does not open automatically.

## Sample Run

1. Start JARVIS.
2. Enter a message such as: `Explain how Python functions work.`
3. Submit the message and review the response.
4. Try uploading a supported PDF and asking a question about its contents.
5. Test the memory, study, coding, and local utility features available in the interface.

## Offline Operation

After Python dependencies, Ollama, and the language model have been installed or downloaded, JARVIS is designed to run locally without requiring an internet connection for its core AI features. Initial setup and downloads require internet access. Some optional features may have additional requirements.

## Model and Dataset

JARVIS uses the pretrained Llama 3.2 3B model through Ollama. The project does not currently claim custom model training or fine-tuning. User-provided PDF documents and locally stored memories can supply additional context at runtime.

## Privacy

Conversation history and saved memories are stored locally using SQLite. Do not upload personal databases, private documents, credentials, or other sensitive information to a public repository.

## Testing Status

Core features have undergone initial functional testing. Formal accuracy benchmarks and standardized performance evaluations have not yet been established.

## Limitations

- Responses may contain errors and should be verified when accuracy is important.
- Performance depends on the computer's hardware and available memory.
- Supported features depend on the installed dependencies and local configuration.

## Team Members

|   Team Member    | Roll Number |               Role               |
| Prajapati Unnati | 254081      | Project Lead and Integration     |
| Chaudhary Sejal  | 256006      | AI Model Integration             |
| Rajput Karishma  | 254088      | Python Backend Development       |
| Prajapati Niki   | 252042      | Memory and PDF Processing        |
| Vyas Vishwa      | 254115      | UI/UX, Testing and Documentation |

