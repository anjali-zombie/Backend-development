from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import FinancialRecord
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from .serializers import FinancialRecordSerializer
from users.permissions import IsAnalyst, IsViewer

class FinancialRecordViewSet(ModelViewSet):
    serializer_class = FinancialRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = FinancialRecord.objects.filter(user=user)

        if user.role == 'admin':
            return FinancialRecord.objects.all()

        if user.role != 'admin':
            queryset = queryset.filter(user=user)

        category = self.request.query_params.get('category')
        record_type = self.request.query_params.get('type')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if category:
            queryset = queryset.filter(category=category)

        if record_type:
            queryset = queryset.filter(type=record_type)

        if start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])

        return queryset
    
    def perform_update(self, serializer):
        instance = serializer.instance
        user = self.request.user

        if user.role != 'admin' and instance.user != user:
            raise PermissionDenied("You cannot update this record")

        serializer.save()
    def perform_destroy(self, instance):
        user = self.request.user

        if user.role != 'admin' and instance.user != user:
            raise PermissionDenied("You cannot delete this record")

        instance.delete()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAnalyst()]
        return [IsAuthenticated(), IsViewer()]

class SummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        queryset = FinancialRecord.objects.all()

        if user.role != 'admin':
            queryset = queryset.filter(user=user)

        total_income = queryset.filter(type='income').aggregate(total=Sum('amount'))
        total_expense = queryset.filter(type='expense').aggregate(total=Sum('amount'))

        return Response({
            "total_income": total_income['total'] or 0,
            "total_expense": total_expense['total'] or 0
        })
    
class DashboardView(APIView):
    permission_classes = [IsAuthenticated ,IsViewer]

    def get_queryset(self, user):
        queryset = FinancialRecord.objects.all()
        if user.role != 'admin':
            queryset = queryset.filter(user=user)
        return queryset

    def get(self, request):
        user = request.user
        queryset = self.get_queryset(user)

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])

        total_income = queryset.filter(type='income').aggregate(
            total=Sum('amount')
        )['total'] or 0

        total_expense = queryset.filter(type='expense').aggregate(
            total=Sum('amount')
        )['total'] or 0

        net_balance = total_income - total_expense

        category_data = (
            queryset.values('category')
            .annotate(total=Sum('amount'))
            .order_by('-total')
        )

        recent = queryset.order_by('-created_at')[:5].values(
            'id', 'amount', 'type', 'category', 'date'
        )

        monthly = (
            queryset.annotate(month=TruncMonth('date'))
            .values('month')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )

        return Response({
            "total_income": total_income,
            "total_expense": total_expense,
            "net_balance": net_balance,
            "category_breakdown": list(category_data),
            "recent_transactions": list(recent),
            "monthly_trends": list(monthly),
        })