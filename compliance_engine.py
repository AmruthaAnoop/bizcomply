import re
from typing import Dict, List, Optional
from business_profile import business_profile_manager

class ComplianceEngine:
    """AI Compliance Engine that uses business profiles for personalized responses"""
    
    def __init__(self):
        self.compliance_rules = self._load_compliance_rules()
    
    def _load_compliance_rules(self) -> Dict:
        """Load compliance rules based on business type and industry"""
        return {
            "retail": {
                "licenses": ["Business Operating License", "Seller's Permit", "Health Department Permit"],
                "taxes": ["Sales Tax Collection", "Income Tax", "Payroll Tax"],
                "filings": ["Annual Report", "Sales Tax Returns", "Business License Renewal"],
                "deadlines": ["Quarterly Sales Tax", "Annual Business Report", "License Renewal"]
            },
            "technology": {
                "licenses": ["Business Operating License", "Software License", "Data Privacy Registration"],
                "taxes": ["Income Tax", "Payroll Tax", "R&D Tax Credits"],
                "filings": ["Annual Report", "Privacy Policy Updates", "Software Compliance"],
                "deadlines": ["Annual Tax Return", "Privacy Audit", "Software License Renewal"]
            },
            "healthcare": {
                "licenses": ["Business Operating License", "Healthcare Facility License", "Medical Practice License"],
                "taxes": ["Income Tax", "Payroll Tax", "Medicare/Medicaid Tax"],
                "filings": ["HIPAA Compliance", "Annual Report", "Health Inspections"],
                "deadlines": ["HIPAA Annual Assessment", "Health Inspection", "License Renewal"]
            },
            "restaurant": {
                "licenses": ["Business Operating License", "Food Service Permit", "Liquor License (if applicable)"],
                "taxes": ["Sales Tax Collection", "Income Tax", "Payroll Tax", "Food & Beverage Tax"],
                "filings": ["Health Inspection Reports", "Food Safety Plans", "Annual Report"],
                "deadlines": ["Health Inspection", "Food Safety Training", "License Renewal"]
            },
            "consulting": {
                "licenses": ["Business Operating License", "Professional Certification (if required)"],
                "taxes": ["Income Tax", "Payroll Tax", "Self-Employment Tax"],
                "filings": ["Annual Report", "Professional Development Records"],
                "deadlines": ["Quarterly Tax Estimates", "Annual Report", "Certification Renewal"]
            }
        }
    
    def get_personalized_response(self, query: str, business_profile: Optional[Dict] = None) -> str:
        """Generate personalized compliance response based on business profile"""
        
        if not business_profile:
            return self._get_generic_response(query)
        
        # Extract business information
        business_name = business_profile.get('business_name', 'Your Business')
        industry = business_profile.get('industry', '').lower()
        business_type = business_profile.get('business_type', '')
        location = business_profile.get('location', '')
        employee_count = business_profile.get('employee_count', '')
        
        # Analyze query intent
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in ['license', 'permit', 'registration']):
            return self._get_license_response(business_name, industry, business_type, location)
        
        elif any(keyword in query_lower for keyword in ['tax', 'filing', 'return']):
            return self._get_tax_response(business_name, industry, employee_count)
        
        elif any(keyword in query_lower for keyword in ['deadline', 'due date', 'when']):
            return self._get_deadline_response(business_name, industry)
        
        elif any(keyword in query_lower for keyword in ['gdpr', 'privacy', 'data protection']):
            return self._get_privacy_response(business_name, industry, employee_count)
        
        elif any(keyword in query_lower for keyword in ['compliance', 'requirement', 'regulation']):
            return self._get_compliance_response(business_name, industry, business_type, location)
        
        else:
            return self._get_general_response(business_name, industry, business_type)
    
    def _get_generic_response(self, query: str) -> str:
        """Get generic response when no business profile is available"""
        return f"""
        <p><strong>I understand you're asking about:</strong> {query}</p>
        <p><strong>To provide you with accurate compliance guidance, I need to understand your business first.</strong></p>
        <p><strong>Please set up your business profile with:</strong></p>
        <ul>
            <li>🏢 Business name and registration number</li>
            <li>📍 Business location</li>
            <li>🏭 Industry/sector</li>
            <li>📋 Business type (LLC, corporation, etc.)</li>
            <li>👥 Employee count</li>
            <li>💰 Revenue range</li>
        </ul>
        <p>Once your business profile is set up, I can provide personalized compliance guidance!</p>
        """
    
    def _get_license_response(self, business_name: str, industry: str, business_type: str, location: str) -> str:
        """Get personalized license requirements"""
        industry_rules = self.compliance_rules.get(industry, self.compliance_rules["consulting"])
        licenses = industry_rules.get("licenses", [])
        
        return f"""
        <p><strong>License Requirements for {business_name}</strong></p>
        <p><strong>Based on your {industry} business in {location}:</strong></p>
        <ul>
            {"".join([f"<li>📋 {license}</li>" for license in licenses])}
        </ul>
        <p><strong>Additional considerations for {business_type}:</strong></p>
        <ul>
            <li>🏢 State-specific business registration</li>
            <li>📍 Local permits and zoning requirements</li>
            <li>📊 Industry-specific certifications</li>
        </ul>
        <p><em>Would you like me to help you create a license application checklist?</em></p>
        """
    
    def _get_tax_response(self, business_name: str, industry: str, employee_count: str) -> str:
        """Get personalized tax requirements"""
        industry_rules = self.compliance_rules.get(industry, self.compliance_rules["consulting"])
        taxes = industry_rules.get("taxes", [])
        
        payroll_note = ""
        if employee_count and int(employee_count.replace('+', '').replace(' employees', '').strip()) > 0:
            payroll_note = "<li>👥 Payroll tax filings and reporting</li>"
        
        return f"""
        <p><strong>Tax Compliance for {business_name}</strong></p>
        <p><strong>Your {industry} business requires:</strong></p>
        <ul>
            {"".join([f"<li>💰 {tax}</li>" for tax in taxes])}
            {payroll_note}
        </ul>
        <p><strong>Filing requirements:</strong></p>
        <ul>
            <li>📅 Quarterly estimated tax payments</li>
            <li>📊 Annual tax return</li>
            <li>🧾 Monthly/quarterly sales tax (if applicable)</li>
        </ul>
        <p><em>Would you like specific tax filing deadlines for your business?</em></p>
        """
    
    def _get_deadline_response(self, business_name: str, industry: str) -> str:
        """Get personalized deadline information"""
        industry_rules = self.compliance_rules.get(industry, self.compliance_rules["consulting"])
        deadlines = industry_rules.get("deadlines", [])
        
        return f"""
        <p><strong>Important Compliance Deadlines for {business_name}</strong></p>
        <p><strong>For your {industry} business:</strong></p>
        <ul>
            {"".join([f"<li>📅 {deadline}</li>" for deadline in deadlines])}
        </ul>
        <p><strong>General deadlines for all businesses:</strong></p>
        <ul>
            <li>📊 April 15 - Annual tax return</li>
            <li>🏢 Annual report filing (varies by state)</li>
            <li>📋 Business license renewal (annual/biennial)</li>
        </ul>
        <p><em>Would you like me to create a personalized compliance calendar?</em></p>
        """
    
    def _get_privacy_response(self, business_name: str, industry: str, employee_count: str) -> str:
        """Get privacy compliance response"""
        gdpr_required = "Yes" if industry in ["technology", "consulting"] else "Depends on customer base"
        
        return f"""
        <p><strong>Privacy Compliance for {business_name}</strong></p>
        <p><strong>GDPR Requirements: {gdpr_required}</strong></p>
        <ul>
            <li>🔒 Data protection officer (if >250 employees)</li>
            <li>📋 Privacy policy and consent forms</li>
            <li>🔐 Data breach notification procedures</li>
            <li>📊 Data processing records</li>
        </ul>
        <p><strong>Additional privacy considerations:</strong></p>
        <ul>
            <li>🏢 CCPA compliance (if serving California customers)</li>
            <li>🔍 Industry-specific data regulations</li>
            <li>📝 Employee data privacy policies</li>
        </ul>
        <p><em>Would you like help creating a privacy compliance checklist?</em></p>
        """
    
    def _get_compliance_response(self, business_name: str, industry: str, business_type: str, location: str) -> str:
        """Get general compliance response"""
        industry_rules = self.compliance_rules.get(industry, self.compliance_rules["consulting"])
        filings = industry_rules.get("filings", [])
        
        return f"""
        <p><strong>Compliance Requirements for {business_name}</strong></p>
        <p><strong>As a {business_type} in the {industry} sector in {location}:</strong></p>
        <ul>
            {"".join([f"<li>📝 {filing}</li>" for filing in filings])}
        </ul>
        <p><strong>Ongoing compliance activities:</strong></p>
        <ul>
            <li>📊 Record keeping and documentation</li>
            <li>🔍 Regular compliance audits</li>
            <li>📅 Staff training on regulations</li>
            <li>🏢 Industry-specific monitoring</li>
        </ul>
        <p><em>Would you like a detailed compliance plan for your business?</em></p>
        """
    
    def _get_general_response(self, business_name: str, industry: str, business_type: str) -> str:
        """Get general business guidance"""
        return f"""
        <p><strong>Welcome, {business_name}!</strong></p>
        <p><strong>Your {business_type} in the {industry} sector</strong> has specific compliance needs.</p>
        <p><strong>I can help you with:</strong></p>
        <ul>
            <li>📋 Industry-specific licenses and permits</li>
            <li>💰 Tax registration and filing requirements</li>
            <li>📝 Compliance deadlines and forms</li>
            <li>🔍 Regulatory requirements for your sector</li>
            <li>📅 Important filing dates</li>
        </ul>
        <p><strong>Ask me about any specific compliance topic and I'll provide personalized guidance!</strong></p>
        """
    
    def extract_business_info_from_text(self, text: str) -> Dict:
        """Extract business information from user text"""
        info = {}
        
        # Business name patterns
        name_patterns = [
            r'(?:my business|our company|we are|i have|business name is)\s+([A-Za-z0-9\s&]+?)(?:\.|,|\s|$)',
            r'([A-Za-z0-9\s&]+?)(?:\.|,|\s|$)(?:is my|is our|business|company)',
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info['business_name'] = match.group(1).strip()
                break
        
        # Industry patterns
        industries = ["retail", "technology", "healthcare", "restaurant", "consulting", "manufacturing", "construction"]
        for industry in industries:
            if industry in text.lower():
                info['industry'] = industry
                break
        
        # Business type patterns
        business_types = ["llc", "corporation", "sole proprietorship", "partnership", "s-corp", "c-corp"]
        for btype in business_types:
            if btype in text.lower():
                info['business_type'] = btype
                break
        
        # Location patterns
        location_patterns = [
            r'(?:in|located in|based in)\s+([A-Za-z\s]+?)(?:\.|,|\s|$)',
            r'([A-Za-z\s]+?)(?:\.|,|\s|$)(?:state|city|location)',
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and len(match.group(1).strip()) > 2:
                info['location'] = match.group(1).strip()
                break
        
        return info

# Global instance
compliance_engine = ComplianceEngine()
