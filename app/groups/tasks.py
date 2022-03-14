from datetime import timedelta
from django.utils import timezone
from django.db import connection, transaction
from celery import shared_task
from celery.utils.log import get_task_logger
from .models import Group
from .vk_api import fetch_members_count_info


logger = get_task_logger('groups_tasks_logger')


# https://stackoverflow.com/questions/18797608/update-multiple-rows-in-same-query-using-postgresql
def generate_update_sql(member_counts):
    return f"""
    UPDATE groups_group AS u SET -- postgres FTW
      group_id = u2.group_id,
      users_count = u2.users_count,
      updated_at = current_timestamp
    FROM (VALUES
      {','.join([str(item) for item in member_counts])}
    ) AS u2(group_id, users_count)
    where u2.group_id = u.group_id;
    """


@shared_task
def update_groups_members_count(last_updated_minutes: int = 60, max_at_once: int = 500):
    """Celery task for updating VK groups members counts

    :param last_updated_minutes: update groups which were last updated more than last_updated_minutes ago
    :type last_updated_minutes: int
    :param max_at_once: update not more max_at_once groups at once (but no more than 500)
    :type max_at_once: int
    """

    if max_at_once <= 0:
        raise ValueError("max_at_once must be greater than 0")

    max_at_once = min(500, max_at_once)
    last_updated_margin = timezone.now() - timedelta(minutes=last_updated_minutes)
    groups = Group.objects.filter(updated_at__lte=last_updated_margin)[:max_at_once]

    if len(groups) == 0:
        logger.info(f"update_groups_members_count: no groups to update")
        return

    group_ids = [group.group_id for group in groups]
    logger.info(f"update_groups_members_count: updating {len(group_ids)} groups")
    member_counts = fetch_members_count_info(group_ids)

    query = generate_update_sql(member_counts)
    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute(query)

    if len(groups) == max_at_once:  # database can contain more outdated groups, 500 is VK restriction
        logger.info(f"update_groups_members_count: creating another task")
        update_groups_members_count.delay(last_updated_minutes, max_at_once)
