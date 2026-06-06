from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("profile/images/", views.manage_profile_images, name="manage_profile_images"),
    path("profile/images/delete/<int:image_id>/", views.delete_profile_image, name="delete_profile_image"),
    path("",views.home, name="home"),
]
