from django import forms
from django.db.models import Q
from .models import Student, StudentAttachment, Classroom
from .utils import parse_egyptian_national_id
from datetime import date
from django.contrib.auth.models import User
import random
import string


class StudentForm(forms.ModelForm):
    """نموذج إضافة طالب"""
    
    class Meta:
        model = Student
        fields = [
            'student_code', 'name', 'religion', 'nationality', 
            'registration_status', 'registration_type', 'section',
            'national_id', 'exam_age', 'school', 'guardian_name', 'photo',
            'address', 'phone', 'guardian_phone',
            'governorate', 'administration', 'grade', 'academic_year'
        ]
        widgets = {
            'student_code': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'religion': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'nationality': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'registration_status': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'registration_type': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'section': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'national_id': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'maxlength': '14', 'id': 'national_id_input'}),
            'exam_age': forms.NumberInput(attrs={'class': 'form-control', 'required': True, 'min': '1', 'max': '100'}),
            'school': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'guardian_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'guardian_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'governorate': forms.TextInput(attrs={'class': 'form-control'}),
            'administration': forms.TextInput(attrs={'class': 'form-control'}),
            'grade': forms.TextInput(attrs={'class': 'form-control'}),
            'academic_year': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'student_code': 'كود الطالب',
            'name': 'اسم الطالب',
            'religion': 'الديانة',
            'nationality': 'التبعية',
            'registration_status': 'حالة القيد',
            'registration_type': 'نوع القيد',
            'section': 'الشعبة',
            'national_id': 'الرقم القومي (14 رقم)',
            'exam_age': 'السن عند الامتحان',
            'school': 'المدرسة',
            'guardian_name': 'اسم ولي الأمر',
            'address': 'العنوان',
            'phone': 'هاتف الطالب',
            'guardian_phone': 'هاتف ولي الأمر',
            'photo': 'صورة الطالب',
            'governorate': 'المحافظة',
            'administration': 'الإدارة',
            'grade': 'الصف',
            'academic_year': 'العام الأكاديمي',
        }


class ExcelUploadForm(forms.Form):
    """نموذج رفع ملف Excel"""
    excel_file = forms.FileField(
        label='ملف Excel',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx,.xls'
        }),
        help_text='يرجى رفع ملف Excel بصيغة .xlsx أو .xls'
    )


class AttachmentForm(forms.ModelForm):
    """نموذج إضافة مرفق للطالب"""
    
    class Meta:
        model = StudentAttachment
        fields = ['title', 'file', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'file': forms.FileInput(attrs={'class': 'form-control', 'required': True}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'title': 'عنوان المستند',
            'file': 'الملف',
            'description': 'الوصف (اختياري)',
        }


class RecordsForm(forms.ModelForm):
    """نموذج إنشاء سجل طالب (موسع)"""
    # إدخال السن في أول أكتوبر (اختياري: سنوات/أشهر/أيام - نخزن السنوات فقط في exam_age)
    exam_age_years = forms.IntegerField(required=False, min_value=0, label='سنوات')
    exam_age_months = forms.IntegerField(required=False, min_value=0, max_value=11, label='أشهر')
    exam_age_days = forms.IntegerField(required=False, min_value=0, max_value=30, label='أيام')
    
    class Meta:
        model = Student
        fields = [
            # أساسي (حقول السجل داخل الطالب دون تكرار هوية الطالب)
            'nationality', 'grade', 'section', 'exam_age',
            # بقية الحقول الخاصة بالسجل
            'first_foreign_language', 'second_foreign_language',
            'registration_type', 'registration_status',
            'inclusion_status', 'inclusion_details',
            'guardian_name', 'school', 'academic_year',
            # أكواد
            'admin_code', 'school_serial',
            # وافد
            'is_foreign_student', 'foreign_birth_date', 'foreign_birth_place', 'foreign_gender',
            # حالات إضافية
            'exam_round', 'transferred_from', 'transferred_to', 'is_returnee',
        ]
        widgets = {
            'nationality': forms.Select(attrs={'class': 'form-select'}),
            'grade': forms.TextInput(attrs={'class': 'form-control'}),
            'section': forms.Select(attrs={'class': 'form-select'}),
            'exam_age': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'first_foreign_language': forms.Select(attrs={'class': 'form-select'}),
            'second_foreign_language': forms.Select(attrs={'class': 'form-select'}),
            'registration_type': forms.Select(attrs={'class': 'form-select'}),
            'registration_status': forms.Select(attrs={'class': 'form-select'}),
            'inclusion_status': forms.Select(attrs={'class': 'form-select', 'id': 'id_inclusion_status'}),
            'inclusion_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'guardian_name': forms.TextInput(attrs={'class': 'form-control'}),
            'school': forms.TextInput(attrs={'class': 'form-control'}),
            'academic_year': forms.TextInput(attrs={'class': 'form-control'}),
            'admin_code': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'school_serial': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'is_foreign_student': forms.CheckboxInput(attrs={'id': 'id_is_foreign_student', 'class': 'form-check-input'}),
            'foreign_birth_date': forms.DateInput(attrs={'class': 'form-control', 'id': 'id_foreign_birth_date'}),
            'foreign_birth_place': forms.TextInput(attrs={'class': 'form-control'}),
            'foreign_gender': forms.Select(attrs={'class': 'form-select'}),
            'exam_round': forms.Select(attrs={'class': 'form-select'}),
            'transferred_from': forms.TextInput(attrs={'class': 'form-control'}),
            'transferred_to': forms.TextInput(attrs={'class': 'form-control'}),
            'is_returnee': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_is_returnee'}),
        }
        labels = {
            'nationality': 'تبعية المدرسة',
            'grade': 'الصف الدراسي',
            'section': 'الشعبة',
            'exam_age': 'السن في أول أكتوبر (سنوات فقط)',
            'first_foreign_language': 'اللغة الأجنبية الأولى',
            'second_foreign_language': 'اللغة الأجنبية الثانية',
            'registration_type': 'نوع القيد',
            'registration_status': 'حالة القيد',
            'inclusion_status': 'موقف الدمج',
            'inclusion_details': 'تفاصيل الدمج/الإعاقة',
            'guardian_name': 'اسم ولي الأمر',
            'school': 'المدرسة',
            'academic_year': 'العام الدراسي',
            'admin_code': 'كود الإدارة',
            'school_serial': 'مسلسل المدرسة',
            'is_foreign_student': 'طالب وافد',
            'foreign_birth_date': 'تاريخ ميلاد الوافد',
            'foreign_birth_place': 'محل ميلاد الوافد',
            'foreign_gender': 'نوع الوافد',
            'exam_round': 'حالة الدور',
            'transferred_from': 'محول من مدرسة',
            'transferred_to': 'محول إلى مدرسة',
            'is_returnee': 'عائد',
        }

    def clean(self):
        cleaned = super().clean()
        years = cleaned.get('exam_age_years')
        if years is not None:
            cleaned['exam_age'] = years
        return cleaned


class SelectStudentForm(forms.Form):
    """اختيار طالب موجود لإضافة/تحديث سجل."""
    student = forms.ModelChoiceField(
        queryset=Student.objects.all().order_by('student_code'),
        label='اختر الطالب',
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class StudentContactForm(forms.ModelForm):
    """نموذج لتحديث العنوان وأرقام الهواتف من الملف الشخصي"""
    class Meta:
        model = Student
        fields = ['address', 'phone', 'guardian_phone']
        widgets = {
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'العنوان'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'هاتف الطالب'}),
            'guardian_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'هاتف ولي الأمر'}),
        }
        labels = {
            'address': 'العنوان',
            'phone': 'هاتف الطالب',
            'guardian_phone': 'هاتف ولي الأمر',
        }

class ClassroomForm(forms.ModelForm):
    """نموذج إنشاء/تعديل فصل"""
    class Meta:
        model = Classroom
        fields = ['grade', 'gender', 'class_number', 'seats_count', 'floor', 'name']
        widgets = {
            'grade': forms.Select(attrs={'class': 'form-select'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'class_number': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'seats_count': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'floor': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم اختياري للفصل'}),
        }
        labels = {
            'grade': 'الصف',
            'gender': 'النوع',
            'class_number': 'رقم الفصل',
            'seats_count': 'عدد المقاعد',
            'floor': 'الطابق',
            'name': 'اسم الفصل (اختياري)',
        }


class AddStudentToClassroomForm(forms.Form):
    """نموذج إضافة طلاب إلى فصل (متعدد) مع بحث بالاسم"""
    students = forms.ModelMultipleChoiceField(
        queryset=Student.objects.none(),
        label='اختر الطلبة',
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': '12'})
    )

    def __init__(self, *args, **kwargs):
        classroom: Classroom = kwargs.pop('classroom')
        search_query: str = kwargs.pop('search_query', '')
        super().__init__(*args, **kwargs)
        # فلترة الطلاب وفق صف ونوع الفصل، وغير مسندين لأي فصل
        qs = Student.objects.filter(
            gender=classroom.gender,
            classroom__isnull=True,
        )
        # دعم صيغ متعددة للصف: رموز g1/g2/g3 أو أرقام أو أسماء عربية
        if classroom.grade == 'g1':
            grade_filter = (
                Q(grade__iexact='g1') |
                Q(grade__icontains='1') |
                Q(grade__icontains='الأول') |
                Q(grade__icontains='اول')
            )
            qs = qs.filter(grade_filter)
        elif classroom.grade == 'g2':
            grade_filter = (
                Q(grade__iexact='g2') |
                Q(grade__icontains='2') |
                Q(grade__icontains='الثاني') |
                Q(grade__icontains='ثاني')
            )
            qs = qs.filter(grade_filter)
        elif classroom.grade == 'g3':
            grade_filter = (
                Q(grade__iexact='g3') |
                Q(grade__icontains='3') |
                Q(grade__icontains='الثالث') |
                Q(grade__icontains='ثالث')
            )
            qs = qs.filter(grade_filter)
        # بحث بالاسم (اختياري)
        if search_query:
            qs = qs.filter(name__icontains=search_query)
        # ترتيب أبجدي بالاسم ثم بالكود
        self.fields['students'].queryset = qs.order_by('name', 'student_code')
        # شكل التسمية داخل القائمة المنسدلة: الاسم - الكود
        self.fields['students'].label_from_instance = lambda s: f"{s.name} - {s.student_code}"


class AdminCreateUserForm(forms.Form):
    """نموذج إنشاء مستخدم جديد من لوحة التحكم"""
    full_name = forms.CharField(
        label='الاسم الثلاثي', 
        max_length=200, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'required': True})
    )
    phone = forms.CharField(
        label='رقم الهاتف', 
        max_length=20, 
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='البريد الإلكتروني', 
        widget=forms.EmailInput(attrs={'class': 'form-control', 'required': True})
    )

    generated_username = None
    generated_password = None

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('هذا البريد الإلكتروني مستخدم بالفعل')
        return email

    def _generate_username(self, base: str) -> str:
        """توليد اسم مستخدم فريد"""
        base = ''.join(ch for ch in base.lower() if ch.isalnum())[:12] or 'user'
        candidate = base
        suffix = 1
        while User.objects.filter(username=candidate).exists():
            candidate = f"{base}{suffix}"
            suffix += 1
        return candidate

    def _generate_password(self, length: int = 10) -> str:
        """توليد كلمة مرور عشوائية"""
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    def save(self):
        """إنشاء المستخدم والبروفايل"""
        full_name = self.cleaned_data['full_name'].strip()
        email = self.cleaned_data['email']
        phone = self.cleaned_data.get('phone', '')

        # توليد اسم المستخدم من أول جزء من الاسم
        base = full_name.split()[0] if full_name else 'user'
        username = self._generate_username(base)
        password = self._generate_password()

        # تقسيم الاسم إلى first_name و last_name
        name_parts = full_name.split()
        first_name = name_parts[0] if name_parts else ''
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

        # إنشاء المستخدم
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        # إنشاء أو تحديث البروفايل
        from .models import UserProfile
        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults={'full_name': full_name, 'phone': phone}
        )
        if not profile.full_name:
            profile.full_name = full_name
        profile.phone = phone
        profile.save()

        # حفظ البيانات المُولدة للعرض
        self.generated_username = username
        self.generated_password = password
        return user

