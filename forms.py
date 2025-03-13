from django import forms
from .models import JobUser, User,Jobs,Candidate,HRUser

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'email']
        widgets = {
            'password': forms.PasswordInput(),
        }

class JobUserForm(forms.ModelForm):
    skills = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'EX:Python,JavaScript'}),
        help_text="Enter skills separated by commas"
    )

    class Meta:
        model = JobUser
        fields = ['first_name', 'last_name', 'education', 'experience', 'skills']

    def clean_skills(self):
        skills = self.cleaned_data['skills']
        return ",".join([skill.strip() for skill in skills.split(',') if skill.strip()])
    
class HrForm(forms.ModelForm):
    class Meta:
        model = HRUser
        fields = ['first_name', 'last_name', 'company_name', 'industry']




class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'input-field', 'placeholder': 'Password'})
    )

class AddjobsForm(forms.ModelForm):
   
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Describe the job responsibilities and requirements'}),
        help_text="Provide detailed information about the job"
    )
    
   
    requirements = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Ex: Python, Django, JavaScript'}),
        help_text="Enter required skills separated by commas"
    )
    
    class Meta:
        model = Jobs
        exclude = ['company_name', 'hr_id']
        fields = ['job_name', 'location', 
                 'description', 'requirements', 'salary_package',]
        widgets = {
            'job_name': forms.TextInput(attrs={'placeholder': 'Enter job title'}),
            'location': forms.TextInput(attrs={'placeholder': 'City, State or Remote'}),
            'salary_package': forms.TextInput(attrs={'placeholder': 'Ex: $50,000-$70,000 or Competitive'}),
        }
    
    def clean_required_skills(self):
        skills = self.cleaned_data['required_skills']
        # Normalize skills format (strip whitespace, convert to lowercase)
        return ",".join([skill.strip() for skill in skills.split(',') if skill.strip()])
    
    
   
    
    
   
