from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [

    # =================
    # PUBLIC / USER
    # =================
    path('', views.home, name='home'),
    path('projects/', views.projects, name='projects'),
    path('kk-profiling/', views.kk_profiling, name='kk_profiling'),
    path('sk-members/', views.sk_members, name='sk_members'),
    path('about-us/', views.about_us, name='about_us'),
    path('suggestions/', views.suggestion_box, name='suggestions'),

  # =================
    # AUTH
    # =================
    path('login/', RedirectView.as_view(url='/accounts/login/'), name='login'),

    # ✅ CUSTOM SIGNUP (THIS FIXES EVERYTHING)
    path('signup/', views.signup, name='signup'),

    path('accounts/', include('allauth.urls')),
    path('redirect-after-login/', views.redirect_after_login, name='redirect_after_login'),

    # =================
    # USER LOGOUT
    # =================
    path("local-logout/", views.local_logout, name="local_logout"),
    path("logout/confirm/", views.logout_confirm, name="logout_confirm"),

    # =================
    # ADMIN LOGOUT (CUSTOM DASHBOARD)
    # =================
    path("dashboard/logout/", views.admin_logout, name="admin_logout"),
    path("dashboard/logout/confirm/", views.admin_logout_confirm, name="admin_logout_confirm"),
    # =================
    # PASSWORD RESET
    # =================
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='core/password_reset.html'
    ), name='password_reset'),

    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='core/password_reset_done.html'
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='core/password_reset_confirm.html'
    ), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='core/password_reset_complete.html'
    ), name='password_reset_complete'),

    # =================
    # ADMIN DASHBOARD
    # =================
    path('dashboard/', views.dashboard, name='dashboard'),

# =================
# RESIDENTS (ADMIN)
# =================
path('dashboard/residents/', views.residents_list, name='residents_list'),
path('dashboard/residents/add/', views.residents_add, name='residents_add'),
path('dashboard/residents/<int:pk>/edit/', views.residents_edit, name='residents_edit'),
path('dashboard/residents/<int:pk>/delete/', views.residents_delete, name='residents_delete'),
  
# =================
# PROJECTS (ADMIN)
# =================
path('dashboard/projects/', views.projects_list, name='projects_list'),
path('dashboard/projects/add/', views.projects_add, name='projects_add'),
path('dashboard/projects/<int:pk>/edit/', views.projects_edit, name='projects_edit'),
path('dashboard/projects/<int:pk>/delete/', views.projects_delete, name='projects_delete'),

# =================
# KK PROFILES (ADMIN)
# =================
path('dashboard/kk-profiles/', views.kk_profiles_list, name='kk_profiles_list'),
path('dashboard/kk-profiles/pdf/', views.kk_profiles_pdf, name='kk_profiles_pdf'),

# =================
# SK MEMBERS (ADMIN)
# =================
path('dashboard/sk-members/', views.sk_members_admin, name='sk_members_admin'),
path('dashboard/sk-members/add/', views.sk_member_add, name='sk_member_add'),
path('dashboard/sk-members/<int:pk>/edit/', views.sk_member_edit, name='sk_member_edit'),
path('dashboard/sk-members/<int:pk>/delete/', views.sk_member_delete, name='sk_member_delete'),

# =================
# SUGGESTIONS (ADMIN)
# =================
path('dashboard/suggestions/', views.suggestions_admin, name='suggestions_admin'),
path('dashboard/suggestions/<int:pk>/', views.suggestion_detail, name='suggestion_detail'),
path('dashboard/suggestions/important/<int:pk>/', views.suggestion_mark_important, name='suggestion_important'),
path('dashboard/suggestions/delete/<int:pk>/', views.suggestion_delete, name='suggestion_delete'),


    # =================
    # CHARTS
    # =================
    path(
        'admin/charts/residents-by-purok/',
        views.chart_residents_by_purok,
        name='chart_residents_by_purok'
    ),
    path(
        'admin/charts/community-engagement/',
        views.admin_engagement_chart,
        name='admin_engagement_chart'
    ),
    path(
        'charts/public/community-engagement/',
        views.public_engagement_chart,
        name='public_engagement_chart'
    ),


path('dashboard/reports/', views.reports, name='reports'),

path('projects/<int:project_id>/react/<str:reaction_type>/', 
     views.react_project, 
     name='react_project'),

path('api/public-engagement-chart/', views.public_engagement_chart, name='public_engagement_chart'),

]
