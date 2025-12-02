from llama_cpp import Llama
from huggingface_hub import hf_hub_download

class LLM_model:
    def __init__(
        self,
        repo_id: str = "SofieSchn/kth-llama-lora",
        model_filename: str = "Llama-3.2-1B-Instruct-Q4_1.gguf",
        lora_filename: str = "lora_adapter_q8_0.gguf",
        n_ctx: int = 2048,
        n_threads: int = 4,
    ):
        # Ladda ner modellerna från Hugging Face om de inte finns lokalt
        base_model_path = hf_hub_download(repo_id=repo_id, filename=model_filename)
        lora_model_path = hf_hub_download(repo_id=repo_id, filename=lora_filename)

        self.llm = Llama(
            model_path=base_model_path,
            lora_path=lora_model_path,
            n_ctx=n_ctx,
            n_threads=n_threads,
        )
        self.history_str = (
            "System: You are a friendly KTH chatbot. "
            "Answer the user's question directly in a conversational way. "
            "Do not summarize what the user said, just respond naturally.\n"
        )

    def chat_fn(self, message):
        self.history_str += f"User: {message}\nAssistant: "
        output = self.llm(
            self.history_str,
            max_tokens=256,
            temperature=0.7,
            stop=["User:", "Assistant:"],
        )
        answer = output["choices"][0]["text"].strip()
        self.history_str += f"{answer}\n"
        return answer