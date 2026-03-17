#配置文件

md5_path= "md5.text"

#chroma
collection_name="rag"
persist_directory="./chroma_db"


#spliter
chunk_size=1000  #分割后文本最大长度
chunk_overlap=100 #连续文本之间的字符重叠数量
separators=["\n\n","\n",".","!","?","。","？","！",""," "]


similarity_threshold=2   #检索返回匹配的文档数量

embedding_model_name="text-embedding-v4"
chat_model_name="qwen3-max"



session_config={
    "configurable":{
        "session_id":"user_001"
        }
    }