#std-lib
import time
import random
import typing

import streamlit as st


def get_llm_response(prompt: str) -> str:
    """
    Simula uma chamada de API para um Large Language Model.

    Args:
        prompt: O texto de entrada do usuário.

    Returns:
        Uma resposta de texto gerada pelo "modelo".
    """
    print(f"DEBUG: Enviando para a API (simulado): '{prompt}'")
    
    # API do Google Gemini (requer 'pip install google-generativeai')
    #
    # import google.generativeai as genai
    #
    # genai.configure(api_key="SUA_API_KEY_AQUI")
    # model = genai.GenerativeModel('gemini-pro')
    # try:
    #     response = model.generate_content(prompt)
    #     return response.text
    # except Exception as e:
    #     print(f"Ocorreu um erro na API: {e}")
    #     return "Desculpe, não consegui processar sua solicitação no momento."

    time.sleep(random.uniform(1, 2.5))
    
    mock_responses = [
        f"Esta é uma resposta simulada para a sua pergunta sobre '{prompt}'. Em um ambiente real, eu me conectaria a uma API de LLM.",
        "Processando sua solicitação... Ah, lembrei que sou apenas uma simulação! Mas se eu fosse real, daria uma resposta incrível.",
        f"Interessante você perguntar sobre '{prompt}'. O integrador de API está funcionando, mas está configurado para retornar esta mensagem de teste.",
        "Para conectar a uma API real, edite a função `get_llm_response` neste script Python. As instruções estão nos comentários do código."
    ]
    
    return random.choice(mock_responses)

st.set_page_config(page_title="Meu Gemini", page_icon="🤖")

st.title("Dakila IA")
st.caption("Interface de comunicação para a Dakila IA")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Como posso te ajudar hoje?"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Digite sua mensagem..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            response = get_llm_response(prompt)
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            st.markdown(response)