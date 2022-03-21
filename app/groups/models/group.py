from django.db import models
from django.utils import timezone
from typing import Tuple


class Group(models.Model):
    group_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=200)
    users_count = models.IntegerField(null=True)
    updated_at = models.DateTimeField(default=timezone.now)

    @staticmethod
    def get_cache_key(group_id: int) -> str:
        return f"group:{group_id}"

    @classmethod
    def create_from_cache_entry(cls, data: dict):
        return Group.objects.create(
            group_id=data['id'],
            title=data['title'],
            users_count=data.get('users_count')
        )

    @property
    def to_cache_entry(self) -> Tuple[str, dict]:
        return (
            f"group:{self.group_id}",
            {
                'id': self.group_id,
                'title': self.title,
                'users_count': self.users_count
            }
        )