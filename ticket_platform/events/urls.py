from django.urls import path
from . import views

urlpatterns = [

    # 🎟️ Listă completă de evenimente
    path('list/', views.events_list, name='events_list'),

    # 📅 Detalii pentru un eveniment
    path('<int:pk>/', views.event_detail, name='event_detail'),

    # 👤 Paginile participantului
    path('my-tickets/', views.my_tickets, name='my_tickets'),
    path('my-reservations/', views.my_reservations, name='my_reservations'),

    # 🧑‍💼 Paginile organizatorului
    path('create/', views.create_event, name='create_event'),
    path('edit/<int:event_id>/', views.edit_event, name='edit_event'),
    path('<int:event_id>/tickets/', views.ticket_management, name='ticket_management'),
    path('<int:event_id>/customize/', views.customize_event, name='customize_event'),
path('my-events/', views.my_events, name='my_events'),
path('payment/<int:reservation_id>/', views.payment_page, name='payment_page'),
path('payment/create-intent/<int:reservation_id>/', views.create_payment_intent, name='create_payment_intent'),
path('payment/success/', views.payment_success, name='payment_success'),
path('payment/cancel/', views.payment_cancel, name='payment_cancel'),
path('webhook/', views.stripe_webhook, name='stripe_webhook'),

]

