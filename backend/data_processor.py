import pandas as pd
import numpy as np
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
import os
from typing import List, Dict
import torch
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm

class DataProcessor:
    def __init__(self):
        # 使用相对路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.law_data_path = os.path.join(current_dir, 'law_data_3k.csv')
        self.law_qa_path = os.path.join(current_dir, 'law_QA.csv')
        self.embeddings_dir = os.path.join(current_dir, 'embeddings')
        
        # 创建embeddings目录
        os.makedirs(self.embeddings_dir, exist_ok=True)
        
        # 加载数据
        print("正在加载数据...")
        try:
            self.law_data = pd.read_csv(self.law_data_path)
            self.law_qa = pd.read_csv(self.law_qa_path)
            print(f"数据加载完成。法律条文数量：{len(self.law_data)}，问答数据数量：{len(self.law_qa)}")
        except Exception as e:
            print(f"加载数据文件失败: {str(e)}")
            raise
        
        # 初始化文本嵌入模型
        print("正在加载文本嵌入模型...")
        self.text_embedding = pipeline(
            Tasks.sentence_embedding,
            model='damo/nlp_corom_sentence-embedding_chinese-base',
            model_revision='v1.0.0'
        )
        print("模型加载完成")
        
        # 尝试加载已有的嵌入向量
        self.law_data_embeddings = self.load_embeddings('law_data_embeddings.npy')
        self.law_qa_embeddings = self.load_embeddings('law_qa_embeddings.npy')
        
        # 如果没有找到嵌入向量文件，则重新计算
        if self.law_data_embeddings is None or self.law_qa_embeddings is None:
            print("未找到预计算的嵌入向量，开始计算...")
            self.compute_and_save_embeddings()
    
    def load_embeddings(self, filename):
        """加载嵌入向量"""
        filepath = os.path.join(self.embeddings_dir, filename)
        if os.path.exists(filepath):
            print(f"加载嵌入向量: {filename}")
            return np.load(filepath)
        return None
    
    def save_embeddings(self, embeddings, filename):
        """保存嵌入向量"""
        filepath = os.path.join(self.embeddings_dir, filename)
        np.save(filepath, embeddings)
        print(f"嵌入向量已保存: {filename}")
    
    def compute_and_save_embeddings(self):
        """计算并保存嵌入向量"""
        # 计算法律条文的嵌入向量
        print("计算法律条文嵌入向量...")
        self.law_data_embeddings = []
        for _, row in tqdm(self.law_data.iterrows(), total=len(self.law_data), desc="计算法律条文嵌入"):
            result = self.text_embedding({'source_sentence': [row['data']]})
            embedding = result['text_embedding']
            self.law_data_embeddings.append(embedding)
        self.law_data_embeddings = np.array(self.law_data_embeddings)
        self.save_embeddings(self.law_data_embeddings, 'law_data_embeddings.npy')
        
        # 计算问答数据的嵌入向量
        print("计算问答数据嵌入向量...")
        self.law_qa_embeddings = []
        for _, row in tqdm(self.law_qa.iterrows(), total=len(self.law_qa), desc="计算问答数据嵌入"):
            result = self.text_embedding({'source_sentence': [row['data']]})
            embedding = result['text_embedding']
            self.law_qa_embeddings.append(embedding)
        self.law_qa_embeddings = np.array(self.law_qa_embeddings)
        self.save_embeddings(self.law_qa_embeddings, 'law_qa_embeddings.npy')
        
        print("所有嵌入向量计算完成")

    def find_relevant_cases(self, query, law_top_k=3, qa_top_k=3, similarity_threshold=0.3):
        """
        查找与查询最相关的案例
        :param query: 用户查询
        :param law_top_k: 返回的法条数量
        :param qa_top_k: 返回的问答数量
        :param similarity_threshold: 相似度阈值
        :return: 相关案例列表
        """
        # 计算查询的嵌入向量
        query_result = self.text_embedding({'source_sentence': [query]})
        query_embedding = np.array(query_result['text_embedding']).reshape(1, -1)
        
        # 确保法律条文嵌入向量的维度正确
        if len(self.law_data_embeddings.shape) == 3:
            self.law_data_embeddings = self.law_data_embeddings.squeeze(1)
        if len(self.law_qa_embeddings.shape) == 3:
            self.law_qa_embeddings = self.law_qa_embeddings.squeeze(1)
        
        # 计算与法律条文的相似度
        law_similarities = cosine_similarity(query_embedding, self.law_data_embeddings)[0]
        # 筛选相似度高于阈值的案例
        law_mask = law_similarities > similarity_threshold
        law_indices = np.where(law_mask)[0]
        # 如果有满足条件的案例，取law_top_k个最相关的
        if len(law_indices) > 0:
            law_indices = law_indices[np.argsort(law_similarities[law_indices])[-law_top_k:][::-1]]
        
        # 计算与问答数据的相似度
        qa_similarities = cosine_similarity(query_embedding, self.law_qa_embeddings)[0]
        # 筛选相似度高于阈值的问答
        qa_mask = qa_similarities > similarity_threshold
        qa_indices = np.where(qa_mask)[0]
        # 如果有满足条件的问答，取qa_top_k个最相关的
        if len(qa_indices) > 0:
            qa_indices = qa_indices[np.argsort(qa_similarities[qa_indices])[-qa_top_k:][::-1]]
        
        # 获取相关案例
        relevant_laws = []
        if len(law_indices) > 0:
            relevant_laws = self.law_data.iloc[law_indices]['data'].tolist()
        
        relevant_qas = []
        if len(qa_indices) > 0:
            relevant_qas = self.law_qa.iloc[qa_indices]['data'].tolist()
        
        # 合并结果并标记来源
        results = []
        for i, law in enumerate(relevant_laws, 1):
            results.append(f"[法条{i}] {law}")
        for i, qa in enumerate(relevant_qas, 1):
            results.append(f"[问答{i}] {qa}")
        
        return results

# 单例模式
_data_processor = None

def get_data_processor():
    global _data_processor
    if _data_processor is None:
        _data_processor = DataProcessor()
    return _data_processor 