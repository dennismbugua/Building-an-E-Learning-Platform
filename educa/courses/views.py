from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from .models import Course, Subject, Module
from .forms import CourseForm, ModuleForm, UserProfileForm
from django.db.models import Count

# Create your views here.


def home(request):
    """Home page view"""
    # Get statistics for the home page
    total_courses = Course.objects.count()
    total_subjects = Subject.objects.count()
    total_users = Course.objects.values('owner').distinct().count()
    
    # Get featured courses (latest 6 courses)
    featured_courses = Course.objects.select_related('subject', 'owner').prefetch_related('modules')[:6]
    
    # Get all subjects with course count
    subjects = Subject.objects.annotate(total_courses=Count('courses'))[:8]
    
    context = {
        'total_courses': total_courses,
        'total_subjects': total_subjects,
        'total_users': total_users,
        'featured_courses': featured_courses,
        'subjects': subjects,
    }
    
    return render(request, 'courses/home.html', context)


def signup(request):
    """User signup view"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in after successful registration
            login(request, user)
            messages.success(request, f'Welcome {user.username}! Your account has been created successfully.')
            # Redirect to profile page where they can add courses/subjects
            return redirect('profile')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def profile(request):
    """User profile view"""
    # Get courses created by the user
    created_courses = Course.objects.filter(owner=request.user).select_related('subject').prefetch_related('modules')
    
    # Get all subjects with course count
    subjects = Subject.objects.annotate(total_courses=Count('courses'))
    
    # Get statistics
    total_courses_created = created_courses.count()
    total_modules = sum(course.modules.count() for course in created_courses)
    
    context = {
        'created_courses': created_courses,
        'subjects': subjects,
        'total_courses_created': total_courses_created,
        'total_modules': total_modules,
    }
    
    return render(request, 'courses/profile.html', context)


@login_required
def profile_edit(request):
    """Edit user profile"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'courses/profile_edit.html', {'form': form})


@login_required
def course_create(request):
    """Create a new course"""
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.owner = request.user
            course.save()
            messages.success(request, f'Course "{course.title}" has been created successfully!')
            return redirect('course_detail', course_id=course.id)
    else:
        form = CourseForm()
    
    return render(request, 'courses/course_form.html', {
        'form': form,
        'title': 'Create New Course'
    })


@login_required
def course_edit(request, course_id):
    """Edit an existing course"""
    course = get_object_or_404(Course, id=course_id, owner=request.user)
    
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, f'Course "{course.title}" has been updated successfully!')
            return redirect('course_detail', course_id=course.id)
    else:
        form = CourseForm(instance=course)
    
    return render(request, 'courses/course_form.html', {
        'form': form,
        'course': course,
        'title': f'Edit Course: {course.title}'
    })


@login_required
def course_detail(request, course_id):
    """View course details and modules"""
    course = get_object_or_404(Course, id=course_id, owner=request.user)
    modules = course.modules.all()
    
    return render(request, 'courses/course_detail.html', {
        'course': course,
        'modules': modules
    })


@login_required
def course_delete(request, course_id):
    """Delete a course"""
    course = get_object_or_404(Course, id=course_id, owner=request.user)
    
    if request.method == 'POST':
        course_title = course.title
        course.delete()
        messages.success(request, f'Course "{course_title}" has been deleted.')
        return redirect('profile')
    
    return render(request, 'courses/course_confirm_delete.html', {'course': course})


@login_required
def module_create(request, course_id):
    """Add a module to a course"""
    course = get_object_or_404(Course, id=course_id, owner=request.user)
    
    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.course = course
            module.save()
            messages.success(request, f'Module "{module.title}" has been added to the course!')
            return redirect('course_detail', course_id=course.id)
    else:
        form = ModuleForm()
    
    return render(request, 'courses/module_form.html', {
        'form': form,
        'course': course,
        'title': f'Add Module to {course.title}'
    })
