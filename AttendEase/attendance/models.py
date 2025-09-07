from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save





#======================================= 1. Student Profile ================================================

class Student(models.Model):
    avatar = models.ImageField(upload_to='avatars/students/', default='avatars/students/default.png')
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # 👈 Add this line
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    roll_no = models.CharField(max_length=50, unique=True)
    course = models.CharField(max_length=100)
    class_name = models.CharField(max_length=100, default="Class A")  # Set default value

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    

# ============================================= 2.Faculty Profile =========================================================

class Faculty(models.Model):
    avatar = models.ImageField(upload_to='avatars/faculty/', default='avatars/faculty/default.png')
    first_name = models.CharField(max_length=100, default="FacultyFirst")  # Default value for first_name
    last_name = models.CharField(max_length=100, default="FacultyLast")  # Default value for last_name
    username = models.CharField(max_length=100, unique=True, default="FacultyUsername")  # Default value for username
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

# ====================================================================== 3. Subject ===============================================================================================

class Subject(models.Model):
    course_name = models.CharField(max_length=255)
    course_code = models.CharField(max_length=100)
    short_name = models.CharField(max_length=50)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)  # Ensure Faculty model exists
    academic_year = models.CharField(max_length=20)
    semester = models.CharField(max_length=10)
    student_class = models.CharField(max_length=50)

    def __str__(self):
        return self.course_name



# ======================================================================4. Attendance Record =============================================================================

class AttendanceRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date = models.DateField()
    present = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.student} - {self.subject} - {self.date} - {'Present' if self.present else 'Absent'}"

# ===================================================================User Profile to handle roles   =====================================================================  

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('faculty', 'Faculty'),
        ('student', 'Student'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    
# Auto-create UserProfile When a New User is Created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Default role is student unless changed manually
        UserProfile.objects.create(user=instance, role='student')

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()
    
     

# =========================================  Attendance ============================================

# models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone



class Attendance(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    status = models.BooleanField(default=False)  # True if present, False if absent

    class Meta:
        unique_together = ['student', 'subject', 'date']  # To avoid duplicate entries

    def __str__(self):
        return f"{self.student.username} - {self.subject.name} - {self.date} - {'Present' if self.status else 'Absent'}"
    
    
    
    