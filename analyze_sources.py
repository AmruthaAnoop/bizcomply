# Check what documents are actually being found for startup queries

from bot_engine import get_compliance_answer

question = "What is the startup turnover limit according to G.S.R. 127(E) 2019?"
result = get_compliance_answer(question)

print("🔍 Document Analysis for Startup Query")
print("=" * 60)
print(f"Question: {question}")
print(f"Answer: {result['result'][:300]}...")
print(f"\nSources found: {len(result['source_documents'])}")

print("\n📚 All Source Documents:")
for i, doc in enumerate(result['source_documents'], 1):
    source_name = doc.metadata.get('source', 'Unknown')
    print(f"{i}. {source_name}")
    
    # Check if this document contains startup information
    content_lower = doc.page_content.lower()
    if any(keyword in content_lower for keyword in ['startup', '100 crore', 'gs.r. 127', 'dpiit']):
        print(f"   ✅ Contains startup info")
        # Show relevant snippet
        content_snippet = doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content
        print(f"   Preview: {content_snippet}")
    else:
        print(f"   ❌ No startup info")

print("=" * 60)
