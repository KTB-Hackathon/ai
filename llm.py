from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_upstage import UpstageEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_upstage import ChatUpstage
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI


store = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]






def get_llm():
  llm = ChatOpenAI(model='gpt-4o')
  return llm

def get_retriever():
  embedding = UpstageEmbeddings(model="solar-embedding-1-large")
  index_name = 'journey-mate'
  database = PineconeVectorStore.from_existing_index(index_name=index_name, embedding=embedding)
  retriever = database.as_retriever(search_kwargs={'k': 4})
  return retriever


def get_dictionary_chain():
    
    dictionary = ["""
          
                      
                  """]
    llm = get_llm()

    prompt = ChatPromptTemplate.from_template(f"""
        한국어로 답변해주세요.
        사용자의 질문을 보고, 사전을 참고하여 비슷한 양식으로 답변을 생성해주세요.
        답변에 포함되어야할 내용은 다음과 같습니다.                            
                                              
        관광코스 또한 제작하여 제공합니다. 
        관광코스는 세개가 넘어도 됩니다.    
        지금까지 선택한 관광지를 종합하여 관광코스를 제작하여 제공합니다.
        최근에 선택한 관광지일 수록 나중에 방문합니다.
        관광 코스에 포함되는 관광지는 모두 사용자의 질문에 포함된 관광지만으로 이루어집니다.                                                                                          
                                
        사전: {dictionary}
        
        질문: {{question}}
    """)

    dictionary_chain = prompt | llm | StrOutputParser()
    return dictionary_chain


def get_rag_chain():
  llm = get_llm()
  retriever = get_retriever()

  contextualize_q_system_prompt = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, "
    "just reformulate it if needed and otherwise return it as is."
    "다음 추천되는 세곳의 관광지는 모두 이전 선택관광지에서 30분 거리에 있어야합니다."
    "입력된 관광지가 있다면, 다음 추천되는 곳까지 이동시간을 알려주세요."
    "관광코스를 제공할때는, 히스토리에서 지금까지 선택한 관광지를 모두 포함하여 제공합니다."
  )

  contextualize_q_prompt = ChatPromptTemplate.from_messages(
      [
          ("system", contextualize_q_system_prompt),
          MessagesPlaceholder("chat_history"),
          ("human", "{input}"),
      ]
  )

  history_aware_retriever = create_history_aware_retriever(
      llm, retriever, contextualize_q_prompt
  )

  system_prompt = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer "
    "the question. If you don't know the answer, say that you "
    "\n\n"
    "{context}"
  )
  qa_prompt = ChatPromptTemplate.from_messages(
      [
          ("system", system_prompt),
          MessagesPlaceholder("chat_history"),
          ("human", "{input}"),
      ]
  )
  question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

  rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

  conversational_rag_chain = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
  )
  
  return conversational_rag_chain

def get_ai_message(user_message):
    dictionary_chain = get_dictionary_chain()
    rag_chain = get_rag_chain()

    tax_chain = {"input": dictionary_chain} | rag_chain
    ai_message = tax_chain.invoke(
        {
          'question': user_message
        },
        config={
          "configurable": {"session_id": "abc123"}
        },
    )

    # ai_message = qa_chain.invoke({"query": user_message})
    return ai_message['answer']