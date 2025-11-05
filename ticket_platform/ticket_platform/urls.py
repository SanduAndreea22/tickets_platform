from django.urls import path, include

urlpatterns = [
    path('', include('pages.urls')),
    path('users/', include('users.urls'))
    # rutele aplicației tale
]

