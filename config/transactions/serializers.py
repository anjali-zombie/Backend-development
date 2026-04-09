from rest_framework import serializers
from .models import FinancialRecord
from datetime import date

class FinancialRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialRecord
        fields = '__all__'
        read_only_fields = ['user']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value
    
    def validate_type(self, value):
        if value not in ['income', 'expense']:
            raise serializers.ValidationError("Type must be 'income' or 'expense'")
        return value
    
    def validate_date(self, value):
        if value > date.today():
            raise serializers.ValidationError("Date cannot be in the future")
        return value

    def validate(self, data):
        # Example: Prevent invalid combinations
        if data.get('category') == "":
            raise serializers.ValidationError({
                "category": "Category cannot be empty"
            })
        return data