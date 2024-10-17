# SIN FUNCIONAR, EN PROCESO EN BORRADOR


import getpass
import os
import glob
from langchain import hub
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI

os.environ["OPENAI_API_KEY"] = getpass.getpass()

llm = ChatOpenAI(model="gpt-4o-mini")

# Function to load text files from a directory
def load_texts_from_directory(directory):
    text_files = glob.glob(os.path.join(directory, "*.txt"))
    documents = []
    for file_path in text_files:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            documents.append(content)
    return documents

# Load documents from the specified folders
transcriptions = load_texts_from_directory("Data Formated/Transcriptions")
descriptions = load_texts_from_directory("Data Formated/Descriptions")
comments = load_texts_from_directory("Data Formated/Comments")

# Combine all documents
all_docs = transcriptions + descriptions + comments

# Split the documents into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(all_docs)
vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())

# Retrieve and generate using the relevant snippets of the documents
retriever = vectorstore.as_retriever()
prompt = hub.pull("rlm/rag-prompt")

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

rag_chain.invoke("What is Task Decomposition?")