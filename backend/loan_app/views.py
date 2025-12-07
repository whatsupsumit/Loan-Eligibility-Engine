import csv
import io
import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import UserProfile, LoanProduct, UserLoanMatch, CSVUpload


def home(request):
    """Home page with upload form"""
    recent_uploads = CSVUpload.objects.all()[:10]
    total_users = UserProfile.objects.count()
    total_products = LoanProduct.objects.count()
    total_matches = UserLoanMatch.objects.count()
    
    context = {
        'recent_uploads': recent_uploads,
        'total_users': total_users,
        'total_products': total_products,
        'total_matches': total_matches,
    }
    return render(request, 'home.html', context)


@csrf_exempt
def upload_csv(request):
    """Handle CSV file upload and process user data"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    if 'csv_file' not in request.FILES:
        return JsonResponse({'error': 'No CSV file provided'}, status=400)
    
    csv_file = request.FILES['csv_file']
    
    # Validate file extension
    if not csv_file.name.endswith('.csv'):
        return JsonResponse({'error': 'File must be a CSV'}, status=400)
    
    # Create upload record
    upload_record = CSVUpload.objects.create(
        filename=csv_file.name,
        status='processing'
    )
    
    try:
        # Read and decode CSV file
        file_data = csv_file.read().decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(file_data))
        
        successful = 0
        failed = 0
        errors = []
        new_user_ids = []
        
        for row_num, row in enumerate(csv_reader, start=2):
            try:
                # Create or update user profile
                user, created = UserProfile.objects.update_or_create(
                    user_id=row['user_id'],
                    defaults={
                        'email': row['email'],
                        'monthly_income': float(row['monthly_income']),
                        'credit_score': int(row['credit_score']),
                        'employment_status': row['employment_status'],
                        'age': int(row['age']),
                    }
                )
                successful += 1
                if created:
                    new_user_ids.append(user.user_id)
                    
            except Exception as e:
                failed += 1
                errors.append(f"Row {row_num}: {str(e)}")
        
        # Update upload record
        upload_record.total_records = successful + failed
        upload_record.successful_records = successful
        upload_record.failed_records = failed
        upload_record.status = 'completed'
        if errors:
            upload_record.error_log = '\n'.join(errors[:100])  # Limit error log
        upload_record.save()
        
        # Trigger n8n workflow for matching (Workflow B)
        try:
            webhook_url = f"{settings.N8N_WEBHOOK_URL}/user-matching"
            response = requests.post(
                webhook_url,
                json={
                    'upload_id': upload_record.id,
                    'new_user_count': len(new_user_ids),
                    'new_user_ids': new_user_ids
                },
                timeout=5
            )
        except Exception as e:
            print(f"Failed to trigger n8n workflow: {e}")
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully processed {successful} records',
            'upload_id': upload_record.id,
            'successful': successful,
            'failed': failed,
            'errors': errors[:10]  # Return first 10 errors
        })
        
    except Exception as e:
        upload_record.status = 'failed'
        upload_record.error_log = str(e)
        upload_record.save()
        return JsonResponse({'error': f'Failed to process CSV: {str(e)}'}, status=500)


def dashboard(request):
    """Dashboard showing statistics and recent matches"""
    users = UserProfile.objects.all()[:20]
    products = LoanProduct.objects.all()
    recent_matches = UserLoanMatch.objects.select_related('user', 'loan_product')[:50]
    
    context = {
        'users': users,
        'products': products,
        'recent_matches': recent_matches,
        'total_users': UserProfile.objects.count(),
        'total_products': LoanProduct.objects.count(),
        'total_matches': UserLoanMatch.objects.count(),
        'notified_matches': UserLoanMatch.objects.filter(notified=True).count(),
    }
    return render(request, 'dashboard.html', context)


@csrf_exempt
def api_get_users(request):
    """API endpoint for n8n to fetch user data"""
    users = UserProfile.objects.all().values(
        'id', 'user_id', 'email', 'monthly_income', 
        'credit_score', 'employment_status', 'age'
    )
    return JsonResponse(list(users), safe=False)


@csrf_exempt
def api_get_products(request):
    """API endpoint for n8n to fetch loan products"""
    products = LoanProduct.objects.all().values(
        'id', 'product_name', 'provider', 'interest_rate',
        'min_income', 'min_credit_score', 'max_credit_score',
        'min_age', 'max_age', 'employment_required', 'product_url'
    )
    return JsonResponse(list(products), safe=False)


@csrf_exempt
def api_create_match(request):
    """API endpoint for n8n to create user-loan matches"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    import json
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        product_id = data.get('product_id')
        match_score = data.get('match_score', 100)
        
        user = UserProfile.objects.get(id=user_id)
        product = LoanProduct.objects.get(id=product_id)
        
        match, created = UserLoanMatch.objects.get_or_create(
            user=user,
            loan_product=product,
            defaults={'match_score': match_score}
        )
        
        return JsonResponse({
            'success': True,
            'match_id': match.id,
            'created': created
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
