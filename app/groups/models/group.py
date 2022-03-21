from django.db import models
from django.utils import timezone


class Group(models.Model):
    group_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=200)
    users_count = models.IntegerField(null=True)
    updated_at = models.DateTimeField(default=timezone.now)

    @staticmethod
    def get_cache_key(group_id: int) -> str:
        return f"group:{group_id}"

    @property
    def cache_info(self) -> dict:
        return {
            'id': self.group_id,
            'title': self.title,
            'users_count': self.users_count
        }
