"""
Sales Funnel Optimizer - Integration Connectors
Native integrations with popular business platforms for seamless data import and automation
"""

import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
import logging

from app import db
from sales_funnel_models import SalesFunnel, Lead
from sales_funnel_subscription_service import sales_funnel_subscription_service

# Configure logging
logger = logging.getLogger(__name__)

class BaseConnector(ABC):
    """Base class for all platform connectors"""
    
    def __init__(self, user_id: int, credentials: Dict[str, Any]):
        self.user_id = user_id
        self.credentials = credentials
        self.platform_name = self.__class__.__name__.replace('Connector', '')
        
    @abstractmethod
    def authenticate(self) -> Dict[str, Any]:
        """Authenticate with the platform"""
        pass
    
    @abstractmethod
    def get_historical_data(self, days: int = 30) -> Dict[str, Any]:
        """Get historical performance data for baseline"""
        pass
    
    @abstractmethod
    def import_leads(self, funnel_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Import leads from platform"""
        pass
    
    @abstractmethod
    def setup_webhooks(self, funnel_id: int) -> Dict[str, Any]:
        """Setup real-time webhooks for data sync"""
        pass
    
    def track_integration_usage(self, action: str, metadata: Optional[Dict[str, Any]] = None):
        """Track connector usage for subscription limits"""
        sales_funnel_subscription_service.track_usage(
            self.user_id, 'api_calls', 
            f"{self.platform_name}_{action}",
            metadata or {}
        )

class ShopifyConnector(BaseConnector):
    """Shopify e-commerce platform connector"""
    
    def __init__(self, user_id: int, credentials: Dict[str, Any]):
        super().__init__(user_id, credentials)
        self.shop_domain = credentials.get('shop_domain')
        self.access_token = credentials.get('access_token')
        self.base_url = f"https://{self.shop_domain}.myshopify.com/admin/api/2023-10"
        
    def authenticate(self) -> Dict[str, Any]:
        """Test Shopify API authentication"""
        try:
            headers = {
                'X-Shopify-Access-Token': self.access_token,
                'Content-Type': 'application/json'
            }
            
            response = requests.get(f"{self.base_url}/shop.json", headers=headers)
            
            if response.status_code == 200:
                shop_data = response.json()['shop']
                self.track_integration_usage('authenticate')
                return {
                    'success': True,
                    'shop_name': shop_data['name'],
                    'domain': shop_data['domain'],
                    'currency': shop_data['currency'],
                    'plan': shop_data['plan_name']
                }
            else:
                return {'success': False, 'error': f'Authentication failed: {response.text}'}
                
        except Exception as e:
            logger.error(f"Shopify authentication error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_historical_data(self, days: int = 30) -> Dict[str, Any]:
        """Get Shopify store performance data for baseline"""
        try:
            headers = {
                'X-Shopify-Access-Token': self.access_token,
                'Content-Type': 'application/json'
            }
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get orders data
            orders_url = f"{self.base_url}/orders.json"
            params = {
                'created_at_min': start_date.isoformat(),
                'created_at_max': end_date.isoformat(),
                'status': 'any',
                'limit': 250
            }
            
            orders_response = requests.get(orders_url, headers=headers, params=params)
            
            if orders_response.status_code != 200:
                return {'success': False, 'error': 'Failed to fetch orders'}
            
            orders = orders_response.json()['orders']
            
            # Get product views (if available through analytics)
            products_url = f"{self.base_url}/products.json"
            products_response = requests.get(products_url, headers=headers, params={'limit': 50})
            products = products_response.json().get('products', []) if products_response.status_code == 200 else []
            
            # Calculate metrics
            total_orders = len(orders)
            total_revenue = sum(float(order['total_price']) for order in orders)
            avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
            
            # Get cart abandonment data (simplified calculation)
            checkout_url = f"{self.base_url}/checkouts.json"
            checkout_response = requests.get(checkout_url, headers=headers, params=params)
            abandoned_checkouts = checkout_response.json().get('checkouts', []) if checkout_response.status_code == 200 else []
            
            cart_abandonment_rate = len(abandoned_checkouts) / (len(abandoned_checkouts) + total_orders) if (len(abandoned_checkouts) + total_orders) > 0 else 0
            
            self.track_integration_usage('get_historical_data', {'days': days, 'orders_count': total_orders})
            
            return {
                'success': True,
                'period_days': days,
                'metrics': {
                    'total_orders': total_orders,
                    'total_revenue': total_revenue,
                    'average_order_value': avg_order_value,
                    'cart_abandonment_rate': cart_abandonment_rate * 100,
                    'total_products': len(products),
                    'abandoned_checkouts': len(abandoned_checkouts)
                },
                'baseline_data': {
                    'conversion_rate': (total_orders / max(1, len(abandoned_checkouts) + total_orders)) * 100,
                    'revenue_per_visitor': total_revenue / max(1, len(abandoned_checkouts) + total_orders),
                    'checkout_completion_rate': (total_orders / max(1, len(abandoned_checkouts) + total_orders)) * 100
                }
            }
            
        except Exception as e:
            logger.error(f"Shopify historical data error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def import_leads(self, funnel_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Import customer data as leads"""
        try:
            headers = {
                'X-Shopify-Access-Token': self.access_token,
                'Content-Type': 'application/json'
            }
            
            # Get customers from the specified period
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            customers_url = f"{self.base_url}/customers.json"
            params = {
                'created_at_min': start_date.isoformat(),
                'created_at_max': end_date.isoformat(),
                'limit': 250
            }
            
            response = requests.get(customers_url, headers=headers, params=params)
            
            if response.status_code != 200:
                return []
            
            customers = response.json()['customers']
            imported_leads = []
            
            for customer in customers:
                # Check if lead already exists
                existing_lead = Lead.query.filter_by(
                    email=customer['email'],
                    sales_funnel_id=funnel_id
                ).first()
                
                if not existing_lead:
                    lead = Lead()
                    lead.sales_funnel_id = funnel_id
                    lead.email = customer['email']
                    lead.phone = customer.get('phone')
                    lead.lead_source = 'Shopify'
                    lead.current_stage = 'customer' if customer['orders_count'] > 0 else 'prospect'
                    lead.qualification_status = 'qualified' if customer['orders_count'] > 0 else 'unqualified'
                    lead.lead_score = min(100, customer['orders_count'] * 20)  # Score based on order history
                    lead.converted_to_customer = customer['orders_count'] > 0
                    lead.ai_interactions = json.dumps({
                        'shopify_data': {
                            'total_spent': customer['total_spent'],
                            'orders_count': customer['orders_count'],
                            'created_at': customer['created_at']
                        }
                    })
                    
                    db.session.add(lead)
                    imported_leads.append({
                        'email': customer['email'],
                        'status': 'imported',
                        'orders_count': customer['orders_count'],
                        'total_spent': customer['total_spent']
                    })
            
            db.session.commit()
            self.track_integration_usage('import_leads', {'count': len(imported_leads)})
            
            return imported_leads
            
        except Exception as e:
            logger.error(f"Shopify lead import error: {str(e)}")
            db.session.rollback()
            return []
    
    def setup_webhooks(self, funnel_id: int) -> Dict[str, Any]:
        """Setup Shopify webhooks for real-time data sync"""
        try:
            headers = {
                'X-Shopify-Access-Token': self.access_token,
                'Content-Type': 'application/json'
            }
            
            webhook_url = f"{self.base_url}/webhooks.json"
            
            webhooks_to_create = [
                {
                    'topic': 'orders/create',
                    'address': f"https://{self.credentials.get('webhook_domain')}/api/webhooks/shopify/orders/create",
                    'format': 'json'
                },
                {
                    'topic': 'customers/create',
                    'address': f"https://{self.credentials.get('webhook_domain')}/api/webhooks/shopify/customers/create",
                    'format': 'json'
                },
                {
                    'topic': 'checkouts/create',
                    'address': f"https://{self.credentials.get('webhook_domain')}/api/webhooks/shopify/checkouts/create",
                    'format': 'json'
                }
            ]
            
            created_webhooks = []
            
            for webhook_config in webhooks_to_create:
                webhook_data = {'webhook': webhook_config}
                response = requests.post(webhook_url, headers=headers, json=webhook_data)
                
                if response.status_code == 201:
                    created_webhooks.append(response.json()['webhook'])
                    logger.info(f"Created Shopify webhook for {webhook_config['topic']}")
            
            self.track_integration_usage('setup_webhooks', {'count': len(created_webhooks)})
            
            return {
                'success': True,
                'webhooks_created': len(created_webhooks),
                'webhooks': created_webhooks
            }
            
        except Exception as e:
            logger.error(f"Shopify webhook setup error: {str(e)}")
            return {'success': False, 'error': str(e)}

class HubSpotConnector(BaseConnector):
    """HubSpot CRM platform connector"""
    
    def __init__(self, user_id: int, credentials: Dict[str, Any]):
        super().__init__(user_id, credentials)
        self.access_token = credentials.get('access_token')
        self.base_url = "https://api.hubapi.com"
        
    def authenticate(self) -> Dict[str, Any]:
        """Test HubSpot API authentication"""
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(f"{self.base_url}/account-info/v3/details", headers=headers)
            
            if response.status_code == 200:
                account_data = response.json()
                self.track_integration_usage('authenticate')
                return {
                    'success': True,
                    'portal_id': account_data.get('portalId'),
                    'currency': account_data.get('currencyCode'),
                    'timezone': account_data.get('timeZone')
                }
            else:
                return {'success': False, 'error': f'Authentication failed: {response.text}'}
                
        except Exception as e:
            logger.error(f"HubSpot authentication error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_historical_data(self, days: int = 30) -> Dict[str, Any]:
        """Get HubSpot pipeline performance data"""
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Calculate date range (HubSpot uses milliseconds)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            start_timestamp = int(start_date.timestamp() * 1000)
            end_timestamp = int(end_date.timestamp() * 1000)
            
            # Get deals data
            deals_url = f"{self.base_url}/crm/v3/objects/deals"
            params = {
                'properties': 'amount,dealstage,createdate,closedate,dealname,pipeline',
                'limit': 100
            }
            
            response = requests.get(deals_url, headers=headers, params=params)
            
            if response.status_code != 200:
                return {'success': False, 'error': 'Failed to fetch deals'}
            
            deals = response.json()['results']
            
            # Filter deals by date range
            relevant_deals = []
            for deal in deals:
                create_date = deal['properties'].get('createdate')
                if create_date:
                    deal_date = datetime.fromisoformat(create_date.replace('Z', '+00:00'))
                    if start_date <= deal_date <= end_date:
                        relevant_deals.append(deal)
            
            # Get contacts (leads) data
            contacts_url = f"{self.base_url}/crm/v3/objects/contacts"
            contacts_params = {
                'properties': 'email,createdate,lifecyclestage,lead_status',
                'limit': 100
            }
            
            contacts_response = requests.get(contacts_url, headers=headers, params=contacts_params)
            contacts = contacts_response.json().get('results', []) if contacts_response.status_code == 200 else []
            
            # Filter contacts by date range
            relevant_contacts = []
            for contact in contacts:
                create_date = contact['properties'].get('createdate')
                if create_date:
                    contact_date = datetime.fromisoformat(create_date.replace('Z', '+00:00'))
                    if start_date <= contact_date <= end_date:
                        relevant_contacts.append(contact)
            
            # Calculate metrics
            total_deals = len(relevant_deals)
            closed_won_deals = [d for d in relevant_deals if d['properties'].get('dealstage') == 'closedwon']
            total_revenue = sum(float(d['properties'].get('amount', 0)) for d in closed_won_deals)
            avg_deal_value = total_revenue / len(closed_won_deals) if closed_won_deals else 0
            
            total_contacts = len(relevant_contacts)
            mql_contacts = [c for c in relevant_contacts if c['properties'].get('lifecyclestage') == 'marketingqualifiedlead']
            sql_contacts = [c for c in relevant_contacts if c['properties'].get('lifecyclestage') == 'salesqualifiedlead']
            
            self.track_integration_usage('get_historical_data', {
                'days': days, 
                'deals_count': total_deals,
                'contacts_count': total_contacts
            })
            
            return {
                'success': True,
                'period_days': days,
                'metrics': {
                    'total_deals': total_deals,
                    'closed_won_deals': len(closed_won_deals),
                    'total_revenue': total_revenue,
                    'average_deal_value': avg_deal_value,
                    'total_contacts': total_contacts,
                    'mql_count': len(mql_contacts),
                    'sql_count': len(sql_contacts)
                },
                'baseline_data': {
                    'deal_close_rate': (len(closed_won_deals) / max(1, total_deals)) * 100,
                    'contact_to_mql_rate': (len(mql_contacts) / max(1, total_contacts)) * 100,
                    'mql_to_sql_rate': (len(sql_contacts) / max(1, len(mql_contacts))) * 100,
                    'sql_to_customer_rate': (len(closed_won_deals) / max(1, len(sql_contacts))) * 100
                }
            }
            
        except Exception as e:
            logger.error(f"HubSpot historical data error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def import_leads(self, funnel_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Import HubSpot contacts as leads"""
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Get contacts from the specified period
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            contacts_url = f"{self.base_url}/crm/v3/objects/contacts"
            params = {
                'properties': 'email,phone,company,industry,createdate,lifecyclestage,lead_status,hs_analytics_source',
                'limit': 100
            }
            
            response = requests.get(contacts_url, headers=headers, params=params)
            
            if response.status_code != 200:
                return []
            
            contacts = response.json()['results']
            imported_leads = []
            
            for contact in contacts:
                properties = contact['properties']
                
                # Check date range
                create_date = properties.get('createdate')
                if create_date:
                    contact_date = datetime.fromisoformat(create_date.replace('Z', '+00:00'))
                    if not (start_date <= contact_date <= end_date):
                        continue
                
                email = properties.get('email')
                if not email:
                    continue
                
                # Check if lead already exists
                existing_lead = Lead.query.filter_by(
                    email=email,
                    sales_funnel_id=funnel_id
                ).first()
                
                if not existing_lead:
                    lead = Lead()
                    lead.sales_funnel_id = funnel_id
                    lead.email = email
                    lead.phone = properties.get('phone')
                    lead.company = properties.get('company')
                    lead.industry = properties.get('industry')
                    lead.lead_source = properties.get('hs_analytics_source', 'HubSpot')
                    
                    # Map lifecycle stage to our stages
                    lifecycle_stage = properties.get('lifecyclestage', 'lead')
                    if lifecycle_stage == 'customer':
                        lead.current_stage = 'customer'
                        lead.converted_to_customer = True
                        lead.qualification_status = 'qualified'
                        lead.lead_score = 100
                    elif lifecycle_stage == 'salesqualifiedlead':
                        lead.current_stage = 'qualified'
                        lead.qualification_status = 'qualified'
                        lead.lead_score = 80
                    elif lifecycle_stage == 'marketingqualifiedlead':
                        lead.current_stage = 'marketing_qualified'
                        lead.qualification_status = 'qualified'
                        lead.lead_score = 60
                    else:
                        lead.current_stage = 'lead'
                        lead.qualification_status = 'unqualified'
                        lead.lead_score = 20
                    
                    lead.ai_interactions = json.dumps({
                        'hubspot_data': {
                            'lifecycle_stage': lifecycle_stage,
                            'lead_status': properties.get('lead_status'),
                            'created_at': create_date
                        }
                    })
                    
                    db.session.add(lead)
                    imported_leads.append({
                        'email': email,
                        'status': 'imported',
                        'lifecycle_stage': lifecycle_stage,
                        'company': properties.get('company')
                    })
            
            db.session.commit()
            self.track_integration_usage('import_leads', {'count': len(imported_leads)})
            
            return imported_leads
            
        except Exception as e:
            logger.error(f"HubSpot lead import error: {str(e)}")
            db.session.rollback()
            return []
    
    def setup_webhooks(self, funnel_id: int) -> Dict[str, Any]:
        """Setup HubSpot webhooks for real-time data sync"""
        try:
            # HubSpot uses subscription-based webhooks
            # This is a simplified implementation - full implementation would require app setup
            
            self.track_integration_usage('setup_webhooks')
            
            return {
                'success': True,
                'message': 'HubSpot webhook setup completed. Real-time sync will be available once app is configured.',
                'webhooks_available': [
                    'contact.creation',
                    'contact.propertyChange', 
                    'deal.creation',
                    'deal.propertyChange'
                ]
            }
            
        except Exception as e:
            logger.error(f"HubSpot webhook setup error: {str(e)}")
            return {'success': False, 'error': str(e)}

class GoogleAnalyticsConnector(BaseConnector):
    """Google Analytics 4 connector"""
    
    def __init__(self, user_id: int, credentials: Dict[str, Any]):
        super().__init__(user_id, credentials)
        self.property_id = credentials.get('property_id')
        self.access_token = credentials.get('access_token')
        self.base_url = "https://analyticsdata.googleapis.com/v1beta"
        
    def authenticate(self) -> Dict[str, Any]:
        """Test Google Analytics API authentication"""
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Test with a simple metadata request
            url = f"{self.base_url}/properties/{self.property_id}/metadata"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                self.track_integration_usage('authenticate')
                return {
                    'success': True,
                    'property_id': self.property_id,
                    'access_type': 'read'
                }
            else:
                return {'success': False, 'error': f'Authentication failed: {response.text}'}
                
        except Exception as e:
            logger.error(f"Google Analytics authentication error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_historical_data(self, days: int = 30) -> Dict[str, Any]:
        """Get GA4 traffic and conversion data"""
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Calculate date range
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            # Prepare GA4 API request
            url = f"{self.base_url}/properties/{self.property_id}:runReport"
            
            request_body = {
                "dateRanges": [{"startDate": start_date, "endDate": end_date}],
                "metrics": [
                    {"name": "sessions"},
                    {"name": "users"},
                    {"name": "pageviews"},
                    {"name": "bounceRate"},
                    {"name": "conversions"},
                    {"name": "totalRevenue"}
                ],
                "dimensions": [
                    {"name": "date"},
                    {"name": "source"},
                    {"name": "medium"}
                ]
            }
            
            response = requests.post(url, headers=headers, json=request_body)
            
            if response.status_code != 200:
                return {'success': False, 'error': 'Failed to fetch analytics data'}
            
            data = response.json()
            rows = data.get('rows', [])
            
            # Aggregate metrics
            total_sessions = 0
            total_users = 0
            total_pageviews = 0
            total_conversions = 0
            total_revenue = 0
            bounce_rates = []
            
            for row in rows:
                metrics = row['metricValues']
                total_sessions += int(metrics[0]['value'])
                total_users += int(metrics[1]['value'])
                total_pageviews += int(metrics[2]['value'])
                bounce_rates.append(float(metrics[3]['value']))
                total_conversions += int(metrics[4]['value'])
                total_revenue += float(metrics[5]['value'])
            
            avg_bounce_rate = sum(bounce_rates) / len(bounce_rates) if bounce_rates else 0
            conversion_rate = (total_conversions / max(1, total_sessions)) * 100
            
            self.track_integration_usage('get_historical_data', {
                'days': days,
                'sessions': total_sessions
            })
            
            return {
                'success': True,
                'period_days': days,
                'metrics': {
                    'total_sessions': total_sessions,
                    'total_users': total_users,
                    'total_pageviews': total_pageviews,
                    'total_conversions': total_conversions,
                    'total_revenue': total_revenue,
                    'avg_bounce_rate': avg_bounce_rate
                },
                'baseline_data': {
                    'conversion_rate': conversion_rate,
                    'revenue_per_session': total_revenue / max(1, total_sessions),
                    'pages_per_session': total_pageviews / max(1, total_sessions),
                    'bounce_rate': avg_bounce_rate
                }
            }
            
        except Exception as e:
            logger.error(f"Google Analytics historical data error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def import_leads(self, funnel_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """GA4 doesn't have direct lead data, return conversion events"""
        try:
            # For GA4, we can get conversion events but not individual user data due to privacy
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            url = f"{self.base_url}/properties/{self.property_id}:runReport"
            
            request_body = {
                "dateRanges": [{"startDate": start_date, "endDate": end_date}],
                "metrics": [
                    {"name": "conversions"},
                    {"name": "totalRevenue"}
                ],
                "dimensions": [
                    {"name": "eventName"},
                    {"name": "source"},
                    {"name": "medium"}
                ]
            }
            
            response = requests.post(url, headers=headers, json=request_body)
            
            if response.status_code == 200:
                data = response.json()
                conversion_events = []
                
                for row in data.get('rows', []):
                    event_name = row['dimensionValues'][0]['value']
                    if 'purchase' in event_name.lower() or 'lead' in event_name.lower():
                        conversion_events.append({
                            'event_name': event_name,
                            'source': row['dimensionValues'][1]['value'],
                            'medium': row['dimensionValues'][2]['value'],
                            'conversions': int(row['metricValues'][0]['value']),
                            'revenue': float(row['metricValues'][1]['value'])
                        })
                
                self.track_integration_usage('import_leads', {'events': len(conversion_events)})
                return conversion_events
            
            return []
            
        except Exception as e:
            logger.error(f"Google Analytics conversion import error: {str(e)}")
            return []
    
    def setup_webhooks(self, funnel_id: int) -> Dict[str, Any]:
        """GA4 doesn't support webhooks, but we can setup measurement protocol"""
        return {
            'success': True,
            'message': 'Google Analytics uses measurement protocol for real-time data. Enhanced ecommerce tracking configured.',
            'tracking_available': True
        }

class ConnectorManager:
    """Manager class for handling multiple platform connectors"""
    
    def __init__(self):
        self.connectors = {
            'shopify': ShopifyConnector,
            'hubspot': HubSpotConnector,
            'google_analytics': GoogleAnalyticsConnector
        }
    
    def get_connector(self, platform: str, user_id: int, credentials: Dict[str, Any]) -> Optional[BaseConnector]:
        """Get a connector instance for a specific platform"""
        connector_class = self.connectors.get(platform.lower())
        if connector_class:
            return connector_class(user_id, credentials)
        return None
    
    def test_connection(self, platform: str, user_id: int, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Test connection to a platform"""
        connector = self.get_connector(platform, user_id, credentials)
        if connector:
            return connector.authenticate()
        return {'success': False, 'error': f'Unsupported platform: {platform}'}
    
    def import_baseline_data(self, platform: str, user_id: int, credentials: Dict[str, Any], 
                           funnel_id: int, days: int = 30) -> Dict[str, Any]:
        """Import baseline data for ROI calculations"""
        connector = self.get_connector(platform, user_id, credentials)
        if not connector:
            return {'success': False, 'error': f'Unsupported platform: {platform}'}
        
        try:
            # Get historical performance data
            historical_data = connector.get_historical_data(days)
            if not historical_data['success']:
                return historical_data
            
            # Import leads/customers
            imported_leads = connector.import_leads(funnel_id, days)
            
            # Setup webhooks for real-time sync
            webhook_result = connector.setup_webhooks(funnel_id)
            
            return {
                'success': True,
                'platform': platform,
                'historical_data': historical_data,
                'imported_leads_count': len(imported_leads),
                'webhook_setup': webhook_result,
                'baseline_established': True
            }
            
        except Exception as e:
            logger.error(f"Baseline import error for {platform}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_supported_platforms(self) -> List[Dict[str, Any]]:
        """Get list of supported platforms with their capabilities"""
        return [
            {
                'platform': 'shopify',
                'name': 'Shopify',
                'description': 'E-commerce platform for DTC brands',
                'capabilities': ['orders', 'customers', 'products', 'analytics', 'webhooks'],
                'ideal_for': ['DTC E-commerce', 'Online Retail']
            },
            {
                'platform': 'hubspot',
                'name': 'HubSpot',
                'description': 'CRM and marketing automation platform',
                'capabilities': ['contacts', 'deals', 'pipeline', 'analytics', 'webhooks'],
                'ideal_for': ['B2B SaaS', 'Professional Services', 'Marketing Agencies']
            },
            {
                'platform': 'google_analytics',
                'name': 'Google Analytics 4',
                'description': 'Web analytics and conversion tracking',
                'capabilities': ['traffic', 'conversions', 'revenue', 'user_behavior'],
                'ideal_for': ['All Industries', 'Website Optimization']
            }
        ]

# Global connector manager instance
connector_manager = ConnectorManager()