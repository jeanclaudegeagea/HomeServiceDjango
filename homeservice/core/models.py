from django.db import models
from django.contrib.auth.models import AbstractUser

class Location(models.Model):
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

class Specialization(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

class ServiceProviderDocument(models.Model):
    DOCUMENT_TYPES = [
        ('license', 'Professional License'),
        ('certification', 'Certification'),
        ('insurance', 'Insurance Document'),
    ]
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='provider_documents/')
    issue_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)

class User (AbstractUser):
    CUSTOMER = 1
    SERVICE_PROVIDER = 2
    ROLE_CHOICES = (
        (CUSTOMER, 'Customer'),
        (SERVICE_PROVIDER, 'Service Provider')
    )
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    location = models.OneToOneField(Location, on_delete=models.CASCADE, null=True)

class ServiceProvider(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    documents = models.ManyToManyField(ServiceProviderDocument, blank=True)
    specialization = models.ManyToManyField(Specialization)