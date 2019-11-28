# from django.urls import path,re_path
# from accounts import views as account_views
# from django.views.generic import TemplateView

# urlpatterns = [
#     path('signup/', views.SignUp.as_view(), name='signup'),
#     path('accounts/login/',accounts_views.login,name='login'),
#     path('accounts/logout/', accounts_views.logout,name='logout'),
#     path('accounts/password_change/',accounts_views.password_change,name='password_change'),
#     path('accounts/password_change/done/', accounts_views.password_change_done,name='password_change_done'),
#     path('accounts/password_reset/',accounts_views.password_reset,name='password_reset'),
#     path('accounts/password_reset/done/',accounts_views.password_reset_done,name='password_reset_done'),
#     re_path('accounts/reset/<uidb64>/<token>/',accounts_views.password_reset_confirm,name='password_reset_confirm'),
#     path('accounts/reset/done/', accounts_views.password_reset_complete,name='password_reset_complete'),

# ]

from django.urls import path
from . import views
from django.views.generic.base import TemplateView

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
	path('profile/', TemplateView.as_view(template_name='profile.html'), name='profile'),
]