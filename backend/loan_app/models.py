from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class UserProfile(models.Model):
    """Store user data from CSV upload"""
    user_id = models.CharField(max_length=100, unique=True)
    email = models.EmailField()
    monthly_income = models.DecimalField(max_digits=10, decimal_places=2)
    credit_score = models.IntegerField(
        validators=[MinValueValidator(300), MaxValueValidator(850)]
    )
    employment_status = models.CharField(max_length=100)
    age = models.IntegerField(validators=[MinValueValidator(18)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_profiles'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user_id} - {self.email}"


class LoanProduct(models.Model):
    """Store loan products discovered by n8n web crawler"""
    product_name = models.CharField(max_length=255)
    provider = models.CharField(max_length=255)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    min_income = models.DecimalField(max_digits=10, decimal_places=2)
    min_credit_score = models.IntegerField()
    max_credit_score = models.IntegerField(default=850)
    min_age = models.IntegerField(default=18)
    max_age = models.IntegerField(default=65)
    employment_required = models.CharField(max_length=255, blank=True, null=True)
    product_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'loan_products'
        ordering = ['interest_rate']

    def __str__(self):
        return f"{self.product_name} ({self.provider}) - {self.interest_rate}%"


class UserLoanMatch(models.Model):
    """Store matches between users and eligible loan products"""
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='matches')
    loan_product = models.ForeignKey(LoanProduct, on_delete=models.CASCADE, related_name='matches')
    match_score = models.IntegerField(default=100)  # Percentage match score
    notified = models.BooleanField(default=False)
    notified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_loan_matches'
        unique_together = ['user', 'loan_product']
        ordering = ['-match_score', '-created_at']

    def __str__(self):
        return f"{self.user.user_id} -> {self.loan_product.product_name}"


class CSVUpload(models.Model):
    """Track CSV upload history"""
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    total_records = models.IntegerField(default=0)
    successful_records = models.IntegerField(default=0)
    failed_records = models.IntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed')
        ],
        default='pending'
    )
    error_log = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'csv_uploads'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.filename} - {self.status}"
