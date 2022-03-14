import json
import aioredis
import traceback

from asgiref.sync import sync_to_async

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.conf import settings
from django.core import serializers
from django.forms.models import model_to_dict

from groups.vk_api import fetch_group_info
from groups.models import Group

from .utils import get_group_from_db, create_group_from_api_response


@sync_to_async
def index_groups(req: HttpRequest) -> JsonResponse:
    """Return all group ids"""

    groups = Group.objects.all()
    groups = [model_to_dict(group) for group in groups]
    data = {"groups": groups}
    return JsonResponse(data)


async def get_group_info(req: HttpRequest, group_id: int) -> HttpResponse:
    """Return information about single group"""

    cache: aioredis.Redis = await aioredis.from_url(settings.REDIS_CACHE_URL, max_connections=1)

    try:
        cached_group_info = await cache.get(Group.get_cache_key(group_id))

        if cached_group_info:
            return HttpResponse(cached_group_info, content_type="application/json; charset=utf-8")  # no need to do json.loads

        group = await get_group_from_db(group_id)

        if not group:
            (error_code, api_response) = await fetch_group_info(group_id)

            if error_code is not None:
                return HttpResponse(f"API responded with {error_code} error_code", status=422)

            group = await create_group_from_api_response(api_response)

        await cache.set(Group.get_cache_key(group.group_id), json.dumps(group.cache_info))

        return JsonResponse(group.cache_info)
    except Exception as error:
        print(error)
        print(traceback.format_exc())

        return HttpResponse("Internal server error/problems with connection/API is not responding", status=500)
    finally:
        await cache.close()
