from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.db.models import Q

from .models import Event, TicketType, Reservation, Payment

# 🎟️ Listă completă de evenimente
def events_list(request):
    query = request.GET.get('q', '')
    date = request.GET.get('date', '')

    events = Event.objects.all()

    # Căutare text
    if query:
        events = events.filter(Q(title__icontains=query) | Q(location__icontains=query))

    # Filtrare după dată (dacă a fost selectată)
    if date:
        events = events.filter(start_date__date=date)

    events = events.order_by('start_date')

    return render(request, 'events/events_list.html', {
        'events': events,
        'query': query,
        'date': date
    })


# 📅 Detalii pentru un eveniment
def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)

    # 🔹 Când utilizatorul trimite formularul de rezervare
    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "Trebuie să fii autentificat pentru a rezerva bilete.")
            return redirect("login")

        if not getattr(request.user, "is_participant", False):
            messages.error(request, "Doar participanții pot rezerva bilete.")
            return redirect("events_list")

        ticket_id = request.POST.get("ticket_id")
        quantity = int(request.POST.get("quantity", 1))

        ticket_type = get_object_or_404(TicketType, id=ticket_id, event=event)

        # 🔹 Verificare stoc disponibil
        if quantity > ticket_type.available_quantity:
            messages.error(request, "Nu sunt suficiente bilete disponibile.")
            return redirect("event_detail", pk=event.pk)

        # 🔹 Creăm rezervarea
        Reservation.objects.create(
            user=request.user,
            ticket_type=ticket_type,
            quantity=quantity,
            confirmed=False
        )

        # 🔹 Scădem biletele rezervate
        ticket_type.available_quantity -= quantity
        ticket_type.save()

        messages.success(request, f"Ai rezervat {quantity} bilet(e) la {event.title}!")
        return redirect("my_reservations")

    # 🔹 Returnăm pagina normal
    return render(request, "events/event_detail.html", {"event": event})



# 👤 Biletele utilizatorului (participant)
@login_required
def my_tickets(request):
    if not getattr(request.user, 'is_participant', False):
        messages.error(request, "Doar participanții pot accesa biletele.")
        return redirect('home')

    tickets = Reservation.objects.filter(user=request.user, confirmed=True).select_related('ticket_type__event')
    return render(request, 'events/my_tickets.html', {'tickets': tickets})


# 📦 Rezervările utilizatorului (participant)
@login_required
def my_reservations(request):
    if not getattr(request.user, 'is_participant', False):
        messages.error(request, "Doar participanții pot accesa această pagină.")
        return redirect('home')

    reservations = Reservation.objects.filter(user=request.user).select_related('ticket_type__event')

    if request.method == 'POST':
        reservation_id = request.POST.get('reservation_id')
        reservation = Reservation.objects.filter(id=reservation_id, user=request.user).first()

        if reservation:
            # Eliberăm biletele
            ticket_type = reservation.ticket_type
            ticket_type.available_quantity += reservation.quantity
            ticket_type.save()
            reservation.delete()
            messages.success(request, "Rezervarea a fost anulată cu succes!")
        else:
            messages.error(request, "Rezervarea nu a fost găsită.")

        return redirect('my_reservations')

    return render(request, 'events/my_reservations.html', {'reservations': reservations})


# 🧑‍💼 Creare eveniment (organizator)
@login_required
def create_event(request):
    if not getattr(request.user, 'is_organizer', False):
        messages.error(request, "Doar organizatorii pot crea evenimente.")
        return redirect('home')

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        location = request.POST.get('location')

        # conversie corectă a datelor
        start_date = parse_datetime(request.POST.get('start_date'))
        end_date = parse_datetime(request.POST.get('end_date'))

        image = request.FILES.get('image')

        if not all([title, description, location, start_date, end_date]):
            messages.error(request, "Completează toate câmpurile.")
            return redirect('create_event')

        event = Event.objects.create(
            organizer=request.user,
            title=title,
            description=description,
            location=location,
            start_date=start_date,
            end_date=end_date,
            image=image,
        )

        # Adaugă tipurile de bilete
        ticket_names = request.POST.getlist('ticket_name')
        ticket_prices = request.POST.getlist('ticket_price')
        ticket_quantities = request.POST.getlist('ticket_quantity')

        for name, price, qty in zip(ticket_names, ticket_prices, ticket_quantities):
            if name and price and qty:
                TicketType.objects.create(
                    event=event,
                    name=name,
                    price=price,
                    total_quantity=int(qty),
                    available_quantity=int(qty)
                )

        messages.success(request, "Evenimentul a fost creat cu succes!")
        return redirect('events_list')

    return render(request, 'events/create_event.html')


# ✏️ Editare eveniment (organizator)
@login_required
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, organizer=request.user)

    if not request.user.is_organizer:
        messages.error(request, "Nu ai permisiunea să editezi acest eveniment.")
        return redirect('home')

    if request.method == 'POST':
        event.title = request.POST.get('title')
        event.description = request.POST.get('description')
        event.location = request.POST.get('location')
        event.start_date = parse_datetime(request.POST.get('start_date'))
        event.end_date = parse_datetime(request.POST.get('end_date'))

        if request.FILES.get('image'):
            event.image = request.FILES.get('image')

        event.save()

        # actualizare bilete existente
        ticket_ids = request.POST.getlist('ticket_id')
        ticket_names = request.POST.getlist('ticket_name')
        ticket_prices = request.POST.getlist('ticket_price')
        ticket_quantities = request.POST.getlist('ticket_quantity')

        for ticket_id, name, price, qty in zip(ticket_ids, ticket_names, ticket_prices, ticket_quantities):
            ticket = TicketType.objects.get(id=ticket_id, event=event)
            ticket.name = name
            ticket.price = price
            ticket.available_quantity = int(qty)
            ticket.total_quantity = int(qty)
            ticket.save()

        messages.success(request, "Evenimentul a fost actualizat cu succes!")
        return redirect('event_detail', pk=event.id)

    tickets = event.ticket_types.all()
    return render(request, 'events/edit_event.html', {'event': event, 'tickets': tickets})


# 🧾 Gestionare rezervări (organizator)
@login_required
def ticket_management(request, event_id):
    if not request.user.is_organizer:
        messages.error(request, "Doar organizatorii pot accesa această pagină.")
        return redirect('home')

    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    reservations = Reservation.objects.filter(ticket_type__event=event).select_related('user', 'ticket_type')

    if request.method == 'POST':
        reservation_id = request.POST.get('reservation_id')
        action = request.POST.get('action')

        reservation = Reservation.objects.filter(id=reservation_id, ticket_type__event=event).first()
        if reservation:
            if action == 'confirm':
                reservation.confirmed = True
                reservation.save()
                messages.success(request, "Rezervarea a fost confirmată.")
            elif action == 'delete':
                ticket_type = reservation.ticket_type
                ticket_type.available_quantity += reservation.quantity
                ticket_type.save()
                reservation.delete()
                messages.success(request, "Rezervarea a fost ștearsă.")
        else:
            messages.error(request, "Rezervarea nu a fost găsită.")

        return redirect('ticket_management', event_id=event_id)

    return render(request, 'events/ticket_management.html', {
        'event': event,
        'reservations': reservations
    })


# 🎨 Personalizare eveniment (organizator)
@login_required
def customize_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, organizer=request.user)

    if not request.user.is_organizer:
        messages.error(request, "Nu ai permisiunea să modifici acest eveniment.")
        return redirect('home')

    if request.method == 'POST':
        event.theme_color = request.POST.get('theme_color')
        event.banner_text = request.POST.get('banner_text')
        event.promo_message = request.POST.get('promo_message')

        if request.FILES.get('image'):
            event.image = request.FILES.get('image')

        event.save()
        messages.success(request, "Personalizarea evenimentului a fost salvată!")
        return redirect('event_detail', pk=event.id)

    return render(request, 'events/customize_event.html', {'event': event})

@login_required
def my_events(request):
    if not getattr(request.user, "is_organizer", False):
        messages.error(request, "Doar organizatorii pot accesa această pagină.")
        return redirect('events_list')

    events = Event.objects.filter(organizer=request.user).order_by('-start_date')
    return render(request, 'events/my_events.html', {'events': events})

import stripe, json
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Payment


@login_required
def payment_page(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    amount = float(reservation.ticket_type.price) * reservation.quantity

    payment, _ = Payment.objects.get_or_create(
        reservation=reservation,
        defaults={'amount': amount}
    )

    context = {
        'reservation': reservation,
        'payment': payment,
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
        'CURRENCY': settings.STRIPE_CURRENCY,
    }
    return render(request, 'events/payment_page.html', context)


@login_required
def create_payment_intent(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    amount = float(reservation.ticket_type.price) * reservation.quantity
    stripe.api_key = settings.STRIPE_SECRET_KEY

    intent = stripe.PaymentIntent.create(
        amount=int(amount * 100),
        currency=settings.STRIPE_CURRENCY,
        metadata={'reservation_id': reservation.id, 'user_id': request.user.id}
    )

    payment, created = Payment.objects.get_or_create(
        reservation=reservation,
        defaults={
            'amount': amount,
            'stripe_payment_intent': intent.id,
            'stripe_client_secret': intent.client_secret
        }
    )
    if not created:
        payment.stripe_payment_intent = intent.id
        payment.stripe_client_secret = intent.client_secret
        payment.amount = amount
        payment.save()

    return JsonResponse({'clientSecret': intent.client_secret})


@login_required
def payment_success(request):
    messages.success(request, "✅ Plata a fost efectuată cu succes! Vezi biletele tale.")
    return redirect('my_tickets')


@login_required
def payment_cancel(request):
    messages.warning(request, "❌ Plata a fost anulată.")
    return redirect('my_reservations')


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    stripe.api_key = settings.STRIPE_SECRET_KEY

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        pi_id = intent.get('id')
        payment = Payment.objects.filter(stripe_payment_intent=pi_id).first()
        if payment:
            payment.status = 'completed'
            payment.save()
            reservation = payment.reservation
            reservation.confirmed = True
            reservation.save()

    return HttpResponse(status=200)
