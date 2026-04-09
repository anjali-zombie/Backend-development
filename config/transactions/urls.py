from rest_framework.routers import DefaultRouter
from .views import FinancialRecordViewSet, SummaryView
from django.urls import path

router = DefaultRouter()
router.register('records', FinancialRecordViewSet, basename='records')

urlpatterns = [
    path('summary/', SummaryView.as_view()),
]

urlpatterns += router.urls