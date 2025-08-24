"""
Sales Funnel Optimizer - Industry Vertical Templates
Pre-built funnels, benchmark KPIs, and automations for target market segments
"""

import json
from datetime import datetime
from typing import Dict, List, Any
from app import db
from sales_funnel_models import SalesFunnel, Lead

class VerticalTemplateService:
    """Service for managing industry-specific funnel templates"""
    
    def __init__(self):
        self.templates = {
            'dtc_ecommerce': self._get_dtc_template(),
            'b2b_saas': self._get_b2b_saas_template(),
            'home_services': self._get_home_services_template(),
            'marketing_agency': self._get_marketing_agency_template(),
            'education_courses': self._get_education_template(),
            'real_estate': self._get_real_estate_template()
        }
    
    def _get_dtc_template(self) -> Dict[str, Any]:
        """DTC E-commerce funnel template"""
        return {
            'template_id': 'dtc_ecommerce',
            'name': 'DTC E-commerce Sales Funnel',
            'description': 'Optimized for direct-to-consumer brands with $5M-$100M revenue',
            'target_revenue_range': '$5M-$100M',
            'ideal_aov': '$60-$300',
            'tech_stack': ['Shopify', 'BigCommerce', 'Klaviyo', 'Meta Ads', 'Google Ads', 'GA4'],
            'stages': [
                {
                    'name': 'Ad Click',
                    'description': 'Visitor clicks on paid ad',
                    'benchmark_conversion': 100.0,  # Entry point
                    'benchmark_time_to_next': 0,  # Immediate
                    'key_metrics': ['CPM', 'CTR', 'CPC'],
                    'ai_optimizations': [
                        'Ad creative fatigue detection',
                        'Audience expansion recommendations',
                        'Bid optimization alerts'
                    ]
                },
                {
                    'name': 'Landing Page Visit',
                    'description': 'Visitor arrives on product/category page',
                    'benchmark_conversion': 45.0,  # 45% view product
                    'benchmark_time_to_next': 30,  # 30 seconds average
                    'key_metrics': ['Bounce Rate', 'Time on Page', 'Page Views'],
                    'ai_optimizations': [
                        'A/B test headlines and CTAs',
                        'Product recommendation engine',
                        'Exit-intent popup optimization'
                    ]
                },
                {
                    'name': 'Product View',
                    'description': 'Customer views specific product',
                    'benchmark_conversion': 25.0,  # 25% add to cart
                    'benchmark_time_to_next': 120,  # 2 minutes browsing
                    'key_metrics': ['Product Page Views', 'Reviews Read', 'Image Interactions'],
                    'ai_optimizations': [
                        'Dynamic product descriptions',
                        'Social proof optimization',
                        'Cross-sell recommendations'
                    ]
                },
                {
                    'name': 'Add to Cart',
                    'description': 'Customer adds product to cart',
                    'benchmark_conversion': 70.0,  # 70% proceed to checkout
                    'benchmark_time_to_next': 300,  # 5 minutes cart review
                    'key_metrics': ['Cart Abandonment Rate', 'Average Cart Value', 'Items per Cart'],
                    'ai_optimizations': [
                        'Cart abandonment email triggers',
                        'Upsell/cross-sell at cart',
                        'Shipping calculator optimization'
                    ]
                },
                {
                    'name': 'Checkout Started',
                    'description': 'Customer begins checkout process',
                    'benchmark_conversion': 85.0,  # 85% complete purchase
                    'benchmark_time_to_next': 180,  # 3 minutes checkout
                    'key_metrics': ['Checkout Abandonment', 'Form Completion Rate', 'Payment Method Usage'],
                    'ai_optimizations': [
                        'One-click checkout optimization',
                        'Payment method recommendations',
                        'Trust badge placement'
                    ]
                },
                {
                    'name': 'Purchase Complete',
                    'description': 'Customer completes purchase',
                    'benchmark_conversion': 100.0,  # Purchase complete
                    'benchmark_time_to_next': 0,
                    'key_metrics': ['AOV', 'Purchase Rate', 'Payment Success Rate'],
                    'ai_optimizations': [
                        'Post-purchase upsells',
                        'Review request automation',
                        'Loyalty program enrollment'
                    ]
                }
            ],
            'benchmark_kpis': {
                'overall_conversion_rate': '2.5%',
                'average_order_value': '$150',
                'cart_abandonment_rate': '69%',
                'checkout_abandonment_rate': '18%',
                'customer_acquisition_cost': '$45',
                'return_on_ad_spend': '4:1',
                'customer_lifetime_value': '$450'
            },
            'quick_wins': [
                'Implement exit-intent popups (5-15% conversion boost)',
                'Add cart abandonment email sequence (10-25% recovery)',
                'Optimize checkout form fields (5-10% completion boost)',
                'Add urgency/scarcity elements (3-8% conversion boost)',
                'Implement one-click upsells (15-30% AOV increase)'
            ],
            'automation_triggers': [
                'Cart abandonment after 30 minutes',
                'Browse abandonment after 24 hours',
                'Post-purchase review request after 7 days',
                'Replenishment reminder based on product cycle',
                'Win-back campaign after 90 days inactive'
            ]
        }
    
    def _get_b2b_saas_template(self) -> Dict[str, Any]:
        """B2B SaaS funnel template"""
        return {
            'template_id': 'b2b_saas',
            'name': 'B2B SaaS Sales Funnel',
            'description': 'Optimized for Series A-C SaaS companies with $3M-$75M ARR',
            'target_revenue_range': '$3M-$75M ARR',
            'ideal_acv': '$2,000-$50,000',
            'tech_stack': ['HubSpot', 'Salesforce', 'Marketo', 'LinkedIn Ads', 'Google Ads', 'Mixpanel'],
            'stages': [
                {
                    'name': 'Website Visit',
                    'description': 'Prospect visits website from organic or paid traffic',
                    'benchmark_conversion': 100.0,  # Entry point
                    'benchmark_time_to_next': 0,
                    'key_metrics': ['Traffic Sources', 'Page Views', 'Session Duration'],
                    'ai_optimizations': [
                        'Personalized content by industry',
                        'Intent-based CTAs',
                        'Progressive profiling'
                    ]
                },
                {
                    'name': 'Content Engagement',
                    'description': 'Prospect engages with content (blog, resources)',
                    'benchmark_conversion': 15.0,  # 15% become leads
                    'benchmark_time_to_next': 300,  # 5 minutes reading
                    'key_metrics': ['Content Views', 'Time on Page', 'Download Rate'],
                    'ai_optimizations': [
                        'Content recommendation engine',
                        'Gated content optimization',
                        'Lead scoring based on content consumption'
                    ]
                },
                {
                    'name': 'Marketing Qualified Lead (MQL)',
                    'description': 'Prospect submits form and meets MQL criteria',
                    'benchmark_conversion': 25.0,  # 25% become SQLs
                    'benchmark_time_to_next': 432000,  # 5 days nurturing
                    'key_metrics': ['Form Completion Rate', 'Lead Score', 'Source Quality'],
                    'ai_optimizations': [
                        'Dynamic lead scoring',
                        'Automated nurture sequences',
                        'Sales alert optimization'
                    ]
                },
                {
                    'name': 'Sales Qualified Lead (SQL)',
                    'description': 'Lead qualifies for sales outreach',
                    'benchmark_conversion': 30.0,  # 30% book meetings
                    'benchmark_time_to_next': 259200,  # 3 days to book
                    'key_metrics': ['Response Rate', 'Meeting Booking Rate', 'Qualification Rate'],
                    'ai_optimizations': [
                        'Optimal outreach timing',
                        'Personalized messaging',
                        'Channel preference optimization'
                    ]
                },
                {
                    'name': 'Discovery Call',
                    'description': 'Initial sales conversation and qualification',
                    'benchmark_conversion': 60.0,  # 60% advance to demo
                    'benchmark_time_to_next': 604800,  # 7 days to demo
                    'key_metrics': ['Show Rate', 'Qualification Rate', 'Next Step Rate'],
                    'ai_optimizations': [
                        'Meeting preparation insights',
                        'Question optimization',
                        'Follow-up automation'
                    ]
                },
                {
                    'name': 'Product Demo',
                    'description': 'Product demonstration and value presentation',
                    'benchmark_conversion': 40.0,  # 40% advance to proposal
                    'benchmark_time_to_next': 604800,  # 7 days to proposal
                    'key_metrics': ['Demo Completion Rate', 'Feature Interest', 'Technical Questions'],
                    'ai_optimizations': [
                        'Demo customization by role',
                        'Feature priority recommendations',
                        'Objection handling prompts'
                    ]
                },
                {
                    'name': 'Proposal/Trial',
                    'description': 'Formal proposal or trial access provided',
                    'benchmark_conversion': 50.0,  # 50% close as customers
                    'benchmark_time_to_next': 1209600,  # 14 days decision
                    'key_metrics': ['Proposal Accept Rate', 'Trial Engagement', 'Negotiation Cycles'],
                    'ai_optimizations': [
                        'Proposal personalization',
                        'Trial engagement tracking',
                        'Decision maker identification'
                    ]
                },
                {
                    'name': 'Customer',
                    'description': 'Closed deal, customer onboarding',
                    'benchmark_conversion': 100.0,  # Customer
                    'benchmark_time_to_next': 0,
                    'key_metrics': ['Deal Size', 'Time to Close', 'Onboarding Success'],
                    'ai_optimizations': [
                        'Expansion opportunity identification',
                        'Onboarding automation',
                        'Success metric tracking'
                    ]
                }
            ],
            'benchmark_kpis': {
                'website_to_mql': '2-5%',
                'mql_to_sql': '20-30%',
                'sql_to_customer': '15-25%',
                'average_deal_size': '$15,000',
                'sales_cycle_length': '45-90 days',
                'customer_acquisition_cost': '$2,500',
                'monthly_recurring_revenue_growth': '10-20%',
                'net_revenue_retention': '110-130%'
            },
            'quick_wins': [
                'Implement progressive profiling (20-40% form completion boost)',
                'Add social proof on key pages (10-25% conversion boost)',
                'Optimize trial signup flow (15-30% trial conversion)',
                'Implement lead scoring automation (25-40% SQL quality boost)',
                'Add meeting booking widget (30-50% booking rate increase)'
            ],
            'automation_triggers': [
                'MQL scoring threshold reached',
                'Content download follow-up sequence',
                'Trial expiration reminders',
                'Meeting no-show follow-up',
                'Proposal follow-up sequence'
            ]
        }
    
    def _get_home_services_template(self) -> Dict[str, Any]:
        """Home Services funnel template"""
        return {
            'template_id': 'home_services',
            'name': 'Home Services Sales Funnel',
            'description': 'Optimized for HVAC, roofing, home improvement companies',
            'target_revenue_range': '$2M-$20M',
            'ideal_job_value': '$500-$15,000',
            'tech_stack': ['ServiceTitan', 'Jobber', 'CallRail', 'Google Ads', 'Facebook Ads', 'HubSpot'],
            'stages': [
                {
                    'name': 'Lead Generation',
                    'description': 'Customer discovers service through ads or search',
                    'benchmark_conversion': 100.0,  # Entry point
                    'benchmark_time_to_next': 0,
                    'key_metrics': ['Lead Source', 'Cost per Lead', 'Lead Volume'],
                    'ai_optimizations': [
                        'Seasonal demand forecasting',
                        'Local SEO optimization',
                        'Ad spend allocation by geography'
                    ]
                },
                {
                    'name': 'Phone Call',
                    'description': 'Customer calls business',
                    'benchmark_conversion': 85.0,  # 85% calls answered
                    'benchmark_time_to_next': 30,  # 30 seconds to answer
                    'key_metrics': ['Call Answer Rate', 'Ring Time', 'Call Quality Score'],
                    'ai_optimizations': [
                        'Call routing optimization',
                        'Script personalization by service',
                        'Missed call recovery automation'
                    ]
                },
                {
                    'name': 'Appointment Scheduled',
                    'description': 'Service appointment booked',
                    'benchmark_conversion': 65.0,  # 65% book appointments
                    'benchmark_time_to_next': 300,  # 5 minute call
                    'key_metrics': ['Booking Rate', 'Appointment Availability', 'Customer Preference'],
                    'ai_optimizations': [
                        'Optimal scheduling recommendations',
                        'Service upsell suggestions',
                        'Technician matching by skills'
                    ]
                },
                {
                    'name': 'Service Visit',
                    'description': 'Technician arrives and diagnoses',
                    'benchmark_conversion': 90.0,  # 90% show rate
                    'benchmark_time_to_next': 172800,  # 2 days average
                    'key_metrics': ['Show Rate', 'On-time Rate', 'Diagnosis Accuracy'],
                    'ai_optimizations': [
                        'Route optimization',
                        'Appointment reminders',
                        'Preparation instructions'
                    ]
                },
                {
                    'name': 'Estimate Provided',
                    'description': 'Customer receives service estimate',
                    'benchmark_conversion': 85.0,  # 85% receive estimates
                    'benchmark_time_to_next': 1800,  # 30 minutes on-site
                    'key_metrics': ['Estimate Accuracy', 'Presentation Quality', 'Option Variety'],
                    'ai_optimizations': [
                        'Dynamic pricing recommendations',
                        'Competitive analysis integration',
                        'Financing option presentation'
                    ]
                },
                {
                    'name': 'Sale Closed',
                    'description': 'Customer approves work',
                    'benchmark_conversion': 40.0,  # 40% close rate
                    'benchmark_time_to_next': 86400,  # 1 day decision
                    'key_metrics': ['Close Rate', 'Average Job Size', 'Payment Method'],
                    'ai_optimizations': [
                        'Objection handling prompts',
                        'Urgency creation strategies',
                        'Follow-up sequence automation'
                    ]
                },
                {
                    'name': 'Work Completed',
                    'description': 'Service work finished and paid',
                    'benchmark_conversion': 95.0,  # 95% completion rate
                    'benchmark_time_to_next': 0,
                    'key_metrics': ['Completion Rate', 'Customer Satisfaction', 'Payment Collection'],
                    'ai_optimizations': [
                        'Quality control checklists',
                        'Review request automation',
                        'Maintenance plan upsells'
                    ]
                }
            ],
            'benchmark_kpis': {
                'lead_to_appointment': '65%',
                'appointment_show_rate': '90%',
                'estimate_to_sale': '40%',
                'average_job_value': '$3,500',
                'cost_per_lead': '$85',
                'customer_acquisition_cost': '$275',
                'seasonal_revenue_variance': '30-50%',
                'repeat_customer_rate': '25%'
            },
            'quick_wins': [
                'Implement speed-to-lead automation (20-40% booking boost)',
                'Add call recording and coaching (15-25% close rate boost)',
                'Optimize appointment scheduling (10-20% show rate boost)',
                'Add financing options presentation (25-40% close rate boost)',
                'Implement review automation (30-50% review volume boost)'
            ],
            'automation_triggers': [
                'Missed call follow-up within 5 minutes',
                'Appointment confirmation 24 hours prior',
                'Post-service review request within 2 hours',
                'Maintenance reminder based on service type',
                'Emergency service priority routing'
            ]
        }
    
    def _get_marketing_agency_template(self) -> Dict[str, Any]:
        """Marketing Agency funnel template"""
        return {
            'template_id': 'marketing_agency',
            'name': 'Marketing Agency Sales Funnel',
            'description': 'Optimized for digital marketing and consulting agencies',
            'target_revenue_range': '$2M-$50M',
            'ideal_client_value': '$5,000-$50,000/month',
            'tech_stack': ['HubSpot', 'Pipedrive', 'ActiveCampaign', 'LinkedIn', 'Google Ads', 'Calendly'],
            'stages': [
                {
                    'name': 'Content Discovery',
                    'description': 'Prospect discovers agency through content marketing',
                    'benchmark_conversion': 100.0,  # Entry point
                    'benchmark_time_to_next': 0,
                    'key_metrics': ['Content Views', 'Engagement Rate', 'Source Attribution'],
                    'ai_optimizations': [
                        'Content personalization by industry',
                        'Distribution channel optimization',
                        'Thought leadership positioning'
                    ]
                },
                {
                    'name': 'Lead Magnet Download',
                    'description': 'Prospect downloads valuable resource',
                    'benchmark_conversion': 8.0,  # 8% download rate
                    'benchmark_time_to_next': 600,  # 10 minutes consideration
                    'key_metrics': ['Download Rate', 'Content Completion', 'Follow-up Engagement'],
                    'ai_optimizations': [
                        'Lead magnet optimization by vertical',
                        'Progressive profiling implementation',
                        'Content scoring and segmentation'
                    ]
                },
                {
                    'name': 'Nurture Sequence',
                    'description': 'Automated email sequence educates prospect',
                    'benchmark_conversion': 12.0,  # 12% book consultation
                    'benchmark_time_to_next': 604800,  # 7 days nurturing
                    'key_metrics': ['Email Open Rate', 'Click Rate', 'Sequence Completion'],
                    'ai_optimizations': [
                        'Send time optimization',
                        'Content personalization',
                        'Behavioral trigger automation'
                    ]
                },
                {
                    'name': 'Strategy Call Booked',
                    'description': 'Prospect schedules consultation call',
                    'benchmark_conversion': 75.0,  # 75% show rate
                    'benchmark_time_to_next': 259200,  # 3 days to call
                    'key_metrics': ['Booking Rate', 'Calendar Utilization', 'Qualification Score'],
                    'ai_optimizations': [
                        'Calendar optimization',
                        'Pre-call questionnaire automation',
                        'Reminder sequence optimization'
                    ]
                },
                {
                    'name': 'Discovery Call',
                    'description': 'Initial consultation and needs assessment',
                    'benchmark_conversion': 50.0,  # 50% advance to proposal
                    'benchmark_time_to_next': 3600,  # 1 hour call
                    'key_metrics': ['Show Rate', 'Call Duration', 'Next Step Rate'],
                    'ai_optimizations': [
                        'Call preparation insights',
                        'Question framework optimization',
                        'Authority positioning strategies'
                    ]
                },
                {
                    'name': 'Proposal Delivered',
                    'description': 'Custom proposal sent to prospect',
                    'benchmark_conversion': 35.0,  # 35% close rate
                    'benchmark_time_to_next': 604800,  # 7 days to deliver
                    'key_metrics': ['Proposal Quality', 'Response Rate', 'Negotiation Frequency'],
                    'ai_optimizations': [
                        'Proposal personalization',
                        'Pricing optimization',
                        'Case study integration'
                    ]
                },
                {
                    'name': 'Client Onboarded',
                    'description': 'Contract signed and client onboarding',
                    'benchmark_conversion': 100.0,  # Client onboarded
                    'benchmark_time_to_next': 0,
                    'key_metrics': ['Contract Value', 'Onboarding Completion', 'Time to Value'],
                    'ai_optimizations': [
                        'Onboarding automation',
                        'Expectation setting optimization',
                        'Success milestone tracking'
                    ]
                }
            ],
            'benchmark_kpis': {
                'content_to_lead': '3-8%',
                'lead_to_consultation': '10-15%',
                'consultation_show_rate': '75%',
                'consultation_to_proposal': '50%',
                'proposal_to_client': '35%',
                'average_client_value': '$8,500/month',
                'sales_cycle_length': '30-60 days',
                'client_retention_rate': '80%'
            },
            'quick_wins': [
                'Implement social proof throughout funnel (15-25% conversion boost)',
                'Add case study library by industry (20-30% proposal win rate boost)',
                'Optimize consultation booking flow (25-40% booking rate boost)',
                'Implement proposal templates (30-50% delivery speed boost)',
                'Add client testimonial automation (20-35% close rate boost)'
            ],
            'automation_triggers': [
                'Lead magnet download follow-up sequence',
                'Consultation booking confirmation and reminders',
                'Proposal delivery and follow-up automation',
                'Client onboarding workflow initiation',
                'Quarterly business review scheduling'
            ]
        }
    
    def _get_education_template(self) -> Dict[str, Any]:
        """Education/Courses funnel template"""
        return {
            'template_id': 'education_courses',
            'name': 'Online Education Sales Funnel',
            'description': 'Optimized for online courses, bootcamps, and education platforms',
            'target_revenue_range': '$2M-$30M',
            'ideal_course_price': '$500-$15,000',
            'tech_stack': ['Teachable', 'Thinkific', 'ClickFunnels', 'Facebook Ads', 'YouTube', 'Email'],
            'stages': [
                {
                    'name': 'Free Content Consumption',
                    'description': 'Prospect discovers and consumes free educational content',
                    'benchmark_conversion': 100.0,
                    'benchmark_time_to_next': 0,
                    'key_metrics': ['Video Completion Rate', 'Content Engagement', 'Channel Growth'],
                    'ai_optimizations': [
                        'Content recommendation engine',
                        'Engagement optimization',
                        'Authority building content'
                    ]
                },
                {
                    'name': 'Email List Signup',
                    'description': 'Prospect joins email list for valuable resource',
                    'benchmark_conversion': 5.0,
                    'benchmark_time_to_next': 900,
                    'key_metrics': ['Opt-in Rate', 'Lead Magnet Performance', 'Source Quality'],
                    'ai_optimizations': [
                        'Lead magnet optimization',
                        'Opt-in form placement',
                        'Value proposition testing'
                    ]
                },
                {
                    'name': 'Webinar Registration',
                    'description': 'Prospect registers for educational webinar',
                    'benchmark_conversion': 25.0,
                    'benchmark_time_to_next': 432000,
                    'key_metrics': ['Registration Rate', 'Email Engagement', 'Topic Interest'],
                    'ai_optimizations': [
                        'Webinar topic optimization',
                        'Registration page testing',
                        'Email sequence optimization'
                    ]
                },
                {
                    'name': 'Webinar Attendance',
                    'description': 'Prospect attends live or recorded webinar',
                    'benchmark_conversion': 45.0,
                    'benchmark_time_to_next': 3600,
                    'key_metrics': ['Show Rate', 'Completion Rate', 'Engagement Level'],
                    'ai_optimizations': [
                        'Attendance optimization',
                        'Content engagement tracking',
                        'Interactive element optimization'
                    ]
                },
                {
                    'name': 'Course Purchase',
                    'description': 'Prospect purchases course or program',
                    'benchmark_conversion': 8.0,
                    'benchmark_time_to_next': 86400,
                    'key_metrics': ['Conversion Rate', 'Cart Abandonment', 'Payment Success'],
                    'ai_optimizations': [
                        'Pricing optimization',
                        'Payment plan offers',
                        'Urgency and scarcity elements'
                    ]
                },
                {
                    'name': 'Course Completion',
                    'description': 'Student completes course and achieves results',
                    'benchmark_conversion': 60.0,
                    'benchmark_time_to_next': 0,
                    'key_metrics': ['Completion Rate', 'Satisfaction Score', 'Results Achievement'],
                    'ai_optimizations': [
                        'Progress tracking automation',
                        'Engagement optimization',
                        'Success milestone celebration'
                    ]
                }
            ],
            'benchmark_kpis': {
                'content_to_email': '3-7%',
                'email_to_webinar': '20-30%',
                'webinar_show_rate': '45%',
                'webinar_to_purchase': '8-15%',
                'course_completion_rate': '60%',
                'average_course_price': '$1,500',
                'customer_lifetime_value': '$2,800',
                'refund_rate': '5-10%'
            },
            'quick_wins': [
                'Implement social proof on sales pages (20-35% conversion boost)',
                'Add payment plans and financing (40-60% purchase rate boost)',
                'Optimize webinar registration flow (25-40% registration boost)',
                'Add course preview content (15-25% purchase rate boost)',
                'Implement urgency and scarcity (10-20% conversion boost)'
            ],
            'automation_triggers': [
                'Email sequence after opt-in',
                'Webinar reminder sequence',
                'Cart abandonment recovery',
                'Course completion congratulations',
                'Upsell sequence for advanced courses'
            ]
        }
    
    def _get_real_estate_template(self) -> Dict[str, Any]:
        """Real Estate funnel template"""
        return {
            'template_id': 'real_estate',
            'name': 'Real Estate Sales Funnel',
            'description': 'Optimized for real estate teams and brokerages',
            'target_revenue_range': '$2M-$20M',
            'ideal_commission': '$5,000-$25,000',
            'tech_stack': ['Chime', 'BoomTown', 'KvCORE', 'Zillow', 'Realtor.com', 'Facebook'],
            'stages': [
                {
                    'name': 'Property Search',
                    'description': 'Prospect searches for properties online',
                    'benchmark_conversion': 100.0,
                    'benchmark_time_to_next': 0,
                    'key_metrics': ['Search Volume', 'Property Views', 'Saved Properties'],
                    'ai_optimizations': [
                        'Property recommendation engine',
                        'Search optimization',
                        'Market trend insights'
                    ]
                },
                {
                    'name': 'Lead Capture',
                    'description': 'Prospect provides contact information for property details',
                    'benchmark_conversion': 8.0,
                    'benchmark_time_to_next': 300,
                    'key_metrics': ['Conversion Rate', 'Form Completion', 'Lead Quality'],
                    'ai_optimizations': [
                        'Lead capture optimization',
                        'Progressive profiling',
                        'Instant response setup'
                    ]
                },
                {
                    'name': 'Agent Contact',
                    'description': 'Agent makes initial contact with prospect',
                    'benchmark_conversion': 85.0,
                    'benchmark_time_to_next': 300,
                    'key_metrics': ['Response Time', 'Contact Rate', 'Conversation Quality'],
                    'ai_optimizations': [
                        'Speed-to-lead optimization',
                        'Contact method selection',
                        'Script personalization'
                    ]
                },
                {
                    'name': 'Property Showing',
                    'description': 'Prospect schedules and attends property viewing',
                    'benchmark_conversion': 40.0,
                    'benchmark_time_to_next': 172800,
                    'key_metrics': ['Showing Rate', 'Multiple Showings', 'Feedback Quality'],
                    'ai_optimizations': [
                        'Showing optimization',
                        'Property matching',
                        'Market education automation'
                    ]
                },
                {
                    'name': 'Offer Submitted',
                    'description': 'Prospect submits offer on property',
                    'benchmark_conversion': 30.0,
                    'benchmark_time_to_next': 86400,
                    'key_metrics': ['Offer Rate', 'Offer Strength', 'Negotiation Success'],
                    'ai_optimizations': [
                        'Offer strategy optimization',
                        'Market analysis automation',
                        'Negotiation support tools'
                    ]
                },
                {
                    'name': 'Transaction Closed',
                    'description': 'Property purchase/sale successfully completed',
                    'benchmark_conversion': 75.0,
                    'benchmark_time_to_next': 0,
                    'key_metrics': ['Close Rate', 'Transaction Value', 'Satisfaction Score'],
                    'ai_optimizations': [
                        'Transaction management',
                        'Timeline optimization',
                        'Service excellence tracking'
                    ]
                }
            ],
            'benchmark_kpis': {
                'lead_conversion_rate': '5-10%',
                'showing_to_offer': '30%',
                'offer_acceptance_rate': '75%',
                'average_commission': '$12,000',
                'transaction_timeline': '30-45 days',
                'client_satisfaction': '95%',
                'referral_rate': '35%',
                'repeat_client_rate': '20%'
            },
            'quick_wins': [
                'Implement speed-to-lead automation (30-50% contact rate boost)',
                'Add property valuation tools (25-40% lead quality boost)',
                'Optimize showing scheduling (20-30% showing rate boost)',
                'Add market reports automation (15-25% engagement boost)',
                'Implement referral automation (40-60% referral rate boost)'
            ],
            'automation_triggers': [
                'Instant lead notification and response',
                'Property match alerts based on criteria',
                'Market update reports monthly',
                'Transaction milestone notifications',
                'Post-close satisfaction and referral requests'
            ]
        }
    
    def create_funnel_from_template(self, user_id: int, template_id: str, 
                                   custom_name: str = None) -> Dict[str, Any]:
        """Create a new sales funnel from a vertical template"""
        
        if template_id not in self.templates:
            return {'success': False, 'error': f'Template {template_id} not found'}
        
        template = self.templates[template_id]
        
        try:
            # Create the main funnel
            funnel = SalesFunnel()
            funnel.user_id = user_id
            funnel.funnel_name = custom_name or template['name']
            funnel.description = template['description']
            funnel.target_market = template_id
            funnel.status = 'active'
            
            # Store stages configuration
            funnel.stages_config = json.dumps(template['stages'])
            
            # Store automation rules
            funnel.automation_rules = json.dumps(template['automation_triggers'])
            
            db.session.add(funnel)
            db.session.flush()  # Get the funnel ID
            
            # Additional template metadata can be stored as needed
            # The main functionality is in stages_config and automation_rules
            
            db.session.commit()
            
            return {
                'success': True,
                'funnel_id': funnel.id,
                'template_applied': template_id,
                'stages_configured': len(template['stages']),
                'quick_wins': template['quick_wins']
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def get_template_recommendations(self, user_industry: str = None, 
                                   revenue_range: str = None) -> List[Dict[str, Any]]:
        """Get template recommendations based on user characteristics"""
        
        recommendations = []
        
        for template_id, template in self.templates.items():
            score = 0
            reasons = []
            
            # Industry matching
            if user_industry:
                if user_industry.lower() in template_id.lower():
                    score += 50
                    reasons.append(f"Perfect industry match for {user_industry}")
                elif any(keyword in template['description'].lower() 
                        for keyword in user_industry.lower().split()):
                    score += 25
                    reasons.append(f"Related to {user_industry} industry")
            
            # Revenue range matching
            if revenue_range and 'target_revenue_range' in template:
                # Simple revenue matching logic
                if revenue_range in template['target_revenue_range']:
                    score += 30
                    reasons.append("Revenue range matches your business size")
            
            # Add general benefits
            score += len(template['quick_wins']) * 5
            reasons.extend([f"Quick win: {win[:50]}..." for win in template['quick_wins'][:2]])
            
            recommendations.append({
                'template_id': template_id,
                'name': template['name'],
                'description': template['description'],
                'score': score,
                'reasons': reasons,
                'benchmark_kpis': template['benchmark_kpis'],
                'quick_wins_count': len(template['quick_wins']),
                'stages_count': len(template['stages'])
            })
        
        # Sort by score (highest first)
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return recommendations

# Global service instance
vertical_template_service = VerticalTemplateService()