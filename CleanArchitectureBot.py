from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import streamlit as st
import json
from openai import OpenAI
import history_init as hi


client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_db = Chroma(persist_directory="./chroma_db_nccn", embedding_function=embedding_function)

HISTORY_FILE = 'init_history.json'


def load_history():
    try:
        with open(HISTORY_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_history(history):
    with open(HISTORY_FILE, "w") as file:
        json.dump(history, file)


def interact_with_assistant(history):
    completion = client.chat.completions.create(
        model="TheBloke/Mistral-7B-Code-16K-qlora-GGUF",
        messages=history,
        temperature=0.01,
        stream=True
    )

    new_message = {"role": "assistant", "content": ""}
    for chunk in completion:
        if chunk.choices[0].delta.content:
            new_message["content"] += chunk.choices[0].delta.content

    return new_message


def main():

    if 'initialized' not in st.session_state or not st.session_state.initialized:
        hi.main()
        st.session_state.initialized = True
        history = load_history()
        interact_with_assistant(history)
        save_history(history)


    history = load_history()


    st.title("Clean Architecture Bot")
    st.markdown("Fotis, the Clean Architecture Expert")


    for message in history:
        if message["role"] == 'user':
            with st.chat_message('user'):
                st.write(message["content"])
        elif message["role"] == 'assistant':
            with st.chat_message('assistant'):
                st.write(message["content"])

    user_input = st.chat_input("Your message:", max_chars=500)
    if user_input:
        with st.chat_message('user'):
            st.write(user_input)
        search_results = vector_db.similarity_search(user_input, 3)
        some_context = ""
        for result in search_results:
            some_context += result.page_content + '\n\n'
        new_user_message = {"role": 'user', "content": some_context + user_input}
        history.append({"role": 'user', "content": user_input})

        new_message = interact_with_assistant([new_user_message])
        history.append(new_message)

        save_history(history)

        with st.chat_message('assistant'):
            st.write(new_message["content"])


if __name__ == "__main__":
    main()
