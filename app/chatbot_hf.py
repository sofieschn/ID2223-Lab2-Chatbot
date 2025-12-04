from __future__ import annotations

from dataclasses import dataclass

from huggingface_hub import hf_hub_download
from llama_cpp import Llama


@dataclass
class ModelConfig:
    repo_id: str = "SofieSchn/kth-llama-lora"
    base_filename: str = "Llama-3.2-1B-Instruct-Q4_1.gguf"
    lora_filename: str = "lora_adapter_q8_0.gguf"
    # Smaller context & slightly more threads to be faster in constrained envs
    n_ctx: int = 1024
    n_threads: int = 4


class LLM_model:
    """
    Hugging Face-backed variant of LLM_model.
    Loads GGUF weights from SofieSchn/kth-llama-lora at startup and
    maintains its own conversation history string.
    """

    def __init__(self, config: ModelConfig | None = None):
        self.config = config or ModelConfig()

        base_model_path = hf_hub_download(
            repo_id=self.config.repo_id,
            filename=self.config.base_filename,
        )
        lora_model_path = hf_hub_download(
            repo_id=self.config.repo_id,
            filename=self.config.lora_filename,
        )

        self.llm = Llama(
            model_path=base_model_path,
            lora_path=lora_model_path,
            n_ctx=self.config.n_ctx,
            n_threads=self.config.n_threads,
        )

        # Store system prompt separately so we can reset history when needed
        self._system_prompt = (
            "System: You are a friendly KTH chatbot. "
            "Answer the user's question directly in a conversational way. "
            "Do not summarize what the user said, just respond naturally with no more than 64 words.\n"
        )
        self.history_str = self._system_prompt

    def chat_fn(self, message: str) -> str:
        """Generate a reply given the latest user message."""
        self.history_str += f"User: {message}\nAssistant: "
        output = self.llm(
            self.history_str,
            # Keep responses short to avoid timeouts on limited CPUs
            max_tokens=64,
            temperature=0.7,
            stop=["User:", "Assistant:"],
        )
        answer = output["choices"][0]["text"].strip()
        self.history_str += f"{answer}\n"
        return answer

    def reset_history(self) -> None:
        """Reset the in-memory conversation history to just the system prompt."""
        self.history_str = self._system_prompt


