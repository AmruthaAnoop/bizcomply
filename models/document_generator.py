import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
import uuid

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

from config.config import TEMPLATES_DIR, DOCUMENTS_DIR
from .compliance_engine import BusinessProfile, ComplianceRequirement

@dataclass
class GeneratedDocument:
    """Represents a generated document with its metadata and content."""
    id: str
    business_id: str
    title: str
    document_type: str
    file_path: str
    mime_type: str
    metadata: Dict[str, Any]
    created_at: str
    updated_at: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert the document to a dictionary."""
        return {
            'id': self.id,
            'business_id': self.business_id,
            'title': self.title,
            'document_type': self.document_type,
            'file_path': self.file_path,
            'mime_type': self.mime_type,
            'metadata': self.metadata,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class DocumentGenerator:
    """Handles generation of various business documents using templates."""
    
    def __init__(self, templates_dir: str = TEMPLATES_DIR, output_dir: str = DOCUMENTS_DIR):
        """Initialize the document generator with template and output directories."""
        self.templates_dir = Path(templates_dir)
        self.output_dir = Path(output_dir)
        
        # Create directories if they don't exist
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Register custom filters
        self.env.filters['format_date'] = self._format_date
        self.env.filters['format_currency'] = self._format_currency
    
    def _format_date(self, value: str, format_str: str = "%B %d, %Y") -> str:
        """Format a date string."""
        if not value:
            return ""
        try:
            date_obj = datetime.strptime(value, "%Y-%m-%d")
            return date_obj.strftime(format_str)
        except (ValueError, TypeError):
            return str(value)
    
    def _format_currency(self, value: float) -> str:
        """Format a number as currency."""
        try:
            return f"${value:,.2f}"
        except (ValueError, TypeError):
            return str(value)
    
    def _get_template(self, template_name: str):
        """Get a template by name."""
        template_path = self.templates_dir / f"{template_name}.html"
        if not template_path.exists():
            # Try to use a default template if the specified one doesn't exist
            default_template = self.templates_dir / f"default_{template_name}.html"
            if default_template.exists():
                return self.env.get_template(f"default_{template_name}.html")
            raise FileNotFoundError(f"Template '{template_name}' not found in {self.templates_dir}")
        return self.env.get_template(f"{template_name}.html")
    
    def _save_document(self, content: str, filename: str, format: str = 'pdf') -> str:
        """Save the generated document to disk."""
        output_path = self.output_dir / f"{filename}.{format}"
        
        if format.lower() == 'pdf':
            HTML(string=content).write_pdf(str(output_path))
        else:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return str(output_path)
    
    def generate_nda(
        self,
        business: BusinessProfile,
        counterparty: Dict[str, Any],
        effective_date: str,
        term_years: int = 1,
        template_name: str = "nda"
    ) -> GeneratedDocument:
        """Generate a Non-Disclosure Agreement (NDA) document.
        
        Args:
            business: The business profile of the disclosing party
            counterparty: Information about the receiving party
            effective_date: Effective date of the NDA (YYYY-MM-DD)
            term_years: Term of the NDA in years
            template_name: Name of the template to use
            
        Returns:
            GeneratedDocument: The generated NDA document
        """
        # Prepare template context
        context = {
            'disclosing_party': {
                'name': business.name,
                'address': business.address,
                'registration_number': business.registration_number
            },
            'receiving_party': {
                'name': counterparty.get('name', ''),
                'address': counterparty.get('address', {}),
                'registration_number': counterparty.get('registration_number', '')
            },
            'effective_date': effective_date,
            'term_years': term_years,
            'expiration_date': self._calculate_expiration_date(effective_date, term_years),
            'confidential_info': counterparty.get('confidential_info', []),
            'permitted_use': counterparty.get('permitted_use', 'evaluation purposes only'),
            'jurisdiction': business.jurisdiction.value.replace('_', ' ').title(),
            'generated_date': datetime.utcnow().strftime("%B %d, %Y")
        }
        
        # Render template
        template = self._get_template(template_name)
        rendered = template.render(**context)
        
        # Generate document ID and filename
        doc_id = str(uuid.uuid4())
        filename = f"NDA_{business.name.replace(' ', '_')}_{doc_id[:8]}"
        
        # Save the document
        file_path = self._save_document(rendered, filename, 'pdf')
        
        # Create and return document metadata
        return GeneratedDocument(
            id=doc_id,
            business_id=business.id,
            title=f"NDA - {business.name} and {counterparty.get('name', 'Counterparty')}",
            document_type="nda",
            file_path=file_path,
            mime_type="application/pdf",
            metadata={
                'parties': {
                    'disclosing_party': business.name,
                    'receiving_party': counterparty.get('name', '')
                },
                'effective_date': effective_date,
                'term_years': term_years,
                'template_used': template_name
            },
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat()
        )
    
    def generate_rental_agreement(
        self,
        business: BusinessProfile,
        property_info: Dict[str, Any],
        landlord_info: Dict[str, Any],
        start_date: str,
        term_months: int = 12,
        monthly_rent: float = 0.0,
        security_deposit: float = 0.0,
        template_name: str = "rental_agreement"
    ) -> GeneratedDocument:
        """Generate a rental/lease agreement document.
        
        Args:
            business: The business profile of the tenant
            property_info: Information about the rental property
            landlord_info: Information about the landlord
            start_date: Lease start date (YYYY-MM-DD)
            term_months: Lease term in months
            monthly_rent: Monthly rent amount
            security_deposit: Security deposit amount
            template_name: Name of the template to use
            
        Returns:
            GeneratedDocument: The generated rental agreement document
        """
        # Calculate end date
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_obj = self._add_months(start_date_obj, term_months)
        
        # Prepare template context
        context = {
            'landlord': {
                'name': landlord_info.get('name', ''),
                'address': landlord_info.get('address', {}),
                'contact': landlord_info.get('contact', {})
            },
            'tenant': {
                'name': business.name,
                'business_type': business.business_type.value.replace('_', ' ').title(),
                'registration_number': business.registration_number,
                'address': business.address,
                'contact': business.contact
            },
            'property': {
                'address': property_info.get('address', {}),
                'type': property_info.get('type', 'commercial space'),
                'square_footage': property_info.get('square_footage', ''),
                'permitted_use': property_info.get('permitted_use', 'general office use')
            },
            'lease_terms': {
                'start_date': start_date,
                'end_date': end_date_obj.strftime("%Y-%m-%d"),
                'term_months': term_months,
                'monthly_rent': monthly_rent,
                'security_deposit': security_deposit,
                'rent_due_day': property_info.get('rent_due_day', 1),
                'late_fee': property_info.get('late_fee', 0.0),
                'utilities_included': property_info.get('utilities_included', []),
                'maintenance_responsibilities': property_info.get('maintenance_responsibilities', {})
            },
            'jurisdiction': business.jurisdiction.value.replace('_', ' ').title(),
            'generated_date': datetime.utcnow().strftime("%B %d, %Y")
        }
        
        # Render template
        template = self._get_template(template_name)
        rendered = template.render(**context)
        
        # Generate document ID and filename
        doc_id = str(uuid.uuid4())
        filename = f"Lease_{business.name.replace(' ', '_')}_{doc_id[:8]}"
        
        # Save the document
        file_path = self._save_document(rendered, filename, 'pdf')
        
        # Create and return document metadata
        return GeneratedDocument(
            id=doc_id,
            business_id=business.id,
            title=f"Lease Agreement - {business.name} - {property_info.get('address', {}).get('street', 'Property')}",
            document_type="lease_agreement",
            file_path=file_path,
            mime_type="application/pdf",
            metadata={
                'parties': {
                    'landlord': landlord_info.get('name', ''),
                    'tenant': business.name
                },
                'property': property_info.get('address', {}).get('street', ''),
                'start_date': start_date,
                'term_months': term_months,
                'monthly_rent': monthly_rent,
                'template_used': template_name
            },
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat()
        )
    
    def generate_business_plan(
        self,
        business: BusinessProfile,
        business_plan_data: Dict[str, Any],
        template_name: str = "business_plan"
    ) -> GeneratedDocument:
        """Generate a business plan document.
        
        Args:
            business: The business profile
            business_plan_data: Business plan content and financial data
            template_name: Name of the template to use
            
        Returns:
            GeneratedDocument: The generated business plan document
        """
        # Prepare template context
        context = {
            'business': {
                'name': business.name,
                'business_type': business.business_type.value.replace('_', ' ').title(),
                'jurisdiction': business.jurisdiction.value.replace('_', ' ').title(),
                'registration_number': business.registration_number,
                'registration_date': business.registration_date,
                'address': business.address,
                'contact': business.contact,
                'industry': business_plan_data.get('industry', ''),
                'founding_date': business_plan_data.get('founding_date', business.registration_date)
            },
            'executive_summary': business_plan_data.get('executive_summary', ''),
            'business_description': business_plan_data.get('business_description', ''),
            'market_analysis': business_plan_data.get('market_analysis', {}),
            'organization_management': business_plan_data.get('organization_management', {}),
            'products_services': business_plan_data.get('products_services', []),
            'marketing_sales_strategy': business_plan_data.get('marketing_sales_strategy', {}),
            'financial_plan': business_plan_data.get('financial_plan', {}),
            'funding_request': business_plan_data.get('funding_request', {}),
            'appendices': business_plan_data.get('appendices', []),
            'generated_date': datetime.utcnow().strftime("%B %d, %Y")
        }
        
        # Render template
        template = self._get_template(template_name)
        rendered = template.render(**context)
        
        # Generate document ID and filename
        doc_id = str(uuid.uuid4())
        filename = f"BusinessPlan_{business.name.replace(' ', '_')}_{doc_id[:8]}"
        
        # Save the document
        file_path = self._save_document(rendered, filename, 'pdf')
        
        # Create and return document metadata
        return GeneratedDocument(
            id=doc_id,
            business_id=business.id,
            title=f"Business Plan - {business.name}",
            document_type="business_plan",
            file_path=file_path,
            mime_type="application/pdf",
            metadata={
                'business_name': business.name,
                'document_type': 'business_plan',
                'template_used': template_name,
                'generation_date': datetime.utcnow().isoformat()
            },
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat()
        )
    
    def generate_compliance_certificate(
        self,
        business: BusinessProfile,
        requirements: List[ComplianceRequirement],
        template_name: str = "compliance_certificate"
    ) -> GeneratedDocument:
        """Generate a compliance certificate for a business.
        
        Args:
            business: The business profile
            requirements: List of compliance requirements to include
            template_name: Name of the template to use
            
        Returns:
            GeneratedDocument: The generated compliance certificate
        """
        # Categorize requirements by status
        by_status = {}
        for status in ['completed', 'pending', 'overdue']:
            by_status[status] = [
                req for req in requirements 
                if req.status.value.lower() == status
            ]
        
        # Prepare template context
        context = {
            'business': {
                'name': business.name,
                'business_type': business.business_type.value.replace('_', ' ').title(),
                'jurisdiction': business.jurisdiction.value.replace('_', ' ').title(),
                'registration_number': business.registration_number,
                'address': business.address,
                'contact': business.contact
            },
            'requirements': by_status,
            'total_requirements': len(requirements),
            'completed_count': len(by_status['completed']),
            'pending_count': len(by_status['pending']),
            'overdue_count': len(by_status['overdue']),
            'compliance_percentage': round(len(by_status['completed']) / len(requirements) * 100, 2) if requirements else 0,
            'generated_date': datetime.utcnow().strftime("%B %d, %Y"),
            'valid_until': (datetime.utcnow() + timedelta(days=30)).strftime("%B %d, %Y")
        }
        
        # Render template
        template = self._get_template(template_name)
        rendered = template.render(**context)
        
        # Generate document ID and filename
        doc_id = str(uuid.uuid4())
        filename = f"Compliance_Certificate_{business.name.replace(' ', '_')}_{doc_id[:8]}"
        
        # Save the document
        file_path = self._save_document(rendered, filename, 'pdf')
        
        # Create and return document metadata
        return GeneratedDocument(
            id=doc_id,
            business_id=business.id,
            title=f"Compliance Certificate - {business.name}",
            document_type="compliance_certificate",
            file_path=file_path,
            mime_type="application/pdf",
            metadata={
                'business_name': business.name,
                'document_type': 'compliance_certificate',
                'requirements_count': len(requirements),
                'completed_count': len(by_status['completed']),
                'template_used': template_name,
                'generation_date': datetime.utcnow().isoformat(),
                'valid_until': (datetime.utcnow() + timedelta(days=30)).isoformat()
            },
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat()
        )
    
    def _calculate_expiration_date(self, effective_date: str, term_years: int) -> str:
        """Calculate the expiration date based on effective date and term."""
        try:
            effective = datetime.strptime(effective_date, "%Y-%m-%d")
            expiration = effective.replace(year=effective.year + term_years)
            return expiration.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            return ""
    
    def _add_months(self, start_date: datetime, months: int) -> datetime:
        """Add months to a date, handling year rollover."""
        month = start_date.month - 1 + months
        year = start_date.year + month // 12
        month = month % 12 + 1
        day = min(start_date.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
        return start_date.replace(year=year, month=month, day=day)
