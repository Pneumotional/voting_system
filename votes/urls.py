from django.urls import path
from . import views

urlpatterns = [
    path('', views.vote_page, name='vote_page'),
    path('login/', views.login_view, name='login'),  # Login URL
    path('submit_vote/<int:code_id>/', views.submit_vote, name='submit_vote'),
    path('generate_code/', views.generate_code, name='generate_code'),
    path('results/', views.results_page, name='results_page'),
    path('export/excel/', views.export_to_excel, name='export_to_excel'),
    path('export/pdf/', views.export_to_pdf, name='export_to_pdf'),
    path('export/generated_codes/excel/', views.export_generated_codes_to_excel, name='export_generated_codes_excel'),
    path('export/generated_codes/pdf/', views.export_generated_codes_to_pdf, name='export_generated_codes_pdf'),
]
