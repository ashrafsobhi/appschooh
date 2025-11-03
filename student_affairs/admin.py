from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Student, StudentAttachment, SiteSettings


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_code', 'name', 'colored_religion', 'nationality_badge', 'status_badge', 'gender_icon', 'age', 'actions_column']
    list_display_links = ['student_code', 'name']
    list_filter = ['religion', 'nationality', 'registration_status', 'registration_type', 'gender', 'birth_governorate']
    search_fields = ['student_code', 'name', 'national_id', 'guardian_name', 'school']
    readonly_fields = ['created_at', 'updated_at', 'photo_preview']
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('البيانات الأساسية', {
            'fields': ('student_code', 'name', 'gender', 'religion', 'nationality', 'photo', 'photo_preview'),
            'classes': ('wide',)
        }),
        ('البيانات الأكاديمية', {
            'fields': ('registration_status', 'registration_type', 'section', 'school', 'grade', 'academic_year'),
            'classes': ('wide',)
        }),
        ('البيانات الشخصية', {
            'fields': ('national_id', 'birth_date', 'birth_governorate', 'governorate', 'age', 'exam_age'),
            'description': 'ملاحظة: تاريخ الميلاد، السن، محافظة الميلاد، والنوع يتم استخراجهم تلقائياً من الرقم القومي',
            'classes': ('wide',)
        }),
        ('بيانات ولي الأمر', {
            'fields': ('guardian_name',),
            'classes': ('collapse',)
        }),
        ('الإدارة', {
            'fields': ('administration',),
            'classes': ('collapse',)
        }),
        ('معلومات إضافية', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def colored_religion(self, obj):
        """عرض الديانة مع لون مخصص"""
        religion = obj.get_religion_display_by_gender()
        if 'مسلم' in religion:
            color = '#27ae60'
            bg = '#d4edda'
        elif 'مسيحي' in religion:
            color = '#3498db'
            bg = '#d1ecf1'
        else:
            color = '#7f8c8d'
            bg = '#ecf0f1'
        
        return format_html(
            '<span style="background: {}; color: {}; padding: 4px 10px; border-radius: 4px; font-weight: 600; font-size: 12px; display: inline-block;">{}</span>',
            bg, color, religion
        )
    colored_religion.short_description = 'الديانة'
    colored_religion.admin_order_field = 'religion'
    
    def nationality_badge(self, obj):
        """عرض التبعية مع شارة"""
        nationality = obj.get_nationality_display()
        if nationality == 'رسمي':
            color = '#2980b9'
            bg = '#d1ecf1'
        else:
            color = '#f39c12'
            bg = '#fff3cd'
        
        return format_html(
            '<span style="background: {}; color: {}; padding: 4px 10px; border-radius: 4px; font-weight: 600; font-size: 12px; display: inline-block;">{}</span>',
            bg, color, nationality
        )
    nationality_badge.short_description = 'التبعية'
    nationality_badge.admin_order_field = 'nationality'
    
    def status_badge(self, obj):
        """عرض حالة القيد مع شارة ملونة"""
        status = obj.get_registration_status_display()
        if status == 'ناجح ومنقول':
            color = '#27ae60'
            bg = '#d4edda'
        else:
            color = '#e74c3c'
            bg = '#f8d7da'
        
        return format_html(
            '<span style="background: {}; color: {}; padding: 4px 10px; border-radius: 4px; font-weight: 600; font-size: 12px; display: inline-block;">{}</span>',
            bg, color, status
        )
    status_badge.short_description = 'حالة القيد'
    status_badge.admin_order_field = 'registration_status'
    
    def gender_icon(self, obj):
        """عرض الجنس مع أيقونة"""
        if obj.gender == 'male':
            color = '#3498db'
            text = 'ذكر'
        else:
            color = '#e91e63'
            text = 'أنثى'
        
        return format_html(
            '<span style="color: {}; font-weight: 600; font-size: 13px;">{}</span>',
            color, text
        )
    gender_icon.short_description = 'النوع'
    gender_icon.admin_order_field = 'gender'
    
    def photo_preview(self, obj):
        """معاينة الصورة"""
        if obj.photo:
            return format_html(
                '<img src="{}" style="max-width: 150px; max-height: 150px; border-radius: 4px; border: 1px solid #e1e8ed;" />',
                obj.photo.url
            )
        return format_html('<span style="color: #95a5a6; font-size: 13px;">لا توجد صورة</span>')
    photo_preview.short_description = 'معاينة الصورة'
    
    def actions_column(self, obj):
        """عمود الإجراءات السريعة"""
        url = reverse('admin:student_affairs_student_change', args=[obj.pk])
        return format_html(
            '<a href="{}" style="background: #3498db; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 12px; font-weight: 500;">تعديل</a>',
            url
        )
    actions_column.short_description = 'إجراءات'


@admin.register(StudentAttachment)
class StudentAttachmentAdmin(admin.ModelAdmin):
    list_display = ['student_link', 'title', 'file_type_icon', 'uploaded_at', 'file_size']
    list_filter = ['uploaded_at']
    search_fields = ['student__name', 'title', 'student__student_code']
    readonly_fields = ['uploaded_at', 'file_preview']
    date_hierarchy = 'uploaded_at'
    
    def student_link(self, obj):
        """رابط للطالب"""
        url = reverse('admin:student_affairs_student_change', args=[obj.student.pk])
        return format_html(
            '<a href="{}" style="color: #667eea; font-weight: 600; text-decoration: none;">'
            '<i class="fas fa-user"></i> {}'
            '</a>',
            url, obj.student.name
        )
    student_link.short_description = 'الطالب'
    student_link.admin_order_field = 'student__name'
    
    def file_type_icon(self, obj):
        """أيقونة نوع الملف"""
        icon = obj.get_file_icon()
        return format_html('<i class="fas {}" style="font-size: 18px; color: #667eea;"></i>', icon)
    file_type_icon.short_description = 'النوع'
    
    def file_size(self, obj):
        """حجم الملف"""
        if obj.file:
            try:
                size = obj.file.size
                if size < 1024:
                    return f"{size} B"
                elif size < 1024 * 1024:
                    return f"{size / 1024:.1f} KB"
                else:
                    return f"{size / (1024 * 1024):.1f} MB"
            except:
                return "-"
        return "-"
    file_size.short_description = 'الحجم'
    
    def file_preview(self, obj):
        """معاينة الملف"""
        if obj.file:
            file_type = obj.file.name.split('.')[-1].lower()
            if file_type in ['jpg', 'jpeg', 'png', 'gif']:
                return format_html(
                    '<img src="{}" style="max-width: 300px; max-height: 300px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);" />',
                    obj.file.url
                )
            else:
                return format_html(
                    '<a href="{}" target="_blank" style="display: inline-flex; align-items: center; gap: 10px; background: #667eea; color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: 600;">'
                    '<i class="fas {}"></i> فتح الملف'
                    '</a>',
                    obj.file.url, obj.get_file_icon()
                )
        return format_html('<span style="color: #999;">لا يوجد ملف</span>')
    file_preview.short_description = 'معاينة الملف'


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['school_name', 'administration', 'directorate', 'admin_code', 'school_serial', 'school_manager', 'student_affairs_deputy', 'created_info']
    fieldsets = (
        ('إعدادات المدرسة', {
            'fields': ('school_name', 'administration', 'directorate'),
            'description': 'إعدادات المدرسة العامة المستخدمة في جميع أنحاء النظام'
        }),
        ('الأكواد', {
            'fields': ('admin_code', 'school_serial'),
            'description': 'أكواد يتم تمريرها تلقائياً في السجلات'
        }),
        ('المناصب', {
            'fields': ('school_manager', 'student_affairs_deputy'),
            'description': 'أسماء تظهر تلقائياً في تذييل الطباعة'
        }),
    )
    
    def created_info(self, obj):
        """معلومات الإنشاء"""
        if obj.pk:
            return format_html(
                '<span style="color: #6c757d; font-size: 12px;">'
                '<i class="fas fa-info-circle"></i> تم الإعداد'
                '</span>'
            )
        return format_html('<span style="color: #dc3545;">غير محدّد</span>')
    created_info.short_description = 'الحالة'
    
    def has_add_permission(self, request):
        # منع إضافة أكثر من سجل واحد
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # منع الحذف
        return False
    
    def has_change_permission(self, request, obj=None):
        # السماح بالتعديل دائماً
        return True
