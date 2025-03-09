import pandas as pd
import numpy as np
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
import os

class RAGProcessor:
    def __init__(self):
        # 设置数据文件路径
        self.law_data_path = os.path.join(os.path.dirname(__file__), '../RAG_tutorial/实验三/law_data_3k.csv')
        self.law_qa_path = os.path.join(os.path.dirname(__file__), '../RAG_tutorial/实验三/law_QA.csv')
        
        # 加载数据
        self.law_data = pd.read_csv(self.law_data_path)
        self.law_qa = pd.read_csv(self.law_qa_path)
        
        # 初始化文本嵌入模型
        self.text_embedding = pipeline(
            Tasks.sentence_embedding,
            model='damo/nlp_corom_sentence-embedding_chinese-base',
            model_revision='v1.0.0'
        )
        
        # 预计算所有案例的嵌入
        print("正在计算案例嵌入...")
        self.case_embeddings = []
        for _, row in self.law_data.iterrows():
            embedding = self.text_embedding(row['content'])['text_embedding']
            self.case_embeddings.append(embedding)
        self.case_embeddings = np.array(self.case_embeddings)
        print(f"完成案例嵌入计算，共 {len(self.case_embeddings)} 个案例")

    def find_relevant_cases(self, query, top_k=3):
        # 计算查询的嵌入
        query_embedding = self.text_embedding(query)['text_embedding']
        
        # 计算相似度
        similarities = np.dot(self.case_embeddings, query_embedding) / (
            np.linalg.norm(self.case_embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # 获取最相关的案例
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        relevant_cases = []
        
        for idx in top_indices:
            case = self.law_data.iloc[idx]
            relevant_cases.append({
                'title': case['title'],
                'content': case['content'],
                'similarity': float(similarities[idx])
            })
        
        return relevant_cases

    def enhance_prompt(self, query):
        relevant_cases = self.find_relevant_cases(query)
        enhanced_prompt = f"用户问题: {query}\n\n相关案例参考:\n"
        
        for i, case in enumerate(relevant_cases, 1):
            enhanced_prompt += f"\n案例 {i}:\n标题: {case['title']}\n内容: {case['content']}\n"
            
        enhanced_prompt += "\n请根据以上案例，专业地回答用户的问题。回答时要引用相关案例作为依据。"
        return enhanced_prompt

# 单例模式
_rag_processor = None

def get_rag_processor():
    global _rag_processor
    if _rag_processor is None:
        _rag_processor = RAGProcessor()
    return _rag_processor 