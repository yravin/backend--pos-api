# api/api_views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Order

@method_decorator(csrf_exempt, name='dispatch')
class DailySalesAPI(View):
    """API សម្រាប់របាយការណ៍លក់ប្រចាំថ្ងៃ"""
    
    def get(self, request):
        # ទទួលយកថ្ងៃពី parameter (default ថ្ងៃនេះ)
        selected_date = request.GET.get('date')
        
        if selected_date:
            try:
                selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            except ValueError:
                selected_date = timezone.now().date()
        else:
            selected_date = timezone.now().date()
        
        # ទទួលយកទិន្នន័យ
        daily_summary = Order.get_daily_sales_summary(selected_date)
        
        # ទទួលយក order ពិស្តារ
        daily_orders = Order.objects.daily_sales(selected_date)
        
        # រៀបចំទិន្នន័យ order ពិស្តារ
        orders_data = []
        for order in daily_orders:
            orders_data.append({
                'id': order.id,
                'product_name': order.product.product_name,
                'product_category': order.product.category_name.category_name,
                'quantity': order.order_qty,
                'price': float(order.order_price),
                'order_time': order.order_datetime.strftime('%H:%M:%S')
            })
        
        response_data = {
            'success': True,
            'date': selected_date.strftime('%Y-%m-%d'),
            'summary': {
                'total_amount': float(daily_summary['total_amount']),
                'total_quantity': daily_summary['total_quantity'],
                'total_orders': daily_summary['total_orders'],
                'products_sold': daily_summary['products_sold']
            },
            'detailed_orders': orders_data,
            'navigation': {
                'previous_date': (selected_date - timedelta(days=1)).strftime('%Y-%m-%d'),
                'next_date': (selected_date + timedelta(days=1)).strftime('%Y-%m-%d'),
                'current_date': selected_date.strftime('%Y-%m-%d')
            }
        }
        
        return JsonResponse(response_data)

@method_decorator(csrf_exempt, name='dispatch')
class SalesHistoryAPI(View):
    """API សម្រាប់ history លក់"""
    
    def get(self, request):
        days = int(request.GET.get('days', 30))
        sales_history = Order.get_sales_history(days)
        
        # Format dates for JSON
        formatted_history = []
        for day in sales_history:
            formatted_history.append({
                'date': day['date'].strftime('%Y-%m-%d') if day['date'] else '',
                'daily_total': float(day['daily_total']) if day['daily_total'] else 0,
                'daily_quantity': day['daily_quantity'] or 0,
                'daily_orders': day['daily_orders'] or 0
            })
        
        response_data = {
            'success': True,
            'period_days': days,
            'sales_history': formatted_history,
            'summary': {
                'total_period_sales': sum(day['daily_total'] for day in formatted_history),
                'total_period_quantity': sum(day['daily_quantity'] for day in formatted_history),
                'total_period_orders': sum(day['daily_orders'] for day in formatted_history)
            }
        }
        
        return JsonResponse(response_data)