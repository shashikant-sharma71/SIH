from django import forms
from django.contrib.auth.models import User
from .models import Student, Faculty, AttendanceRecord,Subject 


# =======================================1. Student Registration Form =================================


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [ 'first_name', 'last_name', 'email', 'roll_no', 'course', 'class_name', 'avatar']
        widgets = {
                'first_name': forms.TextInput(attrs={'class': 'form-control'}),
                'last_name': forms.TextInput(attrs={'class': 'form-control'}),
                'email': forms.EmailInput(attrs={'class': 'form-control'}),
                'roll_no': forms.TextInput(attrs={'class': 'form-control'}),
                'course': forms.TextInput(attrs={'class': 'form-control'}),
                'class_name': forms.TextInput(attrs={'class': 'form-control'}),
                'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
}

#============================================== 2. Faculty Registration Form =========================================

class FacultyForm(forms.ModelForm):
    class Meta:
        model = Faculty
        fields = ['avatar', 'first_name', 'last_name', 'username', 'email', 'department']
        
#============================================================== 3. Subject Form =============================================================

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['course_name', 'course_code', 'short_name', 'faculty', 'academic_year', 'semester', 'student_class']

# ================================================== 4. Attendance Form =======================================================
from django import forms
from .models import Subject, Student

class AttendanceForm(forms.Form):
    subject = forms.ModelChoiceField(queryset=Subject.objects.all(), label="Select Subject")
    date = forms.DateField(widget=forms.SelectDateWidget, label="Select Date")
    students = forms.ModelMultipleChoiceField(
        queryset=Student.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Select Students Present"
    )



# forms.py

from django import forms
from .models import Attendance, Subject
from django.contrib.auth.models import User

class MarkAttendanceForm(forms.Form):
    date = forms.DateField(widget=forms.SelectDateWidget())
    subject = forms.ModelChoiceField(queryset=Subject.objects.all(), empty_label="Select Subject")
    students = forms.ModelMultipleChoiceField(queryset=User.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)

    def save(self, faculty, *args, **kwargs):
        subject = self.cleaned_data['subject']
        date = self.cleaned_data['date']
        students = self.cleaned_data['students']
        for student in students:
            attendance, created = Attendance.objects.get_or_create(
                student=student,
                subject=subject,
                date=date,
                defaults={'status': True}  # Mark as present by default
            )
        return students