from django.urls import path
from .views import FinancialOverviewView

urlpatterns = [

    path('api/financial-overview/', FinancialOverviewView.as_view(),
         name='financial_overview'),

]
