from django.shortcuts import render

# Create your views here.

def main(request):
    return render(request, 'parking/index.html', {"title": "Fast Parking"})