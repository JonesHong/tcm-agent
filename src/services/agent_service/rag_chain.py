# import logger
import __init__
import os
from langchain_community.llms import Ollama
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import OllamaEmbeddings 
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

from src.utils.log import logger
from src.utils.config.manager import ConfigManager

# logger.basicConfig(level=logger.INFO)
config = ConfigManager()
agent_config = config.agent
model_name = agent_config.model_name
DATA_TXT_DIR = os.path.join(__init__.SRC_DIR,"data",'txt')
# logger.info(DATA_TXT_DIR)
# file_path = "C:\\Users\\User\\Documents\\work\\tcm-agent\\data\\txt"

system_prompt = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer "
    "the question. If you don't know the answer, say that you "
    "don't know. Use five sentences maximum and keep the "
    "answer concise. Answer in Chinese."
    "\n\n"
    "{context}"
)

try:
    llm = Ollama(model=model_name, temperature=0.2, top_p=0.3)
    embedding = OllamaEmbeddings(model=model_name, temperature=0.2, top_p=0.3)
except Exception as e:
    logger.error(f"Failed to initialize LLM or Embeddings: {e}")
    raise
# loader = TextLoader("C:\\Users\\User\\Downloads\\中醫體質與問診.txt")
# loader = TextLoader("C:\\Users\\User\\Downloads\\九大體質.txt")


class RagChain:
    def __init__(self,llm, embedding,file_name,system_prompt) -> None:
        self.llm = llm
        self.embedding = embedding
        # self.system_prompt = system_prompt
        
        total_path = os.path.normpath(f"{DATA_TXT_DIR}/{file_name}")
        try:
            self.loader = TextLoader(total_path, encoding='utf-8')
            self.docs = self.loader.load()
        except Exception as e:
            logger.error(f"Failed to load documents from {total_path}: {e}")
            raise
        
        try:
            self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            self.splits = self.text_splitter.split_documents(self.docs)
            self.vector_store = Chroma.from_documents(documents=self.splits, embedding=embedding)
            self.retriever = self.vector_store.as_retriever()
        except Exception as e:
            logger.error(f"Failed to split documents or initialize vector store: {e}")
            raise
        
        try:
            self.prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", system_prompt),
                    ("human", "{input}"),
                ]
            )
        
            self.question_answer_chain = create_stuff_documents_chain(self.llm, self.prompt)
            self.rag_chain = create_retrieval_chain(self.retriever, self.question_answer_chain)
        except Exception as e:
            logger.error(f"Failed to create chains: {e}")
            raise
        
    def __call__(self, input_data):
        try:
            return self.rag_chain.invoke(input_data)
        except Exception as e:
            logger.info(f"An error occurred: {e}")
            return {"answer": "發生錯誤，請稍後再試。"}

# 中醫十問
try:
    ZhongyiShiwen = RagChain(llm, embedding, "中醫十問.txt", system_prompt)
except Exception as e:
    logger.error(f"Failed to initialize ZhongyiShiwen RAG chain: {e}")

# 九大體質
try:
    JiudaTizhi = RagChain(llm, embedding, "九大體質.txt", system_prompt)
except Exception as e:
    logger.error(f"Failed to initialize JiudaTizhi RAG chain: {e}")
# SelfIntroduction = RagChain(llm, embedding, "自我介紹.txt", system_prompt)  
# SongBieYu = RagChain(llm, embedding, "送別語.txt", system_prompt)  

