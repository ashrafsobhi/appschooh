from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Count, Sum
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, Http404, JsonResponse
from django.conf import settings
from django.urls import reverse
import os
from .models import Student, StudentAttachment, SiteSettings, Classroom
from .forms import (
    StudentForm,
    ExcelUploadForm,
    AttachmentForm,
    RecordsForm,
    SelectStudentForm,
    ClassroomForm,
    AddStudentToClassroomForm,
    StudentContactForm,
    AdminCreateUserForm,
)
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import views as auth_views
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .utils import parse_egyptian_national_id
from .auth_utils import generate_jwt_token, verify_jwt_token, get_token_from_request
import openpyxl
import xlrd
from datetime import datetime, date
from io import BytesIO
import qrcode
import base64
from PIL import Image, ImageDraw, ImageFont
import hashlib
from collections import defaultdict


# ===== BASIC FUNCTIONS (Stubs - يجب التأكد من وجودها) =====
@login_required
def welcome(request):
    """صفحة الترحيب - محمية بتسجيل الدخول"""
    total_students = Student.objects.count()
    active_students = Student.objects.filter(registration_status='ناجح ومنقول').count()
    return render(request, 'student_affairs/welcome.html', {
        'total_students': total_students,
        'active_students': active_students,
    })


def student_list(request):
    """صفحة قيد الطلبة - يجب التأكد من وجودها"""
    # TODO: إضافة الكود الكامل
    return render(request, 'student_affairs/student_list.html', {})


def records_list(request):
    """صفحة السجلات - يجب التأكد من وجودها"""
    # TODO: إضافة الكود الكامل
    return render(request, 'student_affairs/records_list.html', {})


def add_record(request):
    """إضافة سجل - يجب التأكد من وجودها"""
    # TODO: إضافة الكود الكامل
    return render(request, 'student_affairs/add_record.html', {})


def classrooms_list(request):
    """قائمة الفصول - يجب التأكد من وجودها"""
    # TODO: إضافة الكود الكامل
    return render(request, 'student_affairs/classrooms_list.html', {})


def add_classroom(request):
    """إضافة فصل - يجب التأكد من وجودها"""
    # TODO: إضافة الكود الكامل
    return render(request, 'student_affairs/add_classroom.html', {})


def classroom_detail(request, classroom_id):
    """تفاصيل الفصل - يجب التأكد من وجودها"""
    # TODO: إضافة الكود الكامل
    return render(request, 'student_affairs/classroom_detail.html', {})


def classroom_print(request, classroom_id):
    """طباعة قوائم الفصل - يجب التأكد من وجودها"""
    # TODO: إضافة الكود الكامل
    return render(request, 'student_affairs/classroom_print.html', {})


def classrooms_print_grade(request, gender, grade):
    """طباعة قوائم الصف - يجب التأكد من وجودها"""
    # TODO: إضافة الكود الكامل
    return render(request, 'student_affairs/classrooms_print_grade.html', {})


def classrooms_print_absence_grade(request, gender, grade):
    """طباعة قوائم الغياب - يجب التأكد من وجودها"""
    # TODO: إضافة الكود الكامل
    return render(request, 'student_affairs/classrooms_print_absence_grade.html', {})


def print_student_list(request):
    """طباعة قائمة الطلاب - يجب التأكد من وجودها"""
    # TODO: إضافة الكود الكامل
    return render(request, 'student_affairs/print_student_list.html', {})


def add_student(request):
    """إضافة طالب - يجب التأكد من وجودها"""
    # TODO: إضافة الكود الكامل
    return render(request, 'student_affairs/add_student.html', {})


def download_excel_template(request):
    """تحميل قالب Excel - يجب التأكد من وجودها"""
    # TODO: إضافة الكود الكامل
    return HttpResponse("Template")


def student_detail(request, student_id):
    """تفاصيل الطالب - يجب التأكد من وجودها"""
    # TODO: إضافة الكود الكامل
    return render(request, 'student_affairs/student_detail.html', {})


def student_id_card(request, student_id):
    """بطاقة الطالب - يجب التأكد من وجودها"""
    # TODO: إضافة الكود الكامل
    return render(request, 'student_affairs/student_id_card.html', {})


def student_qr(request, student_id):
    """QR code للطالب - يجب التأكد من وجودها"""
    # TODO: إضافة الكود الكامل
    return HttpResponse("QR")


def delete_attachment(request, attachment_id):
    """حذف مرفق - يجب التأكد من وجودها"""
    # TODO: إضافة الكود الكامل
    return redirect('student_affairs:student_detail', student_id=1)


# ===== SYSTEM STATISTICS FUNCTION =====
def system_statistics(request):
    """صفحة إحصائيات النظام - دالة معقدة مع جميع الإحصائيات المطلوبة"""
    from django.db.models import Count, Sum, Case, When, IntegerField
    from django.db.models.functions import Extract
    
    # الحصول على جميع الطلاب
    all_students = Student.objects.all()
    
    # ===== 1. تبويب الراسب =====
    # الراسبين (حالة القيد = راسب وباق للإعادة)
    failed_students = all_students.filter(registration_status='راسب وباق للإعادة')
    
    # تجميع الراسبين حسب الفصل
    failed_by_classroom = {}
    for cls in Classroom.objects.all():
        failed_in_cls = failed_students.filter(classroom=cls)
        if failed_in_cls.exists():
            failed_by_classroom[cls.id] = {
                'classroom': cls,
                'students': failed_in_cls,
                'count': failed_in_cls.count()
            }
    
    # ===== 2. تبويب الإحصاء =====
    # إحصاء حسب النوع والحالة
    stats_by_gender_status = {}
    for gender_key, gender_label in [('male', 'بنين'), ('female', 'بنات')]:
        gender_students = all_students.filter(gender=gender_key)
        stats_by_gender_status[gender_key] = {
            'label': gender_label,
            'regular_new': gender_students.filter(registration_type='نظامي', exam_round='دور أول').count(),
            'regular_repeat': gender_students.filter(registration_type='نظامي', exam_round__in=['دور ثاني', 'باقي']).count(),
            'inclusion': gender_students.filter(inclusion_status__in=['بصري', 'سمعي', 'حركي', 'صعوبات تعلم', 'أخرى']).count(),
            'workers_new': gender_students.filter(registration_type='عمال', exam_round='دور أول').count(),
            'workers_repeat': gender_students.filter(registration_type='عمال', exam_round__in=['دور ثاني', 'باقي']).count(),
            'total': gender_students.count(),
        }
    
    # عدد الفصول حسب الصف والنوع
    classrooms_by_grade_gender = {}
    for grade_key in ['g1', 'g2', 'g3']:
        grade_label = {'g1': 'الصف الأول', 'g2': 'الصف الثاني', 'g3': 'الصف الثالث'}[grade_key]
        classrooms_by_grade_gender[grade_key] = {
            'label': grade_label,
            'male': Classroom.objects.filter(grade=grade_key, gender='male').count(),
            'female': Classroom.objects.filter(grade=grade_key, gender='female').count(),
            'total': Classroom.objects.filter(grade=grade_key).count(),
        }
    
    # ===== 3. إحصاء الطلاب المسيحيين =====
    christian_stats = {
        'male': all_students.filter(religion='مسيحية', gender='male').count(),
        'female': all_students.filter(religion='مسيحية', gender='female').count(),
        'total': all_students.filter(religion='مسيحية').count(),
    }
    
    # ===== 4. إحصاء السحب =====
    withdrawn_students = all_students.filter(exam_round='سحب').order_by('student_code')
    
    # ===== 5. إحصاء المجموع (حسب المرحلة والنوع) =====
    # المرحلة الأولى: حتى 165 (افتراض: 16.5 سنة = 16.5 * 12 = 198 شهر، لكن المستخدم قال 165، ربما يقصد 16.5 سنة)
    # سأفترض أنه يقصد السن عند الامتحان (exam_age) كرقم عشري أو سن
    # المرحلة الأولى: >= 16.5 (أو 165 شهر / 12 = 13.75 سنة؟)
    # المرحلة الثانية: 16.4 إلى 15.0
    # المرحلة الثالثة: 14.9 إلى 14.0
    
    # سأفترض أن exam_age هو السن بالسنوات، والمراحل:
    # المرحلة الأولى: >= 17 سنة
    # المرحلة الثانية: 16-15 سنة
    # المرحلة الثالثة: <= 14 سنة
    
    stage_stats = {}
    for stage_key, stage_label, min_age, max_age in [
        ('stage1', 'المرحلة الأولى', 17, 100),
        ('stage2', 'المرحلة الثانية', 15, 16),
        ('stage3', 'المرحلة الثالثة', 0, 14),
    ]:
        stage_students = all_students.filter(exam_age__gte=min_age, exam_age__lte=max_age)
        stage_stats[stage_key] = {
            'label': stage_label,
            'male': stage_students.filter(gender='male').count(),
            'female': stage_students.filter(gender='female').count(),
            'total': stage_students.count(),
        }
    
    # ===== 6. إجمالي الصف الأول =====
    grade1_students = all_students.filter(
        Q(grade__icontains='1') | Q(grade__icontains='الأول') | Q(grade__icontains='اول')
    )
    
    grade1_stats = {}
    for gender_key, gender_label in [('male', 'بنين'), ('female', 'بنات')]:
        g1_gender = grade1_students.filter(gender=gender_key)
        grade1_stats[gender_key] = {
            'label': gender_label,
            'regular_new': g1_gender.filter(registration_type='نظامي', exam_round='دور أول').count(),
            'regular_repeat': g1_gender.filter(registration_type='نظامي', exam_round__in=['دور ثاني', 'باقي']).count(),
            'inclusion': g1_gender.filter(inclusion_status__in=['بصري', 'سمعي', 'حركي', 'صعوبات تعلم', 'أخرى']).count(),
            'workers_new': g1_gender.filter(registration_type='عمال', exam_round='دور أول').count(),
            'total': g1_gender.count(),
        }
    
    # عدد فصول الصف الأول
    grade1_classrooms = {
        'male': Classroom.objects.filter(grade='g1', gender='male').count(),
        'female': Classroom.objects.filter(grade='g1', gender='female').count(),
        'total': Classroom.objects.filter(grade='g1').count(),
    }
    
    context = {
        'failed_students': failed_students,
        'failed_by_classroom': failed_by_classroom,
        'stats_by_gender_status': stats_by_gender_status,
        'classrooms_by_grade_gender': classrooms_by_grade_gender,
        'christian_stats': christian_stats,
        'withdrawn_students': withdrawn_students,
        'stage_stats': stage_stats,
        'grade1_stats': grade1_stats,
        'grade1_classrooms': grade1_classrooms,
    }
    
    return render(request, 'student_affairs/system_statistics.html', context)


def classroom_failed_details(request, classroom_id):
    """تفاصيل الراسبين في فصل محدد - للاستخدام في Modal"""
    classroom = get_object_or_404(Classroom, id=classroom_id)
    failed_students = Student.objects.filter(
        classroom=classroom,
        registration_status='راسب وباق للإعادة'
    ).order_by('name', 'student_code')
    
    context = {
        'classroom': classroom,
        'students': failed_students,
    }
    return render(request, 'student_affairs/classroom_failed_details.html', context)


@staff_member_required
def admin_create_user(request):
    """إنشاء مستخدم جديد مع توليد اسم مستخدم وكلمة مرور"""
    form = AdminCreateUserForm(request.POST or None)
    created = None
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        created = {
            'username': form.generated_username,
            'password': form.generated_password,
            'email': user.email,
        }
        messages.success(request, 'تم إنشاء المستخدم بنجاح')
    return render(request, 'student_affairs/admin_create_user.html', {
        'form': form,
        'created': created,
    })


def landing(request):
    """صفحة تعريفية احترافية للموقع"""
    site = SiteSettings.get_settings()
    return render(request, 'student_affairs/landing.html', {'site': site})


@require_http_methods(["GET", "POST"])
def custom_login(request):
    """
    صفحة تسجيل الدخول المخصصة مع JWT
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # تسجيل الدخول
            login(request, user)
            
            # توليد JWT token
            token = generate_jwt_token(user)
            
            # حفظ token في session
            request.session['jwt_token'] = token
            request.session['user_id'] = user.id
            
            # إعداد response
            response = redirect('/welcome/')
            
            # إضافة token كـ cookie
            response.set_cookie('jwt_token', token, max_age=7*24*60*60, httponly=True, samesite='Lax')
            
            messages.success(request, f'مرحباً {user.username}! تم تسجيل الدخول بنجاح.')
            return response
        else:
            messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة.')
    
    # إذا كان هناك token في URL، التحقق منه
    token = request.GET.get('token')
    if token:
        user = verify_jwt_token(token)
        if user:
            login(request, user)
            request.session['jwt_token'] = token
            request.session['user_id'] = user.id
            response = redirect('/welcome/')
            response.set_cookie('jwt_token', token, max_age=7*24*60*60, httponly=True, samesite='Lax')
            messages.success(request, f'مرحباً {user.username}! تم تسجيل الدخول بنجاح.')
            return response
    
    from django.contrib.auth.forms import AuthenticationForm
    form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


def custom_logout(request):
    """
    صفحة تسجيل الخروج المخصصة - تقبل GET request
    """
    if request.user.is_authenticated:
        # حذف JWT token من session
        if 'jwt_token' in request.session:
            del request.session['jwt_token']
        if 'user_id' in request.session:
            del request.session['user_id']
        
        # تسجيل الخروج
        logout(request)
        
        # حذف cookie
        response = redirect('/')
        response.delete_cookie('jwt_token')
        
        messages.success(request, 'تم تسجيل الخروج بنجاح.')
        return response
    
    return redirect('/')


def generate_login_link(request, user_id):
    """
    توليد رابط تسجيل دخول مشفر للمستخدم (للمستخدمين المصرح لهم فقط)
    """
    if not request.user.is_staff:
        messages.error(request, 'ليس لديك صلاحية للوصول إلى هذه الصفحة.')
        return redirect('/')
    
    try:
        user = User.objects.get(id=user_id)
        token = generate_jwt_token(user)
        login_url = f"{request.scheme}://{request.get_host()}/accounts/login/?token={token}"
        return render(request, 'student_affairs/generate_login_link.html', {
            'user': user,
            'token': token,
            'login_url': login_url,
        })
    except User.DoesNotExist:
        messages.error(request, 'المستخدم غير موجود.')
        return redirect('/')


@login_required
def chatbot_api(request):
    """
    API endpoint للشات بوت
    """
    if request.method == 'POST':
        import json
        from .chatbot import get_chatbot_response, analyze_image
        
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            image_data = data.get('image', None)
            conversation_history = data.get('history', [])
            
            user_name = request.user.username
            if hasattr(request.user, 'profile') and request.user.profile.full_name:
                user_name = request.user.profile.full_name
            
            # إذا كان هناك صورة، حللها
            if image_data:
                response = analyze_image(image_data, user_message, user_name)
            else:
                response = get_chatbot_response(user_message, user_name, None, conversation_history)
            
            return JsonResponse({
                'success': True,
                'response': response,
                'user_name': user_name
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)
