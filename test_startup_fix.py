# Test the cleaned system for the critical startup question

from bot_engine import get_compliance_answer

# Test the problematic question
question = "What is the annual turnover limit for a Startup to get tax benefits? Is it 25 Crore?"

print("🔍 Testing Cleaned System - Startup Definition")
print("=" * 60)
print(f"Question: {question}")
print("-" * 40)

result = get_compliance_answer(question)

print(f"Answer: {result['result']}")
print(f"Sources found: {len(result['source_documents'])}")

if result['source_documents']:
    print("\n📚 Source Documents:")
    for i, doc in enumerate(result['source_documents'][:3], 1):
        print(f"{i}. {doc.metadata.get('source', 'Unknown')}")
        content_preview = doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
        print(f"   Preview: {content_preview}")

print("=" * 60)
