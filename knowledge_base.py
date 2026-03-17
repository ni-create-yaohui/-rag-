"""
知识库
"""
import os

from datetime import datetime
import config_data as config
from config_data import md5_path
import hashlib
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

def check_md5(md5_str:str):
    #检查传入的MD5字符串是否已经被处理过了
    #return false（未被处理过），true（被处理过有记录）
    if not os.path.exists(md5_path): #第一次运行文件不存在要进行的操作
          open(config.md5_path,'w',encoding='utf-8').close() # 创建文件
          return False
    else:
        for line in open(config.md5_path,'r',encoding='utf-8').readlines():
            line=line.strip()  #处理字符串前后的空格和回车
            if line==md5_str:
                return True
        return  False

def save_md5(md5_str:str):
    #将传入的md5字符串记录到文件内部保存
    with open(config.md5_path,'a',encoding='utf-8') as f:
        f.write(md5_str+'\n')


def get_string_md5(input_str:str,encoding='utf-8'):
    #将传入的字符串转为MD5字符串

    #将字符串转为bytes字节数组
    str_bytes=input_str.encode(encoding=encoding)
    #创建md5对象
    md5_obj = hashlib.md5()# 得到md5对象
    md5_obj.update(str_bytes) #更新内容（传入即将要转换的字节数组）
    md5_hex=md5_obj.hexdigest()  #得到md5十六进制字符串
    return md5_hex

class KnowledgeBaseService(object):

    def __init__(self):
        #如果文件夹不存在则创建
        os.makedirs(config.persist_directory,exist_ok=True)
        self.chroma= Chroma(collection_name=config.collection_name,    #数据库表名
        embedding_function=DashScopeEmbeddings(model="text-embedding-v4"),
        persist_directory=config.persist_directory, #数据库本地存储文件夹
        )
        #向量存储的实例chroma向量库对象
        self.spliter=RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,  #分割后文本段的最大长度
            chunk_overlap=config.chunk_overlap, #连续文本之间的字符重叠数量
            separators=config.separators,        #自然段落划分符号
            length_function=len,          #用python自带的len函数长度统计的依据
        ) #文本分割器的对象

    def upload_by_str(self,data:str,filename):
        #将传入的字符串向量化存入向量数据库中
        #先得到MD5值
        md5_hex=get_string_md5(data)

        if check_md5(md5_hex):
            return "内容已存在于知识库中[跳过]"

        if len(data)>config.chunk_size:
            kowledge_chunks:list[str]=self.spliter.split_text(data)
        else:
            kowledge_chunks=[data]

        metadata={
            "source":filename,
            #改成常用的时间形式
            "create_time":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operator":"汐汐"
        }
        self.chroma.add_texts(
            kowledge_chunks,
            metadatas=[metadata for _ in kowledge_chunks],# 通过列表推导式组装列表每一份元素
        )

        save_md5(md5_hex)
        return "[成功]，内容已经成功载入向量库"

