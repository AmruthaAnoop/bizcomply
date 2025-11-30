# Test direct search for the 2019 startup file

from bot_engine import get_compliance_answer

# Test more specific queries about the 2019 update
test_questions = [
    "What is the startup turnover limit according to G.S.R. 127(E) 2019?",
    "DPIIT notification 2019 startup definition turnover limit",
    "Startup turnover limit 100 crore",
    "G.S.R. 127(E) turnover limit"
]

for i, question in enumerate(test_questions, 1):
    print(f"\n🔍 Test {i}: {question}")
    print("-" * 40)
    
    result = get_compliance_answer(question)
    
    # Check if answer contains the correct information
    answer = result['result'].lower()
    if "100 crore" in answer:
        print("✅ Found correct ₹100 Crore information!")
    elif "25 crore" in answer and "100 crore" not in answer:
        print("❌ Still showing outdated ₹25 Crore information")
    else:
        print("⚠️ Unclear answer")
    
    print(f"Sources found: {len(result['source_documents'])}")
    
    # Check if the 2019 file is in the sources
    found_2019_file = False
    for doc in result['source_documents']:
        if 'startup_definition_update_2019.txt' in doc.metadata.get('source', ''):
            found_2019_file = True
            print("✅ 2019 file found in sources!")
            break
    
    if not found_2019_file:
        print("❌ 2019 file not found in sources")

print("\n" + "=" * 60)
