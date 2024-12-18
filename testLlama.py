from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

model = OllamaLLM(model="llama3.2:latest")

template = """
Answer the question below.

Here is the conversation history: {context}

Here is the next question: {question}

Answer:
"""


res = model.invoke("hey llamma")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

def handleChat():
  context = ""
  while True:
    userInput = input("You: ")
    if userInput.lower() == "exit":
      break

    res = chain.invoke({"context":context,
                        "question":userInput})
    print("Bot: ",res)
    context += f"\nUser: {userInput}\nAI: {res}"

if __name__ == "__main__":
  handleChat()