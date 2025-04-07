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


class User(AbstractUser):
    CUSTOMER = 1
    SERVICE_PROVIDER = 2
    ROLE_CHOICES = ((CUSTOMER, "Customer"), (SERVICE_PROVIDER, "Service Provider"))
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_image = models.ImageField(upload_to="profile_images/", blank=True)
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
    specialization = models.ManyToManyField(Specialization)


class ServiceProviderDocument(models.Model):
    provider = models.ForeignKey(
        ServiceProvider,
        on_delete=models.CASCADE,
    )
    DOCUMENT_TYPES = [
        ("license", "Professional License"),
        ("certification", "Certification"),
        ("insurance", "Insurance Document"),
    ]
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to="provider_documents/")
    issue_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)


class Service(models.Model):
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    specialization = models.ForeignKey(Specialization, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Booking(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    booking_time = models.CharField(max_length=5)
    booking_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.service.name}"


class ServiceReview(models.Model):
    RATING_CHOICES = [
        (1, "Poor"),
        (2, "Fair"),
        (3, "Good"),
        (4, "Very Good"),
        (5, "Excellent"),
    ]

    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, related_name="reviews_given"
    )
    provider = models.ForeignKey(
        ServiceProvider, on_delete=models.CASCADE, related_name="reviews_received"
    )
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("customer", "provider")

    def __str__(self):
        return f"Review for {self.provider.user.get_full_name()} by {self.customer.user.get_full_name()}"


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ("booking", "Booking Update"),
        ("system", "System Notification"),
        ("promotion", "Promotional"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=100)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.user.get_full_name()}"


class ProviderSchedule(models.Model):
    DAY_CHOICES = [
        ("monday", "Monday"),
        ("tuesday", "Tuesday"),
        ("wednesday", "Wednesday"),
        ("thursday", "Thursday"),
        ("friday", "Friday"),
        ("saturday", "Saturday"),
        ("sunday", "Sunday"),
    ]
    provider = models.ForeignKey(
        ServiceProvider, on_delete=models.CASCADE, related_name="schedules"
    )
    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    time_slots = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("provider", "day")
        ordering = ["day"]

    def __str__(self):
        return f"{self.provider.user.get_full_name()} - {self.get_day_display()}"
