from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.messages.chat import ChatMessage
import streamlit as st
import time
import requests
import json

url = "https://api.dai.tec.br/chat/v1/chats"

class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text)

# Pega chae de API
with st.sidebar:
    dai_api_key = st.text_input("Dai API Key", type="password")
    dai_api_id = st.text_input("Numero do Cliente")

# Inicia a primeira msg quando starta o chat
if "messages" not in st.session_state:
    st.session_state["messages"] = [ChatMessage(role="assistant", content="Envie sua primeira mensagem")]

# printa todas as msg de novo no chat
for msg in st.session_state.messages:
    print("content msg passou - ", msg.content)
    st.chat_message(msg.role).write(msg.content)

if prompt := st.chat_input():
    st.session_state.messages.append(ChatMessage(role="user", content=prompt))
    st.chat_message("user").write(prompt)
    

    if not dai_api_key:
        st.info("Insira sua Dai API key para continuar.")
        st.stop()

    with st.chat_message("assistant"):
        
        print("Manda pra orquestradora - ",prompt)

        ## MAAAAANDA MSG PRA DAI        
        payload = json.dumps({
            "username": "Playground",
            "message": prompt,
            "messageServiceId": dai_api_id
        })
        headers = {
        'Content-Type': 'application/json',
        'x-api-key': dai_api_key
        }
        
        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200:
            jsonResponse = json.loads(response.text)
            resposta = jsonResponse['response']
            for element in jsonResponse['commands']:
                if element['params'] is None:
                    resposta += ' \<CMD:' + element['name'] + '\> '
                else:
                    resposta += ' \<CMD:' + element['name'] + ':' + element['params'] + '\> '
        else:
            resposta = "Ops, algo deu errado:" + response.text 
            
        print(resposta)
        ## dai_api_key CHAVE DA APIIII

        stream_handler = StreamHandler(st.empty())
        
        
        
        for text in list(resposta):
            stream_handler.on_llm_new_token(text.replace("$", "\$"))
            time.sleep(0.01)
        
        st.session_state.messages.append(ChatMessage(role="assistant", content=resposta))
