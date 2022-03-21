from asgiref.sync import sync_to_async
from django.db import IntegrityError
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


@sync_to_async(thread_sensitive=True)
def create_group_from_api_response(api_response: dict) -> Group:
    """Async adapter for Group.objects.create"""
    try:
        return Group.objects.create(
            group_id=api_response['id'],
            title=api_response['name'],
            users_count=api_response.get('members_count', None)
        )
    except IntegrityError:  # was just created in other thread
        return Group.objects.get(group_id=api_response['id'])
    except Group.DoesNotExist:
        return None
    except Exception:
        return None
