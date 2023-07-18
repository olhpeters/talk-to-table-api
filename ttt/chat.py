from dotenv import load_dotenv
import os
import openai
import dotenv

dotenv_file = dotenv.find_dotenv()
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def chat(prompt): 
    print(f"chatting using prompt: {prompt}")
    chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])
    print(chat_completion)
    return chat_completion.choices[0].message.content