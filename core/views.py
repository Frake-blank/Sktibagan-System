from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.db.models import Count, Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth import logout
from reportlab.pdfgen import canvas
from django.utils.text import slugify
import csv

from .models import (
    Resident,
    Project,
    ProjectImage,
    ActivityLog,
    KKProfile,
    ProjectReaction,
    SKMember,
    Suggestion,   # ✅ ADDED
)
from .forms import KKProfileForm, SKMemberForm, ResidentForm



# ---------------------
# ROLE / GROUP CHECKS
# ---------------------
def is_admin(user):
    return user.is_superuser or user.groups.filter(name='Admin').exists()

def is_staff_user(user):
    return user.groups.filter(name__in=['Admin', 'Staff']).exists()

# ---------------------
# REDIRECT AFTER LOGIN
# ---------------------
@login_required
def redirect_after_login(request):
    if is_admin(request.user):
        return redirect('dashboard')
    if is_staff_user(request.user):
        return redirect('projects_list')
    return redirect('home')


# ---------------------
# PUBLIC PROJECTS PAGE
# ---------------------
def projects(request):
    projects = Project.objects.all().order_by('-created_at')
    return render(request, 'core/projects.html', {
        'projects': projects
    })


# ---------------------
# PROJECT REACTIONS
# ---------------------
@login_required
def react_project(request, project_id, reaction_type):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    if reaction_type not in ['like', 'dislike']:
        return JsonResponse({'error': 'Invalid reaction'}, status=400)

    project = get_object_or_404(Project, id=project_id)

    # Get existing reaction
    reaction = ProjectReaction.objects.filter(
        project=project,
        user=request.user
    ).first()

    if reaction:
        # If same reaction clicked → remove it (toggle off)
        if reaction.reaction == reaction_type:
            reaction.delete()
        else:
            # Switch reaction
            reaction.reaction = reaction_type
            reaction.save()
    else:
        # Create new reaction
        ProjectReaction.objects.create(
            project=project,
            user=request.user,
            reaction=reaction_type
        )

    # IMPORTANT: Recalculate counts AFTER changes
    likes_count = ProjectReaction.objects.filter(
        project=project,
        reaction='like'
    ).count()

    dislikes_count = ProjectReaction.objects.filter(
        project=project,
        reaction='dislike'
    ).count()

    return JsonResponse({
        'likes': likes_count,
        'dislikes': dislikes_count,
    })

# ---------------------
# STATIC PAGES
# ---------------------
def about_us(request):
    return render(request, 'core/about_us.html')

def suggestions(request):
    return render(request, 'core/suggestions.html')


# ---------------------
# KK PROFILING
# ---------------------

@login_required
def kk_profiling(request):

    # ✅ BLOCK MULTIPLE SUBMISSIONS
    if hasattr(request.user, 'kk_profile'):
        messages.warning(request, "You have already submitted your KK Profile.")
        return redirect('home')

    if request.method == 'POST':
        resident_form = ResidentForm(request.POST)
        kk_form = KKProfileForm(request.POST)

        if resident_form.is_valid() and kk_form.is_valid():
            # SAVE RESIDENT
            resident = resident_form.save()

            # SAVE KK PROFILE (linked)
            kk_profile = kk_form.save(commit=False)
            kk_profile.resident = resident
            kk_profile.user = request.user
            kk_profile.save()

            messages.success(request, "KK Profile submitted successfully!")
            return redirect('home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        resident_form = ResidentForm()
        kk_form = KKProfileForm()

    return render(request, 'core/kk_profiling.html', {
        'resident_form': resident_form,
        'kk_form': kk_form,
    })

# ---------------------
# ADMIN DASHBOARD
# ---------------------
@login_required
@user_passes_test(is_admin, login_url='home')
def dashboard(request):
    return render(request, 'core/dashboard.html', {
        'total_residents': Resident.objects.count(),
        'total_projects': Project.objects.count(),
        'total_kk_profiles': KKProfile.objects.count(),
        'total_sk_members': SKMember.objects.count(),
    })


# ---------------------
# KK PROFILES (ADMIN)
# ---------------------
@login_required
@user_passes_test(is_admin, login_url='home')
def kk_profiles_list(request):
    profiles = KKProfile.objects.order_by('-created_at')
    return render(request, 'core/admin/kk_profiles_lists.html', {
        'profiles': profiles
    })
@login_required
@user_passes_test(is_admin, login_url='home')
def kk_profiles_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="kk_profiles.pdf"'

    p = canvas.Canvas(response)
    width, height = 595, 842
    y = height - 50

    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2, y, "KK PROFILING REPORT")
    y -= 40

    p.setFont("Helvetica", 10)

    for index, profile in enumerate(KKProfile.objects.all(), start=1):
        if y < 60:
            p.showPage()
            p.setFont("Helvetica", 10)
            y = height - 50

        p.drawString(40, y, str(index))
        p.drawString(80, y, profile.email)
        p.drawString(300, y, profile.get_school_status_display())
        y -= 20

    p.save()
    return response


# ---------------------
# RESIDENTS (ADMIN / STAFF)
# ---------------------
@login_required
@user_passes_test(is_staff_user, login_url='home')
def residents_list(request):
    return render(request, 'core/admin/residents_list.html', {
        'residents': Resident.objects.all()
    })

@login_required
@user_passes_test(is_staff_user, login_url='home')
def residents_add(request):
    if request.method == 'POST':
        Resident.objects.create(
            firstname=request.POST.get('firstname'),
            lastname=request.POST.get('lastname'),
            age=request.POST.get('age'),
            gender=request.POST.get('gender'),
            purok=request.POST.get('purok'),
        )

        messages.success(request, "Resident added successfully.")
        return redirect('residents_list')

    return render(request, 'core/admin/residents_add.html')



@login_required
@user_passes_test(is_staff_user, login_url='home')
def residents_edit(request, pk):
    resident = get_object_or_404(Resident, pk=pk)

    if request.method == "POST":
        resident.firstname = request.POST.get("firstname")
        resident.lastname = request.POST.get("lastname")
        resident.gender = request.POST.get("gender")
        resident.purok = request.POST.get("purok")

        resident.save()

        messages.success(request, "Resident updated successfully.")
        return redirect("residents_list")

    return render(request, "core/admin/residents_edit.html", {
        "resident": resident
    })



@login_required
@user_passes_test(is_staff_user, login_url='home')
def residents_delete(request, pk):
    resident = get_object_or_404(Resident, pk=pk)

    if request.method == 'POST':
        resident.delete()
        messages.success(request, "Resident deleted successfully.")
        return redirect('residents_list')

    return render(request, 'core/admin/residents_delete_confirm.html', {
        'resident': resident
    })




# ---------------------
# PROJECTS (ADMIN)
# ---------------------
@login_required
@user_passes_test(is_staff_user, login_url='home')
def projects_list(request):
    projects = Project.objects.order_by('-created_at')
    return render(request, 'core/admin/projects_list.html', {
        'projects': projects
    })


@login_required
@user_passes_test(is_staff_user, login_url='home')
def projects_add(request):
    if request.method == 'POST':
        project = Project.objects.create(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            date_started=request.POST.get('date_started') or None,
            status=request.POST.get('status'),
        )

        for image in request.FILES.getlist('images'):
            ProjectImage.objects.create(project=project, image=image)

        messages.success(request, "Project added successfully.")
        return redirect('projects_list')

    return render(request, 'core/admin/projects_add.html')


@login_required
@user_passes_test(is_staff_user, login_url='home')
def projects_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == 'POST':
        project.title = request.POST.get('title')
        project.description = request.POST.get('description')
        project.date_started = request.POST.get('date_started') or None
        project.status = request.POST.get('status')
        project.save()

        for image in request.FILES.getlist('images'):
            ProjectImage.objects.create(project=project, image=image)

        messages.success(request, "Project updated successfully.")
        return redirect('projects_list')

    return render(request, 'core/admin/projects_edit.html', {
        'project': project
    })


@login_required
@user_passes_test(is_staff_user, login_url='home')
def projects_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == 'POST':
        project.delete()
        messages.success(request, "Project deleted successfully.")
        return redirect('projects_list')

    return render(request, 'core/admin/projects_delete_confirm.html', {
        'project': project
    })


# ---------------------
# ACTIVITY LOGS
# ---------------------
@login_required
@user_passes_test(is_admin, login_url='home')
def activity_logs(request):
    return render(request, 'core/admin/activity_logs.html', {
        'logs': ActivityLog.objects.order_by('-created_at')
    })

# ---------------------
# CHART API (SAFE)
# ---------------------
@login_required
def chart_residents_by_purok(request):
    if not is_admin(request.user):
        return HttpResponseForbidden("Not allowed")

    data = (
        Resident.objects
        .values('purok')
        .annotate(count=Count('id'))
        .order_by('purok')
    )

    return JsonResponse({
        'labels': [item['purok'] or "Unknown" for item in data],
        'counts': [item['count'] for item in data],
    })


@login_required
def admin_engagement_chart(request):
    if not is_admin(request.user):
        return HttpResponseForbidden("Not allowed")

    return JsonResponse({
        "labels": [
            "Users",
            "Residents",
            "KK Profiles",
            "Projects"
        ],
        "data": [
            User.objects.count(),
            Resident.objects.count(),
            KKProfile.objects.count(),
            Project.objects.count(),
        ]
    })


# ---------------------
# USER SIGNUP
# ---------------------

def signup(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').lower().strip()
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if not all([first_name, last_name, email, password1, password2]):
            messages.error(request, "All fields are required.")
            return redirect('signup')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('signup')

        base_username = slugify(f"{first_name}-{last_name}")
        username = base_username
        i = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{i}"
            i += 1

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
            )
        except Exception as e:
            messages.error(request, f"Create user failed: {e}")
            return redirect('signup')

      
         # ✅ EXPLICIT BACKEND (THIS FIXES THE ERROR)
        login(
            request,
            user,
            backend='django.contrib.auth.backends.ModelBackend'
        )

        messages.success(request, "Account created successfully!")
        return redirect('redirect_after_login')

    return render(request, 'account/signup.html')

# ---------------------
# SK MEMBERS (ADMIN)
# ---------------------
@login_required
@user_passes_test(is_admin, login_url='home')
def sk_members_admin(request):
    members = SKMember.objects.order_by('order')
    return render(request, 'core/admin/sk_members_list.html', {
        'members': members
    })


def sk_members(request):
    all_members = SKMember.objects.all()
    members = {m.role: m for m in all_members}

    roles = [
        ('treasurer', 'SK Treasurer'),
        ('appro', 'SK Kagawad – Appro'),
        ('education', 'SK Kagawad – Education'),
        ('health', 'SK Kagawad – Health'),
        ('sports', 'SK Kagawad – Sports'),
        ('social', 'SK Kagawad – Social Inclusion'),
        ('livelihood', 'SK Kagawad – Livelihood'),
        ('environment', 'SK Kagawad – Environment'),
    ]

    return render(request, 'core/sk_members.html', {
        'members': members,
        'roles': roles
    })

@login_required
@user_passes_test(is_admin, login_url='home')
def sk_member_add(request):
    if request.method == 'POST':
        form = SKMemberForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "SK Member added successfully.")  # 👈 ADD HERE
            return redirect('sk_members_admin')
    else:
        form = SKMemberForm()

    return render(request, 'core/admin/sk_member_form.html', {
        'form': form
    })


@login_required
@user_passes_test(is_admin, login_url='home')
def sk_member_edit(request, pk):
    member = get_object_or_404(SKMember, pk=pk)

    if request.method == 'POST':
        form = SKMemberForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, "SK Member updated successfully.")  # 👈 ADD HERE
            return redirect('sk_members_admin')
    else:
        form = SKMemberForm(instance=member)

    return render(request, 'core/admin/sk_member_form.html', {
        'form': form
    })


@login_required
@user_passes_test(is_admin, login_url='home')
def sk_member_delete(request, pk):
    member = get_object_or_404(SKMember, pk=pk)

    if request.method == 'POST':
        member.delete()
        messages.success(request, "SK Member deleted.")
        return redirect('sk_members_admin')

    return render(request, 'core/admin/sk_member_delete.html', {
        'member': member
    })

# ---------------------
# SUGGESTION BOX (USER)
# ---------------------
@login_required
def suggestion_box(request):
    if request.method == "POST":
        message = request.POST.get("message", "").strip()

        if not message:
            messages.error(request, "❌ Please write a suggestion before submitting.")
            return redirect("suggestions")

        Suggestion.objects.create(
            user=request.user,
            message=message
        )

        messages.success(request, "✅ Your suggestion has been sent. Thank you!")
        return redirect("suggestions")

    return render(request, "core/suggestions.html")





# ---------------------
# ADMIN ACTIONS (POST ONLY)
# ---------------------
@login_required
@user_passes_test(is_admin, login_url='home')
def suggestions_admin(request):
    suggestions = Suggestion.objects.order_by(
        'status', '-is_important', '-created_at'
    )

    return render(request, "core/admin/suggestions_list.html", {
        "suggestions": suggestions
    })







@login_required
@user_passes_test(is_admin, login_url='home')
def suggestion_mark_important(request, pk):
    suggestion = get_object_or_404(Suggestion, pk=pk)
    suggestion.is_important = not suggestion.is_important
    suggestion.save()
    return redirect("suggestion_detail", pk=pk)


@login_required
@user_passes_test(is_admin, login_url='home')
def suggestion_delete(request, pk):
    suggestion = get_object_or_404(Suggestion, pk=pk)
    suggestion.delete()
    return redirect("suggestions_admin")

@login_required
@user_passes_test(is_admin, login_url='home')
def suggestion_detail(request, pk):
    suggestion = get_object_or_404(Suggestion, pk=pk)

    # auto mark as read when opened
    if suggestion.status == 'new':
        suggestion.status = 'reviewed'
        suggestion.save()

    return render(request, "core/admin/suggestion_detail.html", {
        "suggestion": suggestion
    })


# ---------------------
# HOME (PUBLIC)
# ---------------------
def home(request):
    # Transparency counts
    total_users = User.objects.count()
    total_residents = Resident.objects.count()
    total_kk_profiles = KKProfile.objects.count()

    # Latest project for "What's New"
    latest_project = Project.objects.order_by('-created_at').first()

    context = {
        'total_users': total_users,
        'total_residents': total_residents,
        'total_kk_profiles': total_kk_profiles,
        'latest_project': latest_project,
    }

    return render(request, 'core/home.html', context)

def public_engagement_chart(request):
    project_likes = ProjectReaction.objects.filter(reaction='like').count()
    project_dislikes = ProjectReaction.objects.filter(reaction='dislike').count()

    kk_profiles = KKProfile.objects.count()
    users = User.objects.count()
    residents = Resident.objects.count()

    return JsonResponse({
        'labels': [
            'Project Likes',
            'Project Dislikes',
            'KK Profiles',
            'Users',
            'Residents'
        ],
        'data': [
            project_likes,
            project_dislikes,
            kk_profiles,
            users,
            residents
        ]
    })
# ----------------
# LOGIN / LOGOUT
# ----------------
# ---------- ROLE CHECK ----------

@login_required
def login_redirect(request):
    # optional helper
    return redirect('/accounts/login/')


def local_logout(request):
    logout(request)
    return redirect('home')

@login_required
def logout_confirm(request):
    # USER logout confirmation
    return render(request, "account/logout_confirm.html")


@login_required
@user_passes_test(is_admin, login_url='home')
def admin_logout_confirm(request):
    # ADMIN logout confirmation
    return render(request, "core/admin/logout_confirm.html")

@login_required
@user_passes_test(is_admin, login_url="home")
def admin_logout(request):
    logout(request)
    return redirect("home")


#-----------
#Reports (CSV Export)
#-----------
@login_required
@user_passes_test(is_admin, login_url='home')
def reports(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sk_tibagan_report.csv"'

    writer = csv.writer(response)

    # ===== USERS =====
    writer.writerow(['USERS'])
    writer.writerow(['Username', 'Email', 'First Name', 'Last Name'])
    for user in User.objects.all():
        writer.writerow([
            user.username,
            user.email,
            user.first_name,
            user.last_name
        ])

    writer.writerow([])

    # ===== RESIDENTS =====
    writer.writerow(['RESIDENTS'])
    writer.writerow(['First Name', 'Last Name', 'Age', 'Gender', 'Purok'])
    for r in Resident.objects.all():
        writer.writerow([
            r.firstname,
            r.lastname,
            r.age,
            r.gender,
            r.purok
        ])

    writer.writerow([])

    # ===== KK PROFILES =====
    writer.writerow(['KK PROFILES'])
    writer.writerow(['Email', 'School Status'])
    for k in KKProfile.objects.all():
        writer.writerow([
            k.email,
            k.get_school_status_display()
        ])

    return response

    