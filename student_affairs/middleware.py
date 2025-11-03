"""
Middleware للتحقق من JWT token في الطلبات
"""
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import logout
from django.shortcuts import redirect
from .auth_utils import get_token_from_request, verify_jwt_token


class JWTAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware للتحقق من JWT token وتحديث الجلسة
    """
    def process_request(self, request):
        # تخطي الصفحات العامة
        public_paths = ['/accounts/login/', '/', '/accounts/logout/']
        if any(request.path.startswith(path) for path in public_paths):
            return None
        
        # إذا كان المستخدم مسجل دخول بالفعل، لا حاجة للتحقق
        if request.user.is_authenticated:
            # التحقق من token في session
            token = request.session.get('jwt_token')
            if token:
                user = verify_jwt_token(token)
                if not user or user.id != request.user.id:
                    # Token غير صالح، تسجيل الخروج
                    logout(request)
                    request.session.flush()
                    return redirect('/accounts/login/')
            return None
        
        # محاولة التحقق من token في الطلب
        token = get_token_from_request(request)
        if token:
            user = verify_jwt_token(token)
            if user:
                from django.contrib.auth import login
                login(request, user)
                request.session['jwt_token'] = token
                request.session['user_id'] = user.id
                return None
        
        return None

