import json
import aioredis
import traceback

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.conf import settings

from groups.vk_api import fetch_group_info
from groups.models import Group
from groups.tasks import create_group_from_cache_entry

from .utils import get_group_from_db


cache: aioredis.Redis = None


def _init_cache():
    print('Creating new Redis instance...', flush=True)
    global cache
    cache = aioredis.from_url(settings.KEYDB_CACHE_URL)


async def get_group_info(req: HttpRequest, group_id: int) -> HttpResponse:
    """Return information about single group"""

    if not cache:
        _init_cache()

    try:
        cached_group_info = await cache.get(Group.get_cache_key(group_id))

        if cached_group_info:
            return HttpResponse(cached_group_info, content_type="application/json; charset=utf-8")  # no need to do json.loads

        group = await get_group_from_db(group_id)

        if group:
            cache_key, cache_entry = group.to_cache_entry()
        else:
            (error_code, api_response) = await fetch_group_info(group_id)

            if error_code is not None:
                return HttpResponse(f"Bad VK API response, error_code {error_code}", status=422)

            cache_key, cache_entry = api_response.to_cache_entry()
            create_group_from_cache_entry.delay(cache_entry)

        await cache.set(cache_key, json.dumps(cache_entry), ex=60)
        return JsonResponse(cache_entry)
    except Exception as error:
        print(error)
        print(traceback.format_exc())

        return HttpResponse("Internal server error/problems with connection/API is not responding", status=500)
