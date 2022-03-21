from asgiref.sync import sync_to_async
from groups.models import Group
from typing import Optional


@sync_to_async
def get_group_from_db(group_id: int) -> Optional[Group]:
    """Async adapter for Group.objects.get"""
    try:
        return Group.objects.get(group_id=group_id)
    except Group.DoesNotExist:
        return None
    except Exception:
        return None
