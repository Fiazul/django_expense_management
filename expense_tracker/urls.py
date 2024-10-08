from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('acc.urls')),
    path('expenses/', include('expenses.urls')),
]
