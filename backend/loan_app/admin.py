from django.contrib import admin
from .models import UserProfile, LoanProduct, UserLoanMatch, CSVUpload


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'email', 'monthly_income', 'credit_score', 'employment_status', 'age', 'created_at']
    search_fields = ['user_id', 'email']
    list_filter = ['employment_status', 'created_at']


@admin.register(LoanProduct)
class LoanProductAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'provider', 'interest_rate', 'min_income', 'min_credit_score', 'created_at']
    search_fields = ['product_name', 'provider']
    list_filter = ['provider', 'created_at']


@admin.register(UserLoanMatch)
class UserLoanMatchAdmin(admin.ModelAdmin):
    list_display = ['user', 'loan_product', 'match_score', 'notified', 'created_at']
    search_fields = ['user__user_id', 'loan_product__product_name']
    list_filter = ['notified', 'created_at']


@admin.register(CSVUpload)
class CSVUploadAdmin(admin.ModelAdmin):
    list_display = ['filename', 'uploaded_at', 'total_records', 'successful_records', 'failed_records', 'status']
    list_filter = ['status', 'uploaded_at']
    readonly_fields = ['uploaded_at']
