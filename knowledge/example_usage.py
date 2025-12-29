# example_usage.py
# 知识库使用示例

"""
知识库使用示例脚本

演示如何使用知识库构建器和检索器
"""

from knowledge_builder import KnowledgeBaseBuilder
from knowledge_retriever import get_retriever


def example_build():
    """示例：构建知识库"""
    print("=" * 60)
    print("示例1: 构建知识库")
    print("=" * 60)
    
    builder = KnowledgeBaseBuilder()
    
    # 构建所有知识库
    results = builder.build_all_knowledge(chunk_method="paragraph")
    
    print(f"\n构建结果:")
    for dept, success in results.items():
        status = "✅ 成功" if success else "❌ 失败"
        print(f"  {dept}: {status}")


def example_retrieve():
    """示例：检索知识"""
    print("\n" + "=" * 60)
    print("示例2: 检索知识")
    print("=" * 60)
    
    retriever = get_retriever()
    
    # 获取可用科室
    departments = retriever.get_available_departments()
    print(f"\n可用的科室知识库: {departments}")
    
    if not departments:
        print("⚠️  没有可用的知识库，请先运行构建脚本")
        return
    
    # 测试检索
    test_queries = [
        "诊疗规范",
        "质控要求",
        "病历书写规范"
    ]
    
    for query in test_queries:
        print(f"\n查询: '{query}'")
        print("-" * 60)
        
        # 从第一个可用科室检索
        results = retriever.retrieve_by_department(
            query=query,
            department_name=departments[0],
            top_k=3
        )
        
        if results:
            print(f"找到 {len(results)} 个结果:")
            for idx, result in enumerate(results, 1):
                print(f"\n结果 {idx}:")
                print(f"  相似度: {result['similarity']:.3f}")
                print(f"  内容: {result['content'][:100]}...")
                print(f"  来源: {result['metadata'].get('source', '未知')}")
        else:
            print("未找到相关结果")


def example_format_for_llm():
    """示例：格式化结果用于 LLM"""
    print("\n" + "=" * 60)
    print("示例3: 格式化结果用于 LLM")
    print("=" * 60)
    
    retriever = get_retriever()
    departments = retriever.get_available_departments()
    
    if not departments:
        print("⚠️  没有可用的知识库")
        return
    
    query = "诊疗规范要求"
    results = retriever.retrieve_by_department(
        query=query,
        department_name=departments[0],
        top_k=3
    )
    
    # 格式化结果
    formatted_text = retriever.format_results_for_llm(results)
    
    print(f"\n查询: '{query}'")
    print("\n格式化后的文本（可用于 LLM 输入）:")
    print("-" * 60)
    print(formatted_text)


def example_meta_info():
    """示例：查看元数据信息"""
    print("\n" + "=" * 60)
    print("示例4: 查看元数据信息")
    print("=" * 60)
    
    builder = KnowledgeBaseBuilder()
    meta = builder.get_meta_info()
    
    if meta:
        import json
        print("\n知识库元数据:")
        print(json.dumps(meta, ensure_ascii=False, indent=2))
    else:
        print("暂无元数据信息")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        action = sys.argv[1]
        if action == "build":
            example_build()
        elif action == "retrieve":
            example_retrieve()
        elif action == "format":
            example_format_for_llm()
        elif action == "meta":
            example_meta_info()
        else:
            print(f"未知操作: {action}")
            print("可用操作: build, retrieve, format, meta")
    else:
        # 运行所有示例
        print("运行所有示例...\n")
        
        # 注意：构建操作可能需要较长时间，默认跳过
        # example_build()
        
        example_retrieve()
        example_format_for_llm()
        example_meta_info()

