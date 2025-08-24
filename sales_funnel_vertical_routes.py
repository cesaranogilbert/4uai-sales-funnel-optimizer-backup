"""
Sales Funnel Optimizer - Vertical Template Routes
Routes for managing industry-specific funnel templates
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
import json

from app import db
from sales_funnel_vertical_templates import vertical_template_service
from sales_funnel_subscription_service import sales_funnel_subscription_service

vertical_bp = Blueprint('vertical_templates', __name__)

@vertical_bp.route('/templates')
@login_required
def template_gallery():
    """Display available vertical templates"""
    
    # Get user's industry preference if available
    user_industry = request.args.get('industry', '')
    revenue_range = request.args.get('revenue', '')
    
    # Get template recommendations
    recommendations = vertical_template_service.get_template_recommendations(
        user_industry, revenue_range
    )
    
    # Check user's subscription for template access
    subscription = sales_funnel_subscription_service.get_user_subscription(current_user.id)
    
    return render_template('sales_funnel/templates.html',
                         templates=recommendations,
                         user_industry=user_industry,
                         revenue_range=revenue_range,
                         subscription=subscription)

@vertical_bp.route('/template/<template_id>')
@login_required 
def template_detail(template_id):
    """Show detailed view of a specific template"""
    
    if template_id not in vertical_template_service.templates:
        flash('Template not found', 'error')
        return redirect(url_for('vertical_templates.template_gallery'))
    
    template = vertical_template_service.templates[template_id]
    
    # Check usage limits
    usage_check = sales_funnel_subscription_service.check_usage_limits(
        current_user.id, 'sales_funnels'
    )
    
    return render_template('sales_funnel/template_detail.html',
                         template=template,
                         template_id=template_id,
                         usage_check=usage_check)

@vertical_bp.route('/api/create-from-template', methods=['POST'])
@login_required
def api_create_from_template():
    """API endpoint to create funnel from template"""
    
    try:
        data = request.get_json()
        template_id = data.get('template_id')
        custom_name = data.get('custom_name')
        
        if not template_id:
            return jsonify({'error': 'Template ID is required'}), 400
        
        # Check usage limits
        usage_check = sales_funnel_subscription_service.check_usage_limits(
            current_user.id, 'sales_funnels'
        )
        
        if not usage_check['allowed']:
            return jsonify({
                'error': usage_check['reason'],
                'upgrade_required': usage_check.get('upgrade_required', False)
            }), 403
        
        # Create funnel from template
        result = vertical_template_service.create_funnel_from_template(
            current_user.id, template_id, custom_name
        )
        
        if result['success']:
            # Track usage
            sales_funnel_subscription_service.track_usage(
                current_user.id, 'sales_funnels', 
                str(result['funnel_id']), 
                {'template_id': template_id}
            )
            
            return jsonify({
                'success': True,
                'funnel_id': result['funnel_id'],
                'redirect_url': f"/sales-funnel/funnel/{result['funnel_id']}"
            })
        else:
            return jsonify({'error': result['error']}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vertical_bp.route('/api/template-preview/<template_id>')
@login_required
def api_template_preview(template_id):
    """API endpoint to get template preview data"""
    
    if template_id not in vertical_template_service.templates:
        return jsonify({'error': 'Template not found'}), 404
    
    template = vertical_template_service.templates[template_id]
    
    # Return relevant preview data
    preview_data = {
        'name': template['name'],
        'description': template['description'],
        'stages': [
            {
                'name': stage['name'],
                'description': stage['description'],
                'benchmark_conversion': stage['benchmark_conversion'],
                'key_metrics': stage['key_metrics']
            }
            for stage in template['stages']
        ],
        'benchmark_kpis': template['benchmark_kpis'],
        'quick_wins': template['quick_wins'][:3],  # Show top 3 quick wins
        'total_stages': len(template['stages']),
        'estimated_setup_time': '15-30 minutes'
    }
    
    return jsonify(preview_data)

@vertical_bp.route('/api/industry-match', methods=['POST'])
@login_required
def api_industry_match():
    """API endpoint to get template recommendations based on industry"""
    
    try:
        data = request.get_json()
        industry = data.get('industry', '')
        revenue = data.get('revenue', '')
        company_size = data.get('company_size', '')
        
        recommendations = vertical_template_service.get_template_recommendations(
            industry, revenue
        )
        
        # Filter to top 3 recommendations
        top_recommendations = recommendations[:3]
        
        return jsonify({
            'success': True,
            'recommendations': top_recommendations,
            'total_templates': len(vertical_template_service.templates)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vertical_bp.route('/api/template-stats')
@login_required
def api_template_stats():
    """API endpoint to get template usage statistics"""
    
    try:
        # Get template usage stats (would be from actual usage data)
        template_stats = {
            'dtc_ecommerce': {
                'usage_count': 156,
                'avg_improvement': '32%',
                'success_rate': '89%',
                'popular_optimizations': ['Cart abandonment', 'Checkout flow', 'Product recommendations']
            },
            'b2b_saas': {
                'usage_count': 203,
                'avg_improvement': '28%',
                'success_rate': '91%',
                'popular_optimizations': ['Lead scoring', 'Demo booking', 'Trial conversion']
            },
            'home_services': {
                'usage_count': 89,
                'avg_improvement': '45%',
                'success_rate': '94%',
                'popular_optimizations': ['Speed-to-lead', 'Call routing', 'Appointment booking']
            },
            'marketing_agency': {
                'usage_count': 67,
                'avg_improvement': '38%',
                'success_rate': '87%',
                'popular_optimizations': ['Consultation booking', 'Proposal automation', 'Case studies']
            },
            'education_courses': {
                'usage_count': 45,
                'avg_improvement': '41%',
                'success_rate': '85%',
                'popular_optimizations': ['Webinar attendance', 'Course completion', 'Upsells']
            },
            'real_estate': {
                'usage_count': 78,
                'avg_improvement': '35%',
                'success_rate': '92%',
                'popular_optimizations': ['Lead response', 'Showing booking', 'Follow-up automation']
            }
        }
        
        return jsonify({
            'success': True,
            'stats': template_stats,
            'total_users': sum(stats['usage_count'] for stats in template_stats.values())
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500