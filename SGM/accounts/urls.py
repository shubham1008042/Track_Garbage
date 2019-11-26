from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.Signup.as_view(), name='signup'),
    path('activate/<str:uid>/<str:token>', views.Activate.as_view(), name='activate'),
]
