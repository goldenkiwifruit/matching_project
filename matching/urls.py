from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_list, name='user_list'),
    path("users/<int:user_id>/", views.user_detail, name="user_detail"),
    path("jobs/", views.job_list, name="job_list"),
    path("jobs/create/", views.create_job, name="create_job"),
    path("jobs/apply/<int:job_id>/", views.apply_job, name="apply_job"),
    path("applications/<int:app_id>/accept/", views.accept_application, name="accept_application"),
    path("jobs/<int:job_id>/", views.job_detail, name="job_detail"),
    path("applications/", views.my_applications, name="my_applications"),
    path("jobs/<int:job_id>/applications/", views.job_applications, name="job_applications"),
    path("contracts/", views.contract_list, name="contract_list"),
    path("chat/<int:contract_id>/", views.contract_chat, name="contract_chat"),
    path("contracts/<int:contract_id>/complete/", views.contract_complete, name="contract_complete"),
    path("contracts/<int:contract_id>/review/",views.create_review,name="create_review"),
    path("users/<int:user_id>/reviews/",views.review_list,name="review_list")
]