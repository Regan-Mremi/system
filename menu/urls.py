from django.urls import path
from . import views


urlpatterns = [
    path('', views.menu_view, name='menu'),
    path('order/', views.create_order, name='create_order'),
    path('kitchen/', views.kitchen_view, name='kitchen'),

    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('export/', views.export_excel, name='export_excel'),
    path('reports/', views.reports_page, name='reports_page'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path("chart-data/", views.chart_data, name="chart_data"),
]