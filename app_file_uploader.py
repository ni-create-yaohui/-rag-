import time

import streamlit as st
from knowledge_base import KnowledgeBaseService

#添加网页标题
st.title("知识库更新服务")

#初始化服务
if "service" not in st.session_state:
    st.session_state["service"]=KnowledgeBaseService()

#文件上传服务
uploader_file =st.file_uploader(
    "请上传TXT文件",
     type=['txt'],
    accept_multiple_files = False,  #仅接受一个文件的上传
)

if uploader_file is not None:
    #接收文件成功，提取文件信息
    file_name=uploader_file.name
    file_type=uploader_file.type
    file_size=uploader_file.size/1024  #KB

    st.subheader(f"文件名:{file_name}") #网页子标题
    st.write(f"格式:{file_type} |  大小:{file_size :.2f}KB") #网页文本

    # 获取文件内容->bytes->decode('utf-8')
    text=uploader_file.getvalue().decode("utf-8")#得到字节数组并编为字符串


    with st.spinner("载入知识库中。。。"):   #给予加载动画避免过快导致用户没反应过来
        time.sleep(1)
        result=st.session_state["service"].upload_by_str(text,file_name)
        st.write(result)

# 分隔线
st.divider()

# ============ 文件管理区域 ============
st.header("文件管理")

# 显示已有文件列表
files_info = st.session_state["service"].list_files()

if files_info:
    st.subheader("已上传的文件")

    # 创建表格显示文件信息
    for filename, info in files_info.items():
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

            with col1:
                st.write(f"**{filename}**")
            with col2:
                st.write(f"文档数: {info['count']}")
            with col3:
                st.write(f"创建时间: {info['create_time']}")
            with col4:
                # 删除按钮
                if st.button("🗑️", key=f"del_{filename}"):
                    with st.spinner(f"正在删除 {filename}..."):
                        result = st.session_state["service"].delete_by_filename(filename)
                        st.success(result)
                        st.rerun()  # 刷新页面

            st.divider()
else:
    st.info("暂无上传的文件")


