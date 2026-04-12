# Just a Chat Bot

Just — A lightweight local AI runtime with memory and fast search.

---

### **Features**

- Local LLM inference (GGUF models)
- Persistent memory (SQLite)
- Fast semantic search (Rust backend)
- Configurable system behavior

---

### **Disclaimer**

This project was heavily assisted by AI-generated code.
Expect:

- weird artifacts
- occasional hallucinations
- unexpected bugs

👉 Please double check… no… triple check the code before running.

---

### **Requirements**

- Python 3.9+
- Rust (for building the search module)
- A model supported by the model runner
- llama-cpp
- (Optional) Ollama / LM Studio if replacing the model runner
- git (to clone the repo)
- wget (optional)

---

### **Setup**

1. Clone the repo

``` Bash
git clone <repo-url>
cd <repo-path>
```

---

2. Install Python dependencies

```Bash
pip install -r requirements.txt
```

(doesn’t exist yet 😅 just install "llama-cpp-python" manually for now)

---

3. Build Rust module

cd rust_search
cargo build --release
cd ..

---

4. Add models

Place your models inside:

Models/

Example:

- Llama GGUF model
- embedding model

---

5. Initialize database

python setup_db.py

---

6. Run

python main.py

---

### Configuration

Edit files in:

configs/

- "model_config.json"
- "system_config.json"

👉 Actually do this before running "main.py"

---

### Notes

- "Models/" folder is not included in the repo
- "memory.db" is generated locally
- Rust build is currently optimized for aarch64 CPUs

---

### Project Status

Experimental. Things may break. That’s part of the fun.
Don’t expect high-end stuff — it’s just a timepass 😁

---

### First Run Tip

If it crashes, it’s probably:

- missing model
- wrong config
- Rust choked
- or skill issue 😄

Check configs and logs.

---

Final Words

Use whatever model your hardware — and your sanity — can survive running 😄

---

Just don't expect this to run on a calculator* 😶‍🌫️👍
