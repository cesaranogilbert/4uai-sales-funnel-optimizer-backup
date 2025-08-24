"""
Sales Funnel Optimizer - ROI Baseline & Performance Fee Service
Automated ROI tracking, baseline calculation, and performance-based fee computation
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
from decimal import Decimal, ROUND_HALF_UP
import statistics

from app import db
from sales_funnel_models import SalesFunnel, Lead, FunnelAnalytics
from sales_funnel_subscription_service import sales_funnel_subscription_service

# Configure logging
logger = logging.getLogger(__name__)

class ROIBaselineService:
    """Service for calculating and managing ROI baselines and performance fees"""
    
    def __init__(self):
        self.performance_fee_rates = {
            'starter': 0.05,  # 5% performance fee
            'professional': 0.07,  # 7% performance fee  
            'enterprise': 0.10   # 10% performance fee
        }
        
        self.minimum_improvement_threshold = 0.05  # 5% minimum improvement to trigger fees
        
    def calculate_baseline_metrics(self, funnel_id: int, platform_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate baseline performance metrics from imported platform data"""
        
        try:
            funnel = SalesFunnel.query.get(funnel_id)
            if not funnel:
                return {'success': False, 'error': 'Funnel not found'}
            
            # Extract metrics based on platform
            platform = platform_data.get('platform', 'unknown')
            metrics = platform_data.get('metrics', {})
            baseline_data = platform_data.get('baseline_data', {})
            period_days = platform_data.get('period_days', 30)
            
            # Standardize baseline metrics across all platforms
            standardized_baseline = self._standardize_baseline_metrics(platform, metrics, baseline_data)
            
            # Calculate key performance indicators
            roi_baseline = {
                'platform': platform,
                'calculation_date': datetime.utcnow().isoformat(),
                'period_days': period_days,
                'baseline_metrics': standardized_baseline,
                'raw_platform_data': {
                    'metrics': metrics,
                    'baseline_data': baseline_data
                },
                'performance_targets': self._calculate_performance_targets(standardized_baseline),
                'fee_calculation_ready': True
            }
            
            # Store baseline in funnel
            automation_rules = json.loads(funnel.automation_rules) if funnel.automation_rules else {}
            automation_rules['roi_baseline'] = roi_baseline
            funnel.automation_rules = json.dumps(automation_rules)
            
            # Update funnel financial metrics
            funnel.total_investment = standardized_baseline.get('operational_costs', 0)
            funnel.generated_revenue = standardized_baseline.get('total_revenue', 0)
            funnel.calculated_roi = standardized_baseline.get('roi_percentage', 0)
            
            db.session.commit()
            
            logger.info(f"ROI baseline calculated for funnel {funnel_id} with {platform} data")
            
            return {
                'success': True,
                'funnel_id': funnel_id,
                'platform': platform,
                'baseline_metrics': standardized_baseline,
                'performance_targets': roi_baseline['performance_targets'],
                'baseline_revenue': standardized_baseline.get('total_revenue', 0),
                'baseline_conversion_rate': standardized_baseline.get('conversion_rate', 0)
            }
            
        except Exception as e:
            logger.error(f"Error calculating baseline metrics: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _standardize_baseline_metrics(self, platform: str, metrics: Dict[str, Any], 
                                    baseline_data: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize metrics from different platforms into common format"""
        
        standardized = {
            'total_revenue': 0.0,
            'total_transactions': 0,
            'conversion_rate': 0.0,
            'average_order_value': 0.0,
            'total_leads': 0,
            'cost_per_lead': 0.0,
            'customer_acquisition_cost': 0.0,
            'lifetime_value': 0.0,
            'roi_percentage': 0.0,
            'operational_costs': 0.0
        }
        
        if platform == 'shopify':
            standardized.update({
                'total_revenue': metrics.get('total_revenue', 0),
                'total_transactions': metrics.get('total_orders', 0),
                'conversion_rate': baseline_data.get('conversion_rate', 0),
                'average_order_value': metrics.get('average_order_value', 0),
                'total_leads': metrics.get('total_orders', 0) + metrics.get('abandoned_checkouts', 0),
                'customer_acquisition_cost': self._estimate_cac(metrics.get('total_revenue', 0), 
                                                              metrics.get('total_orders', 0)),
                'operational_costs': metrics.get('total_revenue', 0) * 0.3  # Estimate 30% operational costs
            })
            
        elif platform == 'hubspot':
            standardized.update({
                'total_revenue': metrics.get('total_revenue', 0),
                'total_transactions': metrics.get('closed_won_deals', 0),
                'conversion_rate': baseline_data.get('deal_close_rate', 0),
                'average_order_value': metrics.get('average_deal_value', 0),
                'total_leads': metrics.get('total_contacts', 0),
                'cost_per_lead': self._estimate_cost_per_lead(metrics.get('total_contacts', 0)),
                'customer_acquisition_cost': self._estimate_cac(metrics.get('total_revenue', 0),
                                                              metrics.get('closed_won_deals', 0))
            })
            
        elif platform == 'google_analytics':
            revenue = metrics.get('total_revenue', 0)
            conversions = metrics.get('total_conversions', 0)
            sessions = metrics.get('total_sessions', 0)
            
            standardized.update({
                'total_revenue': revenue,
                'total_transactions': conversions,
                'conversion_rate': baseline_data.get('conversion_rate', 0),
                'average_order_value': revenue / max(1, conversions),
                'total_leads': sessions,  # Using sessions as lead proxy
                'cost_per_lead': self._estimate_cost_per_lead(sessions),
                'customer_acquisition_cost': self._estimate_cac(revenue, conversions)
            })
        
        # Calculate ROI percentage
        if standardized['operational_costs'] > 0:
            standardized['roi_percentage'] = ((standardized['total_revenue'] - 
                                            standardized['operational_costs']) / 
                                           standardized['operational_costs']) * 100
        
        # Estimate lifetime value (simplified calculation)
        if standardized['total_transactions'] > 0:
            standardized['lifetime_value'] = standardized['average_order_value'] * 2.5  # Conservative estimate
            
        return standardized
    
    def _estimate_cac(self, revenue: float, customers: int) -> float:
        """Estimate customer acquisition cost based on industry benchmarks"""
        if customers == 0:
            return 0.0
        # Conservative estimate: 20% of revenue as marketing/sales cost
        return (revenue * 0.20) / customers
    
    def _estimate_cost_per_lead(self, leads: int) -> float:
        """Estimate cost per lead based on industry benchmarks"""
        if leads == 0:
            return 0.0
        # Conservative estimate: $25 per lead average
        return min(25.0, 1000.0 / leads)
    
    def _calculate_performance_targets(self, baseline: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate performance improvement targets for fee calculation"""
        
        targets = {}
        
        # Revenue targets (10%, 25%, 50% improvement tiers)
        base_revenue = baseline.get('total_revenue', 0)
        targets['revenue'] = {
            'tier_1': base_revenue * 1.10,  # 10% improvement
            'tier_2': base_revenue * 1.25,  # 25% improvement
            'tier_3': base_revenue * 1.50,  # 50% improvement
            'baseline': base_revenue
        }
        
        # Conversion rate targets
        base_conversion = baseline.get('conversion_rate', 0)
        targets['conversion_rate'] = {
            'tier_1': base_conversion * 1.15,  # 15% improvement
            'tier_2': base_conversion * 1.30,  # 30% improvement
            'tier_3': base_conversion * 1.50,  # 50% improvement
            'baseline': base_conversion
        }
        
        # AOV/Deal Value targets
        base_aov = baseline.get('average_order_value', 0)
        targets['average_order_value'] = {
            'tier_1': base_aov * 1.10,  # 10% improvement
            'tier_2': base_aov * 1.20,  # 20% improvement
            'tier_3': base_aov * 1.35,  # 35% improvement
            'baseline': base_aov
        }
        
        # ROI targets
        base_roi = baseline.get('roi_percentage', 0)
        targets['roi_percentage'] = {
            'tier_1': base_roi + 15,  # +15 percentage points
            'tier_2': base_roi + 30,  # +30 percentage points  
            'tier_3': base_roi + 50,  # +50 percentage points
            'baseline': base_roi
        }
        
        return targets
    
    def calculate_performance_fees(self, funnel_id: int, current_period_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate performance fees based on improvement over baseline"""
        
        try:
            funnel = SalesFunnel.query.get(funnel_id)
            if not funnel:
                return {'success': False, 'error': 'Funnel not found'}
            
            # Get ROI baseline data
            automation_rules = json.loads(funnel.automation_rules) if funnel.automation_rules else {}
            roi_baseline = automation_rules.get('roi_baseline')
            
            if not roi_baseline:
                return {'success': False, 'error': 'No ROI baseline found. Please import baseline data first.'}
            
            # Get user subscription for fee rate
            subscription = sales_funnel_subscription_service.get_user_subscription(funnel.user_id)
            plan_name = 'starter'  # Default to starter plan
            if subscription:
                # Handle both dict and object return types
                if hasattr(subscription, 'plan_name'):
                    plan_name = subscription.plan_name.lower()
                elif isinstance(subscription, dict) and subscription.get('plan'):
                    plan_name = subscription['plan'].get('plan_name', 'starter').lower()
            fee_rate = self.performance_fee_rates.get(plan_name, 0.05)
            
            baseline_metrics = roi_baseline['baseline_metrics']
            performance_targets = roi_baseline['performance_targets']
            
            # Calculate current performance metrics
            current_metrics = self._standardize_baseline_metrics(
                current_period_data.get('platform', roi_baseline['platform']),
                current_period_data.get('metrics', {}),
                current_period_data.get('baseline_data', {})
            )
            
            # Calculate improvements
            improvements = self._calculate_improvements(baseline_metrics, current_metrics)
            
            # Determine fee tier and calculate fees
            fee_calculation = self._calculate_tiered_fees(
                improvements, performance_targets, current_metrics, fee_rate
            )
            
            # Update funnel performance tracking
            funnel.generated_revenue = current_metrics.get('total_revenue', 0)
            funnel.calculated_roi = current_metrics.get('roi_percentage', 0)
            
            # Store performance calculation
            performance_data = {
                'calculation_date': datetime.utcnow().isoformat(),
                'baseline_metrics': baseline_metrics,
                'current_metrics': current_metrics,
                'improvements': improvements,
                'fee_calculation': fee_calculation,
                'fee_rate_applied': fee_rate,
                'plan_name': plan_name
            }
            
            automation_rules['latest_performance'] = performance_data
            funnel.automation_rules = json.dumps(automation_rules)
            db.session.commit()
            
            logger.info(f"Performance fees calculated for funnel {funnel_id}: ${fee_calculation['total_fees']:.2f}")
            
            return {
                'success': True,
                'funnel_id': funnel_id,
                'baseline_revenue': baseline_metrics.get('total_revenue', 0),
                'current_revenue': current_metrics.get('total_revenue', 0),
                'revenue_improvement': improvements.get('revenue', {}).get('percentage', 0),
                'total_fees': fee_calculation['total_fees'],
                'fee_breakdown': fee_calculation['breakdown'],
                'fee_rate': fee_rate,
                'qualifying_improvements': improvements
            }
            
        except Exception as e:
            logger.error(f"Error calculating performance fees: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _calculate_improvements(self, baseline: Dict[str, Any], current: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate percentage improvements from baseline to current performance"""
        
        improvements = {}
        
        key_metrics = ['total_revenue', 'conversion_rate', 'average_order_value', 'roi_percentage']
        
        for metric in key_metrics:
            baseline_value = baseline.get(metric, 0)
            current_value = current.get(metric, 0)
            
            if baseline_value > 0:
                absolute_change = current_value - baseline_value
                percentage_change = (absolute_change / baseline_value) * 100
                
                improvements[metric] = {
                    'baseline': baseline_value,
                    'current': current_value,
                    'absolute_change': absolute_change,
                    'percentage': percentage_change,
                    'improved': percentage_change > self.minimum_improvement_threshold * 100
                }
            else:
                improvements[metric] = {
                    'baseline': baseline_value,
                    'current': current_value,
                    'absolute_change': current_value,
                    'percentage': 0,
                    'improved': False
                }
        
        return improvements
    
    def _calculate_tiered_fees(self, improvements: Dict[str, Any], targets: Dict[str, Any], 
                              current_metrics: Dict[str, Any], fee_rate: float) -> Dict[str, Any]:
        """Calculate tiered performance fees based on achievement levels"""
        
        breakdown = {}
        total_fees = 0.0
        
        # Revenue-based fees (primary fee structure)
        revenue_improvement = improvements.get('total_revenue', {})
        if revenue_improvement.get('improved', False):
            incremental_revenue = max(0, revenue_improvement.get('absolute_change', 0))
            
            # Apply fee rate to incremental revenue only
            revenue_fee = incremental_revenue * fee_rate
            total_fees += revenue_fee
            
            breakdown['revenue_fee'] = {
                'incremental_revenue': incremental_revenue,
                'fee_rate': fee_rate,
                'fee_amount': revenue_fee,
                'improvement_percentage': revenue_improvement.get('percentage', 0)
            }
        
        # Conversion rate bonus fees (applied to total current revenue)
        conversion_improvement = improvements.get('conversion_rate', {})
        if conversion_improvement.get('improved', False) and conversion_improvement.get('percentage', 0) > 15:
            # Bonus fee for significant conversion improvements
            current_revenue = current_metrics.get('total_revenue', 0)
            conversion_bonus_rate = min(0.02, (conversion_improvement.get('percentage', 0) - 15) * 0.001)
            conversion_bonus = current_revenue * conversion_bonus_rate
            total_fees += conversion_bonus
            
            breakdown['conversion_bonus'] = {
                'improvement_percentage': conversion_improvement.get('percentage', 0),
                'bonus_rate': conversion_bonus_rate,
                'bonus_amount': conversion_bonus,
                'applied_to_revenue': current_revenue
            }
        
        # AOV improvement bonus
        aov_improvement = improvements.get('average_order_value', {})
        if aov_improvement.get('improved', False) and aov_improvement.get('percentage', 0) > 10:
            # Small bonus for AOV improvements
            aov_bonus_rate = min(0.01, (aov_improvement.get('percentage', 0) - 10) * 0.0005)
            aov_bonus = current_metrics.get('total_revenue', 0) * aov_bonus_rate
            total_fees += aov_bonus
            
            breakdown['aov_bonus'] = {
                'improvement_percentage': aov_improvement.get('percentage', 0),
                'bonus_rate': aov_bonus_rate,
                'bonus_amount': aov_bonus
            }
        
        # Cap total fees at reasonable percentage of current revenue
        current_revenue = current_metrics.get('total_revenue', 0)
        max_fee_cap = current_revenue * 0.15  # 15% maximum of total revenue
        if total_fees > max_fee_cap and current_revenue > 0:
            breakdown['fee_cap_applied'] = {
                'calculated_fees': total_fees,
                'capped_fees': max_fee_cap,
                'cap_percentage': 0.15
            }
            total_fees = max_fee_cap
        
        return {
            'total_fees': round(total_fees, 2),
            'breakdown': breakdown,
            'fee_qualifying': total_fees > 0
        }
    
    def get_funnel_roi_summary(self, funnel_id: int) -> Dict[str, Any]:
        """Get comprehensive ROI and performance fee summary for a funnel"""
        
        try:
            funnel = SalesFunnel.query.get(funnel_id)
            if not funnel:
                return {'success': False, 'error': 'Funnel not found'}
            
            automation_rules = json.loads(funnel.automation_rules) if funnel.automation_rules else {}
            roi_baseline = automation_rules.get('roi_baseline')
            latest_performance = automation_rules.get('latest_performance')
            
            summary = {
                'funnel_id': funnel_id,
                'funnel_name': funnel.funnel_name,
                'baseline_established': roi_baseline is not None,
                'performance_tracking_active': latest_performance is not None
            }
            
            if roi_baseline:
                summary['baseline'] = {
                    'platform': roi_baseline['platform'],
                    'calculation_date': roi_baseline['calculation_date'],
                    'period_days': roi_baseline['period_days'],
                    'baseline_revenue': roi_baseline['baseline_metrics'].get('total_revenue', 0),
                    'baseline_conversion_rate': roi_baseline['baseline_metrics'].get('conversion_rate', 0),
                    'baseline_aov': roi_baseline['baseline_metrics'].get('average_order_value', 0)
                }
            
            if latest_performance:
                summary['current_performance'] = {
                    'calculation_date': latest_performance['calculation_date'],
                    'current_revenue': latest_performance['current_metrics'].get('total_revenue', 0),
                    'current_conversion_rate': latest_performance['current_metrics'].get('conversion_rate', 0),
                    'total_fees_due': latest_performance['fee_calculation'].get('total_fees', 0),
                    'fee_rate': latest_performance.get('fee_rate_applied', 0),
                    'improvements': latest_performance['improvements']
                }
            
            return {'success': True, **summary}
            
        except Exception as e:
            logger.error(f"Error getting ROI summary: {str(e)}")
            return {'success': False, 'error': str(e)}

# Global service instance
roi_baseline_service = ROIBaselineService()