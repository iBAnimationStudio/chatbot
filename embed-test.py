from llama_cpp import Llama

llm_embed = Llama(
    model_path="models/all-MiniLM-L6-v2-ggml-model-f16.gguf",
    embedding=True,
    n_ctx=512
)

def get_embedding(text):
    return llm_embed.create_embedding(text)['data'][0]['embedding']

vec = get_embedding("test sentence")
print(len(vec))