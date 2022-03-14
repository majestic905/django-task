import pytest
from django.utils import timezone
from groups.tasks import update_groups_members_count
from groups.models import Group
from datetime import datetime, timedelta


@pytest.mark.django_db
def test_update_groups_members_count():
    updated_at = timezone.now() - timedelta(days=365)
    group = Group.objects.create(group_id=1, title="Name", users_count=0, updated_at=updated_at)

    update_groups_members_count(60, 500)
    group.refresh_from_db()

    assert group.users_count > 0
    assert group.updated_at > timezone.now() - timedelta(hours=1)
