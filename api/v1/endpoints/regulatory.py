"""
Regulatory API Endpoints

This module provides API endpoints for managing regulatory compliance integration.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.background import BackgroundTasks
from typing import List, Optional
from sqlalchemy.orm import Session
import logging

from models.database import get_db
from models.business import Business
from services.regulatory_compliance_integrator import RegulatoryComplianceIntegrator
from services.regulatory_monitor import RegulatoryMonitor
from schemas.regulatory import (
    RegulatoryUpdateResponse,
    ComplianceImpactResponse,
    ProcessUpdatesResponse
)

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/updates", response_model=List[RegulatoryUpdateResponse])
async def get_regulatory_updates(
    business_id: Optional[str] = None,
    processed: bool = False,
    limit: int = 100,
    skip: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get regulatory updates, optionally filtered by business and processing status.
    """
    try:
        monitor = RegulatoryMonitor()
        updates = await monitor.get_updates(
            business_id=business_id,
            processed=processed,
            limit=limit,
            skip=skip
        )
        return updates
    except Exception as e:
        logger.error(f"Error fetching regulatory updates: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch regulatory updates"
        )

@router.get("/updates/{update_id}/impact", response_model=ComplianceImpactResponse)
async def analyze_update_impact(
    update_id: str,
    business_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Analyze the impact of a specific regulatory update on compliance requirements.
    """
    try:
        integrator = RegulatoryComplianceIntegrator(db)
        monitor = RegulatoryMonitor()
        
        # Get the specific update
        updates = await monitor.get_updates(update_id=update_id)
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Regulatory update {update_id} not found"
            )
        
        # Analyze impact
        impacted_requirements = await integrator.analyze_impact(
            updates[0], 
            business_id=business_id
        )
        
        return {
            "update_id": update_id,
            "impacted_requirements": impacted_requirements,
            "total_impacted": len(impacted_requirements)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing update impact: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze update impact"
        )

@router.post("/updates/process", response_model=ProcessUpdatesResponse)
async def process_regulatory_updates(
    background_tasks: BackgroundTasks,
    business_id: Optional[str] = None,
    update_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Process regulatory updates and update compliance requirements.
    
    This endpoint can process a specific update or all unprocessed updates.
    Processing happens in the background.
    """
    try:
        integrator = RegulatoryComplianceIntegrator(db)
        
        if update_id:
            # Process a specific update
            background_tasks.add_task(
                integrator.process_single_update,
                update_id=update_id,
                business_id=business_id
            )
            message = f"Processing of update {update_id} has been queued"
        else:
            # Process all unprocessed updates
            background_tasks.add_task(
                integrator.process_new_updates,
                business_id=business_id
            )
            message = "Processing of all unprocessed updates has been queued"
        
        return {
            "status": "processing",
            "message": message,
            "update_id": update_id
        }
        
    except Exception as e:
        logger.error(f"Error queuing update processing: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to queue update processing"
        )

@router.get("/business/{business_id}/requirements/upcoming", response_model=List[dict])
async def get_upcoming_requirements(
    business_id: str,
    days_ahead: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get upcoming compliance requirements for a business based on regulatory changes.
    """
    try:
        # Verify business exists
        business = db.query(Business).filter(Business.id == business_id).first()
        if not business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Business {business_id} not found"
            )
        
        # Get recent regulatory updates
        monitor = RegulatoryMonitor()
        updates = await monitor.get_updates(processed=True, limit=100)  # Get recent updates
        
        # Get compliance requirements from these updates
        requirements = []
        for update in updates:
            impacted = await integrator.analyze_impact(update, business_id=business_id)
            for req in impacted:
                requirements.append({
                    "update_id": update.id,
                    "update_title": update.title,
                    "update_date": update.published,
                    "requirement_id": req['id'],
                    "requirement_name": req['name'],
                    "action_required": req.get('is_new', False) or req.get('requires_update', False),
                    "deadline": None  # Would be calculated based on regulation
                })
        
        return requirements
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching upcoming requirements: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch upcoming requirements"
        )
