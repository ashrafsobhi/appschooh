from django.urls import path
from . import views

app_name = 'student_affairs'

urlpatterns = [
    path('', views.landing, name='landing'),
    path('welcome/', views.welcome, name='welcome'),
    path('students/', views.student_list, name='student_list'),
    path('records/', views.records_list, name='records_list'),
    path('records/add/', views.add_record, name='add_record'),
    path('classrooms/', views.classrooms_list, name='classrooms_list'),
    path('classrooms/add/', views.add_classroom, name='add_classroom'),
    path('classrooms/<int:classroom_id>/', views.classroom_detail, name='classroom_detail'),
    path('classrooms/<int:classroom_id>/print/', views.classroom_print, name='classroom_print'),
    path('classrooms/print/<str:gender>/<str:grade>/', views.classrooms_print_grade, name='classrooms_print_grade'),
    path('classrooms/print-absence/<str:gender>/<str:grade>/', views.classrooms_print_absence_grade, name='classrooms_print_absence_grade'),
    path('students/print/', views.print_student_list, name='print_student_list'),
    path('students/add/', views.add_student, name='add_student'),
    path('students/download-template/', views.download_excel_template, name='download_template'),
    path('students/<int:student_id>/', views.student_detail, name='student_detail'),
    path('students/<int:student_id>/id-card/', views.student_id_card, name='student_id_card'),
    path('qr/<int:student_id>/', views.student_qr, name='student_qr'),
    path('attachments/<int:attachment_id>/delete/', views.delete_attachment, name='delete_attachment'),
    path('statistics/', views.system_statistics, name='system_statistics'),
    path('statistics/classroom/<int:classroom_id>/failed/', views.classroom_failed_details, name='classroom_failed_details'),
    path('admin/users/create/', views.admin_create_user, name='admin_create_user'),
    path('admin/users/<int:user_id>/login-link/', views.generate_login_link, name='generate_login_link'),
    path('api/chatbot/', views.chatbot_api, name='chatbot_api'),
    path('api/text-to-speech/', views.text_to_speech_api, name='text_to_speech_api'),
    path('profile/', views.profile, name='profile'),
]

