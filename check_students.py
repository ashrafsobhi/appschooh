"""
سكريبت للتحقق من الطلاب في قاعدة البيانات
يمكن تشغيله من Django shell أو من Terminal
"""

# للتشغيل من Django shell:
# python manage.py shell
# ثم انسخ والصق الكود التالي:

from student_affairs.models import Student
from django.db.models import Q

# البحث عن الطالب "رحمة صبحي رزق يوسف"
student = Student.objects.filter(name__icontains='رحمة صبحي').first()

if student:
    print(f"تم العثور على الطالب: {student.name}")
    print(f"كود الطالب: {student.student_code}")
    print(f"الصف (grade): {repr(student.grade)}")
    print(f"الصف فارغ؟: {student.grade is None or student.grade == ''}")
    print(f"الفصل (classroom): {student.classroom}")
    if student.classroom:
        print(f"صف الفصل: {student.classroom.grade}")
    print(f"النوع (gender): {student.gender}")
    print("\n" + "="*50)
    
    # التحقق من الفلترة
    all_students = Student.objects.all()
    
    # فلترة الصف الأول للبنات
    female_g1 = all_students.filter(
        Q(gender='female') & (
            Q(grade='g1') | 
            Q(classroom__grade='g1') |
            (
                (Q(grade__isnull=True) | Q(grade='')) &
                ~(Q(grade__in=['g2', 'g3']) | Q(classroom__grade__in=['g2', 'g3']))
            )
        )
    ).distinct()
    
    print(f"\nالطلاب في الصف الأول (بنات): {female_g1.count()}")
    if student in female_g1:
        print("✓ الطالب موجود في قائمة الصف الأول للبنات")
    else:
        print("✗ الطالب غير موجود في قائمة الصف الأول للبنات")
        
        # تحقق من السبب
        print("\nالتحقق من الشروط:")
        print(f"  - grade='g1'? {student.grade == 'g1'}")
        print(f"  - classroom__grade='g1'? {student.classroom and student.classroom.grade == 'g1'}")
        print(f"  - grade فارغ أو null? {student.grade is None or student.grade == ''}")
        print(f"  - ليس g2 أو g3 في grade? {student.grade not in ['g2', 'g3']}")
        if student.classroom:
            print(f"  - ليس g2 أو g3 في classroom? {student.classroom.grade not in ['g2', 'g3']}")
        else:
            print(f"  - ليس g2 أو g3 في classroom? True (لا يوجد classroom)")
else:
    print("لم يتم العثور على الطالب")

print("\n" + "="*50)
print("جميع الطلاب بدون grade محدد:")
students_no_grade = Student.objects.filter(
    Q(grade__isnull=True) | Q(grade='')
)
print(f"العدد: {students_no_grade.count()}")
for s in students_no_grade[:10]:  # أول 10 طلاب
    print(f"  - {s.name} ({s.student_code}): grade={repr(s.grade)}, classroom={s.classroom}")

