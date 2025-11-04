"""
Management command للتحقق من الطلاب في قاعدة البيانات
الاستخدام: python manage.py check_students
"""

from django.core.management.base import BaseCommand
from student_affairs.models import Student
from django.db.models import Q


class Command(BaseCommand):
    help = 'التحقق من الطلاب في قاعدة البيانات واختبار الفلترة'

    def add_arguments(self, parser):
        parser.add_argument(
            '--name',
            type=str,
            help='اسم الطالب للبحث عنه',
            default=None,
            nargs='?'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='عرض جميع الطلاب بدون grade'
        )

    def handle(self, *args, **options):
        search_name = options.get('name')
        show_all = options.get('all', False)
        
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS('التحقق من الطلاب في قاعدة البيانات'))
        self.stdout.write("=" * 60)
        
        # البحث عن الطالب
        if search_name:
            student = Student.objects.filter(name__icontains=search_name).first()
        else:
            student = None
        
        if student:
            self.stdout.write(f"\n✓ تم العثور على الطالب: {student.name}")
            self.stdout.write(f"  - كود الطالب: {student.student_code}")
            self.stdout.write(f"  - الصف (grade): {repr(student.grade)}")
            self.stdout.write(f"  - الصف فارغ؟: {student.grade is None or student.grade == ''}")
            self.stdout.write(f"  - الفصل (classroom): {student.classroom}")
            if student.classroom:
                self.stdout.write(f"  - صف الفصل: {student.classroom.grade}")
            self.stdout.write(f"  - النوع (gender): {student.gender}")
            self.stdout.write("\n" + "-" * 60)
            
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
            
            self.stdout.write(f"\nالطلاب في الصف الأول (بنات): {female_g1.count()}")
            
            # التحقق إذا كان الطالب في القائمة
            student_in_list = list(female_g1).__contains__(student)
            
            if student_in_list:
                self.stdout.write(self.style.SUCCESS("✓ الطالب موجود في قائمة الصف الأول للبنات"))
            else:
                self.stdout.write(self.style.ERROR("✗ الطالب غير موجود في قائمة الصف الأول للبنات"))
                
                # تحقق من السبب
                self.stdout.write("\nالتحقق من الشروط:")
                self.stdout.write(f"  - grade='g1'? {student.grade == 'g1'}")
                self.stdout.write(f"  - classroom__grade='g1'? {student.classroom and student.classroom.grade == 'g1'}")
                self.stdout.write(f"  - grade فارغ أو null? {student.grade is None or student.grade == ''}")
                self.stdout.write(f"  - ليس g2 أو g3 في grade? {student.grade not in ['g2', 'g3']}")
                if student.classroom:
                    self.stdout.write(f"  - ليس g2 أو g3 في classroom? {student.classroom.grade not in ['g2', 'g3']}")
                else:
                    self.stdout.write(f"  - ليس g2 أو g3 في classroom? True (لا يوجد classroom)")
        else:
            self.stdout.write(self.style.WARNING(f"لم يتم العثور على طالب باسم يحتوي على '{search_name}'"))
        
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("جميع الطلاب بدون grade محدد:")
        students_no_grade = Student.objects.filter(
            Q(grade__isnull=True) | Q(grade='')
        )
        self.stdout.write(f"العدد: {students_no_grade.count()}")
        
        limit = None if show_all else 10
        for s in students_no_grade[:limit] if limit else students_no_grade:
            classroom_info = f", classroom={s.classroom.grade}" if s.classroom else ", بدون فصل"
            self.stdout.write(f"  - {s.name} ({s.student_code}): grade={repr(s.grade)}{classroom_info}")
        
        if not show_all and students_no_grade.count() > 10:
            self.stdout.write(f"  ... (عرض أول 10 طلاب فقط. استخدم --all لعرض الجميع)")
        
        self.stdout.write("\n" + "=" * 60)
        
        # إحصائيات سريعة
        self.stdout.write("\nإحصائيات سريعة:")
        total = Student.objects.count()
        self.stdout.write(f"  - إجمالي الطلاب: {total}")
        self.stdout.write(f"  - طلاب بدون grade: {students_no_grade.count()}")
        self.stdout.write(f"  - طلاب مع grade='g1': {Student.objects.filter(grade='g1').count()}")
        self.stdout.write(f"  - طلاب مع grade='g2': {Student.objects.filter(grade='g2').count()}")
        self.stdout.write(f"  - طلاب مع grade='g3': {Student.objects.filter(grade='g3').count()}")
        
        # عرض جميع الطلاب مع قيم grade الفعلية
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("جميع الطلاب مع قيم grade الفعلية:")
        for s in Student.objects.all().order_by('name')[:20]:
            grade_repr = repr(s.grade) if s.grade else "None"
            classroom_info = f" (فصل: {s.classroom.grade})" if s.classroom else ""
            self.stdout.write(f"  - {s.name} ({s.student_code}): grade={grade_repr}{classroom_info}")
        
        if total > 20:
            self.stdout.write(f"  ... (عرض أول 20 طالب فقط)")
        
        # التحقق من القيم المختلفة في grade
        self.stdout.write("\n" + "-" * 60)
        self.stdout.write("القيم المختلفة في حقل grade:")
        unique_grades = Student.objects.exclude(grade__isnull=True).exclude(grade='').values_list('grade', flat=True).distinct()
        for grade_val in unique_grades:
            count = Student.objects.filter(grade=grade_val).count()
            self.stdout.write(f"  - grade='{grade_val}': {count} طالب")
        
        self.stdout.write("\n" + "=" * 60)

