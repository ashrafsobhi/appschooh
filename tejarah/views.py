"""
Views للمشروع الرئيسي
"""
from django.shortcuts import render
from django.http import Http404


def custom_404(request, exception=None):
    """صفحة 404 مخصصة"""
    return render(request, '404.html', status=404)


def test_404(request):
    """صفحة اختبار لصفحة 404 (للتطوير فقط)"""
    raise Http404("صفحة تجريبية لاختبار 404")

