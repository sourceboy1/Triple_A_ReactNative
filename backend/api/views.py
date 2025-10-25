from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse

def test_api(request):
    return JsonResponse({"message": "Backend is connected successfully!"})
