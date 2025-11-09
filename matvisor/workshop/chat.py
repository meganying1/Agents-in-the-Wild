class Chat:
    
    def __init__(self, llm, system_prompt: str):
        self.llm = llm
        self.conversation = [
            {"role": "system", "content": system_prompt},
        ]

    def send_message(self, message: str) -> str:
        self.conversation.append({"role": "user", "content": message})
        response = self.llm.create_chat_completion(
                messages=self.conversation,
                max_tokens=500,
                temperature=0.5
            )
        result = response["choices"][0]["message"]["content"]
        self.conversation.append({"role": "assistant", "content": result})
        return result
    

if __name__ == "__main__":
    
    from matvisor.workshop.llm import load_llama

    llm = load_llama(modelsize="7")
    chat = Chat(llm, system_prompt="You are an expert materials science tutor.")

    print("--------------------------------------------------------------")

    message_1 = "Explain what ductility means in less than 5 sentences."
    print("User: " + message_1 + "\n")
    response_1 = chat.send_message(message_1)
    print("Assistant: ", response_1 + "\n")

    message_2 = "Explain how it is measured."
    print("User: " + message_2 + "\n")
    response_2 = chat.send_message(message_2)
    print("Assistant: ", response_2 + "\n")