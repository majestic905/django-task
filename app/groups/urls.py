from django.urls import path
from .views import get_group_info

urlpatterns = [
    path('<int:group_id>', get_group_info, name='get_group_info'),
]
