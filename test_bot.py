# Save this as test_bot.py
from bot_engine import get_compliance_answer

def test_collateral_limits():
    """Test if bot knows the 2025 Credit Limits"""
    print("Testing: Collateral Free Limits (2025)...")
    
    response = get_compliance_answer(
        "What is the maximum limit for collateral-free loans for Micro and Small Enterprises?"
    )['result']
    
    # The Rubric: It passes only if it mentions these specific details
    assert "10 Lakh" in response, "Failed: Missed RBI mandatory limit"
    assert "10 Crore" in response, "Failed: Missed new CGTMSE limit"
    assert "April 1, 2025" in response, "Failed: Missed CGTMSE effective date"
    
    print("✅ PASS: Collateral Limits are accurate.")

def test_opc_exemptions():
    """Test if bot knows One Person Company rules"""
    print("Testing: OPC Exemptions...")
    
    response = get_compliance_answer(
        "Does a One Person Company need to hold an AGM?"
    )['result']
    
    # It must say 'No' or 'Exempt'
    assert "exempt" in response.lower() or "no" in response.lower(), "Failed: Did not confirm AGM exemption"
    
    print("✅ PASS: OPC Rules are accurate.")

def test_llp_audit_requirements():
    """Test if bot correctly cites LLP Act for LLP questions"""
    print("Testing: LLP Audit Requirements (Citation Test)...")
    
    response = get_compliance_answer(
        "Does my LLP need to get accounts audited if turnover is ₹35 Lakhs?"
    )['result']
    
    # Must cite LLP Act, not Companies Act
    assert "Limited Liability Partnership Act, 2008" in response, "Failed: Should cite LLP Act, not Companies Act"
    assert "Companies Act" not in response, "Failed: Should not cite Companies Act for LLP questions"
    assert "not required" in response.lower() or "no audit" in response.lower(), "Failed: Should say LLP doesn't need audit at ₹35L"
    
    print("✅ PASS: LLP citations are correct.")

def test_holiday_work_compensation():
    """Test if bot correctly distinguishes working on holidays vs paid holidays"""
    print("Testing: Holiday Work Compensation (Double Wages Test)...")
    
    response = get_compliance_answer(
        "What should I pay if an employee works on Republic Day in Delhi?"
    )['result']
    
    # Must mention double wages or 200% pay
    assert "double" in response.lower() or "200%" in response or "twice" in response.lower(), "Failed: Should mention double wages for holiday work"
    
    # Should distinguish between working vs not working
    assert "working on" in response.lower() or "provides labor" in response.lower(), "Failed: Should distinguish between working vs taking holiday off"
    
    # Should mention the correct compensation for working (not just normal pay)
    assert "200%" in response or "double wages" in response.lower(), "Failed: Should emphasize double wages for working on holidays"
    
    print("✅ PASS: Holiday work compensation is correct.")

def test_section_447():
    """Test if bot knows fraud punishment details"""
    print("Testing: Section 447 Fraud Punishment...")
    
    response = get_compliance_answer(
        "What is the punishment for fraud under Section 447?"
    )['result']
    
    # Must include both minimum and maximum penalties
    assert "six months" in response.lower(), "Failed: Missed minimum imprisonment"
    assert "ten years" in response.lower(), "Failed: Missed maximum imprisonment"
    
    print("✅ PASS: Section 447 details are accurate.")

if __name__ == "__main__":
    try:
        test_collateral_limits()
        test_opc_exemptions()
        test_llp_audit_requirements()
        test_holiday_work_compensation()
        test_section_447()
        print("\n🎉 ALL SYSTEMS GO: Your Legal Bot is smarter than most consultants!")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
