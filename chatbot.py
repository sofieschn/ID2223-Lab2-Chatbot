from llama_cpp import Llama
import gradio as gr

class LLM_model():
    def __init__(self, model_path,lora_path=None, n_ctx=2048, n_threads=4, save_hist=True):
        self.llm = Llama(
            model_path = model_path,
            lora_path=lora_path,
            n_ctx=n_ctx,     # context legth
            n_threads=n_threads     # adjusted according to CPU cores
        )
        self.history_str = ''
        self.save_hist = save_hist

    # Let's develop a simple chat function
    def generate_chat_history(self,history_chat_gradio):
        conversation = ''
        for line in history_chat_gradio:
            role = line['role']
            if role == 'user':
                conversation += 'User: '
            elif role == 'assistant':
                conversation += 'Assistant: '
            conversation += line['content'][0]['text'] + '\n'
        
        return conversation


    def chat_fn(self, message):
        # Build a conversation prompt from history
        #conversation = generate_chat_history(history)
        self.history_str += f'User: {message}\nAssistant: '
        output = self.llm(self.history_str, max_tokens=256, temperature=0.7,
                    stop=['User:','Assistant:'])
        answer = output['choices'][0]['text'].strip()
        if self.save_hist:
            self.history_str += f'{answer}\n'
        else:
            self.history_str = ''
        return answer

'User: What is your name?' 'Assistant: I do not have name' 'Your name is KTH'

#demo = gr.ChatInterface(fn=chat_fn,title='Fine-tunned LLM', description='Test chat')
#app = demo

def test_lora():
    # 1. With LoRA
    model_with_lora = LLM_model(
        model_path="models/Llama-3.2-1B-Instruct-Q4_1.gguf",
        lora_path="models/lora_adapter_q8_0.gguf",
    )

    # 2. Without LoRA (pass None or remove lora_path)
    model_no_lora = LLM_model(
        model_path="models/Llama-3.2-1B-Instruct-Q4_1.gguf"
    )

    print('########')
    print('Lora model:')
    print(model_with_lora.chat_fn("Summarize: a 10 word phrase about white houses"))
    print('No lora model:')
    print(model_no_lora.chat_fn("Summarize: a 10 word phrase about white houses"))

    print('########')
    print('Lora model:')
    print(model_with_lora.chat_fn("Summarize: meaning of life in 20 words"))
    print('No lora model:')
    print(model_no_lora.chat_fn("Summarize: meaning of life in 20 words")) # type: ignore


if __name__ == '__main__':
    #test_lora()
    save_history = True
    model_path = "models/Llama-3.2-1B-Instruct-Q4_1.gguf"
    lora_path = "models/lora_adapter_q8_0_60_steps.gguf"
    model = LLM_model(model_path, lora_path, save_hist=save_history)
    while True:
        message = input('Insert your message: ')
        answer = model.chat_fn(message)
        #print(model.history_str)
        print('Answer:', answer)

    #demo.launch()
