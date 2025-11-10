from django.db import models
from django.conf import settings

class Event(models.Model):
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organized_events'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    theme_color = models.CharField(max_length=20, default="#4f46e5")
    banner_text = models.CharField(max_length=100, blank=True, null=True)
    promo_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

    @property
    def available_tickets(self):
        total = sum(t.available_quantity for t in self.ticket_types.all())
        return total


class TicketType(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='ticket_types')
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    total_quantity = models.PositiveIntegerField()
    available_quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} - {self.event.title}"


class Reservation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservations')
    ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.ticket_type.name}"


class Payment(models.Model):
    reservation = models.OneToOneField(
        'Reservation', on_delete=models.CASCADE, related_name='payment'
    )
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    stripe_payment_intent = models.CharField(max_length=255, blank=True, null=True)
    stripe_client_secret = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Plată {self.id} - {self.reservation.user.username} ({self.status})"

