from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns =[
    path("", views.index, name='index'),
      path("login", views.user_login, name='login'),
        path("signup", views.user_signup, name='signup'),
        path("logout/", views.user_signout, name='signout'),
        path('generate-blog/', views.generate_blog, name="generate_blog"),
        path('public/', views.public_page, name='public_page'),
        path('blogs/', views.my_blogs, name='my_blogs'),
        path("blogs/<int:blog_id>/", views.blog_detail, name="blog_detail"),
        path("blogs/<int:blog_id>/edit/", views.edit_blog, name="edit_blog"),
        path('profile/', views.profile, name="profile"),
        path("profile/<int:user_id>/edit/", views.edit_profile, name="edit_profile"),
        
]
