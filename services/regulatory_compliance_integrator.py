"""
Regulatory Compliance Integrator

This service connects the regulatory monitoring system with the compliance engine,
analyzing regulatory updates and mapping them to relevant compliance requirements.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import re
from sqlalchemy.orm import Session

from models.compliance import ComplianceRequirement, BusinessCompliance, ComplianceCheckpoint
from models.compliance_engine import ComplianceEngine
from services.regulatory_monitor import RegulatoryUpdate, RegulatoryMonitor
from models.business import Business

logger = logging.getLogger(__name__)

class RegulatoryComplianceIntegrator:
    """
    Integrates regulatory updates with the compliance management system.
    
    This service analyzes regulatory updates and maps them to relevant compliance
    requirements, creating or updating them as needed.
    """
    
    def __init__(self, db_session: Session, regulatory_monitor: Optional[RegulatoryMonitor] = None):
        """Initialize the integrator with a database session and optional regulatory monitor."""
        self.db = db_session
        self.regulatory_monitor = regulatory_monitor or RegulatoryMonitor()
        self.compliance_engine = ComplianceEngine()
    
    async def process_new_updates(self, business_id: str = None) -> List[Dict[str, Any]]:
        """
        Process new regulatory updates and map them to compliance requirements.
        
        Args:
            business_id: Optional business ID to filter updates for specific business
            
        Returns:
            List of created/updated compliance requirements
        """
        # Get unprocessed regulatory updates
        updates = await self.regulatory_monitor.get_updates(processed=False)
        
        results = []
        for update in updates:
            try:
                # Analyze impact on requirements
                impacted_requirements = await self.analyze_impact(update, business_id)
                
                # Update or create compliance requirements
                for req_data in impacted_requirements:
                    requirement = self.update_or_create_requirement(req_data)
                    
                    # Create checkpoints for affected businesses
                    self.create_compliance_checkpoints(requirement, update)
                    
                    results.append({
                        'update_id': update.id,
                        'requirement_id': requirement.id,
                        'action': 'created' if req_data.get('is_new') else 'updated',
                        'businesses_affected': len(req_data.get('business_ids', []))
                    })
                
                # Mark update as processed
                await self.regulatory_monitor.mark_as_processed(update.id)
                
            except Exception as e:
                logger.error(f"Error processing regulatory update {update.id}: {str(e)}", 
                            exc_info=True)
        
        return results
    
    async def analyze_impact(self, update: RegulatoryUpdate, business_id: str = None) -> List[Dict[str, Any]]:
        """
        Analyze the impact of a regulatory update on compliance requirements.
        
        Args:
            update: The regulatory update to analyze
            business_id: Optional business ID to filter impact analysis
            
        Returns:
            List of requirement data dictionaries with impact details
        """
        # Extract key information from the update
        content = f"{update.title} {update.summary} {json.dumps(update.metadata)}"
        # Identify affected jurisdictions and categories
        jurisdictions = self._extract_jurisdictions(content)
        categories = self._identify_categories(content)
        
        # Find affected businesses if not specified
        if business_id:
            businesses = [self.db.query(Business).get(business_id)]
        else:
            businesses = self._find_affected_businesses(jurisdictions, categories)
        
        # Map to compliance requirements
        requirements = []
        for business in businesses:
            # Check if this affects existing requirements
            existing_reqs = self._find_related_requirements(business.id, jurisdictions, categories)
            
            if existing_reqs:
                # Update existing requirements
                for req in existing_reqs:
                    requirements.append(self._update_existing_requirement(req, update))
            else:
                # Create new requirement
                requirements.append(self._create_new_requirement(update, business, jurisdictions, categories))
        
        return requirements
    
    def _extract_jurisdictions(self, content: str) -> List[Dict[str, str]]:
        """Extract jurisdiction information from update content."""
        # This is a simplified example - in practice, you'd use NLP or more sophisticated pattern matching
        jurisdictions = []
        
        # Look for country/state codes
        country_pattern = r'\b(?:USA|UK|EU|IN|CA|AU|JP|CN|DE|FR|IT|ES|BR|MX)\b'
        state_pattern = r'\b(?:CA|NY|TX|FL|ON|BC|NSW|VIC|MH|KA|TN|UP|MH|GJ|RJ|AP|TS|WB|MP|PB|HR|KA|TN|KL|OR|AS|BR|JH|UK|HP|JK|GA|NL|MN|ML|TR|AR|MZ|NL|SK|LD|AN|PY|CH|DD|DN|DL|LD)\b'
        
        countries = set(re.findall(country_pattern, content, re.IGNORECASE))
        states = set(re.findall(state_pattern, content, re.IGNORECASE))
        
        for country in countries:
            jurisdictions.append({
                'type': 'country',
                'code': country.upper(),
                'name': self._get_country_name(country)
            })
        
        for state in states:
            jurisdictions.append({
                'type': 'state',
                'code': state.upper(),
                'name': self._get_state_name(state)
            })
        
        return jurisdictions
    
    def _identify_categories(self, content: str) -> List[str]:
        """Identify compliance categories from update content."""
        categories = set()
        
        # Map keywords to categories
        category_keywords = {
            'tax': ['tax', 'irs', 'gst', 'vat', 'withholding'],
            'employment': ['labor', 'employment', 'wage', 'benefits', 'leave'],
            'privacy': ['gdpr', 'privacy', 'data protection', 'ccpa'],
            'environmental': ['environment', 'emission', 'sustainability', 'waste'],
            'safety': ['safety', 'osha', 'health and safety', 'workplace safety']
        }
        
        content_lower = content.lower()
        for category, keywords in category_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                categories.add(category)
        
        return list(categories)
    
    def _find_affected_businesses(self, jurisdictions: List[Dict], categories: List[str]):
        """Find businesses affected by the regulatory update."""
        query = self.db.query(Business)
        
        # Filter by jurisdiction
        jurisdiction_codes = [j['code'] for j in jurisdictions]
        if jurisdiction_codes:
            query = query.filter(
                (Business.jurisdiction.in_(jurisdiction_codes)) |
                (Business.operating_countries.any(jurisdiction_codes))
            )
        
        # Filter by business category/industry if categories are identified
        if categories:
            query = query.filter(Business.industry.in_(categories))
        
        return query.all()
    
    def _find_related_requirements(self, business_id: str, jurisdictions: List[Dict], categories: List[str]):
        """Find existing compliance requirements related to the update."""
        query = self.db.query(ComplianceRequirement)\
            .join(BusinessCompliance)\
            .filter(BusinessCompliance.business_id == business_id)
        
        # Filter by jurisdiction
        jurisdiction_codes = [j['code'] for j in jurisdictions]
        if jurisdiction_codes:
            query = query.filter(ComplianceRequirement.jurisdiction_code.in_(jurisdiction_codes))
        
        # Filter by category
        if categories:
            query = query.filter(ComplianceRequirement.category.in_(categories))
        
        return query.all()
    
    def _update_existing_requirement(self, requirement: ComplianceRequirement, update: RegulatoryUpdate) -> Dict:
        """Update an existing compliance requirement based on regulatory update."""
        # Update the requirement based on the update
        requirement.description = f"{requirement.description}\n\nUpdate from {update.published}: {update.summary}"
        requirement.last_updated = datetime.utcnow()
        requirement.next_check_due = requirement.get_next_check_date()
        
        # Update risk score if needed
        if 'high' in update.summary.lower() or 'critical' in update.summary.lower():
            requirement.severity = 'high'
            requirement.risk_score = requirement.calculate_risk_score()
        
        self.db.commit()
        
        return {
            'id': requirement.id,
            'name': requirement.name,
            'is_new': False,
            'business_ids': [bc.business_id for bc in requirement.business_compliances]
        }
    
    def _create_new_requirement(self, update: RegulatoryUpdate, business: Business, 
                              jurisdictions: List[Dict], categories: List[str]) -> Dict:
        """Create a new compliance requirement from a regulatory update."""
        # Create a new requirement
        requirement = ComplianceRequirement(
            id=str(uuid.uuid4()),
            name=f"Regulatory Update: {update.title[:100]}",
            description=update.summary,
            category=categories[0] if categories else 'regulatory',
            subcategory=update.source,
            regulation_id=f"REG-{update.id}",
            regulation_name=update.title,
            regulation_url=update.link,
            jurisdiction_type='country',
            jurisdiction_code=jurisdictions[0]['code'] if jurisdictions else 'GLOBAL',
            jurisdiction_name=jurisdictions[0].get('name') if jurisdictions else 'Global',
            frequency='one_time',
            severity='medium',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.db.add(requirement)
        self.db.commit()
        
        # Create business compliance record
        business_compliance = BusinessCompliance(
            id=str(uuid.uuid4()),
            business_id=business.id,
            requirement_id=requirement.id,
            status='not_started',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.db.add(business_compliance)
        self.db.commit()
        
        return {
            'id': requirement.id,
            'name': requirement.name,
            'is_new': True,
            'business_ids': [business.id]
        }
    
    def create_compliance_checkpoints(self, requirement: ComplianceRequirement, update: RegulatoryUpdate) -> None:
        """Create compliance checkpoints for affected businesses."""
        for bc in requirement.business_compliances:
            checkpoint = ComplianceCheckpoint(
                id=str(uuid.uuid4()),
                business_compliance_id=bc.id,
                checkpoint_type='regulatory_update',
                status='pending_review',
                notes=f"New regulatory update: {update.title}",
                due_date=datetime.utcnow() + timedelta(days=30),  # 30 days to review
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.db.add(checkpoint)
        
        self.db.commit()
    
    def _get_country_name(self, code: str) -> str:
        """Get country name from code."""
        countries = {
            'US': 'United States',
            'UK': 'United Kingdom',
            'IN': 'India',
            'CA': 'Canada',
            'AU': 'Australia',
            'JP': 'Japan',
            'CN': 'China',
            'DE': 'Germany',
            'FR': 'France',
            'IT': 'Italy',
            'ES': 'Spain',
            'BR': 'Brazil',
            'MX': 'Mexico'
        }
        return countries.get(code.upper(), code)
    
    def _get_state_name(self, code: str) -> str:
        """Get state name from code."""
        states = {
            'CA': 'California',
            'NY': 'New York',
            'TX': 'Texas',
            'FL': 'Florida',
            'ON': 'Ontario',
            'BC': 'British Columbia',
            'NSW': 'New South Wales',
            'VIC': 'Victoria',
            'MH': 'Maharashtra',
            'KA': 'Karnataka',
            'TN': 'Tamil Nadu',
            'UP': 'Uttar Pradesh',
            'GJ': 'Gujarat',
            'RJ': 'Rajasthan',
            'AP': 'Andhra Pradesh',
            'TS': 'Telangana',
            'WB': 'West Bengal',
            'MP': 'Madhya Pradesh',
            'PB': 'Punjab',
            'HR': 'Haryana',
            'KL': 'Kerala',
            'OR': 'Odisha',
            'AS': 'Assam',
            'BR': 'Bihar',
            'JH': 'Jharkhand',
            'UK': 'Uttarakhand',
            'HP': 'Himachal Pradesh',
            'JK': 'Jammu and Kashmir',
            'GA': 'Goa',
            'NL': 'Nagaland',
            'MN': 'Manipur',
            'ML': 'Meghalaya',
            'TR': 'Tripura',
            'AR': 'Arunachal Pradesh',
            'MZ': 'Mizoram',
            'SK': 'Sikkim',
            'LD': 'Lakshadweep',
            'AN': 'Andaman and Nicobar Islands',
            'PY': 'Puducherry',
            'CH': 'Chandigarh',
            'DD': 'Daman and Diu',
            'DN': 'Dadra and Nagar Haveli',
            'DL': 'Delhi'
        }
        return states.get(code.upper(), code)
