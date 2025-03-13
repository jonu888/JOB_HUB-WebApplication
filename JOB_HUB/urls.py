from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from JH import views

urlpatterns = [
    # Authentication & Core Pages
    path('',views.WelcomeView.as_view(), name='welcome'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('options/', views.OptionView.as_view(), name='options'),
    path('hrregister/', views.HrRegisterView.as_view(), name='hrregister'),
   
    

    # Dashboard Routes
    path('userdashboard/<int:pk>/', views.UserdashboardView.as_view(), name='userdashboard'),
    path('admindashboard/<int:pk>/', views.AdmindashboardView.as_view(), name='admindashboard'),
    
    # Job Management
    path('jobdisplay/<int:pk>/', views.JobsDisplayView.as_view(), name='jobdisplay'),
    path('addjobs/<int:pk>/', views.AddjobsView.as_view(), name='addjobs'),
    path('job_update/<int:pk>/', views.JobUpdateView.as_view(), name='job_update'),
    path('job_delete/<int:pk>/', views.JobDeleteView.as_view(), name='job_delete'),
    
    # Job Application & Candidate Management
    path('applyjobs/<int:pk>/', views.ApplyJobsView.as_view(), name='applyjobs'),
    path('candidate_detail/<int:candidate_id>/', views.CandidateDetailView.as_view(), name='candidate_detail'),
    path('candidate_info/<int:pk>/', views.CandidateInfoView.as_view(), name='candidate_info'),
    
    # User Profile
    path('profile/<int:pk>/', views.ProfileView.as_view(), name='profile'),
    
    # Resume Builder Routes
    path('template_select/<int:pk>/', views.template_select, name='template_select'),  # Choose resume template
    path('resume_form/<str:template>/', views.resume_form, name='resume_form'),        # Create new resume
    path('resume_list/<int:pk>/', views.resume_list, name='resume_list'),             # List all resumes
    path('resume_preview/<int:resume_id>/', views.resume_preview, name='resume_preview'),  # Preview resume
    path('edit_resume/<int:resume_id>/', views.edit_resume, name='edit_resume'),      # Edit existing resume
    path('download/<int:resume_id>/', views.download_pdf, name='download_pdf'),        # Download resume as PDF
    
    # ATS (Applicant Tracking System)
    path('ats/', views.index, name='ATS_score'),  # Check resume ATS score
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# URL Pattern Guide:
# <int:pk> - Primary key for user/job identification
# <int:resume_id> - Specific resume identifier
# <int:candidate_id> - Specific candidate identifier
# <str:template> - Template name for resume creation 