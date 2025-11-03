"""
أدوات المصادقة باستخدام JWT
"""
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User


def generate_jwt_token(user):
    """
    توليد JWT token للمستخدم
    """
    payload = {
        'user_id': user.id,
        'username': user.username,
        'exp': datetime.utcnow() + timedelta(days=7),  # Token صالح لمدة 7 أيام
        'iat': datetime.utcnow(),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token


def verify_jwt_token(token):
    """
    التحقق من JWT token
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')
        if user_id:
            user = User.objects.get(id=user_id)
            return user
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
        return None
    return None


def get_token_from_request(request):
    """
    استخراج JWT token من الطلب
    """
    # محاولة الحصول من query parameter
    token = request.GET.get('token')
    if token:
        return token
    
    # محاولة الحصول من session
    token = request.session.get('jwt_token')
    if token:
        return token
    
    # محاولة الحصول من cookie
    token = request.COOKIES.get('jwt_token')
    if token:
        return token
    
    return None

