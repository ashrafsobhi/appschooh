"""
أدوات مساعدة لاستخراج البيانات من الرقم القومي المصري
"""
from datetime import date
from django.core.exceptions import ValidationError


# أكواد محافظات مصر
GOVERNORATE_CODES = {
    '01': 'القاهرة',
    '02': 'الإسكندرية',
    '03': 'بورسعيد',
    '04': 'السويس',
    '11': 'دمياط',
    '12': 'الدقهلية',
    '13': 'الشرقية',
    '14': 'القليوبية',
    '15': 'كفر الشيخ',
    '16': 'الغربية',
    '17': 'المنوفية',
    '18': 'البحيرة',
    '19': 'الإسماعيلية',
    '21': 'الجيزة',
    '22': 'بني سويف',
    '23': 'الفيوم',
    '24': 'المنيا',
    '25': 'أسيوط',
    '26': 'سوهاج',
    '27': 'قنا',
    '28': 'أسوان',
    '29': 'الأقصر',
    '31': 'البحر الأحمر',
    '32': 'الوادي الجديد',
    '33': 'مطروح',
    '34': 'شمال سيناء',
    '35': 'جنوب سيناء',
    '88': 'خارج الجمهورية',
}


def parse_egyptian_national_id(national_id):
    """
    استخراج البيانات من الرقم القومي المصري
    
    الرقم القومي يتكون من 14 رقم:
    - الرقم 1: القرن (2 = 1900-1999, 3 = 2000-2099)
    - الأرقام 2-7: تاريخ الميلاد (YYMMDD)
    - الأرقام 8-9: كود المحافظة
    - الأرقام 10-13: التسلسل (الرقم 13 يحدد الجنس: فردي=ذكر، زوجي=أنثى)
    - الرقم 14: رقم التحقق
    """
    if not national_id:
        return None
    
    national_id = str(national_id).strip()
    
    # التحقق من طول الرقم القومي
    if len(national_id) != 14:
        raise ValidationError('الرقم القومي يجب أن يكون 14 رقم')
    
    # التحقق من أن جميع الأرقام رقمية
    if not national_id.isdigit():
        raise ValidationError('الرقم القومي يجب أن يحتوي على أرقام فقط')
    
    try:
        # استخراج القرن
        century_digit = int(national_id[0])
        century = 1900 if century_digit == 2 else 2000 if century_digit == 3 else 1800
        
        # استخراج تاريخ الميلاد (الأرقام 2-7: YYMMDD)
        year = int(national_id[1:3])
        month = int(national_id[3:5])
        day = int(national_id[5:7])
        
        # حساب السنة الكاملة
        full_year = century + year
        
        # التحقق من صحة التاريخ
        try:
            birth_date = date(full_year, month, day)
        except ValueError:
            raise ValidationError('تاريخ الميلاد المستخرج من الرقم القومي غير صحيح')
        
        # استخراج محافظة الميلاد (الأرقام 8-9)
        governorate_code = national_id[7:9]
        birth_governorate = GOVERNORATE_CODES.get(governorate_code, 'غير محدد')
        
        # استخراج الجنس من الرقم 13 (من اليسار، أي الرقم 12 من 0-indexed)
        # الرقم 13 هو الرقم 12 في الفهرس (من 0)
        gender_digit = int(national_id[12])
        gender = 'male' if gender_digit % 2 == 1 else 'female'
        
        # حساب السن
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        
        return {
            'birth_date': birth_date,
            'birth_governorate': birth_governorate,
            'gender': gender,
            'age': age,
        }
    except (ValueError, IndexError) as e:
        raise ValidationError(f'خطأ في قراءة الرقم القومي: {str(e)}')


