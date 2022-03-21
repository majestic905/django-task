from datetime import timedelta, datetime
from django.utils import timezone
from django.db.models import Min
from celery import shared_task
from celery.utils.log import get_task_logger
from .models import Group
from .vk_api import fetch_groups_info


logger = get_task_logger('groups_tasks_logger')


def setup_another_task_chain(minutes: int = 60, max_at_once: int = 500):
    min_updated_at = Group.objects.all().aggregate(Min('updated_at'))['updated_at__min']  # would be None when no groups
    min_updated_at = min_updated_at or datetime.now()
    next_update_at = min_updated_at + timedelta(minutes=minutes)
    update_groups_members_count.apply_async((minutes, max_at_once), eta=next_update_at)
    logger.info(f"update_groups_members_count: set up new task to run at {next_update_at}")


def update_groups_info(groups):
    logger.info(f"update_groups_members_count: updating {len(groups)} groups")

    group_ids = [group.group_id for group in groups]
    groups_info = fetch_groups_info(group_ids)

    for group_info, group in zip(groups_info, groups):
        group.title = group_info['name']
        group.users_count = group_info['members_count']
        group.updated_at = timezone.now()

    Group.objects.bulk_update(groups, ['title', 'users_count', 'updated_at'])


@shared_task
def update_groups_members_count(minutes: int = 60, max_at_once: int = 500):
    """Celery task for updating VK groups members counts

    :param minutes: update groups which were last updated more than last_updated_minutes ago
    :type minutes: int
    :param max_at_once: update not more max_at_once groups at once (but no more than 500)
    :type max_at_once: int
    """

    if max_at_once <= 0:
        raise ValueError("max_at_once must be greater than 0")

    try:
        max_at_once = min(500, max_at_once)
        time_margin = timezone.now() - timedelta(minutes=minutes)
        groups = Group.objects.only('group_id', 'updated_at').filter(updated_at__lte=time_margin)[:max_at_once]

        if len(groups) == 0:
            logger.info(f"update_groups_members_count: no groups to update")
            setup_another_task_chain(minutes=minutes)
            return

        update_groups_info(groups)

        logger.info(f"update_groups_members_count: creating another task")
        update_groups_members_count.delay(minutes, max_at_once)
    except Exception as error:
        logger.info(error)
        logger.info(f"update_groups_members_count: error happened, setting up another task")
        update_groups_members_count.apply_async((minutes, max_at_once), countdown=(minutes * 60))
