import os
from langchain_community.llms import Ollama
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import OllamaEmbeddings 
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

model_name = "llamafamily/llama3-chinese-8b-instruct"
file_path = "C:\\Users\\User\\Documents\\work\\tcm-agent\\data\\txt"

system_prompt = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer "
    "the question. If you don't know the answer, say that you "
    "don't know. Use five sentences maximum and keep the "
    "answer concise. Answer in Chinese."
    "\n\n"
    "{context}"
)

llm = Ollama(model=model_name,temperature=0.2,top_p=0.3)
embedding= OllamaEmbeddings(model=model_name,temperature=0.2,top_p=0.3)
# loader = TextLoader("C:\\Users\\User\\Downloads\\中醫體質與問診.txt")
# loader = TextLoader("C:\\Users\\User\\Downloads\\九大體質.txt")


class RagChain:
    def __init__(self,llm, embedding,file_name,system_prompt) -> None:
        self.llm = llm
        self.embedding = embedding
        # self.system_prompt = system_prompt
        
        total_path = os.path.normpath(f"{file_path}/{file_name}")
        self.loader = TextLoader(total_path,encoding='utf-8')
        self.docs = self.loader.load()
        
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        self.splits = self.text_splitter.split_documents(self.docs)
        self.vector_store = Chroma.from_documents(documents= self.splits, embedding= embedding)
        self.retriever = self.vector_store.as_retriever()
        
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{input}"),
            ]
        )
        
        self.question_answer_chain = create_stuff_documents_chain(self.llm, self.prompt)
        self.rag_chain = create_retrieval_chain(self.retriever, self.question_answer_chain)
            
    def __call__(self, input_data):
        return self.rag_chain.invoke(input_data)

    
# 中醫十問
ZhongyiShiwen = RagChain(llm, embedding, "中醫十問.txt", system_prompt)   
# 九大體質
JiudaTizhi = RagChain(llm, embedding, "九大體質.txt", system_prompt) 
SelfIntroduction = RagChain(llm, embedding, "自我介紹.txt", system_prompt)  
SongBieYu = RagChain(llm, embedding, "送別語.txt", system_prompt)  



# response_1 = ZhongyiShiwen({"input": "based on knowledge。請按照＂自我介紹.txt＂文件做自我介紹"})
# print(response_1['answer'])

# response_2 = JiudaTizhi({"input": "based on knowledge。請分析文件，中醫十問是哪十問?請告訴我問診名稱就好。"})
# print(response_2['answer'])

# response_3 = SelfIntroduction({"input": "based on knowledge。請分析文件中有提到以下描述嗎?如果沒有請回答不知道，如果有，這是哪一種體質?\n- - -\n常見表現特徵為手腳冰冷、臉色蒼白、身體畏寒、喜歡吃溫熱飲食。容易發生水腫、腹瀉大便不成形，易表現出精神不濟，容易感冒。體態上呈現肌肉鬆軟不結實，舌頭胖大、舌苔變厚呈白色水滑。"})
# print(response_3['answer'])


# response_4 = SongBieYu({"input": "based on knowledge。請參考＂送別語.txt＂文件做送別的話語"})
# print(response_4['answer'])