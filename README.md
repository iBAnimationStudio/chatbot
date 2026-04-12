# just a chat bot

### Jaus A lightweight local AI runtime with memory and fast search.

---

**Features**

- Local LLM inference (GGUF models)
- Persistent memory (SQLite)
- Fast semantic search (Rust backend)
- Configurable system behavior

---

**Disclaimer**

This project was heavily assisted by AI-generated code.
Expect:

- weird artifacts
- occasional hallucinations
- unexpected bugs

👉 Please double check... no... triple check! code before running.

---

**Requirements**

- Python 3.9+
- Rust (for building the search module)
- A supported GGUF model
- llama-cpp
- optinal ollama if you replace the model runner

---

**Setup**

1. Clone the repo

``` Bash
git clone <repo-url>
cd <repo path>
```

2. Install Python dependencies

``` Bash
pip install -r requirements.txt
```
(dosenot exist 😅 lust install these for now -> llama-cpp rust python git and sqlit3 if not installed.)

3. Build Rust module

``` Bash
cd rust_search
cargo build --release
cd ..
```

4. Add models

Place your models inside:

Models/

Example:

- Llama GGUF model
- embedding model

---

5. Initialize database

``` Bash
python setup_db.py
```

---

6. Run

``` Bash 
python main.py
```

---

**Configuration**

Edit files in:

configs/

- "model_config.json"
- "system_config.json"
(Do it before running the main.py)

---

**Notes**

- "Models/" folder is not included in the repo
- "memory.db" is generated locally
- Rust build is currently optimized for aarch64 CPUs

---

**Project Status**

Experimental. Things may break. That’s part of the fun.
don't expect hi-end stuff it just a timepass 😁.

---

## First Run Tip
If it crashes, it’s probably:
- missing model
- wrong config
- rust choked 
- or skill issue 😄

Check configs and logs.

---

**Final Words**

Use whatever model your hardware and your sanity can survive running 😄
