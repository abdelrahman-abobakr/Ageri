from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone, translation
from django.http import JsonResponse
from django.core.paginator import Paginator
from datetime import datetime, timedelta

from accounts.models import User
from research.models import Publication
from organization.models import Department, Lab, OrganizationSettings
from training.models import Course, SummerTraining
from services.models import ServiceRequest, TestService
from content.models import Announcement, Post, AnnouncementImage, AnnouncementAttachment


@staff_member_required
def dashboard_home(request):
    """Main dashboard home page with overview statistics"""

    # Get organization settings for vision/message display
    org_settings = OrganizationSettings.get_settings()

    # Get overview statistics
    stats = {
        'total_users': User.objects.count(),
        'pending_users': User.objects.filter(is_approved=False).count(),
        'total_publications': Publication.objects.count(),
        'pending_publications': Publication.objects.filter(status='pending').count(),
        'total_departments': Department.objects.count(),
        'total_labs': Lab.objects.count(),
        'total_courses': Course.objects.count(),
        'active_service_requests': ServiceRequest.objects.filter(status__in=['pending', 'approved', 'in_progress']).count(),
        'total_announcements': Announcement.objects.count(),
    }

    # Recent activity
    recent_users = User.objects.filter(is_approved=False).order_by('-date_joined')[:5]
    recent_publications = Publication.objects.filter(status='pending').order_by('-created_at')[:5]
    recent_service_requests = ServiceRequest.objects.filter(status='pending').order_by('-created_at')[:5]

    # Monthly user registrations (last 6 months)
    six_months_ago = timezone.now() - timedelta(days=180)
    monthly_users = []
    for i in range(6):
        month_start = six_months_ago + timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        count = User.objects.filter(date_joined__range=[month_start, month_end]).count()
        monthly_users.append({
            'month': month_start.strftime('%b %Y'),
            'count': count
        })

    context = {
        'stats': stats,
        'recent_users': recent_users,
        'recent_publications': recent_publications,
        'recent_service_requests': recent_service_requests,
        'monthly_users': monthly_users,
        'org_settings': org_settings,  # Add organization settings to context
    }

    return render(request, 'dashboard/home.html', context)


@staff_member_required
def user_management(request):
    """Enhanced user management page with bulk actions"""

    # Handle POST actions (bulk operations)
    if request.method == 'POST':
        action = request.POST.get('action')
        user_ids = request.POST.getlist('user_ids')

        if not user_ids:
            messages.error(request, 'Please select at least one user.')
            return redirect('dashboard:user_management')

        if action == 'approve_users':
            User.objects.filter(id__in=user_ids).update(
                is_approved=True,
                approved_by=request.user,
                approved_at=timezone.now()
            )
            messages.success(request, f'Approved {len(user_ids)} users successfully.')

        elif action == 'reject_users':
            User.objects.filter(id__in=user_ids).update(
                is_approved=False,
                is_active=False
            )
            messages.success(request, f'Rejected {len(user_ids)} users successfully.')

        elif action == 'activate_users':
            User.objects.filter(id__in=user_ids).update(is_active=True)
            messages.success(request, f'Activated {len(user_ids)} users successfully.')

        elif action == 'deactivate_users':
            User.objects.filter(id__in=user_ids).update(is_active=False)
            messages.success(request, f'Deactivated {len(user_ids)} users successfully.')

        elif action == 'delete_users':
            # Don't allow deleting current user or other admins
            users_to_delete = User.objects.filter(
                id__in=user_ids
            ).exclude(
                Q(id=request.user.id) | Q(role='admin')
            )
            count = users_to_delete.count()
            users_to_delete.delete()
            messages.success(request, f'Deleted {count} users successfully.')

        elif action == 'change_role':
            new_role = request.POST.get('new_role')
            if new_role in ['researcher', 'moderator', 'admin']:
                # Don't allow changing current user's role
                User.objects.filter(
                    id__in=user_ids
                ).exclude(
                    id=request.user.id
                ).update(role=new_role)
                messages.success(request, f'Changed role to {new_role} for selected users.')
            else:
                messages.error(request, 'Invalid role selected.')

        return redirect('dashboard:user_management')

    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    role_filter = request.GET.get('role', 'all')
    search_query = request.GET.get('search', '')

    # Build queryset
    users = User.objects.all().select_related('approved_by')

    if status_filter == 'pending':
        users = users.filter(is_approved=False)
    elif status_filter == 'approved':
        users = users.filter(is_approved=True)
    elif status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)

    if role_filter != 'all':
        users = users.filter(role=role_filter)

    if search_query:
        users = users.filter(
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(username__icontains=search_query)
        )

    users = users.order_by('-date_joined')

    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'role_filter': role_filter,
        'search_query': search_query,
        'total_users': users.count(),
    }

    return render(request, 'dashboard/user_management.html', context)


@staff_member_required
def approve_user(request, user_id):
    """Approve a user"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        user.is_approved = True
        user.approved_by = request.user
        user.approval_date = timezone.now()
        user.save()

        messages.success(request, f'User {user.email} has been approved successfully.')

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': 'User approved successfully'})

    return redirect('dashboard:user_management')


@staff_member_required
def reject_user(request, user_id):
    """Reject/revoke user approval"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        user.is_approved = False
        user.approved_by = None
        user.approval_date = None
        user.save()

        messages.warning(request, f'User {user.email} approval has been revoked.')

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': 'User approval revoked'})

    return redirect('dashboard:user_management')


@staff_member_required
def publication_management(request):
    """Publication management page"""

    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '')

    # Build queryset
    publications = Publication.objects.all().select_related('corresponding_author', 'submitted_by').prefetch_related('authors')

    if status_filter != 'all':
        publications = publications.filter(status=status_filter)

    if search_query:
        publications = publications.filter(
            Q(title__icontains=search_query) |
            Q(abstract__icontains=search_query) |
            Q(journal_name__icontains=search_query) |
            Q(authors__first_name__icontains=search_query) |
            Q(authors__last_name__icontains=search_query)
        ).distinct()

    publications = publications.order_by('-created_at')

    # Pagination
    paginator = Paginator(publications, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search_query': search_query,
        'total_publications': publications.count(),
    }

    return render(request, 'dashboard/publication_management.html', context)


@staff_member_required
def service_requests(request):
    """Service requests management page"""

    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    service_filter = request.GET.get('service', 'all')
    search_query = request.GET.get('search', '')

    # Build queryset
    requests = ServiceRequest.objects.all().select_related('service', 'client', 'assigned_technician')

    if status_filter != 'all':
        requests = requests.filter(status=status_filter)

    if service_filter != 'all':
        requests = requests.filter(service_id=service_filter)

    if search_query:
        requests = requests.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(client__name__icontains=search_query) |
            Q(request_id__icontains=search_query)
        )

    requests = requests.order_by('-created_at')

    # Get services for filter dropdown
    services = TestService.objects.all().order_by('name')

    # Pagination
    paginator = Paginator(requests, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'service_filter': service_filter,
        'search_query': search_query,
        'services': services,
        'total_requests': requests.count(),
    }

    return render(request, 'dashboard/service_requests.html', context)


@staff_member_required
def system_settings(request):
    """System settings and configuration"""

    # Get system statistics
    system_stats = {
        'database_size': 'N/A',  # Would need database-specific queries
        'total_files': 'N/A',    # Would need file system queries
        'last_backup': 'N/A',    # Would need backup system integration
    }

    context = {
        'system_stats': system_stats,
    }

    return render(request, 'dashboard/system_settings.html', context)


@staff_member_required
def content_management(request):
    """Enhanced content management with CRUD operations"""

    # Handle POST actions (bulk operations)
    if request.method == 'POST':
        action = request.POST.get('action')
        item_ids = request.POST.getlist('item_ids')
        content_type = request.POST.get('content_type', 'announcements')

        if not item_ids:
            messages.error(request, 'Please select at least one item.')
            return redirect(f'dashboard:content_management?type={content_type}')

        if content_type == 'announcements':
            model = Announcement
        else:
            model = Post

        if action == 'approve_items':
            model.objects.filter(id__in=item_ids).update(
                status='published',
                approved_by=request.user,
                approved_at=timezone.now()
            )
            messages.success(request, f'Approved {len(item_ids)} {content_type} successfully.')

        elif action == 'reject_items':
            model.objects.filter(id__in=item_ids).update(status='rejected')
            messages.success(request, f'Rejected {len(item_ids)} {content_type} successfully.')

        elif action == 'publish_items':
            model.objects.filter(id__in=item_ids).update(status='published')
            messages.success(request, f'Published {len(item_ids)} {content_type} successfully.')

        elif action == 'unpublish_items':
            model.objects.filter(id__in=item_ids).update(status='draft')
            messages.success(request, f'Unpublished {len(item_ids)} {content_type} successfully.')

        elif action == 'delete_items':
            model.objects.filter(id__in=item_ids).delete()
            messages.success(request, f'Deleted {len(item_ids)} {content_type} successfully.')

        elif action == 'pin_items' and content_type == 'announcements':
            Announcement.objects.filter(id__in=item_ids).update(is_pinned=True)
            messages.success(request, f'Pinned {len(item_ids)} announcements successfully.')

        elif action == 'unpin_items' and content_type == 'announcements':
            Announcement.objects.filter(id__in=item_ids).update(is_pinned=False)
            messages.success(request, f'Unpinned {len(item_ids)} announcements successfully.')

        return redirect(f'dashboard:content_management?type={content_type}')

    # Get filter parameters
    content_type = request.GET.get('type', 'announcements')
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '')

    if content_type == 'announcements':
        # Build announcements queryset
        items = Announcement.objects.all().select_related('author', 'approved_by').prefetch_related('images', 'attachments')

        if status_filter != 'all':
            items = items.filter(status=status_filter)

        if search_query:
            items = items.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query)
            )

        items = items.order_by('-created_at')
        template = 'dashboard/content_announcements.html'

    else:  # posts
        # Build posts queryset
        items = Post.objects.all().select_related('author', 'approved_by')

        if status_filter != 'all':
            items = items.filter(status=status_filter)

        if search_query:
            items = items.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query)
            )

        items = items.order_by('-created_at')
        template = 'dashboard/content_posts.html'

    # Pagination
    paginator = Paginator(items, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'content_type': content_type,
        'status_filter': status_filter,
        'search_query': search_query,
        'total_items': items.count(),
    }

    return render(request, template, context)


@staff_member_required
def organization_management(request):
    """Organization management page for departments and labs"""

    # Get filter parameters
    view_type = request.GET.get('view', 'departments')
    search_query = request.GET.get('search', '')

    if view_type == 'departments':
        items = Department.objects.all().select_related('head').prefetch_related('labs')

        if search_query:
            items = items.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        template = 'dashboard/organization_departments.html'

    else:  # labs
        items = Lab.objects.all().select_related('department', 'head')

        if search_query:
            items = items.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(department__name__icontains=search_query)
            )

        template = 'dashboard/organization_labs.html'

    items = items.order_by('name')

    # Pagination
    paginator = Paginator(items, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'view_type': view_type,
        'search_query': search_query,
        'total_items': items.count(),
    }

    return render(request, template, context)


@staff_member_required
def training_management(request):
    """Training management page for courses and programs"""

    # Get filter parameters
    view_type = request.GET.get('view', 'courses')
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '')

    if view_type == 'courses':
        items = Course.objects.all().select_related('instructor').prefetch_related('enrollments')

        if status_filter != 'all':
            items = items.filter(status=status_filter)

        if search_query:
            items = items.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        template = 'dashboard/training_courses.html'

    else:  # summer programs
        items = SummerTraining.objects.all().select_related('coordinator').prefetch_related('applications')

        if status_filter != 'all':
            items = items.filter(status=status_filter)

        if search_query:
            items = items.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        template = 'dashboard/training_summer.html'

    items = items.order_by('-created_at')

    # Pagination
    paginator = Paginator(items, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'view_type': view_type,
        'status_filter': status_filter,
        'search_query': search_query,
        'total_items': items.count(),
    }

    return render(request, template, context)


@staff_member_required
def analytics_dashboard(request):
    """Advanced analytics dashboard for admins"""

    # Time period filter
    period = request.GET.get('period', '30')  # days
    end_date = timezone.now()
    start_date = end_date - timedelta(days=int(period))

    # User analytics
    user_stats = {
        'total_users': User.objects.count(),
        'new_users': User.objects.filter(date_joined__gte=start_date).count(),
        'pending_approvals': User.objects.filter(is_approved=False).count(),
        'active_users': User.objects.filter(is_active=True, is_approved=True).count(),
    }

    # Content analytics
    content_stats = {
        'total_publications': Publication.objects.count(),
        'new_publications': Publication.objects.filter(created_at__gte=start_date).count(),
        'pending_publications': Publication.objects.filter(status='pending').count(),
        'total_announcements': Announcement.objects.count(),
        'new_announcements': Announcement.objects.filter(created_at__gte=start_date).count(),
    }

    # Training analytics
    training_stats = {
        'total_courses': Course.objects.count(),
        'active_courses': Course.objects.filter(status='active').count(),
        'total_enrollments': Course.objects.aggregate(
            total=models.Sum('enrollments__count')
        )['total'] or 0,
    }

    # Service analytics
    service_stats = {
        'total_requests': ServiceRequest.objects.count(),
        'pending_requests': ServiceRequest.objects.filter(status='pending').count(),
        'completed_requests': ServiceRequest.objects.filter(status='completed').count(),
        'revenue': ServiceRequest.objects.filter(
            status='completed'
        ).aggregate(total=models.Sum('service__price'))['total'] or 0,
    }

    # Daily activity data for charts
    daily_activity = []
    for i in range(int(period)):
        day = start_date + timedelta(days=i)
        day_end = day + timedelta(days=1)

        daily_activity.append({
            'date': day.strftime('%Y-%m-%d'),
            'users': User.objects.filter(date_joined__range=[day, day_end]).count(),
            'publications': Publication.objects.filter(created_at__range=[day, day_end]).count(),
            'service_requests': ServiceRequest.objects.filter(created_at__range=[day, day_end]).count(),
        })

    context = {
        'period': period,
        'user_stats': user_stats,
        'content_stats': content_stats,
        'training_stats': training_stats,
        'service_stats': service_stats,
        'daily_activity': daily_activity,
    }

    return render(request, 'dashboard/analytics.html', context)


@staff_member_required
def translation_management(request):
    """Translation management page for admins"""
    from django.utils import translation
    from django.conf import settings
    import os
    import glob

    # Get available languages
    available_languages = settings.LANGUAGES
    current_language = translation.get_language()

    # Get translation files info
    locale_path = settings.BASE_DIR / 'locale'
    translation_files = []

    for lang_code, lang_name in available_languages:
        po_file = locale_path / lang_code / 'LC_MESSAGES' / 'django.po'
        mo_file = locale_path / lang_code / 'LC_MESSAGES' / 'django.mo'

        if po_file.exists():
            # Count translated vs untranslated strings
            with open(po_file, 'r', encoding='utf-8') as f:
                content = f.read()
                total_strings = content.count('msgid "')
                translated_strings = content.count('msgstr "') - content.count('msgstr ""')

            translation_files.append({
                'language_code': lang_code,
                'language_name': lang_name,
                'po_file_exists': True,
                'mo_file_exists': mo_file.exists(),
                'total_strings': total_strings,
                'translated_strings': translated_strings,
                'completion_percentage': round((translated_strings / total_strings * 100) if total_strings > 0 else 0, 1),
                'po_file_path': str(po_file),
                'mo_file_path': str(mo_file),
            })
        else:
            translation_files.append({
                'language_code': lang_code,
                'language_name': lang_name,
                'po_file_exists': False,
                'mo_file_exists': False,
                'total_strings': 0,
                'translated_strings': 0,
                'completion_percentage': 0,
                'po_file_path': str(po_file),
                'mo_file_path': str(mo_file),
            })

    # Handle POST requests for translation actions
    if request.method == 'POST':
        action = request.POST.get('action')
        language = request.POST.get('language')

        if action == 'compile_translations':
            try:
                # Compile translation files
                from django.core.management import call_command
                call_command('compilemessages', locale=[language] if language else None)
                messages.success(request, f'Translation files compiled successfully for {language}' if language else 'All translation files compiled successfully')
            except Exception as e:
                messages.error(request, f'Error compiling translations: {str(e)}')

        elif action == 'update_translations':
            try:
                # Update translation files
                from django.core.management import call_command
                call_command('makemessages', locale=[language] if language else None, ignore=['venv'])
                messages.success(request, f'Translation files updated successfully for {language}' if language else 'All translation files updated successfully')
            except Exception as e:
                messages.error(request, f'Error updating translations: {str(e)}')

        return redirect('dashboard:translation_management')

    context = {
        'translation_files': translation_files,
        'current_language': current_language,
        'available_languages': available_languages,
    }

    return render(request, 'dashboard/translation_management.html', context)


@staff_member_required
def create_announcement(request):
    """Create new announcement"""
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        announcement_type = request.POST.get('announcement_type', 'general')
        priority = request.POST.get('priority', 'medium')
        target_audience = request.POST.get('target_audience', 'all')
        is_pinned = request.POST.get('is_pinned') == 'on'
        is_featured = request.POST.get('is_featured') == 'on'

        announcement = Announcement.objects.create(
            title=title,
            content=content,
            announcement_type=announcement_type,
            priority=priority,
            target_audience=target_audience,
            is_pinned=is_pinned,
            is_featured=is_featured,
            author=request.user,
            status='published'
        )

        messages.success(request, f'Announcement "{title}" created successfully.')
        return redirect('dashboard:content_management')

    return render(request, 'dashboard/create_announcement.html')


@staff_member_required
def edit_announcement(request, announcement_id):
    """Edit existing announcement"""
    announcement = get_object_or_404(Announcement, id=announcement_id)

    if request.method == 'POST':
        announcement.title = request.POST.get('title')
        announcement.content = request.POST.get('content')
        announcement.announcement_type = request.POST.get('announcement_type', 'general')
        announcement.priority = request.POST.get('priority', 'medium')
        announcement.target_audience = request.POST.get('target_audience', 'all')
        announcement.is_pinned = request.POST.get('is_pinned') == 'on'
        announcement.is_featured = request.POST.get('is_featured') == 'on'
        announcement.save()

        messages.success(request, f'Announcement "{announcement.title}" updated successfully.')
        return redirect('dashboard:content_management')

    context = {'announcement': announcement}
    return render(request, 'dashboard/edit_announcement.html', context)


@staff_member_required
def create_department(request):
    """Create new department"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        head_id = request.POST.get('head')

        department = Department.objects.create(
            name=name,
            description=description,
            head_id=head_id if head_id else None
        )

        messages.success(request, f'Department "{name}" created successfully.')
        return redirect('dashboard:organization_management')

    # Get potential heads (researchers and moderators)
    potential_heads = User.objects.filter(
        role__in=['researcher', 'moderator'],
        is_approved=True,
        is_active=True
    )

    context = {'potential_heads': potential_heads}
    return render(request, 'dashboard/create_department.html', context)


@staff_member_required
def create_lab(request):
    """Create new laboratory"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        department_id = request.POST.get('department')
        head_id = request.POST.get('head')
        capacity = request.POST.get('capacity', 10)

        lab = Lab.objects.create(
            name=name,
            description=description,
            department_id=department_id,
            head_id=head_id if head_id else None,
            capacity=int(capacity),
            created_by=request.user
        )

        messages.success(request, f'Laboratory "{name}" created successfully.')
        return redirect('dashboard:organization_management')

    departments = Department.objects.all()
    potential_heads = User.objects.filter(
        role__in=['researcher', 'moderator'],
        is_approved=True,
        is_active=True
    )

    context = {
        'departments': departments,
        'potential_heads': potential_heads
    }
    return render(request, 'dashboard/create_lab.html', context)


@staff_member_required
def organization_settings(request):
    """Organization settings management"""
    settings = OrganizationSettings.get_settings()

    if request.method == 'POST':
        # Handle form submission
        settings.name = request.POST.get('name', settings.name)
        settings.vision = request.POST.get('vision', settings.vision)
        settings.mission = request.POST.get('mission', settings.mission)
        settings.about = request.POST.get('about', settings.about)
        settings.email = request.POST.get('email', settings.email)
        settings.phone = request.POST.get('phone', settings.phone)
        settings.address = request.POST.get('address', settings.address)
        settings.website = request.POST.get('website', settings.website)
        settings.facebook = request.POST.get('facebook', settings.facebook)
        settings.twitter = request.POST.get('twitter', settings.twitter)
        settings.linkedin = request.POST.get('linkedin', settings.linkedin)
        settings.instagram = request.POST.get('instagram', settings.instagram)
        settings.enable_registration = request.POST.get('enable_registration') == 'on'
        settings.require_approval = request.POST.get('require_approval') == 'on'
        settings.maintenance_mode = request.POST.get('maintenance_mode') == 'on'
        settings.maintenance_message = request.POST.get('maintenance_message', settings.maintenance_message)

        # Handle file uploads
        if 'logo' in request.FILES:
            settings.logo = request.FILES['logo']
        if 'banner' in request.FILES:
            settings.banner = request.FILES['banner']
        if 'vision_image' in request.FILES:
            settings.vision_image = request.FILES['vision_image']
        if 'mission_image' in request.FILES:
            settings.mission_image = request.FILES['mission_image']

        try:
            settings.save()
            messages.success(request, 'Organization settings updated successfully!')
        except Exception as e:
            messages.error(request, f'Error updating settings: {str(e)}')

        return redirect('dashboard:organization_settings')

    context = {
        'settings': settings,
        'page_title': 'Organization Settings'
    }
    return render(request, 'dashboard/organization_settings.html', context)


@staff_member_required
def api_pending_counts(request):
    """API endpoint for pending counts used by dashboard"""
    counts = {
        'pending_users': User.objects.filter(is_approved=False).count(),
        'pending_announcements': Announcement.objects.filter(status='pending').count(),
        'pending_posts': Post.objects.filter(status='pending').count(),
        'pending_publications': Publication.objects.filter(status='pending').count(),
        'pending_service_requests': ServiceRequest.objects.filter(status='pending').count(),
    }
    return JsonResponse(counts)
