from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Expense, Income, Savings, Budget
from .serializers import ExpenseSerializer, IncomeSerializer, SavingsSerializer, BudgetSerializer


class FinancialOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        username = user.username

        expenses = Expense.objects.filter(user=user)
        incomes = Income.objects.filter(user=user)
        savings = Savings.objects.filter(user=user)
        budgets = Budget.objects.filter(user=user)

        response_data = {
            "username": username,  # Include the username in the response
            "expenses": ExpenseSerializer(expenses, many=True).data,
            "incomes": IncomeSerializer(incomes, many=True).data,
            "savings": SavingsSerializer(savings, many=True).data,
            "budgets": BudgetSerializer(budgets, many=True).data,
        }

        return Response(response_data)
