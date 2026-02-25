from django.shortcuts import render

def advertencias(request):
    return render(request, 'advertencia.html')

def nova_advertencia(request):
    return render(request, 'nova_advertencia.html')

def acompanhar_advertencias(request):
    return render(request, 'acompanhar_advertencias.html')

