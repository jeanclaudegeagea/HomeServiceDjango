from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    USER_TYPES = [
        ("customer", "Customer"),
        ("service_provider", "Service Provider"),
        ("admin", "Admin"),
    ]
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPES)


class Service(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey("Category", on_delete=models.CASCADE)
    description = models.TextField()
    image = models.ImageField(upload_to="service_images/")
    pdf_file = models.FileField(upload_to="service_pdfs/")


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    booking_date = models.DateField()
    status = models.CharField(max_length=50)
    payment_id = models.CharField(
        max_length=100
    )  # Assuming a simple payment ID for now


class Category(models.Model):
    name = models.CharField(max_length=100)


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service_provider = models.ForeignKey(
        User, related_name="reviews_received", on_delete=models.CASCADE
    )
    rating = models.IntegerField()
    comment = models.TextField()


class Payment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=50)


class Schedule(models.Model):
    service_provider = models.ForeignKey(User, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=20)  # Example: 'Monday', 'Tuesday', etc.
    start_time = models.TimeField()
    end_time = models.TimeField()


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


class Report(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    report_details = models.TextField()
