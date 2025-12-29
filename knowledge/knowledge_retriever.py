# knowledge_retriever.py
# 知识库检索器

import os
from pathlib import Path
from typing import List, Dict, Optional, Union
from langchain_chroma import Chroma
try:
    from knowledge_config import KNOWLEDGE_CONFIG
    from knowledge_builder import get_embeddings
except ImportError:
    # 如果直接运行脚本，使用相对导入
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from knowledge_config import KNOWLEDGE_CONFIG
    from knowledge_builder import get_embeddings


class KnowledgeRetriever:
    """知识库检索器"""
    
    def __init__(self):
        self.chroma_dir = Path(KNOWLEDGE_CONFIG["chroma_dir"])
        self.embeddings = get_embeddings()
        self.vectorstores = {}  # 缓存已加载的向量库
        self.meta_index = self._load_meta_index()
    
    def _load_meta_index(self) -> Dict:
        """加载元数据索引"""
        meta_file = Path(KNOWLEDGE_CONFIG["meta_file"])
        if meta_file.exists():
            try:
                import json
                with open(meta_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  加载元数据索引失败: {e}")
        return {}
    
    def _load_vectorstore(self, department_name: str) -> Optional[Chroma]:
        """
        加载指定科室的向量库（懒加载，带缓存）
        
        Args:
            department_name: 科室名称
        
        Returns:
            Chroma 向量库实例，如果不存在则返回 None
        """
        # 检查缓存
        if department_name in self.vectorstores:
            return self.vectorstores[department_name]
        
        # 检查向量库是否存在
        persist_dir = self.chroma_dir / "department" / department_name
        
        if not persist_dir.exists():
            return None
        
        try:
            vectorstore = Chroma(
                persist_directory=str(persist_dir),
                embedding_function=self.embeddings,
                collection_metadata=KNOWLEDGE_CONFIG["collection_metadata"]
            )
            # 缓存
            self.vectorstores[department_name] = vectorstore
            return vectorstore
        except Exception as e:
            print(f"❌ 加载向量库失败 {persist_dir}: {e}")
            return None
    
    def retrieve_by_department(
        self, 
        query: str, 
        department_name: str, 
        top_k: Optional[int] = None,
        filter_dict: Optional[Dict] = None
    ) -> List[Dict]:
        """
        从指定科室的知识库检索
        
        Args:
            query: 查询文本
            department_name: 科室名称
            top_k: 返回结果数量，默认使用配置值
            filter_dict: 可选的过滤条件（Chroma metadata filter）
        
        Returns:
            List[Dict]: 检索结果列表，每个结果包含：
                - content: 文本内容
                - score: 距离分数（越小越相似）
                - similarity: 相似度（1 - score，越大越相似）
                - metadata: 元数据
        """
        top_k = top_k or KNOWLEDGE_CONFIG["default_top_k"]
        
        vectorstore = self._load_vectorstore(department_name)
        if not vectorstore:
            print(f"⚠️  向量库不存在: {department_name}")
            return []
        
        try:
            # 执行检索
            results = vectorstore.similarity_search_with_score(
                query,
                k=top_k,
                filter=filter_dict
            )
            
            # 格式化结果
            formatted_results = []
            for doc, distance in results:
                similarity = 1 - distance  # 转换为相似度（0-1）
                
                # 应用相似度阈值过滤（可选）
                threshold = KNOWLEDGE_CONFIG.get("similarity_threshold", 0)
                if similarity < threshold:
                    continue
                
                formatted_results.append({
                    "content": doc.page_content,
                    "score": distance,
                    "similarity": similarity,
                    "metadata": doc.metadata
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"❌ 检索失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def retrieve_all(
        self, 
        query: str, 
        top_k: Optional[int] = None,
        filter_dict: Optional[Dict] = None
    ) -> List[Dict]:
        """
        从所有知识库检索并合并结果
        
        Args:
            query: 查询文本
            top_k: 每个知识库返回的结果数量
            filter_dict: 可选的过滤条件
        
        Returns:
            List[Dict]: 合并后的检索结果，按相似度排序
        """
        top_k = top_k or KNOWLEDGE_CONFIG["default_top_k"]
        all_results = []
        
        # 遍历所有已构建的知识库
        for department_name in self.meta_index.keys():
            results = self.retrieve_by_department(
                query, 
                department_name, 
                top_k=top_k,
                filter_dict=filter_dict
            )
            all_results.extend(results)
        
        # 按相似度排序
        all_results.sort(key=lambda x: x["similarity"], reverse=True)
        
        # 返回前 top_k 个结果
        return all_results[:top_k]
    
    def retrieve_general(
        self, 
        query: str, 
        top_k: Optional[int] = None
    ) -> List[Dict]:
        """
        从通用知识库检索（预留接口）
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
        
        Returns:
            List[Dict]: 检索结果列表
        """
        # TODO: 实现通用知识库检索
        # 目前返回空列表
        return []
    
    def get_available_departments(self) -> List[str]:
        """获取所有可用的科室列表"""
        return list(self.meta_index.keys())
    
    def get_department_info(self, department_name: str) -> Optional[Dict]:
        """获取指定科室的元数据信息"""
        return self.meta_index.get(department_name)
    
    def format_results_for_llm(self, results: List[Dict]) -> str:
        """
        将检索结果格式化为适合 LLM 输入的文本
        
        Args:
            results: 检索结果列表
        
        Returns:
            str: 格式化后的文本
        """
        if not results:
            return "未检索到相关知识。"
        
        formatted_lines = []
        for idx, result in enumerate(results, 1):
            content = result["content"]
            similarity = result["similarity"]
            metadata = result.get("metadata", {})
            source = metadata.get("source", "未知来源")
            
            formatted_lines.append(
                f"【知识片段 {idx}】（来源：{source}，相似度：{similarity:.2f}）\n{content}\n"
            )
        
        return "\n".join(formatted_lines)


# 全局检索器实例（单例模式，避免重复加载向量库）
_retriever_instance = None

def get_retriever() -> KnowledgeRetriever:
    """获取检索器实例（单例模式）"""
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = KnowledgeRetriever()
    return _retriever_instance


if __name__ == "__main__":
    # 测试代码
    retriever = get_retriever()
    
    print("可用的科室知识库:")
    departments = retriever.get_available_departments()
    for dept in departments:
        info = retriever.get_department_info(dept)
        print(f"  - {dept}: {info.get('chunk_count', 0)} 个知识片段")
    
    if departments:
        print(f"\n测试检索（科室: {departments[0]}）:")
        query = "诊疗规范"
        results = retriever.retrieve_by_department(query, departments[0], top_k=3)
        
        print(f"查询: {query}")
        print(f"找到 {len(results)} 个结果:\n")
        
        for idx, result in enumerate(results, 1):
            print(f"结果 {idx} (相似度: {result['similarity']:.3f}):")
            print(f"  {result['content'][:100]}...")
            print()

