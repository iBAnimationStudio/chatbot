import json, sqlite3, subprocess, re, os
from llama_cpp import Llama
from functools import lru_cache

# ---------------- CONFIG ----------------
system_cfg = json.load(open("configs/system_config.json"))
model_cfg = json.load(open("configs/model_config.json"))

# ---------------- MODELS ----------------
llm_chat = Llama(
    model_path=model_cfg["chat_model_path"],
    n_ctx=model_cfg["n_ctx"],
    n_threads=model_cfg["n_threads"],
    n_gpu_layers=model_cfg["n_gpu_layers"],
    verbose=False
)

llm_embed = Llama(
    model_path=model_cfg["embedding_model_path"],
    embedding=True,
    n_ctx=512,
    verbose=False
)

# ---------------- DB ----------------
conn = sqlite3.connect("memory.db", check_same_thread=False)

# ---------------- EMBEDDING CACHE ----------------
@lru_cache(maxsize=1000)
def _embed_cached(text: str):
    return tuple(llm_embed.create_embedding(text)['data'][0]['embedding'])

def get_embedding(text: str):
    return list(_embed_cached(text))

# ---------------- RUST SEARCH ----------------
def rust_search(vec, db_path, limit=3, threshold=0.6):
    bin_path = "./rust_search/target/release/rust_search"

    proc = subprocess.run(
        [bin_path, "search", json.dumps(vec), str(limit), db_path, str(threshold)],
        capture_output=True,
        text=True
    )

    if proc.returncode != 0:
        print("\n[Search Error]", proc.stderr)
        return []

    try:
        return json.loads(proc.stdout)
    except:
        return []

# ---------------- MEMORY OPS ----------------
def save_memory(text, vec, importance=0.5):
    if len(text.split()) < 3:
        return

    conn.execute(
        "INSERT INTO memory (content, embedding, importance) VALUES (?, ?, ?)",
        (text.strip(), json.dumps(vec), importance)
    )
    conn.commit()

def update_memory(mem_id):
    conn.execute("""
    UPDATE memory
    SET accesses = accesses + 1,
        importance = MIN(importance + 0.02, 1.0),
        last_accessed = CURRENT_TIMESTAMP
    WHERE id = ?
    """, (mem_id,))
    conn.commit()

def delete_memory(mem_id):
    conn.execute("DELETE FROM memory WHERE id = ?", (mem_id,))
    conn.commit()

# ---------------- COMMANDS ----------------
CMD_SEARCH = re.compile(r'<m_s>"query: (.*?)"</m_s>')
CMD_WRITE  = re.compile(r'<m_w>"write: (.*?)"</m_w>')
CMD_DELETE = re.compile(r'<m_dl>"delete: (\d+)"</m_dl>')

def execute_commands(response: str):
    executed = False

    # WRITE
    for m in CMD_WRITE.finditer(response):
        raw = m.group(1)

        # optional importance parsing (e.g. "(0.9) text")
        imp_match = re.match(r'\((0\.\d+|1\.0)\)\s*(.*)', raw)
        if imp_match:
            importance = float(imp_match.group(1))
            text = imp_match.group(2)
        else:
            importance = 0.5
            text = raw

        save_memory(text, get_embedding(text), importance)
        executed = True

    # DELETE
    for m in CMD_DELETE.finditer(response):
        delete_memory(int(m.group(1)))
        executed = True

    return executed

# ---------------- FORMAT MEMORY ----------------
def format_memory(results):
    if not results:
        return ""

    lines = [
        f"- (ID:{r['id']} | imp:{r['importance']:.2f}) {r['content']}"
        for r in results
    ]

    return "\n[RELEVANT MEMORY]\n" + "\n".join(lines) + "\n[/RELEVANT MEMORY]\n"

# ---------------- MAIN LOOP ----------------
history = [{"role": "system", "content": system_cfg["system_prompt"]}]
db_path = os.path.abspath("memory.db")

print("🧠 Agent v2.5 Ready")

while True:
    user_input = input("\nUser: ").strip()
    if user_input.lower() == "exit":
        break

    query = user_input
    final_response = ""

    # -------- AGENT LOOP (max 2 passes) --------
    for _ in range(2):

        vec = get_embedding(query)
        results = rust_search(vec, db_path, limit=3, threshold=0.6)

        for r in results:
            update_memory(r["id"])

        memory_context = format_memory(results)

        # Prompt (trim history)
        recent = history[-4:]

        prompt = f"<s>[INST] <<SYS>>\n{system_cfg['system_prompt']}\n{memory_context}<</SYS>>\n\n"

        for msg in recent:
            if msg["role"] == "user":
                prompt += f"{msg['content']} [/INST] "
            else:
                prompt += f"{msg['content']} </s><s>[INST] "

        prompt += f"{query} [/INST]"

        # -------- GENERATE --------
        response = ""

        print("Assistant:", end=" ", flush=True)

        for token in llm_chat(prompt, max_tokens=512, stream=True, echo=False):
            txt = token["choices"][0]["text"]
            print(txt, end="", flush=True)
            response += txt

        print()

        # -------- SEARCH LOOP --------
        match = CMD_SEARCH.search(response)
        if match:
            query = match.group(1)
            continue

        final_response = response
        break

    # -------- EXECUTE COMMANDS --------
    execute_commands(final_response)

    # -------- UPDATE HISTORY --------
    history.append({"role": "user", "content": user_input})
    history.append({"role": "assistant", "content": final_response})