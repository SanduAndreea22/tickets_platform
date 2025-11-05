from django.shortcuts import render, get_object_or_404
from .models import Event

# Pagina principală (homepage)
def home(request):
    events = Event.objects.all().order_by('-start_date')[:3]  # doar 3 cele mai noi
    return render(request, 'events/home.html', {'events': events})


# Listă completă de evenimente
def events_list(request):
    events = Event.objects.all().order_by('start_date')
    return render(request, 'events/events_list.html', {'events': events})


# Detalii pentru un eveniment
def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    return render(request, 'events/event_detail.html', {'event': event})
