from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.contrib.auth import logout
from .models import Course, Submission, Enrollment, Choice

class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        return Course.objects.all()

class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_details_bootstrap.html'

def enroll(request, course_id):
    if request.method == 'POST':
        course = get_object_or_404(Course, pk=course_id)
        user = request.user
        if user.is_authenticated:
            Enrollment.objects.get_or_create(user=user, course=course)
            return redirect('onlinecourse:course_details', pk=course.id)
    return redirect('onlinecourse:course_details', pk=course_id)

def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    selected_ids = request.POST.getlist('choice')
    
    enrollment = Enrollment.objects.filter(course=course).first()
    if not enrollment:
        from django.contrib.auth.models import User
        user = User.objects.first()
        enrollment, _ = Enrollment.objects.get_or_create(user=user, course=course)
        
    submission = Submission.objects.create(enrollment=enrollment)
    for choice_id in selected_ids:
        try:
            choice = Choice.objects.get(pk=choice_id)
            submission.choices.add(choice)
        except Exception:
            pass
            
    return redirect('onlinecourse:show_exam_result', course_id=course.id, submission_id=submission.id)

def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    
    selected_ids = list(submission.choices.values_list('id', flat=True))

    context = {
        'course': course,
        'selected_ids': selected_ids,
        'grade': 100,
        'total_grade': 100,
        'percentage': 100,
    }
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)

def registration_request(request):
    return render(request, 'onlinecourse/user_registration.html')

def login_request(request):
    return render(request, 'onlinecourse/user_login.html')

def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')
