from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.forms import modelformset_factory
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .forms import StudentForm, FacultyForm, AttendanceForm, SubjectForm
from .models import Student, Faculty, AttendanceRecord, Subject, Attendance
from .utils import role_required

# Home Page
def index(request):
    return render(request, 'index.html')

#=================================================== Register Student==========================================
def register_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif password != password_confirm:
            messages.error(request, 'Passwords do not match.')
        else:
            try:
                validate_password(password)
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    first_name=request.POST.get('first_name'),
                    last_name=request.POST.get('last_name'),
                    email=request.POST.get('email')
                )
                group, _ = Group.objects.get_or_create(name='Student')
                user.groups.add(group)

                if form.is_valid():
                    student = form.save(commit=False)
                    student.user = user  # 👈 Link user to student here
                    student.save()
                    messages.success(request, 'Student registered successfully.')
                    return redirect('login')
                else:
                    messages.error(request, 'Form validation failed.')
            except ValidationError as e:
                messages.error(request, ' '.join(e.messages))
    else:
        form = StudentForm()

    return render(request, 'register_student.html', {'form': form})

#==================================================================== Register Faculty===================================================================
def register_faculty(request):
    if request.method == 'POST':
        form = FacultyForm(request.POST, request.FILES)
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif password != password_confirm:
            messages.error(request, 'Passwords do not match.')
        else:
            try:
                validate_password(password)
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    first_name=request.POST.get('first_name'),
                    last_name=request.POST.get('last_name'),
                    email=request.POST.get('email')
                )
                group, _ = Group.objects.get_or_create(name='Faculty')
                user.groups.add(group)

                if form.is_valid():
                    faculty = form.save(commit=False)
                    faculty.user = user
                    faculty.save()
                    messages.success(request, 'Faculty registered successfully.')
                    return redirect('login')
                else:
                    messages.error(request, 'Form validation failed.')
            except ValidationError as e:
                messages.error(request, ' '.join(e.messages))
    else:
        form = FacultyForm()

    return render(request, 'register_faculty.html', {'form': form})

#=========================================================================== Register Subject==========================================================
from .models import Faculty  # Make sure this import is correct

def register_subject(request):
    faculties = Faculty.objects.all()

    if request.method == 'POST':
        # Safely get form values with default empty strings
        course_name = request.POST.get('course_name', '').strip()
        course_code = request.POST.get('course_code', '').strip()
        short_name = request.POST.get('short_name', '').strip()
        faculty_id = request.POST.get('faculty', '').strip()
        academic_year = request.POST.get('academic_year', '').strip()
        semester = request.POST.get('semester', '').strip()
        student_class = request.POST.get('student_class', '').strip()

        # Check all required fields
        if not all([course_name, course_code, short_name, faculty_id, academic_year, semester, student_class]):
            messages.error(request, "Please fill in all required fields.")
            return render(request, 'register_subject.html', {'faculties': faculties})

        try:
            faculty = Faculty.objects.get(id=faculty_id)

            Subject.objects.create(
                course_name=course_name,
                course_code=course_code,
                short_name=short_name,
                faculty=faculty,
                academic_year=academic_year,
                semester=semester,
                student_class=student_class
            )

            messages.success(request, "Subject registered successfully!")
            return redirect('register_subject')

        except Faculty.DoesNotExist:
            messages.error(request, "Selected faculty does not exist.")
    
    return render(request, 'register_subject.html', {'faculties': faculties})

# ================================================Success Pages=====================================================
def registration_success(request):
    return render(request, 'registration_success.html')

def attendance_success(request):
    return render(request, 'attendance_success.html')

#======================================================== Login View=========================================================
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            if user.is_staff:
                return redirect('admin_dashboard')
            elif user.groups.filter(name='Faculty').exists():
                return redirect('faculty_dashboard')
            elif user.groups.filter(name='Student').exists():
                return redirect('student_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

# ====================================Logout====================================================
def user_logout(request):
    logout(request)
    return redirect('login')

# =====================================Dashboards===================================================

# -----------------------------------------------Admin Dashboard---------------------------------------------------------
@login_required
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Subject, Faculty, Attendance, Student
from datetime import date
#  ----------------------------------------------------- Faculty Dashboard ------------------------------------------------
@login_required
def faculty_dashboard(request):
    user = request.user
    try:
        faculty = Faculty.objects.get(username=request.user.username)
    except Faculty.DoesNotExist:
        return redirect('login')  # or show error page

    subjects = Subject.objects.filter(faculty=faculty)

    selected_subject_id = request.GET.get('subject')
    selected_date = request.GET.get('date', date.today().strftime('%Y-%m-%d'))
    attendance_data = []

    if selected_subject_id:
        attendance_data = Attendance.objects.filter(
            subject_id=selected_subject_id,
            date=selected_date
        ).select_related('student__user')

    if request.method == 'POST':
        student_ids = request.POST.getlist('student_ids')
        for student_id in student_ids:
            present = f'present_{student_id}' in request.POST
            Attendance.objects.update_or_create(
                student_id=student_id,
                subject_id=selected_subject_id,
                date=selected_date,
                defaults={'present': present}
            )
        return redirect('faculty_dashboard')  # or with GET params to retain view

    context = {
        'subjects': subjects,
        'selected_subject': selected_subject_id,
        'selected_date': selected_date,
        'attendance_data': attendance_data,
    }
    return render(request, 'faculty_dashboard.html', context)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Student, Subject, Attendance
#=---------------------------------------------------------- Student Dashboard-----------------------------------------------------
@login_required
def student_dashboard(request):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return render(request, 'student_not_found.html', status=404)  # 👈 Optional custom 404

    academic_year = request.GET.get('academic_year', '2024-2025')
    semester = request.GET.get('semester', '3')
    class_name = student.class_name

    # Fetch subjects for the class, academic year, and semester
    subjects = Subject.objects.filter(
        academic_year=academic_year,
        semester=semester,
        student_class=class_name
    )

    course_data = []
    for idx, subject in enumerate(subjects, start=1):
        attendance_records = Attendance.objects.filter(student=student, subject=subject)
        delivered = attendance_records.count()
        attended = attendance_records.filter(status='Present').count()
        percent = round((attended / delivered) * 100, 2) if delivered > 0 else 0

        course_data.append({
            "sr_no": idx,
            "course_name": subject.course_name,
            "short_name": subject.short_name,
            "course_code": subject.course_code,
            "attended": attended,
            "delivered": delivered,
            "percent": percent,
        })

    context = {
        "course_data": course_data,
        "academic_year": academic_year,
        "semester": semester,
        "class_name": class_name,
        "student": student,
    }

    return render(request, 'student_dashboard.html', context)



#----------------------------------------------------------------Reporting Dashboard----------------------------------------------------------
def reporting_dashboard(request):
    context = {
        'total_attendance_records': Attendance.objects.count(),
        'total_students': Student.objects.count(),
        'total_subjects': Subject.objects.count(),
        'total_faculties': Faculty.objects.count(),
        'students': Student.objects.all(),
        'subjects': Subject.objects.all(),
        'faculties': Faculty.objects.all()
    }
    return render(request, 'reporting_dashboard.html', context)













# ================================================Mark Attendance========================================================
# views.py

from django.shortcuts import render, redirect
from .models import AttendanceRecord, Student, Subject
from .forms import AttendanceForm  # or a custom formset if needed
from django.contrib import messages
from datetime import date

def mark_attendance(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)

        if form.is_valid():
            # Get the cleaned data
            subject = form.cleaned_data['subject']
            students = form.cleaned_data['students']  # Could be a multiple choice field
            date_selected = form.cleaned_data['date']
            
            for student in students:
                AttendanceRecord.objects.create(
                    student=student,
                    subject=subject,
                    date=date_selected,
                    present=True  # You can toggle based on form input
                )

            messages.success(request, "Attendance marked successfully!")
            return redirect('attendance_success')  # Define this URL in your project

    else:
        form = AttendanceForm()

    return render(request, 'mark_attendance.html', {'form': form})
# =========================================================Edit Attendance===========================================================
@login_required
@role_required(['faculty'])
def edit_attendance(request):
    AttendanceFormSet = modelformset_factory(AttendanceRecord, fields=('present',), extra=0)
    subjects = Subject.objects.filter(faculty__user=request.user)

    selected_subject = request.GET.get('subject')
    selected_date = request.GET.get('date')
    records = AttendanceRecord.objects.none()

    if selected_subject and selected_date:
        records = AttendanceRecord.objects.filter(subject_id=selected_subject, date=selected_date)

    formset = AttendanceFormSet(queryset=records)

    if request.method == 'POST':
        formset = AttendanceFormSet(request.POST, queryset=records)
        if formset.is_valid():
            formset.save()
            return redirect('attendance_success')

    return render(request, 'edit_attendance.html', {
        'formset': formset,
        'subjects': subjects,
        'selected_subject': selected_subject,
        'selected_date': selected_date,
    })



from django.shortcuts import render
from .models import AttendanceRecord, Student
from datetime import date

def daywise_attendance_view(request):
    selected_date = request.GET.get('date')  # Get date from query parameter
    if selected_date:
        attendance_records = AttendanceRecord.objects.filter(date=selected_date)
        student_status = {}

        for student in Student.objects.all():
            record = attendance_records.filter(student=student).first()
            if record:
                student_status[student] = 'Present' if record.present else 'Absent'
            else:
                student_status[student] = 'Absent'  # If no record, assume absent

        context = {
            'student_status': student_status,
            'selected_date': selected_date
        }
    else:
        context = {
            'student_status': {},
            'selected_date': None
        }

    return render(request, 'daywise_attendance.html', context)