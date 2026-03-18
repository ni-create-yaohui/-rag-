from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory, RunnableLambda
from file_history_store import get_history
from vector_stores import VectorStoresService
from langchain_community.embeddings import DashScopeEmbeddings
import config_data as config
from langchain_core.prompts import ChatPromptTemplate ,MessagesPlaceholder
from langchain_community.chat_models.tongyi import ChatTongyi


def print_prompt(prompt):
    print("="*20)
    print(prompt.to_string())
    print("="*20)
    return prompt

class Ragservice(object):
    def __init__(self):
        self.vector_service = VectorStoresService(
            embedding=DashScopeEmbeddings(model=config.embedding_model_name),
        )

        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", """你是一个专业助手，必须严格按照以下规则回答：

        核心规则：
        1. 仅基于我提供的参考资料回答，不得使用预训练知识或联网搜索
        2. 参考资料：{context}
        3. 你有权限访问历史对话记录，可以参考之前的对话内容
        4. 如果参考资料中没有相关信息，必须明确告知用户"根据提供的资料无法找到相关信息"
        5. 仅允许有限度的编造、推测或使用预训练知识回答
        6. 回答要简洁、专业、客观

        禁止行为：
        - 可以使用你预训练的知识补全用户的问题
        - 不得说"根据我的知识"或"我知道"
        - 可以少量生成未在参考资料中存在的内容帮助回答用户在参考资料中有涉及到的问题
        - 不得假设或推测信息"""),
                ("system","并且我提供用户的对话历史记录，如下："),
                MessagesPlaceholder ("history"),
                ("user","请回答用户提问:{input}")
            ]
        )

        self.chat_model=ChatTongyi(model=config.chat_model_name)

        self.chain=self._get_chain()



    def _get_chain(self):
        #获取最终的执行连
        retriever=self.vector_service.get_retriever()

        def format_document(docs:list[Document]):
            if not docs:
                return "无相关参考资料"

            formatted_str=""
            for doc in docs:
                formatted_str+=f"文档片段:{doc.page_content}\n 文档元数据:{doc.metadata}\n\n"

            return formatted_str

        def format_for_retriever(value:dict)->str:
            return  value["input"]

        def format_for_prompt_template(value) :
            new_value={}
            new_value["input"]=value["input"]["input"]
            new_value["context"]=value["context"]
            new_value["history"]=value["input"]["history"]
            return new_value

        chain=(
            {
                "input":RunnablePassthrough(),
                "context":RunnableLambda(format_for_retriever)|retriever|format_document
            }|RunnableLambda(format_for_prompt_template)|self.prompt_template|print_prompt |self.chat_model|StrOutputParser()
        )
        conversation_chain=RunnableWithMessageHistory(
            chain,
            get_history,
            input_messages_key="input",
            history_messages_key="history",
        )
        return conversation_chain

if __name__=="__main__":
    #session id 配置
    session_config={
        "configurable":{
            "session_id":"user_001"
        }
    }
    res=Ragservice().chain.invoke({"input":"身高185cm，春天穿什么颜色的衣服"},session_config)
    print(res)