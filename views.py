from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q

from django.views.generic import View
from django.contrib.auth.models import User
from .models import JobUser, Jobs, Candidate, HRUser
from .forms import UserForm, JobUserForm, LoginForm, AddjobsForm, HrForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages

from django.shortcuts import render, redirect
from .models import Resume
from .utils import generate_pdf
from django.http import HttpResponse
from django.template.loader import render_to_string

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from .models import Resume
from .utils import render_to_latex, generate_pdf

from django.views import View
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Candidate
from itertools import groupby
from operator import attrgetter
import logging

from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Jobs, JobUser, Candidate

class WelcomeView(View):
    def get(self, request):
        return render(request, 'welcome.html')
    
    
class OptionView(View):
    def get(self, request):
        return render(request, 'option.html')

class RegisterView(View):
    def get(self, request):
        form1 = UserForm()
        form2 = JobUserForm()
        return render(request, 'register.html', {'form1': form1, 'form2': form2})

    def post(self, request):
        form1 = UserForm(request.POST)
        form2 = JobUserForm(request.POST)
        if User.objects.filter(username=request.POST['username']).exists():
            form1.add_error('username', 'Username already exists')
            return render(request, 'register.html', {'form1': form1, 'form2': form2})
        if form1.is_valid() and form2.is_valid():
            user = User.objects.create_user(
                username=form1.cleaned_data['username'],
                password=form1.cleaned_data['password'],
                email=form1.cleaned_data['email'],
                
                
            )
            job_user = JobUser(
                user_id=user,
                first_name=form2.cleaned_data["first_name"],
                last_name=form2.cleaned_data["last_name"],
               
                industry=form2.cleaned_data["industry"],
                
            )
            job_user.save()
            return redirect('login')
        print("Register form errors:", form1.errors, form2.errors)
        return render(request, 'register.html', {'form1': form1, 'form2': form2})
    
class HrRegisterView(View):
    def get(self, request):
        form1 = UserForm()
        form2 = HrForm()
        return render(request, 'hrregister.html', {'form1': form1, 'form2': form2})
    
    def post(self, request):
        form1 = UserForm(request.POST)
        form2 = HrForm(request.POST)
        if User.objects.filter(username=request.POST['username']).exists():
            form1.add_error('username', 'Username already exists')
            return render(request, 'register.html', {'form1': form1, 'form2': form2})
        if form1.is_valid() and form2.is_valid():
            user = User.objects.create_user(
                username=form1.cleaned_data['username'],
                password=form1.cleaned_data['password'],
                email=form1.cleaned_data['email'],
                is_staff=True,
                is_superuser=True,
            )
            hr_user = HRUser(
                user_id=user,
                first_name=form2.cleaned_data["first_name"],
                last_name=form2.cleaned_data["last_name"],
                company_name=form2.cleaned_data["company_name"],
                industry=form2.cleaned_data["industry"],
                
            )
            hr_user.save()
            return redirect('login')
        print("Register form errors:", form1.errors, form2.errors)
        return render(request, 'register.html', {'form1': form1, 'form2': form2})

class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'login.html', {"form": form})

    def post(self, request):
        form = LoginForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data.get('username')
            pswd = form.cleaned_data.get('password')
            
            print(f"Trying to authenticate: {name}")  # Debug print
            user = authenticate(request, username=name, password=pswd)

            if user:
                print("Authentication successful!")  # Debug print
                login(request, user)
                if user.is_staff:
                    return redirect('admindashboard', pk=user.id)  # Redirect with pk

                else:
                    return render(request,'userdashboard.html',{'data':user.id})
            else:
                print("Authentication failed!")  # Debug print
                return render(request, 'login.html', {'form': form, 'error': 'Invalid username or password'})

        print("Form is not valid!")  # Debug print
        return render(request, 'login.html', {'form': form})

class UserdashboardView(View):
    def get(self, request, pk):
        job_user = JobUser.objects.get(user_id=pk)
        if request.user.id == pk and job_user.user_id.id == pk:
            return render(request, 'userdashboard.html', {'data': pk})   
        else:
            return redirect('login')

@method_decorator(login_required, name='dispatch')
class CandidateDetailView(View):
    def get(self, request, candidate_id):
        try:
            
            candidate = get_object_or_404(Candidate, id=candidate_id)
            job_user = get_object_or_404(JobUser, user_id=candidate.user_id)
            user = get_object_or_404(User, id=candidate.user_id)
            username = user.username
            resume_url = candidate.resume.url if candidate.resume else None
            logger.debug(f"Candidate ID: {candidate_id}, Resume URL: {resume_url}, Username: {username}")
            
            if candidate.hr_id.user_id.id==request.user.id:
                return render(request, 'candidate_detail.html', {
                    'candidate': candidate,
                    'job_user': job_user,
                    'username': username,
                    'resume_url': resume_url,
                })
            else:
                return redirect('login')

        except Exception as e:
            logger.error(f"Error in CandidateDetailView: {str(e)}")
            return render(request, 'candidate_detail.html', {
                'error': "An error occurred while fetching candidate details.",
            })

        except Exception as e:
            logger.error(f"Error in CandidateDetailView: {str(e)}")
            return render(request, 'candidate_detail.html', {
                'error': "An error occurred while fetching candidate details.",
            }) 

# Set up logging
logger = logging.getLogger(__name__)

@method_decorator(login_required, name='dispatch')
class CandidateInfoView(View):
    def get(self, request, pk):
        try:
            hr_user = HRUser.objects.get(user_id=pk)
            if request.user.id == pk and hr_user.user_id.id == pk:
                # Fetch candidates using hr_user.id instead of pk
                candidates = Candidate.objects.filter(job__hr_id=hr_user).order_by('job__job_name', '-ats_score')
                logger.debug(f"Retrieved {candidates.count()} candidates")

                # Group candidates by job name
                grouped_candidates = {}
                for job_name, group in groupby(candidates, key=attrgetter('job.job_name')):
                    grouped_candidates[job_name] = list(group)
                logger.debug(f"Grouped candidates: {grouped_candidates.keys()}")

                return render(request, 'candidateinfoview.html', {
                    'grouped_candidates': grouped_candidates,
                    'request': request
                })
            return redirect('login')

        except Exception as e:
            logger.error(f"Error in CandidateInfoView: {str(e)}")
            return render(request, 'candidateinfoview.html', {
                'grouped_candidates': {},
                'error': "An error occurred while fetching candidates.",
                'request': request
            })

class AdmindashboardView(View):

    def get(self, request, pk):

        return render(request, "admindashboard.html",{'data': pk})  

class JobsDisplayView(View):
    def get(self, request,pk):
        if request.user.is_staff:
            new=HRUser.objects.get(user_id=pk)
            if pk == new.user_id.id:
              data = Jobs.objects.filter(hr_id=new.id)
            print("admin")
            return render(request, "adminjobsdispaly.html", {'data': data, 'no': pk}) 

        elif request.user.id==pk:
            job_user = JobUser.objects.get(user_id=pk)
            if job_user.user_id.id==pk:
             data = Jobs.objects.all()
             print("user")
             return render(request, 'userjobsdisplay.html', {'data': data, 'no': pk})
        else:
            return redirect('login')

@method_decorator(login_required, name='dispatch')
class AddjobsView(View):
    def get(self, request, pk):
        form = AddjobsForm()  
        if request.user.is_staff and pk == request.user.id:
            return render(request, "addjobs.html", {
                'form': form,
                'user_id': request.user.id
            })
        else:
            return redirect('login')

    def post(self, request, pk):
        if request.user.is_staff and pk == request.user.id:
            form = AddjobsForm(request.POST)
            try:
                hr_user = HRUser.objects.get(user_id=request.user)
                if form.is_valid():
                    job = form.save(commit=False)
                    job.company_name = hr_user.company_name
                    job.hr_id = hr_user
                    job.save()
                    return redirect('jobdisplay', pk=request.user.id)
            except HRUser.DoesNotExist:
                messages.error(request, "HR profile not found. Please contact admin.")
                return redirect('login')
            
            return render(request, "addjobs.html", {
                'form': form,
                'user_id': request.user.id
            })
        return redirect('login')




# Set up logging
logger = logging.getLogger(__name__)

@method_decorator(login_required, name='dispatch')
class ApplyJobsView(View):
    def post(self, request, pk):
        logger.debug(f"Received POST request for pk={pk}")
        if not pk:
            # Handle case where pk is not provided (e.g., invalid URL)
            data = Jobs.objects.all()
            return render(request, 'userjobsdisplay.html', {'data': data, 'no': request.user.id})

        try:
            # Get the job instance
            jobdata = get_object_or_404(Jobs, id=pk)
            logger.debug(f"Found job: {jobdata.job_name}")

            # Check if the user has already applied
            if Candidate.objects.filter(job=jobdata, user_id=request.user.id).exists():
                messages.error(request, "You have already applied for this job.")
                data = Jobs.objects.all()
                return render(request, 'userjobsdisplay.html', {'data': data,'no':request.user.id})   # Use correct URL name

            # Get the JobUser instance for the current user
            job_user = get_object_or_404(JobUser, user_id=request.user.id)  # Use user_id instead of user
            logger.debug(f"Found JobUser: {job_user}")

            # Get form data
            name = request.POST.get('name')
            email = request.POST.get('email')
            resume = request.FILES.get('resume')
            logger.debug(f"Form data - Name: {name}, Email: {email}, Resume: {resume}")

            if not all([name, email, resume]):
                messages.error(request, "All fields (Name, Email, and Resume) are required.")
                data = Jobs.objects.all()
                return render(request, 'userjobsdisplay.html', {'data': data,'no':request.user.id}) 

            # Validate file type (PDF only)
            if not resume.name.endswith('.pdf'):
                messages.error(request, "Please upload a PDF file for your resume.")
                data = Jobs.objects.all()
                return render(request, 'userjobsdisplay.html', {'data': data,'no':request.user.id}) 

            # Validate file size (e.g., max 5MB)
            if resume.size > 5 * 1024 * 1024:
                messages.error(request, "Resume file size should not exceed 5MB.")
                data = Jobs.objects.all()
                return render(request, 'userjobsdisplay.html', {'data': data,'no':request.user.id}) 
            
            
            
            check_resume = extract_text_from_pdf(resume)
            Atsdata = ats_score_checker(jobdata.job_name, check_resume)
            logger.debug(f"ATS data: {Atsdata}")

            # Extract total_score from Atsdata and convert to integer
            if isinstance(Atsdata, tuple) and len(Atsdata) > 0:
                total_score = int(float(Atsdata[0]))  # Convert 72.15 to 72
            else:
                total_score = 0  # Fallback if Atsdata is not as expected
            logger.debug(f"Total ATS score: {total_score}")

            # Save application
            candidate = Candidate.objects.create(
                job=jobdata,
                user_id=request.user.id,
                email=email,
                is_applied=True,
                no=job_user,
                resume=resume,
                ats_score=total_score,
                hr_id=jobdata.hr_id
            )
            logger.debug(f"Candidate created with ID: {candidate.id}")

            messages.success(request, f"Successfully applied for {jobdata.job_name}!")
            data = Jobs.objects.all()
            return render(request, 'userjobsdisplay.html', {'data': data,'no':request.user.id})

        except JobUser.DoesNotExist:
            logger.error("JobUser not found for the current user")
            messages.error(request, "JobUser profile not found. Please contact support.")
            data = Jobs.objects.all()
            return render(request, 'userjobsdisplay.html', {'data': data,'no':request.user.id}) 
        except Exception as e:
            logger.error(f"Error in apply job: {str(e)}")
            messages.error(request, f"An error occurred: {str(e)}")
            data = Jobs.objects.all()
            return render(request, 'userjobsdisplay.html', {'data': data,'no':request.user.id})

    def get(self, request, pk):
        data = Jobs.objects.all()
        # Handle GET requests (e.g., redirect to job list if accessed directly)
        return render(request, 'userjobsdisplay.html', {'data': data,'no':request.user.id})  # Replace with your job listing URL name
     
class ProfileView(View):
    def get(self, request, pk):
        user = get_object_or_404(User, id=pk)
        job_user = get_object_or_404(JobUser, user_id=user)
        if request.user.id==pk and user.id==pk and job_user.user_id.id==pk:
            return render(request, 'profile.html', {
                'user': user,
                'job_user': job_user,
                'education_choices': JobUser.EDUCATION_CHOICES,
                'experience_choices': JobUser.EXPERIENCE_CHOICES
            })
        else:
            return redirect('login')

    def post(self, request, pk):
        user = get_object_or_404(User, id=pk)
        job_user = get_object_or_404(JobUser, user_id=user)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                # Update user details
                user.email = request.POST.get('email')
                user.save()
                
                # Update job user details
                job_user.first_name = request.POST.get('first_name')
                job_user.last_name = request.POST.get('last_name')
                job_user.education = request.POST.get('education')
                job_user.experience = request.POST.get('experience')
                job_user.skills = request.POST.get('skills')
                job_user.save()
                
                return JsonResponse({'status': 'success'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)})
        
        return redirect('profile', pk=pk)

class JobUpdateView(View):
    def get(self, request, pk):
        
        new=Jobs.objects.get(id=pk)
        if request.user.is_staff and new.hr_id.user_id.id == request.user.id:
            job = get_object_or_404(Jobs, id=pk)
            form = AddjobsForm(instance=job)
            return render(request, 'job_update.html', {
                'form': form,
                'job': job
            })
        else:
            return redirect('login')

    def post(self, request, pk):
        new=Jobs.objects.get(id=pk)
        if request.user.is_staff and new.hr_id.user_id.id == request.user.id:
            job = get_object_or_404(Jobs, id=pk)
            form = AddjobsForm(request.POST, instance=job)
            if form.is_valid():
                form.save()
                return redirect('jobdisplay', pk=request.user.id)  # Redirect to admin jobs display
            else:
                return render(request, 'job_update.html', {
                    'form': form,
                    'job': job
                })
        else:
            return redirect('login')

class JobDeleteView(View):
    def get(self, request, pk):
        new=Jobs.objects.get(id=pk)
        if request.user.is_staff and new.hr_id.user_id.id == request.user.id:
            job = get_object_or_404(Jobs, id=pk)
            job.delete()
            return redirect('jobdisplay', pk=request.user.id)  # Redirect to admin jobs display
        else:
            return redirect('login')

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')
    
    
    
    
    
    
    
    
    
    
    
    
    
    



from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from .models import Resume
from .utils import render_to_latex, generate_pdf

@login_required
def template_select(request, pk):
    if request.user.id != int(pk):
        return redirect('template_select', pk=request.user.id)  # Redirect to user's own page
    return render(request, 'template_select.html', {'pk': pk})

@login_required
def resume_form(request, template):
    resume = None
    if request.method == 'POST':
        education = [
            {
                'degree': request.POST.get(f'edu_degree_{i}', ''),
                'institution': request.POST.get(f'edu_institution_{i}', ''),
                'dates': request.POST.get(f'edu_dates_{i}', ''),
                'cgpa': request.POST.get(f'edu_cgpa_{i}', '')
            } for i in range(12) if request.POST.get(f'edu_degree_{i}', '')
        ]
        experience = [
            {
                'title': request.POST.get(f'exp_title_{i}', ''),
                'company': request.POST.get(f'exp_company_{i}', ''),
                'dates': request.POST.get(f'exp_dates_{i}', ''),
                'details': request.POST.get(f'exp_details_{i}', '').split(', ') if request.POST.get(f'exp_details_{i}', '') else []
            } for i in range(12) if request.POST.get(f'exp_title_{i}', '')
        ]
        projects = [
            {
                'title': request.POST.get(f'proj_title_{i}', ''),
                'url': request.POST.get(f'proj_url_{i}', ''),
                'description': request.POST.get(f'proj_description_{i}', ''),
                'technologies': request.POST.get(f'proj_technologies_{i}', '').split(', ') if request.POST.get(f'proj_technologies_{i}', '') else []
            } for i in range(12) if request.POST.get(f'proj_title_{i}', '')
        ]
        skills = [
            {
                'category': request.POST.get(f'skill_category_{i}', ''),
                'items': request.POST.get(f'skill_items_{i}', '').split(', ') if request.POST.get(f'skill_items_{i}', '') else []
            } for i in range(12) if request.POST.get(f'skill_category_{i}', '')
        ]
        languages = request.POST.get('languages', '').split(', ') if request.POST.get('languages', '') else []

        resume = Resume(
            full_name=request.POST['full_name'],
            email=request.POST['email'],
            phone=request.POST['phone'],
            location=request.POST.get('location', ''),
            github_url=request.POST.get('github_url', ''),
            linkedin_url=request.POST.get('linkedin_url', ''),
            summary=request.POST['summary'],
            education=education,
            experience=experience,
            projects=projects,
            skills=skills,
            languages=languages,
            template=template,
            userid=request.user
        )
        resume.save()
        return redirect('resume_preview', resume_id=resume.id)
    
    return render(request, 'resume_form.html', {'template': template, 'resume': resume})

@login_required
def resume_preview(request, resume_id):
    resume = Resume.objects.get(id=resume_id)
    if resume.userid != request.user:
        return redirect('template_select', pk=request.user.id)

    if request.method == 'POST':
        if 'edit' in request.POST:
            return render(request, 'resume_form.html', {'template': resume.template, 'resume': resume})
        elif 'save' in request.POST:
            resume.full_name = request.POST['full_name']
            resume.email = request.POST['email']
            resume.phone = request.POST['phone']
            resume.location = request.POST.get('location', '')
            resume.github_url = request.POST.get('github_url', '')
            resume.linkedin_url = request.POST.get('linkedin_url', '')
            resume.summary = request.POST['summary']
            resume.education = [
                {
                    'degree': request.POST.get(f'edu_degree_{i}', ''),
                    'institution': request.POST.get(f'edu_institution_{i}', ''),
                    'dates': request.POST.get(f'edu_dates_{i}', ''),
                    'cgpa': request.POST.get(f'edu_cgpa_{i}', '')
                } for i in range(12) if request.POST.get(f'edu_degree_{i}', '')
            ]
            resume.experience = [
                {
                    'title': request.POST.get(f'exp_title_{i}', ''),
                    'company': request.POST.get(f'exp_company_{i}', ''),
                    'dates': request.POST.get(f'exp_dates_{i}', ''),
                    'details': request.POST.get(f'exp_details_{i}', '').split(', ') if request.POST.get(f'exp_details_{i}', '') else []
                } for i in range(12) if request.POST.get(f'exp_title_{i}', '')
            ]
            resume.projects = [
                {
                    'title': request.POST.get(f'proj_title_{i}', ''),
                    'url': request.POST.get(f'proj_url_{i}', ''),
                    'description': request.POST.get(f'proj_description_{i}', ''),
                    'technologies': request.POST.get(f'proj_technologies_{i}', '').split(', ') if request.POST.get(f'proj_technologies_{i}', '') else []
                } for i in range(12) if request.POST.get(f'proj_title_{i}', '')
            ]
            resume.skills = [
                {
                    'category': request.POST.get(f'skill_category_{i}', ''),
                    'items': request.POST.get(f'skill_items_{i}', '').split(', ') if request.POST.get(f'skill_items_{i}', '') else []
                } for i in range(12) if request.POST.get(f'skill_category_{i}', '')
            ]
            resume.languages = request.POST.get('languages', '').split(', ') if request.POST.get('languages', '') else []
            resume.save()
            return redirect('resume_preview', resume_id=resume.id)
    
    resume_content = render_to_string(f'templates/{resume.template}.html', {'resume': resume})
    return render(request, 'resume_preview.html', {'resume': resume, 'resume_content': resume_content})

@login_required
def download_pdf(request, resume_id):
    try:
        resume = Resume.objects.get(id=resume_id)
        if resume.userid != request.user:
            return redirect('template_select', pk=request.user.id)
        
        pdf = generate_pdf(resume)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{resume.full_name}_resume.pdf"'
        return response
    except Resume.DoesNotExist:
        return HttpResponse("Resume not found.", status=404)
    except Exception as e:
        return HttpResponse(f"Error generating PDF: {str(e)}", status=500)
    
    
def resume_list(request,pk):
    resumes = Resume.objects.filter(userid=pk)
    return render(request, 'resume_list.html', {'resumes': resumes})   
    
@login_required
def edit_resume(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id)
    
    # Check if the user owns this resume
    if resume.userid != request.user:
        return redirect('template_select', pk=request.user.id)
    
    if request.method == 'POST':
        # Handle form submission similar to resume_form
        education = [
            {
                'degree': request.POST.get(f'edu_degree_{i}', ''),
                'institution': request.POST.get(f'edu_institution_{i}', ''),
                'dates': request.POST.get(f'edu_dates_{i}', ''),
                'cgpa': request.POST.get(f'edu_cgpa_{i}', '')
            } for i in range(12) if request.POST.get(f'edu_degree_{i}', '')
        ]
        experience = [
            {
                'title': request.POST.get(f'exp_title_{i}', ''),
                'company': request.POST.get(f'exp_company_{i}', ''),
                'dates': request.POST.get(f'exp_dates_{i}', ''),
                'details': request.POST.get(f'exp_details_{i}', '').split(', ') if request.POST.get(f'exp_details_{i}', '') else []
            } for i in range(12) if request.POST.get(f'exp_title_{i}', '')
        ]
        projects = [
            {
                'title': request.POST.get(f'proj_title_{i}', ''),
                'url': request.POST.get(f'proj_url_{i}', ''),
                'description': request.POST.get(f'proj_description_{i}', ''),
                'technologies': request.POST.get(f'proj_technologies_{i}', '').split(', ') if request.POST.get(f'proj_technologies_{i}', '') else []
            } for i in range(12) if request.POST.get(f'proj_title_{i}', '')
        ]
        skills = [
            {
                'category': request.POST.get(f'skill_category_{i}', ''),
                'items': request.POST.get(f'skill_items_{i}', '').split(', ') if request.POST.get(f'skill_items_{i}', '') else []
            } for i in range(12) if request.POST.get(f'skill_category_{i}', '')
        ]
        languages = request.POST.get('languages', '').split(', ') if request.POST.get('languages', '') else []

        # Update resume fields
        resume.full_name = request.POST['full_name']
        resume.email = request.POST['email']
        resume.phone = request.POST['phone']
        resume.location = request.POST.get('location', '')
        resume.github_url = request.POST.get('github_url', '')
        resume.linkedin_url = request.POST.get('linkedin_url', '')
        resume.summary = request.POST['summary']
        resume.education = education
        resume.experience = experience
        resume.projects = projects
        resume.skills = skills
        resume.languages = languages
        resume.save()
        
        return redirect('resume_list', pk=request.user.id)
    
    return render(request, 'editresume.html', {
        'resume': resume,
        'template': resume.template
    })    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
from django.shortcuts import render
import spacy
import PyPDF2

# Load Spacy model (large for max accuracy)
try:
    nlp = spacy.load('en_core_web_lg')
except OSError:
    raise Exception("Spacy model 'en_core_web_lg' not found. Run: python -m spacy download en_core_web_lg")

def ats_score_checker(jobname, resume):
    """
    Calculate ATS score with improved accuracy and slightly higher scoring.
    Args:
        jobname (str): Job description text.
        resume (str): Resume text.
    Returns:
        tuple: (score (float), details (dict)) - ATS score (0-100) and scoring details.
    """
    try:
        # Expanded technical terms for better matching
        technical_terms = {
            'programming': [
                'python', 'java', 'javascript', 'js', 'c++', 'cpp', 'c#', 'csharp', 'php', 'ruby', 'swift', 'kotlin',
                'typescript', 'ts', 'go', 'golang', 'rust', 'scala', 'perl', 'shell', 'bash', 'powershell', 'html',
                'css', 'sass', 'less', 'sql', 'nosql', 'graphql', 'rest', 'restful', 'soap', 'api', 'programming',
                'coding', 'dev', 'development', 'developer', 'software', 'web', 'mobile', 'app', 'backend', 'frontend'
            ],
            'frameworks': [
                'django', 'flask', 'react', 'angular', 'vue', 'vuejs', 'spring', 'laravel', 'express', 'node',
                'nodejs', 'next', 'nextjs', 'nuxt', 'nuxtjs', 'fastapi', 'rails', 'asp', 'dotnet', 'tensorflow',
                'pytorch', 'scikit', 'sklearn', 'keras', 'hadoop', 'spark', 'framework', 'lib', 'library', 'tool'
            ],
            'databases': [
                'sql', 'mysql', 'postgres', 'postgresql', 'mongo', 'mongodb', 'redis', 'oracle', 'sqlite', 'elastic',
                'elasticsearch', 'cassandra', 'dynamodb', 'neo4j', 'firebase', 'bigquery', 'db', 'database', 'data',
                'storage', 'query', 'rdbms'
            ],
            'tools': [
                'git', 'docker', 'k8s', 'kubernetes', 'aws', 'azure', 'gcp', 'google cloud', 'jenkins', 'jira',
                'github', 'gitlab', 'bitbucket', 'confluence', 'slack', 'trello', 'postman', 'swagger', 'sonar',
                'sonarqube', 'splunk', 'grafana', 'prometheus', 'tool', 'system', 'platform', 'ci', 'cd'
            ],
            'methodologies': [
                'agile', 'scrum', 'kanban', 'waterfall', 'devops', 'ci/cd', 'cicd', 'tdd', 'bdd', 'microservices',
                'rest', 'api', 'cloud', 'saas', 'paas', 'iaas', 'ml', 'machine learning', 'ai', 'artificial intelligence',
                'data science', 'big data', 'blockchain', 'method', 'process', 'practice', 'workflow'
            ],
            'soft_skills': [
                'lead', 'leadership', 'comm', 'communication', 'team', 'teamwork', 'problem', 'solving', 'analytical',
                'manage', 'management', 'mentor', 'present', 'presentation', 'negotiation', 'time', 'adapt', 'adaptability',
                'create', 'creativity', 'think', 'thinking', 'skill', 'exp', 'experience', 'know', 'knowledge'
            ]
        }

        experience_levels = {
            'entry': ['entry', 'jr', 'junior', 'assoc', 'associate', 'fresh', 'fresher', 'grad', 'graduate', 'intern',
                      'trainee', 'begin', 'beginner', 'new', 'starter'],
            'mid': ['mid', 'inter', 'intermediate', 'exp', 'experienced', 'prof', 'professional', 'spec', 'specialist',
                    'expert', 'skill', 'skilled'],
            'senior': ['sr', 'senior', 'lead', 'principal', 'arch', 'architect', 'consult', 'consultant', 'strat',
                       'strategist', 'adv', 'advanced'],
            'management': ['mgr', 'manager', 'dir', 'director', 'head', 'chief', 'vp', 'cto', 'cio', 'ceo', 'sup',
                           'supervisor', 'coord', 'coordinator']
        }

        education_levels = {
            'bachelor': ['bachelor', 'bsc', 'ba', 'bs', 'undergrad', 'degree', 'college', 'univ', 'university', 'grad'],
            'master': ['master', 'msc', 'ma', 'ms', 'mba', 'mca', 'grad', 'postgrad', 'postgraduate'],
            'phd': ['phd', 'doctor', 'doctorate', 'doctoral', 'dr']
        }

        # Preprocess text (keep hyphens/slashes for technical terms)
        def preprocess_text(text):
            text = text.lower()
            text = ''.join(c for c in text if c.isalnum() or c in ' -/')
            return text

        job_text = preprocess_text(jobname)
        resume_text = preprocess_text(resume)

        job_doc = nlp(job_text)
        resume_doc = nlp(resume_text)

        # 1. Technical Skills Matching (55% weight) - Slightly higher weight
        job_skills = set()
        resume_skills = set()
        for category, terms in technical_terms.items():
            for term in terms:
                if term in job_text or any(term in token.text for token in job_doc):
                    job_skills.add(term)
                if term in resume_text or any(term in token.text for token in resume_doc):
                    resume_skills.add(term)
        
        # Add noun chunks for skills
        for doc in [job_doc, resume_doc]:
            for chunk in doc.noun_chunks:
                chunk_text = chunk.text.strip()
                if len(chunk_text) > 2 and any(t in chunk_text for t in technical_terms.keys()):
                    if doc == job_doc:
                        job_skills.add(chunk_text)
                    else:
                        resume_skills.add(chunk_text)

        common_skills = job_skills.intersection(resume_skills)
        skills_score = (len(common_skills) / max(len(job_skills), 1)) * 55  # Boosted from 50 to 55
        missing_skills = job_skills - resume_skills

        # 2. Experience Level Matching (20% weight) - Unchanged
        job_level = set()
        resume_level = set()
        for level, terms in experience_levels.items():
            for term in terms:
                if term in job_text:
                    job_level.add(level)
                if term in resume_text:
                    resume_level.add(level)
        common_levels = job_level.intersection(resume_level)
        exp_match_score = (len(common_levels) / max(len(job_level), 1)) * 20 if job_level else 0

        # 3. Education Level Matching (15% weight) - Unchanged
        job_edu = set()
        resume_edu = set()
        for level, terms in education_levels.items():
            for term in terms:
                if term in job_text:
                    job_edu.add(level)
                if term in resume_text:
                    resume_edu.add(level)
        common_edu = job_edu.intersection(resume_edu)
        edu_match_score = (len(common_edu) / max(len(job_edu), 1)) * 15 if job_edu else 0

        # 4. Keyword Matching (5% weight) - Reduced to give more to skills
        job_keywords = {token.text for token in job_doc if token.is_alpha and len(token.text) > 2}
        resume_keywords = {token.text for token in resume_doc if token.is_alpha and len(token.text) > 2}
        common_keywords = job_keywords.intersection(resume_keywords)
        keyword_score = (len(common_keywords) / max(len(job_keywords), 1)) * 5  # Reduced from 10 to 5

        # 5. Semantic Similarity (5% weight) - Unchanged
        similarity_score = resume_doc.similarity(job_doc) * 5

        # Total score with higher boost for partial matches
        total_score = skills_score + exp_match_score + edu_match_score + keyword_score + similarity_score
        if common_skills or common_levels or common_edu or common_keywords:
            total_score = max(total_score, 40)  # Raised from 30 to 40 for any match
        total_score = min(total_score, 100)

        # Detailed output
        details = {
            'skills_score': round(skills_score, 2),
            'exp_match_score': round(exp_match_score, 2),
            'edu_match_score': round(edu_match_score, 2),
            'keyword_score': round(keyword_score, 2),
            'similarity_score': round(similarity_score, 2),
            'total_score': round(total_score, 2),
            'common_skills': list(common_skills),
            'missing_skills': list(missing_skills),
            'common_keywords': list(common_keywords)
        }
        print("Scoring Details:", details)

        return details['total_score'], details
    except Exception as e:
        print(f"Error in ATS scoring: {str(e)}")
        return 0.0, {'error': str(e)}

def extract_text_from_pdf(pdf_file):
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = "".join(page.extract_text() or "" for page in reader.pages)
        return text.strip() if text.strip() else ""
    except Exception as e:
        print(f"PDF extraction failed: {e}")
        return ""

def index(request,):
    if request.method == 'POST':
        resume_input = request.POST.get('resume_text', '').strip()
        job_desc = request.POST.get('job_desc', '').strip()
        resume_file = request.FILES.get('resume_file')

        # Handle resume input (file or text)
        if resume_file:
            try:
                if resume_file.name.endswith('.pdf'):
                    resume_text = extract_text_from_pdf(resume_file)
                elif resume_file.name.endswith('.txt'):
                    resume_text = resume_file.read().decode('utf-8').strip()
                else:
                    return render(request, 'input.html', {'error': 'Unsupported file type (PDF or TXT only)',})
            except Exception as e:
                return render(request, 'input.html', {'error': f'Error reading file: {str(e)}',})
        else:
            resume_text = resume_input

        if not resume_text:
            return render(request, 'input.html', {'error': 'Resume text or file is required'})
        if not job_desc:
            return render(request, 'input.html', {'error': 'Job description is required'})

        # Debug info
        print("Resume text:", resume_text[:100] + "..." if len(resume_text) > 100 else resume_text)
        print("Job description:", job_desc[:100] + "..." if len(job_desc) > 100 else job_desc)

        # Calculate score
        score, details = ats_score_checker(job_desc, resume_text)

        return render(request, 'result.html', {
            'score': score,
            'resume_text': resume_text,
            'job_desc': job_desc,
            'common_skills': details['common_skills'],
            'missing_skills': details['missing_skills'],
            'common_keywords': details['common_keywords']
        })
    return render(request, 'input.html', {'error': None})
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    














    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    












