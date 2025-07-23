from django.db import models
from django.contrib.auth.hashers import make_password
from decimal import Decimal
from django.utils import timezone

class User(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    dob = models.DateField(null=True, blank=True)
    contact = models.CharField(max_length=15)
    status = models.BooleanField(default=True)

    is_super = models.BooleanField(default=False)


    class Meta:
        abstract = True

class Client(User):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    reset_token = models.CharField(max_length=64, null=True, blank=True) # Add reset_token field
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)


from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime

from django.db import models
from django.contrib.auth.hashers import make_password

class Employee(User):
    reset_token = models.CharField(max_length=64, null=True, blank=True)
    approved = models.BooleanField(default=False)
    specializations = models.ManyToManyField('Specialization', blank=True)
    qualification_certificate = models.FileField(upload_to='employee_certificates/', null=True, blank=True)
        
class Specialization(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)


class ServiceCategory(models.Model):
    name = models.CharField(max_length=100)
    specialization = models.ForeignKey(Specialization, on_delete=models.SET_NULL, null=True, blank=True, related_name='service_categories')

    def __str__(self):
        return self.name


class ServiceSubcategory(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True) 
    image = models.ImageField(upload_to='servicesubcategory_images/', blank=True, null=True)
    

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class Service(models.Model):
    subcategory = models.ForeignKey(ServiceSubcategory, on_delete=models.CASCADE, related_name='services')
    service_name = models.CharField(max_length=100)
    description = models.TextField()
    rate = models.DecimalField(max_digits=10, decimal_places=2, help_text="Rate in Indian Rupees")
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    image = models.ImageField(upload_to='service_images/', blank=True, null=True)

    def active_offers(self):
        return self.offers.filter(is_active=True, start_date__lte=timezone.now(), end_date__gte=timezone.now())
    
    def discounted_price(self):
        offers = self.active_offers()
        if offers.exists():
            discount = Decimal(offers.first().discount_percentage)
            return self.rate * (1 - discount / Decimal(100))
        return self.rate

    def __str__(self):
        return f"{self.service_name} ({self.subcategory.name} - {self.subcategory.category.name})"
    


class ServiceCategoryMen(models.Model):
    name = models.CharField(max_length=100)
    specialization = models.ForeignKey(Specialization, on_delete=models.SET_NULL, null=True, blank=True, related_name='service_categories_men')

    def __str__(self):
        return self.name


class ServiceSubcategoryMen(models.Model):
    category = models.ForeignKey(ServiceCategoryMen, on_delete=models.CASCADE, related_name='subcategories_men')
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True) 
    image = models.ImageField(upload_to='servicesubcategory_images_men/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class ServiceMen(models.Model):
    subcategory = models.ForeignKey(ServiceSubcategoryMen, on_delete=models.CASCADE, related_name='services_men')
    service_name = models.CharField(max_length=100)
    description = models.TextField()
    rate = models.DecimalField(max_digits=10, decimal_places=2, help_text="Rate in Indian Rupees")
    image = models.ImageField(upload_to='service_images_men/', blank=True, null=True)

    def active_offers(self):
        return self.offers_male.filter(
            is_active=True,
            start_date__lte=timezone.now().date(),
            end_date__gte=timezone.now().date()
        )

    def get_discounted_price(self):
        active_offer = self.active_offers().first()
        if active_offer:
            discount = Decimal(active_offer.discount_percentage)
            return self.rate - (self.rate * (discount / Decimal('100')))
        return self.rate

    def __str__(self):
        return f"{self.service_name} ({self.subcategory.name} - {self.subcategory.category.name})"
 
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class Booking(models.Model):
    client = models.ForeignKey('Client', on_delete=models.CASCADE)
    service = models.ForeignKey('Service', on_delete=models.CASCADE, null=True, blank=True)  # For women's services
    service_men = models.ForeignKey('ServiceMen', on_delete=models.CASCADE, null=True, blank=True)  # For men's services
    staff = models.ForeignKey('Employee', on_delete=models.CASCADE)
    booking_date = models.DateField()
    booking_time = models.TimeField()
    additional_notes = models.TextField(blank=True)
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
        ('Completed', 'Completed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def clean(self):
        if not self.booking_date:
            raise ValidationError("Booking date is required.")
        if self.booking_date < timezone.now().date():
            raise ValidationError("Booking date cannot be in the past.")
        if self.booking_date.weekday() == 6:  # Sunday
            raise ValidationError("Bookings are not available on Sundays.")
        if self.booking_time:
            if self.booking_time.hour < 8 or self.booking_time.hour >= 19:
                raise ValidationError("Booking time must be between 8 AM and 7 PM.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        service_name = self.service.service_name if self.service else self.service_men.service_name
        return f"{self.client} - {service_name} on {self.booking_date} at {self.booking_time}"
    
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator



class Feedback(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='feedback')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.booking}"
    
from django.db import models
from decimal import Decimal
    
class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    service = models.ForeignKey('Service', on_delete=models.SET_NULL, null=True, blank=True)
    service_men = models.ForeignKey('ServiceMen', on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed')
    ])
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        service_name = self.service.service_name if self.service else self.service_men.service_name
        return f"Payment for {service_name} by {self.client.first_name}"
    
def discounted_amount(self):
        if self.offer:
            discount = self.offer.discount_percentage
            return self.amount * (1 - (discount / Decimal(100)))
        return self.amount  # No discount applied

#######Blog#######
class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    video_url = models.URLField(blank=True, null=True)  # Optional field for video tutorials

    def __str__(self):
        return self.title

########offers##########


class Offer(models.Model):
    service = models.ForeignKey(Service, related_name='offers', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(default="No description available")
    discount_percentage = models.FloatField()
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError("Start date cannot be after the end date.")
        if self.end_date < timezone.now().date():
            raise ValidationError("Offer end date cannot be in the past.")

    def __str__(self):
        return f"Discount: {self.discount_percentage}% off on {self.service.service_name}"
    

class OfferMale(models.Model):
    service = models.ForeignKey(ServiceMen, related_name='offers_male', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(default="No description available")
    discount_percentage = models.FloatField()
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError("Start date cannot be after the end date.")
        if self.end_date < timezone.now().date():
            raise ValidationError("Offer end date cannot be in the past.")

    def __str__(self):
        return f"Male Offer: {self.title} - {self.discount_percentage}% off on {self.service.service_name}"
    

class Bill(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    service = models.ForeignKey('Service', on_delete=models.SET_NULL, null=True, blank=True)
    service_men = models.ForeignKey('ServiceMen', on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Paid', 'Paid')
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        service_name = self.service.service_name if self.service else self.service_men.service_name
        return f"Bill for {service_name} - {self.client.first_name}"


