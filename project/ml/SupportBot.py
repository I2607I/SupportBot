import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings.yandex import YandexGPTEmbeddings
from langchain_community.llms import YandexGPT
from langchain.chat_models import ChatOpenAI
from sentence_transformers import CrossEncoder
from langchain_chroma import Chroma
import re
from time import sleep
from project.ml.update_token import update_token

load_dotenv()


def get_embeddings(embeddings_type: str, embeddings_name: str):
    if embeddings_type == "OPENAI":
        return OpenAIEmbeddings(model=embeddings_name)
    elif embeddings_type == "YANDEXGPT":
        update_token()
        return YandexGPTEmbeddings(model=embeddings_name, folder_id='b1gddmf03uhrco483f82')
    else:
        raise ValueError(f"Неизвестная модель эмбеддингов: {embeddings_type}")


def get_model(model_type: str, model_name: str):
    if model_type == "OPENAI":
        return ChatOpenAI(model=model_name, temperature=0)
    elif model_type == "YANDEXGPT":
        return YandexGPT(model=model_name, temperature=0, model_uri='gpt://b1gddmf03uhrco483f82/yandexgpt/latest')
    else:
        raise ValueError(f"Неизвестная модель: {model_type}")


class SupportBot:
    def __init__(self):
        self.embeddings = get_embeddings(embeddings_type=os.getenv('EMBEDDINGS_TYPE'), embeddings_name=os.getenv('EMBEDDINGS_NAME'))
        self.vector_databases = {
            "docs_context": os.getenv('MONITORING_DOCS_DB'), 
            "so_context": os.getenv('SO_DB')
            }
        self.cross_encoder_model = CrossEncoder("/app/project/ml/my_cross_encoder", max_length=512, device='cpu')
        self.llm = get_model(model_type=os.getenv('LLM_TYPE'), model_name=os.getenv('LLM_NAME'))
        self.num_retrieved_chunks = int(os.getenv('NUM_RETRIEVED_CHUNKS'))
        self.num_reranked_chunks = int(os.getenv('NUM_RERANKED_CHUNKS'))
        self.history_length = int(os.getenv('HISTORY_LENGTH'))
        with open(os.getenv('PROMPT_TEMPLATE_PATH'), 'r', encoding='utf-8') as f:
            self.prompt_template = f.read()
        with open(os.getenv('PROMPT_TEMPLATE_YES_NO'),
                  'r', encoding='utf-8') as f:
            self.prompt_template_yes_no = f.read()

    def update_model(self):
        update_token()
        self.embeddings = YandexGPTEmbeddings(model=os.getenv('EMBEDDINGS_NAME'),
                                              folder_id='b1gddmf03uhrco483f82')
        self.llm = get_model(model_type=os.getenv('LLM_TYPE'),
                             model_name=os.getenv('LLM_NAME'))

    def retrieve_from_db(self, question: str):
        retrieved_chunks = {}
        for context_source, vector_db_path in self.vector_databases.items():
            retriever = Chroma(
                persist_directory=vector_db_path,
                embedding_function=self.embeddings
                )
            retrieved_chunks[context_source] = retriever.similarity_search_with_score(question, k=self.num_retrieved_chunks)
        return retrieved_chunks
    
    def create_prompt_yes_no(self, question, chunk):
        return self.prompt_template_yes_no.format(question=question, 
                                                  chunk=chunk)

    def reranker(self, question, retrieved_chunks):
        def get_top_k(rank_result, docs):
            top_k = []
            for i in range(self.num_reranked_chunks):
                doc = rank_result[i]
                doc_id = doc['corpus_id']
                doc_score = doc['score']
                top_k.append((docs[doc_id], doc_score))
            return top_k

        chunks_to_rank = {}
        for context_source, source_chunks in retrieved_chunks.items():
            chunks_to_rank[context_source] = [chunk[0].page_content for chunk in source_chunks]
        
        chunks_scores = {}
        for context_source, source_chunks in chunks_to_rank.items():
            chunks_scores[context_source] = self.cross_encoder_model.rank(question, source_chunks)

        k_relevant_chunks = {}
        for context_source in chunks_scores.keys():
            k_relevant_chunks[context_source] = get_top_k(chunks_scores.get(context_source), chunks_to_rank.get(context_source))

        return k_relevant_chunks

    def create_prompt(self, question, history, concatenated_chunks):
        return self.prompt_template.format(question=question,
                                           history=history,
                                           **concatenated_chunks)

    def update_history(self, history, question, answer):
        pattern = r'Пользователь:\s*(.*?)\s*Бот:\s*(.*?)\s*(?=Пользователь:|$)'
        messages = re.findall(pattern, history, re.DOTALL)
        messages.append((question, answer))

        messages = messages[-self.history_length:]

        reconstructed_history = ""
        for user_question, bot_answer in messages:
            reconstructed_history += f'''Пользователь:\n{user_question.strip()}
                                         \n\nБот:\n{bot_answer.strip()}\n\n'''

        return reconstructed_history
            
    def parse_response(self, response):
        if isinstance(response, str):
            return response
        return response.content

    def qa(self, question, history):
        print('#'*100)
        print(history)
        print('#'*100)
        retrieved_chunks = self.retrieve_from_db(question=question)
        relevant_chunks = self.reranker(question=question,
                                        retrieved_chunks=retrieved_chunks)
        concatenated_chunks = {}
        for context_source, chunks_with_scores in relevant_chunks.items():
            source_whole_chunk = '\n\n'.join([chunk[0] for chunk in chunks_with_scores])
            concatenated_chunks[context_source] = source_whole_chunk

        prompt_yes_no = self.create_prompt_yes_no(question=question,
            chunk=concatenated_chunks["docs_context"])
        decision_docs = self.llm.invoke(prompt_yes_no)
        decision_docs = self.parse_response(decision_docs)
        sleep(1)

        prompt_yes_no = self.create_prompt_yes_no(question=question,
                                                  chunk=concatenated_chunks["so_context"])
        decision_so = self.llm.invoke(prompt_yes_no)
        decision_so = self.parse_response(decision_so)
        sleep(1)

        if ('да' not in decision_docs.lower() and
                'да' not in decision_so.lower()):
            prompt_yes_no = self.create_prompt_yes_no(question=question,
                                                      chunk=history)
            decision_history = self.llm.invoke(prompt_yes_no)
            decision_history = self.parse_response(decision_history)

            if 'да' not in decision_history.lower():
                return 'я не знаю', 1, history
            sleep(1)
        if 'да' not in decision_docs.lower():
            concatenated_chunks["docs_context"] = ''
        if 'да' not in decision_so.lower():
            concatenated_chunks["so_context"] = ''

        if not history:
            history = 'История сообщений пуста. Это будет первое сообщение.'
        prompt = self.create_prompt(question=question,
                                    history=history,
                                    concatenated_chunks=concatenated_chunks)

        response = self.llm.invoke(prompt)
        answer = self.parse_response(response)
        accuracy_score = 0.01
        updated_history = self.update_history(history=history,
                                              question=question, answer=answer)
        return answer, accuracy_score, updated_history
