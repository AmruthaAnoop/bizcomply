"""
Regulatory monitoring service for the BizComply application.

This module provides functionality to monitor regulatory updates from various sources,
analyze their impact on businesses, and notify relevant stakeholders.
"""

import asyncio
import aiohttp
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Set, Tuple
from dataclasses import dataclass, field, asdict
import json
import logging
import hashlib
import re
from urllib.parse import urlparse
import sqlite3
import os

from config.config import (
    REGULATORY_FEEDS, 
    REGULATORY_UPDATE_FREQUENCY,
    DB_PATH
)
from models.compliance_engine import BusinessProfile

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class RegulatoryUpdate:
    """Represents a regulatory update from a feed or other source."""
    id: str
    title: str
    summary: str
    link: str
    published: str
    source: str
    categories: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    relevance_score: float = 0.0
    affected_businesses: List[str] = field(default_factory=list)
    is_read: bool = False
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert the update to a dictionary."""
        data = asdict(self)
        # Convert datetime objects to ISO format strings
        for field in ['published', 'created_at']:
            if field in data and data[field] and isinstance(data[field], datetime):
                data[field] = data[field].isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RegulatoryUpdate':
        """Create a RegulatoryUpdate from a dictionary."""
        return cls(**data)

class RegulatoryMonitor:
    """Monitor and analyze regulatory updates for businesses.
    
    This service handles fetching updates from configured regulatory feeds,
    analyzing their impact on registered businesses, and notifying relevant
    stakeholders about important changes.
    """
    
    def __init__(self, db_path: str = None):
        """
        Initialize the regulatory monitor.
        
        Args:
            db_path: Path to the SQLite database file. If None, uses the default from config.
        """
        self.db_path = db_path or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'data',
            'regulatory_updates.db'
        )
        
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Initialize the database
        self._init_db()
        
        # Cache for seen update IDs to avoid duplicates
        self.seen_updates: Set[str] = set()
        self._load_seen_updates()
        
        # Keywords for impact analysis
        self.impact_keywords = {
            'tax': ['tax', 'irs', 'gst', 'vat', 'withholding', 'taxation', 'revenue'],
            'employment': ['labor', 'employment', 'wage', 'benefits', 'leave', 'employee', 'worker'],
            'privacy': ['privacy', 'gdpr', 'ccpa', 'data protection', 'personal data', 'compliance'],
            'safety': ['safety', 'osha', 'health', 'compliance', 'workplace safety'],
            'environmental': ['environment', 'emissions', 'sustainability', 'waste', 'pollution'],
            'financial': ['reporting', 'financial', 'accounting', 'audit', 'disclosure'],
            'industry_specific': {
                'healthcare': ['hipaa', 'patient', 'healthcare', 'medical', 'pharma'],
                'finance': ['finra', 'sec', 'securities', 'banking', 'financial'],
                'retail': ['consumer', 'pricing', 'retail', 'ecommerce'],
                'manufacturing': ['manufacturing', 'production', 'safety', 'quality control']
            }
        }
    
    def _init_db(self) -> None:
        """Initialize the database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            # Create regulatory_updates table
            conn.execute('''
            CREATE TABLE IF NOT EXISTS regulatory_updates (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                summary TEXT,
                link TEXT NOT NULL,
                published TEXT,
                source TEXT NOT NULL,
                categories TEXT,
                metadata TEXT,
                relevance_score REAL DEFAULT 0.0,
                affected_businesses TEXT,
                is_read INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
            ''')
            
            # Create update_business_impact table (many-to-many relationship)
            conn.execute('''
            CREATE TABLE IF NOT EXISTS update_business_impact (
                update_id TEXT,
                business_id TEXT,
                impact_score REAL,
                affected_areas TEXT,
                action_items TEXT,
                deadline TEXT,
                severity TEXT,
                notes TEXT,
                created_at TEXT NOT NULL,
                PRIMARY KEY (update_id, business_id),
                FOREIGN KEY (update_id) REFERENCES regulatory_updates (id) ON DELETE CASCADE,
                FOREIGN KEY (business_id) REFERENCES business_profiles (id) ON DELETE CASCADE
            )
            ''')
            
            # Create indexes for better query performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_update_source ON regulatory_updates(source)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_update_date ON regulatory_updates(published)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_update_relevance ON regulatory_updates(relevance_score)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_impact_update ON update_business_impact(update_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_impact_business ON update_business_impact(business_id)')
            
            conn.commit()
    
    def _load_seen_updates(self) -> None:
        """Load previously seen update IDs from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('SELECT id FROM regulatory_updates')
                self.seen_updates = {row[0] for row in cursor.fetchall()}
        except sqlite3.OperationalError as e:
            logger.warning(f"Could not load seen updates: {e}")
            self.seen_updates = set()
    
    async def fetch_feed(
        self,
        session: aiohttp.ClientSession,
        url: str,
        source: str
    ) -> List[RegulatoryUpdate]:
        """Fetch and parse a single regulatory feed.
        
        Args:
            session: aiohttp ClientSession for making HTTP requests
            url: URL of the feed to fetch
            source: Name of the feed source
            
        Returns:
            List of new RegulatoryUpdate objects
        """
        updates = []
        try:
            logger.info(f"Fetching feed: {source} ({url})")
            
            # Set a timeout for the request
            timeout = aiohttp.ClientTimeout(total=30)
            
            async with session.get(url, timeout=timeout) as response:
                if response.status == 200:
                    content = await response.text()
                    feed = feedparser.parse(content)
                    
                    for entry in feed.entries:
                        try:
                            # Generate a unique ID for this update
                            id_str = f"{source}:{entry.get('link', '')}:{entry.get('title', '')}"
                            update_id = hashlib.md5(id_str.encode('utf-8')).hexdigest()
                            
                            # Skip if we've already seen this update
                            if update_id in self.seen_updates:
                                continue
                            
                            # Parse the published date
                            published = entry.get('published_parsed')
                            if published:
                                published = datetime(*published[:6]).isoformat()
                            else:
                                published = datetime.utcnow().isoformat()
                            
                            # Extract categories/tags
                            categories = []
                            if hasattr(entry, 'tags'):
                                categories = [tag.term for tag in entry.tags if hasattr(tag, 'term')]
                            elif hasattr(entry, 'category'):
                                categories = [entry.category]
                            
                            # Create the update
                            update = RegulatoryUpdate(
                                id=update_id,
                                title=entry.get('title', 'No Title'),
                                summary=entry.get('summary', ''),
                                link=entry.get('link', ''),
                                published=published,
                                source=source,
                                categories=categories,
                                metadata={
                                    'author': entry.get('author', ''),
                                    'source_url': url,
                                    'source_title': feed.feed.get('title', source)
                                }
                            )
                            
                            updates.append(update)
                            self.seen_updates.add(update_id)
                            
                        except Exception as e:
                            logger.error(f"Error processing entry from {source}: {e}", exc_info=True)
                            continue
                else:
                    logger.error(f"Failed to fetch {url}: HTTP {response.status}")
                            
        except asyncio.TimeoutError:
            logger.error(f"Timeout while fetching feed: {url}")
        except Exception as e:
            logger.error(f"Error fetching feed {url}: {e}", exc_info=True)
        
        return updates
    
    async def fetch_all_feeds(self) -> List[RegulatoryUpdate]:
        """Fetch updates from all configured regulatory feeds concurrently.
        
        Returns:
            List of new RegulatoryUpdate objects from all feeds
        """
        updates = []
        
        # Set a limit on concurrent connections
        connector = aiohttp.TCPConnector(limit=5)
        timeout = aiohttp.ClientTimeout(total=60)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            tasks = []
            for source, url in REGULATORY_FEEDS.items():
                tasks.append(self.fetch_feed(session, url, source))
            
            # Gather results from all tasks
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for result in results:
                if isinstance(result, list):
                    updates.extend(result)
                elif isinstance(result, Exception):
                    logger.error(f"Error in feed task: {result}", exc_info=True)
        
        logger.info(f"Fetched {len(updates)} new regulatory updates")
        return updates
    
    def analyze_impact(
        self,
        update: RegulatoryUpdate,
        business: BusinessProfile
    ) -> Dict[str, Any]:
        """Analyze the potential impact of a regulatory update on a business.
        
        Args:
            update: The regulatory update to analyze
            business: The business profile to analyze impact for
            
        Returns:
            Dictionary with impact analysis results
        """
        # Initialize impact result
        impact = {
            'relevance_score': 0.0,
            'affected_areas': [],
            'action_items': [],
            'deadline': None,
            'severity': 'low',  # low, medium, high, critical
            'notes': ''
        }
        
        try:
            # Combine text for keyword analysis
            text = f"{update.title} {update.summary}".lower()
            
            # Check for keywords in the update
            for category, keywords in self.impact_keywords.items():
                if category == 'industry_specific':
                    # Handle industry-specific keywords
                    for industry, industry_keywords in keywords.items():
                        if industry.lower() in business.business_type.value.lower():
                            if any(re.search(r'\b' + re.escape(kw) + r'\b', text) for kw in industry_keywords):
                                impact['relevance_score'] += 0.3
                                impact['affected_areas'].append(f"industry_{industry}")
                else:
                    # Handle general keywords
                    if any(re.search(r'\b' + re.escape(kw) + r'\b', text) for kw in keywords):
                        impact['relevance_score'] += 0.2
                        impact['affected_areas'].append(category)
            
            # Adjust relevance based on business type and jurisdiction
            business_type = business.business_type.value.lower()
            jurisdiction = business.jurisdiction.value.lower()
            
            # Check if the update mentions the business's jurisdiction
            if jurisdiction in text or any(
                j in text for j in ['us', 'uk', 'eu', 'india', 'australia']
                if jurisdiction.startswith(j)
            ):
                impact['relevance_score'] += 0.3
                impact['affected_areas'].append(f"jurisdiction_{jurisdiction}")
            
            # Business type adjustments
            if 'llc' in business_type or 'corporation' in business_type:
                if 'tax' in text:
                    impact['relevance_score'] += 0.2
            
            if 'restaurant' in business_type or 'food' in business_type:
                if 'health' in text or 'safety' in text or 'inspection' in text:
                    impact['relevance_score'] += 0.3
            
            # Cap the relevance score at 1.0
            impact['relevance_score'] = min(1.0, impact['relevance_score'])
            
            # Set severity based on relevance score
            if impact['relevance_score'] > 0.7:
                impact['severity'] = 'high'
                impact['action_items'].extend([
                    'Review the full regulatory update',
                    'Assess impact on current operations',
                    'Consult with legal/compliance team',
                    'Update compliance documentation'
                ])
            elif impact['relevance_score'] > 0.4:
                impact['severity'] = 'medium'
                impact['action_items'].extend([
                    'Review the full regulatory update',
                    'Assess impact on current operations'
                ])
            else:
                impact['action_items'].append('Review the full regulatory update')
            
            # Try to extract a deadline from the text
            deadline_matches = re.search(
                r'(deadline|due|effective)\s*(?:date)?\s*(?:of|on)?\s*(\d{1,2}[\-/]\d{1,2}[\-/]\d{2,4})',
                text,
                re.IGNORECASE
            )
            
            if deadline_matches:
                try:
                    deadline_str = deadline_matches.group(2)
                    # Try different date formats
                    for fmt in ('%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d', '%m-%d-%Y'):
                        try:
                            deadline = datetime.strptime(deadline_str, fmt).date()
                            impact['deadline'] = deadline.isoformat()
                            break
                        except ValueError:
                            continue
                except (IndexError, AttributeError):
                    pass
            
            # Add a note if no specific impact was found
            if not impact['affected_areas']:
                impact['notes'] = 'No specific impact areas identified. Review for potential relevance.'
            
        except Exception as e:
            logger.error(f"Error analyzing impact: {e}", exc_info=True)
            impact['notes'] = f'Error during impact analysis: {str(e)}'
        
        return impact
    
    async def process_updates_for_business(
        self, 
        business: BusinessProfile,
        updates: List[RegulatoryUpdate] = None
    ) -> List[Dict[str, Any]]:
        """
        Process regulatory updates for a specific business.
        
        Args:
            business: The business to process updates for
            updates: Optional list of updates to process. If None, fetches new updates.
            
        Returns:
            List of processed updates with impact analysis
        """
        if updates is None:
            updates = await self.fetch_all_feeds()
        
        processed = []
        
        for update in updates:
            try:
                # Analyze impact on this business
                impact = self.analyze_impact(update, business)
                
                # Only include updates with some relevance
                if impact['relevance_score'] > 0.2:
                    # Save the update to the database
                    self._save_update(update, business.id, impact)
                    
                    # Add to results
                    result = update.to_dict()
                    result.update({
                        'business_id': business.id,
                        'impact': impact
                    })
                    processed.append(result)
            
            except Exception as e:
                logger.error(f"Error processing update {update.id} for business {business.id}: {e}", exc_info=True)
        
        return processed
    
    def _save_update(
        self, 
        update: RegulatoryUpdate, 
        business_id: str,
        impact: Dict[str, Any]
    ) -> None:
        """
        Save a regulatory update and its impact on a business to the database.
        
        Args:
            update: The regulatory update to save
            business_id: ID of the affected business
            impact: Impact analysis results
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Convert categories and metadata to JSON strings
                categories_json = json.dumps(update.categories)
                metadata_json = json.dumps(update.metadata)
                
                # Insert or ignore the update
                conn.execute('''
                INSERT OR IGNORE INTO regulatory_updates 
                (id, title, summary, link, published, source, categories, metadata, relevance_score, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    update.id,
                    update.title,
                    update.summary,
                    update.link,
                    update.published,
                    update.source,
                    categories_json,
                    metadata_json,
                    impact['relevance_score'],
                    update.created_at
                ))
                
                # Save the impact on this business
                conn.execute('''
                INSERT OR REPLACE INTO update_business_impact
                (update_id, business_id, impact_score, affected_areas, action_items, deadline, severity, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    update.id,
                    business_id,
                    impact['relevance_score'],
                    json.dumps(impact['affected_areas']),
                    json.dumps(impact['action_items']),
                    impact.get('deadline'),
                    impact['severity'],
                    impact.get('notes', ''),
                    datetime.utcnow().isoformat()
                ))
                
                conn.commit()
                
        except sqlite3.Error as e:
            logger.error(f"Error saving update to database: {e}", exc_info=True)
            # Try to continue even if database save fails
    
    def get_updates_for_business(
        self, 
        business_id: str, 
        limit: int = 50,
        min_relevance: float = 0.0,
        include_read: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get regulatory updates relevant to a specific business.
        
        Args:
            business_id: ID of the business
            limit: Maximum number of updates to return
            min_relevance: Minimum relevance score (0.0 to 1.0)
            include_read: Whether to include updates that have been marked as read
            
        Returns:
            List of updates with impact analysis
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                query = '''
                SELECT u.*, 
                       i.impact_score, 
                       i.affected_areas, 
                       i.action_items, 
                       i.deadline, 
                       i.severity,
                       i.notes,
                       i.created_at as impact_created_at
                FROM regulatory_updates u
                JOIN update_business_impact i ON u.id = i.update_id
                WHERE i.business_id = ? AND i.impact_score >= ?
                '''
                
                params = [business_id, min_relevance]
                
                if not include_read:
                    query += ' AND u.is_read = 0'
                
                query += ' ORDER BY i.impact_score DESC, u.published DESC LIMIT ?'
                params.append(limit)
                
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                
                results = []
                for row in rows:
                    result = dict(row)
                    
                    # Parse JSON fields
                    for field in ['categories', 'metadata', 'affected_areas', 'action_items']:
                        if field in result and result[field]:
                            try:
                                result[field] = json.loads(result[field])
                            except (json.JSONDecodeError, TypeError):
                                result[field] = []
                    
                    results.append(result)
                
                return results
                
        except sqlite3.Error as e:
            logger.error(f"Error fetching updates for business {business_id}: {e}", exc_info=True)
            return []
    
    def mark_as_read(self, update_id: str, business_id: str, read: bool = True) -> bool:
        """
        Mark an update as read or unread for a specific business.
        
        Args:
            update_id: ID of the update
            business_id: ID of the business
            read: Whether to mark as read (True) or unread (False)
            
        Returns:
            True if the update was found and updated, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Update the read status in the impact table
                conn.execute('''
                UPDATE update_business_impact
                SET is_read = ?
                WHERE update_id = ? AND business_id = ?
                ''', (1 if read else 0, update_id, business_id))
                
                # Check if this was the last business to read this update
                if read:
                    cursor = conn.execute('''
                    SELECT COUNT(*) 
                    FROM update_business_impact 
                    WHERE update_id = ? AND is_read = 0
                    ''', (update_id,))
                    
                    unread_count = cursor.fetchone()[0]
                    
                    # If no businesses have this unread, mark the update as read globally
                    if unread_count == 0:
                        conn.execute('''
                        UPDATE regulatory_updates
                        SET is_read = 1
                        WHERE id = ?
                        ''', (update_id,))
                
                conn.commit()
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Error marking update {update_id} as read: {e}", exc_info=True)
            return False
    
    async def monitor_updates_continuously(self, interval: int = None) -> None:
        """
        Continuously monitor for regulatory updates at the specified interval.

        This method runs in an infinite loop, periodically checking for new
        regulatory updates and processing them for all registered businesses.

        Args:
            interval: Time between checks in seconds. Defaults to REGULATORY_UPDATE_FREQUENCY.
        """
        if interval is None:
            interval = REGULATORY_UPDATE_FREQUENCY
        
        logger.info(f"Starting continuous monitoring with {interval}s interval")
        
        while True:
            try:
                # Fetch and process updates
                updates = await self.fetch_all_feeds()
                
                if updates:
                    logger.info(f"Found {len(updates)} new regulatory updates")
                    
                    # Here you would typically get all businesses and process updates for each
                    # For now, we'll just log that we'd process them
                    # In a real implementation, you would call process_updates_for_business for each business
                    logger.info("Updates would be processed for all registered businesses")
                
                # Wait for the next check
                await asyncio.sleep(interval)
                
            except asyncio.CancelledError:
                logger.info("Monitoring task cancelled")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                # Wait a bit before retrying after an error
                await asyncio.sleep(min(300, interval))  # Max 5 minutes between retries


# Example usage
async def example_usage():
    """Example of how to use the RegulatoryMonitor class."""
    # Create a monitor instance
    monitor = RegulatoryMonitor()
    
    # Create a sample business profile
    business = BusinessProfile(
        id="biz_123",
        name="Acme Corp",
        business_type="llc",
        jurisdiction="united_states",
        registration_number="123456789",
        registration_date="2020-01-01",
        address={
            "street": "123 Business St",
            "city": "New York",
            "state": "NY",
            "postal_code": "10001",
            "country": "USA"
        },
        contact={
            "name": "John Doe",
            "email": "john@acmecorp.com",
            "phone": "+1-555-123-4567"
        }
    )
    
    # Fetch and process updates for this business
    updates = await monitor.fetch_all_feeds()
    results = await monitor.process_updates_for_business(business, updates)
    
    # Print the results
    print(f"Found {len(results)} relevant updates for {business.name}:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['title']}")
        print(f"   Source: {result['source']}")
        print(f"   Relevance: {result['impact']['relevance_score']:.1%}")
        print(f"   Severity: {result['impact']['severity']}")
        if result['impact'].get('deadline'):
            print(f"   Deadline: {result['impact']['deadline']}")
        print(f"   Link: {result['link']}")


if __name__ == "__main__":
    # Run the example
    asyncio.run(example_usage())
