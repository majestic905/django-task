from django.urls import path
from . import views

urlpatterns = [
    path('<int:group_id>', views.get_group_info, name='get_group_info'),
    path('', views.index_groups, name='index_groups'),
]
