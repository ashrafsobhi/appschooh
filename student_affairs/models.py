from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from datetime import date
from .utils import parse_egyptian_national_id
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Student(models.Model):
    """نموذج الطالب"""
    
    # اختيارات الديانة
    RELIGION_CHOICES = [
        ('مسلمة', 'مسلمة'),
        ('مسيحية', 'مسيحية'),
    ]
    
    # اختيارات التبعية
    NATIONALITY_CHOICES = [
        ('رسمي', 'رسمي'),
        ('خدمات', 'خدمات'),
    ]
    
    # اختيارات حالة القيد
    REGISTRATION_STATUS_CHOICES = [
        ('ناجح ومنقول', 'ناجح ومنقول'),
        ('راسب وباق للإعادة', 'راسب وباق للإعادة'),
    ]
    
    # اختيارات نوع القيد
    REGISTRATION_TYPE_CHOICES = [
        ('نظامي', 'نظامي'),
        ('عمال', 'عمال'),
    ]
    
    # اختيارات الشعبة
    SECTION_CHOICES = [
        ('فني مبيعات', 'فني مبيعات'),
        ('فني تأمين', 'فني تأمين'),
        ('تأمين', 'تأمين'),
        ('عامة', 'عامة'),
    ]
    
    # اللغات الأجنبية
    LANGUAGE_CHOICES = [
        ('إنجليزي', 'اللغة الإنجليزية'),
        ('فرنسي', 'اللغة الفرنسية'),
        ('ألماني', 'اللغة الألمانية'),
        ('إيطالي', 'اللغة الإيطالية'),
        ('إسباني', 'اللغة الإسبانية'),
        ('لغة أخرى', 'لغة أخرى'),
    ]
    
    # موقف الدمج / الإعاقة
    INCLUSION_CHOICES = [
        ('لا يوجد', 'لا يوجد'),
        ('بصري', 'إعاقة بصرية'),
        ('سمعي', 'إعاقة سمعية'),
        ('حركي', 'إعاقة حركية'),
        ('صعوبات تعلم', 'صعوبات تعلم'),
        ('أخرى', 'أخرى'),
    ]
    
    # حالة الدور/الامتحان
    EXAM_ROUND_CHOICES = [
        ('دور أول', 'دور أول'),
        ('دور ثاني', 'دور ثاني'),
        ('باقي', 'باقي'),
        ('سحب', 'سحب'),
    ]
    
    # اختيارات النوع
    GENDER_CHOICES = [
        ('male', 'ذكر'),
        ('female', 'أنثى'),
    ]
    
    # الحقول الأساسية
    student_code = models.CharField(max_length=50, unique=True, verbose_name='كود الطالب')
    name = models.CharField(max_length=200, verbose_name='اسم الطالب')
    religion = models.CharField(max_length=20, choices=RELIGION_CHOICES, verbose_name='الديانة')
    nationality = models.CharField(max_length=20, choices=NATIONALITY_CHOICES, verbose_name='التبعية')
    registration_status = models.CharField(max_length=30, choices=REGISTRATION_STATUS_CHOICES, verbose_name='حالة القيد')
    registration_type = models.CharField(max_length=20, choices=REGISTRATION_TYPE_CHOICES, verbose_name='نوع القيد')
    section = models.CharField(max_length=100, choices=SECTION_CHOICES, verbose_name='الشعبة')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name='النوع')
    birth_governorate = models.CharField(max_length=100, verbose_name='محافظة الميلاد')
    birth_date = models.DateField(verbose_name='تاريخ الميلاد')
    national_id = models.CharField(max_length=14, unique=True, verbose_name='الرقم القومي')
    age = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)], verbose_name='السن')
    exam_age = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)], verbose_name='السن عند الامتحان')
    school = models.CharField(max_length=200, verbose_name='المدرسة')
    guardian_name = models.CharField(max_length=200, verbose_name='اسم ولي الأمر')
    address = models.CharField(max_length=255, verbose_name='العنوان', blank=True, null=True)
    phone = models.CharField(max_length=20, verbose_name='هاتف الطالب', blank=True, null=True)
    guardian_phone = models.CharField(max_length=20, verbose_name='هاتف ولي الأمر', blank=True, null=True)
    photo = models.ImageField(upload_to='students/photos/', null=True, blank=True, verbose_name='صورة الطالب')
    governorate = models.CharField(max_length=100, verbose_name='المحافظة', blank=True, null=True)
    administration = models.CharField(max_length=200, verbose_name='الإدارة', blank=True, null=True)
    grade = models.CharField(max_length=50, verbose_name='الصف', blank=True, null=True)
    academic_year = models.CharField(max_length=20, verbose_name='العام الأكاديمي', blank=True, null=True)
    
    # أكواد من الإعدادات (تخزين ضمن السجل)
    admin_code = models.CharField(max_length=50, blank=True, null=True, verbose_name='كود الإدارة')
    school_serial = models.CharField(max_length=50, blank=True, null=True, verbose_name='مسلسل المدرسة')
    
    # حقول السجلات الجديدة
    first_foreign_language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, blank=True, null=True, verbose_name='اللغة الأجنبية الأولى')
    second_foreign_language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, blank=True, null=True, verbose_name='اللغة الأجنبية الثانية')
    inclusion_status = models.CharField(max_length=20, choices=INCLUSION_CHOICES, default='لا يوجد', verbose_name='موقف الدمج')
    inclusion_details = models.CharField(max_length=200, blank=True, null=True, verbose_name='تفاصيل الإعاقة (إن وجدت)')
    exam_round = models.CharField(max_length=20, choices=EXAM_ROUND_CHOICES, blank=True, null=True, verbose_name='حالة الطالب (الدور)')
    transferred_from = models.CharField(max_length=200, blank=True, null=True, verbose_name='محول من')
    transferred_to = models.CharField(max_length=200, blank=True, null=True, verbose_name='محول إلى')
    is_returnee = models.BooleanField(default=False, verbose_name='عائد')
    is_withdrawn = models.BooleanField(default=False, verbose_name='سحب')
    # الفصل الدراسي (يرتبط لاحقاً بنموذج Classroom)
    # ملاحظة: سيتم إنشاء نموذج Classroom أدناه وإضافة العلاقة هنا بعد تعريفه باستخدام اسم السلسلة
    classroom = models.ForeignKey('Classroom', on_delete=models.SET_NULL, null=True, blank=True, related_name='students', verbose_name='الفصل')
    
    # وافد
    is_foreign_student = models.BooleanField(default=False, verbose_name='طالب وافد')
    foreign_birth_date = models.DateField(blank=True, null=True, verbose_name='تاريخ ميلاد الوافد')
    foreign_birth_place = models.CharField(max_length=200, blank=True, null=True, verbose_name='محل ميلاد الوافد')
    foreign_gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True, verbose_name='نوع الوافد')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    
    class Meta:
        verbose_name = 'طالب'
        verbose_name_plural = 'الطلبة'
        ordering = ['student_code']
    
    def __str__(self):
        return f"{self.student_code} - {self.name}"
    
    def get_religion_display_by_gender(self):
        """عرض الديانة بشكل صحيح حسب الجنس"""
        if self.religion == 'مسلمة':
            if self.gender == 'male':
                return 'مسلم'
            else:
                return 'مسلمة'
        elif self.religion == 'مسيحية':
            if self.gender == 'male':
                return 'مسيحي'
            else:
                return 'مسيحية'
        return self.get_religion_display()
    
    def clean(self):
        """التحقق من البيانات واستخراجها من الرقم القومي"""
        if self.national_id and len(str(self.national_id)) == 14:
            try:
                data = parse_egyptian_national_id(self.national_id)
                if data:
                    # تعيين البيانات المستخرجة
                    if not self.birth_date:
                        self.birth_date = data['birth_date']
                    if not self.birth_governorate:
                        self.birth_governorate = data['birth_governorate']
                    if not self.gender:
                        self.gender = data['gender']
                    if not self.age:
                        self.age = data['age']
            except ValidationError:
                pass  # تجاهل الأخطاء في حالة عدم اكتمال البيانات
    
    def save(self, *args, **kwargs):
        # استخراج البيانات من الرقم القومي إذا كان موجوداً
        if self.national_id and len(str(self.national_id)) == 14:
            try:
                data = parse_egyptian_national_id(self.national_id)
                if data:
                    self.birth_date = data['birth_date']
                    self.birth_governorate = data['birth_governorate']
                    self.gender = data['gender']
                    self.age = data['age']
            except ValidationError:
                pass
        
        # حساب السن تلقائياً من تاريخ الميلاد
        if self.birth_date:
            today = date.today()
            self.age = today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        # مزامنة السحب مع الحقل المنفصل إن وجد
        try:
            if getattr(self, 'exam_round', None) == 'سحب':
                self.is_withdrawn = True
        except Exception:
            pass
        super().save(*args, **kwargs)


class StudentAttachment(models.Model):
    """نموذج مرفقات الطالب"""
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attachments', verbose_name='الطالب')
    title = models.CharField(max_length=200, verbose_name='عنوان المستند')
    file = models.FileField(upload_to='students/attachments/', verbose_name='الملف')
    description = models.TextField(blank=True, null=True, verbose_name='الوصف')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الرفع')
    
    class Meta:
        verbose_name = 'مرفق طالب'
        verbose_name_plural = 'مرفقات الطلبة'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.student.name} - {self.title}"
    
    def get_file_icon(self):
        """إرجاع أيقونة حسب نوع الملف"""
        ext = self.file.name.split('.')[-1].lower()
        if ext in ['pdf']:
            return 'fa-file-pdf'
        elif ext in ['doc', 'docx']:
            return 'fa-file-word'
        elif ext in ['xls', 'xlsx']:
            return 'fa-file-excel'
        elif ext in ['jpg', 'jpeg', 'png', 'gif']:
            return 'fa-file-image'
        else:
            return 'fa-file'


class UserProfile(models.Model):
    """بيانات إضافية للمستخدم"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=200, verbose_name='الاسم الثلاثي')
    phone = models.CharField(max_length=20, verbose_name='رقم الهاتف', blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True, verbose_name='الصورة الشخصية')

    class Meta:
        verbose_name = 'ملف مستخدم'
        verbose_name_plural = 'ملفات المستخدمين'

    def __str__(self):
        return self.full_name or self.user.username


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance, defaults={'full_name': instance.get_full_name() or instance.username})
    else:
        # لا تُنشئ إن كان موجود؛ حدّث فقط الاسم الكامل إذا كان فارغاً
        try:
            profile = instance.profile
            if not profile.full_name:
                profile.full_name = instance.get_full_name() or instance.username
                profile.save(update_fields=['full_name'])
        except UserProfile.DoesNotExist:
            UserProfile.objects.create(user=instance, full_name=instance.get_full_name() or instance.username)

class SiteSettings(models.Model):
    """إعدادات الموقع العامة"""
    
    school_name = models.CharField(max_length=200, verbose_name='اسم المدرسة', default='المدرسة')
    administration = models.CharField(max_length=200, verbose_name='الإدارة', default='الإدارة التعليمية')
    directorate = models.CharField(max_length=200, verbose_name='المديرية', default='')
    admin_code = models.CharField(max_length=50, verbose_name='كود الإدارة', default='')
    school_serial = models.CharField(max_length=50, verbose_name='مسلسل المدرسة', default='')
    school_manager = models.CharField(max_length=200, verbose_name='مدير المدرسة', blank=True, null=True)
    student_affairs_deputy = models.CharField(max_length=200, verbose_name='وكيل شؤون الطلبة', blank=True, null=True)
    
    class Meta:
        verbose_name = 'إعدادات الموقع'
        verbose_name_plural = 'إعدادات الموقع'
    
    def __str__(self):
        return 'إعدادات الموقع'
    
    def save(self, *args, **kwargs):
        # السماح بسجل واحد فقط
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """الحصول على إعدادات الموقع (إنشاء سجل افتراضي إذا لم يكن موجود)"""
        obj, created = cls.objects.get_or_create(pk=1, defaults={
            'school_name': 'المدرسة',
            'administration': 'الإدارة التعليمية',
            'school_manager': '',
            'student_affairs_deputy': '',
        })
        return obj


class Classroom(models.Model):
    """نموذج الفصل الدراسي"""
    GRADE_CHOICES = [
        ('g1', 'الصف الأول'),
        ('g2', 'الصف الثاني'),
        ('g3', 'الصف الثالث'),
    ]
    GENDER_CHOICES = [
        ('male', 'بنين'),
        ('female', 'بنات'),
    ]

    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, verbose_name='الصف')
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, verbose_name='النوع')
    class_number = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)], verbose_name='رقم الفصل')
    seats_count = models.PositiveIntegerField(default=30, validators=[MinValueValidator(1)], verbose_name='عدد المقاعد')
    floor = models.PositiveIntegerField(default=1, validators=[MinValueValidator(0)], verbose_name='الطابق')
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name='اسم الفصل')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'فصل'
        verbose_name_plural = 'الفصول'
        unique_together = ('grade', 'gender', 'class_number')
        ordering = ['grade', 'class_number']

    def __str__(self):
        return self.display_name

    @property
    def display_name(self) -> str:
        grade_num = {'g1': '1', 'g2': '2', 'g3': '3'}.get(self.grade, '?')
        return f"{grade_num}/{self.class_number}"

    def has_capacity(self) -> bool:
        return self.students.count() < self.seats_count

    def remaining_seats(self) -> int:
        return max(self.seats_count - self.students.count(), 0)

