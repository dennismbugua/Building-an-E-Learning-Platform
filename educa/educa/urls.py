"""educa URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings

# helper function to serve media files with the Django development server during development (that is, when the DEBUG setting is set to True).
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from courses import views


urlpatterns = [
    # Home page
    path('', views.home, name='home'),

    # You are going to use Django's authentication framework for users to authenticate to the e-learning platform. Both instructors and students will be instances of Django's User model, so they will be able to log in to the site using the authentication views of django.contrib.auth.
    path('accounts/login/', auth_views.LoginView.as_view(),
         name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(),
         name='logout'),
    path('accounts/signup/', views.signup, name='signup'),
    path('accounts/profile/', views.profile, name='profile'),
    path('accounts/profile/edit/', views.profile_edit, name='profile_edit'),
    
    # Course management URLs
    path('course/create/', views.course_create, name='course_create'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('course/<int:course_id>/edit/', views.course_edit, name='course_edit'),
    path('course/<int:course_id>/delete/', views.course_delete, name='course_delete'),
    path('course/<int:course_id>/module/add/', views.module_create, name='module_create'),
    
    path('admin/', admin.site.urls),
]


# helper function to serve media files with the Django development server during development (that is, when the DEBUG setting is set to True).
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)


# Remember that the static() helper function is suitable for development but not for production use. Django is very inefficient at serving static files. Never serve your static files with Django in a production environment.
