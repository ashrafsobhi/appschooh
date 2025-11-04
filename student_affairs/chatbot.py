"""
شات بوت بالذكاء الاصطناعي باستخدام Google Gemini
"""
import google.generativeai as genai
from django.conf import settings
import base64
from io import BytesIO
from PIL import Image
import requests
import json


def get_chatbot_response(user_message, user_name=None, image_data=None, conversation_history=None):
    """
    الحصول على رد من الشات بوت
    
    Args:
        user_message: رسالة المستخدم
        user_name: اسم المستخدم (اختياري)
        image_data: بيانات الصورة (base64) (اختياري)
        conversation_history: تاريخ المحادثة (اختياري)
    
    Returns:
        رد الشات بوت
    """
    # استخدام REST API مباشرة (أكثر موثوقية من SDK)
    return get_chatbot_response_via_api(user_message, user_name, conversation_history)
    
    # الكود التالي محفوظ كبديل إذا أردت استخدام SDK
    try:
        # تهيئة Gemini
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # محاولة استخدام النماذج المتاحة بالترتيب (النماذج الأحدث أولاً)
        model = None
        models_to_try = [
            'gemini-2.5-flash',      # الأسرع والأكثر توفراً
            'gemini-2.5-pro',        # الأقوى والأعلى قدرة
            'gemini-1.5-flash',      # احتياطي
            'gemini-1.5-pro'         # احتياطي
        ]
        
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                # استخدام النموذج مباشرة بدون اختبار
                break
            except Exception as e:
                continue
        
        # إذا فشل كل شيء، استخدم REST API
        if model is None:
            return get_chatbot_response_via_api(user_message, user_name, conversation_history)
        
        # بناء النظام الأساسي للبوت بنبرة رسمية ومختصرة
        system_prompt = f"""أنت مساعد رسمي لنظام إدارة شؤون الطلبة.

المهام:
1. الإجابة بدقة واختصار وبلغة عربية فصيحة.
2. الالتزام بالسؤال المطروح فقط دون إطالة أو حشو.
3. توضيح الخطوات عند الطلب فقط.
4. طلب توضيح بجملة واحدة إذا كان السؤال غير محدد.

معلومات عن النظام:
- الاسم: نظام شؤون الطلبة
- المهام الرئيسية:
  * إدارة الطلبة: إضافة/تعديل/طباعة بيانات الطلبة
  * إدارة الفصول: تنظيم الفصول وقوائم الغياب
  * السجلات: حفظ وإدارة السجلات
  * الإحصائيات: إحصائيات مع رسوم بيانية
  * الطباعة: طباعة القوائم والبطاقات والسجلات
- المطور: أشرف صبحي

إرشادات الأسلوب:
- نبرة رسمية ومحايدة.
- إجابات موجزة ومباشرة.
- بدون رموز تعبيرية أو مزاح.

{'المستخدم الحالي: ' + user_name if user_name else ''}
"""
        
        # بناء الرسالة الكاملة
        full_prompt = system_prompt + "\n\n"
        
        # إضافة تاريخ المحادثة إذا كان موجود
        if conversation_history and len(conversation_history) > 0:
            full_prompt += "تاريخ المحادثة السابق:\n"
            for msg in conversation_history[-5:]:  # آخر 5 رسائل
                full_prompt += f"المستخدم: {msg.get('user', '')}\n"
                full_prompt += f"المساعد: {msg.get('assistant', '')}\n\n"
        
        full_prompt += f"المستخدم الآن يسأل: {user_message}\n\n"
        full_prompt += "أجب بإيجاز وبنبرة رسمية، والتزم بالسؤال فقط:"
        
        # إرسال الطلب
        response = model.generate_content(full_prompt)
        
        return response.text.strip()
        
    except Exception as e:
        # محاولة استخدام REST API كبديل
        try:
            return get_chatbot_response_via_api(user_message, user_name, conversation_history)
        except Exception as e2:
            return f"عذراً، حدث خطأ في التواصل مع المساعد الذكي. يرجى المحاولة مرة أخرى. (خطأ: {str(e)})"


def get_chatbot_response_via_api(user_message, user_name=None, conversation_history=None):
    """
    الحصول على رد من الشات بوت باستخدام REST API مباشرة
    """
    try:
        # بناء النظام الأساسي للبوت بنبرة رسمية ومختصرة
        system_prompt = f"""أنت مساعد رسمي لنظام إدارة شؤون الطلبة.

المهام:
1. الإجابة بدقة واختصار وبلغة عربية فصيحة.
2. الالتزام بالسؤال المطروح فقط دون إطالة أو حشو.
3. توضيح الخطوات عند الطلب فقط.
4. طلب توضيح بجملة واحدة إذا كان السؤال غير محدد.

معلومات عن النظام:
- الاسم: نظام شؤون الطلبة
- المهام الرئيسية:
  * إدارة الطلبة: إضافة/تعديل/طباعة بيانات الطلبة
  * إدارة الفصول: تنظيم الفصول وقوائم الغياب
  * السجلات: حفظ وإدارة السجلات
  * الإحصائيات: إحصائيات مع رسوم بيانية
  * الطباعة: طباعة القوائم والبطاقات والسجلات
- المطور: أشرف صبحي

إرشادات الأسلوب:
- نبرة رسمية ومحايدة.
- إجابات موجزة ومباشرة.
- بدون رموز تعبيرية أو مزاح.

{'المستخدم الحالي: ' + user_name if user_name else ''}
"""
        
        # بناء الرسالة الكاملة
        full_prompt = system_prompt + "\n\n"
        
        # إضافة تاريخ المحادثة إذا كان موجود
        if conversation_history and len(conversation_history) > 0:
            full_prompt += "تاريخ المحادثة السابق:\n"
            for msg in conversation_history[-5:]:  # آخر 5 رسائل
                full_prompt += f"المستخدم: {msg.get('user', '')}\n"
                full_prompt += f"المساعد: {msg.get('assistant', '')}\n\n"
        
        full_prompt += f"المستخدم الآن يسأل: {user_message}\n\n"
        full_prompt += "أجب بإيجاز وبنبرة رسمية، والتزم بالسؤال فقط:"
        
        payload = {
            "contents": [{
                "parts": [{"text": full_prompt}]
            }]
        }
        
        # محاولة النماذج المتاحة بالترتيب (النماذج الأحدث أولاً)
        models_to_try = [
            'gemini-2.5-flash',      # الأسرع والأكثر توفراً
            'gemini-2.5-pro',        # الأقوى والأعلى قدرة
            'gemini-1.5-flash',      # احتياطي
            'gemini-1.5-pro'         # احتياطي
        ]
        
        # محاولة استخدام v1 أولاً (الأحدث والأكثر دعماً)، ثم v1beta
        api_versions = ['v1', 'v1beta']
        
        last_error = None
        for api_version in api_versions:
            for model_name in models_to_try:
                try:
                    url = f"https://generativelanguage.googleapis.com/{api_version}/models/{model_name}:generateContent?key={settings.GEMINI_API_KEY}"
                    response = requests.post(url, json=payload, timeout=30)
                    
                    if response.status_code == 200:
                        result = response.json()
                        if 'candidates' in result and len(result['candidates']) > 0:
                            candidate = result['candidates'][0]
                            if 'content' in candidate and 'parts' in candidate['content']:
                                if len(candidate['content']['parts']) > 0:
                                    text = candidate['content']['parts'][0].get('text', '')
                                    if text:
                                        return text
                    
                    # إذا كان الخطأ 404، جرب النموذج التالي
                    if response.status_code == 404:
                        last_error = f"Model {model_name} not found in {api_version}"
                        continue
                    elif response.status_code == 400:
                        # خطأ في الطلب - جرب API version آخر
                        try:
                            error_data = response.json()
                            last_error = f"Bad request: {error_data.get('error', {}).get('message', 'Unknown error')}"
                        except:
                            last_error = f"Bad request (status {response.status_code})"
                        break
                    elif response.status_code == 403:
                        # خطأ في الصلاحيات
                        try:
                            error_data = response.json()
                            last_error = f"Permission denied: {error_data.get('error', {}).get('message', 'Check API key')}"
                        except:
                            last_error = "Permission denied - Check API key"
                        # لا جرب نماذج أخرى إذا كان خطأ في الصلاحيات
                        return f"عذراً، حدث خطأ في الصلاحيات. يرجى التحقق من مفتاح API. ({last_error})"
                    elif response.status_code != 200:
                        # إذا كان خطأ آخر، جرب API version آخر
                        try:
                            error_data = response.json()
                            last_error = f"Error {response.status_code}: {error_data.get('error', {}).get('message', 'Unknown error')}"
                        except:
                            last_error = f"Error {response.status_code}"
                        break
                        
                except requests.exceptions.RequestException as e:
                    last_error = f"Network error: {str(e)}"
                    continue
                except Exception as e:
                    last_error = f"Unexpected error: {str(e)}"
                    continue
        
        return f"عذراً، لم أتمكن من التواصل مع المساعد الذكي. ({last_error if last_error else 'جميع المحاولات فشلت'})"
            
    except Exception as e:
        return f"عذراً، حدث خطأ في التواصل مع المساعد الذكي. يرجى المحاولة مرة أخرى. (خطأ: {str(e)})"


def analyze_image(image_data, user_message="ما الذي تراه في هذه الصورة؟", user_name=None):
    """
    تحليل الصورة باستخدام Gemini Vision
    
    Args:
        image_data: بيانات الصورة (base64)
        user_message: سؤال المستخدم عن الصورة
        user_name: اسم المستخدم
    
    Returns:
        تحليل الصورة
    """
    try:
        # تهيئة Gemini
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # تحويل base64 إلى صورة
        if ',' in image_data:
            image_bytes = base64.b64decode(image_data.split(',')[1])
        else:
            image_bytes = base64.b64decode(image_data)
        
        # استخدام REST API مباشرة لتحليل الصور (أكثر موثوقية)
        return analyze_image_via_api(image_data, user_message, user_name)
        
    except Exception as e:
        return f"عذراً، لم أتمكن من تحليل الصورة. يرجى المحاولة مرة أخرى. (خطأ: {str(e)})"


def analyze_image_via_api(image_data, user_message="ما الذي تراه في هذه الصورة؟", user_name=None):
    """
    تحليل الصورة باستخدام REST API مباشرة
    """
    try:
        # تنظيف image_data
        if ',' in image_data:
            image_base64 = image_data.split(',')[1]
        else:
            image_base64 = image_data
        
        # تحديد نوع الصورة
        mime_type = "image/png"
        if image_data.startswith('data:image/jpeg'):
            mime_type = "image/jpeg"
        elif image_data.startswith('data:image/jpg'):
            mime_type = "image/jpeg"
        elif image_data.startswith('data:image/gif'):
            mime_type = "image/gif"
        elif image_data.startswith('data:image/webp'):
            mime_type = "image/webp"
        
        prompt_text = f"""أنت مساعد رسمي لنظام إدارة شؤون الطلبة.

{'اسم المستخدم: ' + user_name if user_name else ''}

المستخدم يطلب تحليل الصورة. كن دقيقاً ومختصراً وبنبرة رسمية.
السؤال: {user_message}

أجب بإيجاز وبوضوح وبدون رموز تعبيرية:"""
        
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt_text},
                    {"inline_data": {"mime_type": mime_type, "data": image_base64}}
                ]
            }]
        }
        
        # محاولة النماذج المتاحة بالترتيب (النماذج الأحدث أولاً)
        models_to_try = [
            'gemini-2.5-flash',      # الأسرع والأكثر توفراً
            'gemini-2.5-pro',        # الأقوى والأعلى قدرة
            'gemini-1.5-flash',      # احتياطي
            'gemini-1.5-pro'         # احتياطي
        ]
        
        # محاولة استخدام v1 أولاً (الأحدث والأكثر دعماً)، ثم v1beta
        api_versions = ['v1', 'v1beta']
        
        last_error = None
        for api_version in api_versions:
            for model_name in models_to_try:
                try:
                    url = f"https://generativelanguage.googleapis.com/{api_version}/models/{model_name}:generateContent?key={settings.GEMINI_API_KEY}"
                    response = requests.post(url, json=payload, timeout=30)
                    
                    if response.status_code == 200:
                        result = response.json()
                        if 'candidates' in result and len(result['candidates']) > 0:
                            candidate = result['candidates'][0]
                            if 'content' in candidate and 'parts' in candidate['content']:
                                if len(candidate['content']['parts']) > 0:
                                    text = candidate['content']['parts'][0].get('text', '')
                                    if text:
                                        return text
                    
                    # إذا كان الخطأ 404، جرب النموذج التالي
                    if response.status_code == 404:
                        last_error = f"Model {model_name} not found in {api_version}"
                        continue
                    elif response.status_code == 400:
                        # خطأ في الطلب - جرب API version آخر
                        try:
                            error_data = response.json()
                            last_error = f"Bad request: {error_data.get('error', {}).get('message', 'Unknown error')}"
                        except:
                            last_error = f"Bad request (status {response.status_code})"
                        break
                    elif response.status_code == 403:
                        # خطأ في الصلاحيات
                        try:
                            error_data = response.json()
                            last_error = f"Permission denied: {error_data.get('error', {}).get('message', 'Check API key')}"
                        except:
                            last_error = "Permission denied - Check API key"
                        return f"عذراً، حدث خطأ في الصلاحيات. يرجى التحقق من مفتاح API. ({last_error})"
                    elif response.status_code != 200:
                        # إذا كان خطأ آخر، جرب API version آخر
                        try:
                            error_data = response.json()
                            last_error = f"Error {response.status_code}: {error_data.get('error', {}).get('message', 'Unknown error')}"
                        except:
                            last_error = f"Error {response.status_code}"
                        break
                        
                except requests.exceptions.RequestException as e:
                    last_error = f"Network error: {str(e)}"
                    continue
                except Exception as e:
                    last_error = f"Unexpected error: {str(e)}"
                    continue
        
        return f"عذراً، لم أتمكن من تحليل الصورة. ({last_error if last_error else 'جميع المحاولات فشلت'})"
            
    except Exception as e:
        return f"عذراً، لم أتمكن من تحليل الصورة. يرجى المحاولة مرة أخرى. (خطأ: {str(e)})"

