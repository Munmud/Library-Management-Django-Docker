from django.db import models
from core.models import BaseModel
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
from datetime import timedelta


class Category(BaseModel):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    def getName(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['name']


class Book(BaseModel):
    name = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, null=True, blank=True)
    # category = models.ManyToOneRel(Category)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="books")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    format = models.CharField(max_length=50, null=True)
    ratings = models.FloatField(null=True, blank=True)
    cover_image = models.ImageField(
        upload_to='book_covers/', null=True, blank=True)
    availability = models.BooleanField(default=True)
    available_copy = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def getName(self):
        return self.name

    class Meta:
        ordering = ['name']


ACTION_CHOICES = [
    ('PENDING', 'Pending'),
    ('APPROVED', 'Approved'),
    ('CANCELLED', 'Cancelled'),
    ('RETURNED', 'Returned'),
]


class Reservation(BaseModel):
    book = models.ForeignKey(Book, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    requested_at = models.DateTimeField(auto_now_add=True)
    reserved_at = models.DateTimeField(null=True, blank=True)
    expected_return_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=ACTION_CHOICES, default='PENDING')
    isActive = models.BooleanField(default=True)
    # def __str__(self):
    #     return f"{self.user} requested {self.book}"


BILL_CHOICE = [
    ('DELAYED', 'Delayed'),
    ('LOST', 'Lost'),
]


class Bill(BaseModel):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    isActive = models.BooleanField(default=True)
    reason = models.CharField(
        max_length=20, choices=BILL_CHOICE, default='DELAYED')


RATING_CHOICE = [
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
]


class Rating(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rating = models.IntegerField(
        default=0, choices=RATING_CHOICE, help_text="Enter rating from 1 to 5")
    review = models.TextField(blank=True)

    class Meta:
        unique_together = ('user', 'book')


@receiver(pre_save, sender=Reservation)
def reservation_status_change(sender, instance, **kwargs):
    if instance.pk:
        old_status = Reservation.objects.get(pk=instance.pk).status
        new_status = instance.status
        if old_status != new_status:
            if (old_status == "PENDING" and new_status == "APPROVED"):
                instance.reserved_at = timezone.now()
                instance.expected_return_date = instance.reserved_at + \
                    timedelta(days=7)
            elif (old_status == "APPROVED" and new_status == "RETURNED"):
                instance.isActive = False
                book = instance.book
                book.available_copy += 1
                book.availability = True
                book.save()
                # instance.expected_return_date = instance.reserved_at + timedelta(days=7)
                late_days = (timezone.now().date() -
                             instance.expected_return_date).days

                if late_days > 0:
                    Bill.objects.create(
                        reservation=instance,
                        user=instance.user,
                        amount=settings.DELAY_FINE_PER_DAY * late_days,
                    )
            elif (old_status == "PENDING" and new_status == "CANCELLED"):
                instance.isActive = False
                book = instance.book
                book.available_copy += 1
                book.availability = True
                book.save()
            elif (old_status == "APPROVED" and new_status == "CANCELLED"):
                bookprice = instance.book.price
                print(bookprice)
                Bill.objects.create(
                    reservation=instance,
                    user=instance.user,
                    amount=settings.BOOK_LOST_EXTRA_FINE + bookprice,
                    reason='LOST'
                )
            else:
                raise ValidationError(
                    f"Reservation status cannot be changed to {new_status} from {old_status}")
    # else:
    #     instance.status = "PENDING"
    #     user = instance.user
    #     book = instance.book

    #     if (book.availability == False):
    #         raise Exception(f"This Book is not currently available")
    #     if len(Reservation.objects.filter(user = user, isActive = True, book = book)) == 1:
    #         raise Exception("You already have requested this Book")
    #     active_request_count = len(Reservation.objects.filter(user = user, isActive = True ))
    #     if (active_request_count >=settings.USER_BOOK_ACTIVE_COUNT):
    #         raise Exception(f"More than {settings.USER_BOOK_ACTIVE_COUNT} active request")

    #     book.available_copy -=1
    #     if (book.available_copy == 0):
    #         book.availability = False
    #     book.save()


class Notebook(BaseModel):
    title = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Note(BaseModel):
    title = models.CharField(max_length=100)
    content = models.TextField()
    notebook = models.ForeignKey(Notebook, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
