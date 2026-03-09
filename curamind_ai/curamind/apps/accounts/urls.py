from django.urls import path
from . import views

urlpatterns = [
    path('register/',       views.RegisterView.as_view(),          name='register'),
    path('login/',          views.LoginView.as_view(),             name='login'),
    path('logout/',         views.logout_view,                     name='logout'),
    path('password/reset/', views.PasswordResetRequestView.as_view(), name='password_reset'),
    # when the system is offline/maintenance we show a generic notice here
    path('unavailable/',    views.system_unavailable_view,         name='system_unavailable'),
]
