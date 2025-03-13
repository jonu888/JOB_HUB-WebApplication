from django.db import models
from django.contrib.auth.models import User

class HRUser(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    company_name = models.CharField(max_length=100)
    industry = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    class Meta:
        verbose_name = "HR"
        verbose_name_plural = "HRs"

class JobUser(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    EDUCATION_CHOICES = [
        ('HS', 'High School'),
        ('BA', 'Bachelors'),
        ('MA', 'Masters'),
    ]
    education = models.CharField(max_length=3, choices=EDUCATION_CHOICES)

    EXPERIENCE_CHOICES = [
        ('JR', 'Junior'),
        ('FR', 'Fresher'),
        ('IN', 'Intern'),
        ('SR', 'Senior'),
    ]
    experience = models.CharField(max_length=3, choices=EXPERIENCE_CHOICES)

    skills = models.CharField(max_length=255, help_text="Enter skills separated by commas")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Jobs(models.Model):
    job_name = models.CharField(max_length=100) 
    company_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    
    EXPERIENCE_CHOICES = [
        ('JR', 'Junior'),
        ('FR', 'Fresher'),
        ('IN', 'Intern'),
        ('SR', 'Senior'),
    ]
    exp = models.CharField(max_length=3, choices=EXPERIENCE_CHOICES)
    salary_package = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    requirements = models.CharField(max_length=200)
    hr_id = models.ForeignKey(HRUser, on_delete=models.CASCADE, null=True, related_name="HR")

class Candidate(models.Model):
    job = models.ForeignKey(Jobs, on_delete=models.CASCADE, related_name="job_candidates")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_candidates")
    no = models.ForeignKey(JobUser, on_delete=models.CASCADE, related_name="jobuser_candidates", null=True)
    hr_id = models.ForeignKey(HRUser, on_delete=models.CASCADE, related_name="hr_candidates", null=True)
    is_applied = models.BooleanField(default=False)
    email = models.EmailField(max_length=100, null=True)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True) 
    ats_score = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Candidate {self.user.first_name} for {self.job.job_name}"

class Resume(models.Model):
    TEMPLATE_CHOICES = [
        ('elegant', 'Elegant'),
        ('professional', 'Professional'),
        ('modern', 'Modern'),
    ]

    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    location = models.CharField(max_length=100, blank=True, help_text="e.g., Kochi, Kerala")
    github_url = models.URLField(blank=True, null=True, help_text="Link to GitHub profile")
    linkedin_url = models.URLField(blank=True, null=True, help_text="Link to LinkedIn profile")
    summary = models.TextField(help_text="A brief professional summary")
    education = models.JSONField(default=list, help_text="List of education entries: {'degree': '', 'institution': '', 'dates': '', 'cgpa': ''}")
    experience = models.JSONField(default=list, help_text="List of experience entries: {'title': '', 'company': '', 'dates': '', 'details': []}")
    projects = models.JSONField(default=list, help_text="List of project entries: {'title': '', 'url': '', 'description': '', 'technologies': []}")
    skills = models.JSONField(default=list, help_text="List of skill categories: {'category': '', 'items': []}")
    languages = models.JSONField(default=list, help_text="List of languages: ['English', 'Malayalam']")
    template = models.CharField(max_length=20, choices=TEMPLATE_CHOICES, default='modern')
    userid = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_resumes", null=True)

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Resume"
        verbose_name_plural = "Resumes"
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        



      
    



