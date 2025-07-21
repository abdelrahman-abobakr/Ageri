"""
Custom Arabic translation template tags
"""

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

# Arabic translations dictionary
ARABIC_TRANSLATIONS = {
    # Navigation
    "Dashboard": "لوحة التحكم",
    "Users": "المستخدمون", 
    "Publications": "المنشورات",
    "Services": "الخدمات",
    "Management": "الإدارة",
    "Analytics": "التحليلات",
    "Settings": "الإعدادات",
    "Organization": "المؤسسة",
    "Training": "التدريب",
    "Content": "المحتوى",
    "Departments": "الأقسام",
    "Laboratories": "المختبرات",
    "Courses": "الدورات",
    "Announcements": "الإعلانات",
    
    # User Management
    "User Management": "إدارة المستخدمين",
    "Manage user accounts and approvals": "إدارة حسابات المستخدمين والموافقات",
    "Bulk Actions": "الإجراءات المجمعة",
    "Add User": "إضافة مستخدم",
    "All Users": "جميع المستخدمين",
    "Pending Approval": "في انتظار الموافقة",
    "All Roles": "جميع الأدوار",
    "Search by name, email, username...": "البحث بالاسم أو البريد الإلكتروني أو اسم المستخدم...",
    "Clear Filters": "مسح المرشحات",
    "User": "المستخدم",
    "Institution": "المؤسسة",
    "Joined": "تاريخ الانضمام",
    
    # Publication Management
    "Publication Management": "إدارة المنشورات",
    "Manage research publications and submissions": "إدارة المنشورات البحثية والمقدمات",
    "All Publications": "جميع المنشورات",
    "Pending Review": "في انتظار المراجعة",
    "Rejected": "مرفوض",
    "Search by title, author, journal...": "البحث بالعنوان أو المؤلف أو المجلة...",
    
    # Service Requests
    "Service Requests": "طلبات الخدمة",
    "Manage testing service requests and assignments": "إدارة طلبات خدمات الاختبار والتكليفات",
    "All Requests": "جميع الطلبات",
    "In Progress": "قيد التنفيذ",
    "Completed": "مكتمل",
    "Cancelled": "ملغي",
    "Service": "الخدمة",
    "All Services": "جميع الخدمات",
    "Search by title, client, request ID...": "البحث بالعنوان أو العميل أو رقم الطلب...",
    
    # Department Management
    "Create Department": "إنشاء قسم",
    "Create a new department": "إنشاء قسم جديد",
    "Back to Organization": "العودة إلى المؤسسة",
    "New Department": "قسم جديد",
    "Department Name": "اسم القسم",
    "e.g., Computer Science": "مثال: علوم الحاسوب",
    "Brief description of the department's focus and activities": "وصف موجز لتركيز القسم وأنشطته",
    "Department Head": "رئيس القسم",
    "Select Department Head (Optional)": "اختر رئيس القسم (اختياري)",
    "You can assign a department head later if needed.": "يمكنك تعيين رئيس قسم لاحقاً إذا لزم الأمر.",
    
    # Common actions
    "Search": "بحث",
    "Filter": "تصفية", 
    "Save": "حفظ",
    "Cancel": "إلغاء",
    "Edit": "تحرير",
    "Delete": "حذف",
    "Create": "إنشاء",
    "Update": "تحديث",
    "View": "عرض",
    "Add": "إضافة",
    "Remove": "إزالة",
    "Close": "إغلاق",
    "Confirm": "تأكيد",
    "Yes": "نعم",
    "No": "لا",
    "OK": "موافق",
    
    # Status
    "Status": "الحالة",
    "Actions": "الإجراءات",
    "Active": "نشط",
    "Inactive": "غير نشط",
    "Pending": "معلق",
    "Approved": "موافق عليه",
    "Draft": "مسودة",
    "Published": "منشور",
    
    # User fields
    "Name": "الاسم",
    "Email": "البريد الإلكتروني",
    "Role": "الدور",
    "Admin": "مدير",
    "Moderator": "مشرف", 
    "Researcher": "باحث",
    "Guest": "ضيف",
    
    # Content
    "Title": "العنوان",
    "Description": "الوصف",
    "Vision": "الرؤية",
    "Mission": "الرسالة",
    "About": "حول",
    "Contact Information": "معلومات الاتصال",
    "Phone": "الهاتف",
    "Address": "العنوان",
    "Website": "الموقع الإلكتروني",
    "Social Media": "وسائل التواصل الاجتماعي",
    "Facebook": "فيسبوك",
    "Twitter": "تويتر",
    "LinkedIn": "لينكد إن",
    "Instagram": "إنستغرام",
    "Logo": "الشعار",
    "Banner": "البانر",
    
    # Dashboard Home
    "Dashboard Overview": "نظرة عامة على لوحة التحكم",
    "System overview and key metrics": "نظرة عامة على النظام والمقاييس الرئيسية",
    "Total Users": "إجمالي المستخدمين",
    "Pending Approvals": "الموافقات المعلقة",
    "Active Requests": "الطلبات النشطة",
    "Edit Settings": "تحرير الإعدادات",
    
    # Translation Management
    "Translation Management": "إدارة الترجمة",
    "Translate All Content": "ترجمة جميع المحتوى",
    "Language": "اللغة",
    "Current": "الحالي",
    "Available": "متاح",
    "Missing": "مفقود",
    "Translated": "مترجم",
    "Not Translated": "غير مترجم",
    
    # Messages
    "Settings updated successfully.": "تم تحديث الإعدادات بنجاح.",
    "Translation completed successfully.": "تم إكمال الترجمة بنجاح.",
    "Content translated successfully.": "تم ترجمة المحتوى بنجاح.",
}

@register.simple_tag(takes_context=True)
def ar_trans(context, text):
    """
    Custom Arabic translation tag
    Usage: {% ar_trans "Text to translate" %}
    """
    request = context.get('request')
    if request:
        # Check if current language is Arabic
        current_language = getattr(request, 'LANGUAGE_CODE', 'en')
        if current_language == 'ar':
            return mark_safe(ARABIC_TRANSLATIONS.get(text, text))
    
    return text

@register.filter
def ar_translate(text):
    """
    Filter version of Arabic translation
    Usage: {{ "Text to translate"|ar_translate }}
    """
    return ARABIC_TRANSLATIONS.get(text, text)
