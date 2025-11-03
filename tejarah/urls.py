"""
URL configuration for tejarah project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from tejarah import views
from student_affairs import views as student_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', student_views.custom_login, name='login'),
    path('accounts/logout/', student_views.custom_logout, name='logout'),
    path('', include('student_affairs.urls')),
    # للاختبار فقط - يمكن حذفها في الإنتاج
    path('test-404/', views.test_404),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else None)

# تعريف handler404 لعرض صفحة 404 المخصصة
handler404 = 'tejarah.views.custom_404'

