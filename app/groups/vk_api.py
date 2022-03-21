import asyncio
import os
import aiohttp
import requests
from typing import Tuple, Optional, List, TypedDict


ACCESS_TOKEN = os.environ.get('VK_API_SERVICE_ACCESS_TOKEN')
API_VERSION = os.environ.get('API_VERSION')


session = None


async def _init_session():
    global session
    if not session:
        print('Creating new aiohttp session...', flush=True)
        loop = asyncio.get_running_loop()
        connector = aiohttp.TCPConnector(limit=4)
        timeout = aiohttp.ClientTimeout(total=3)
        session = aiohttp.ClientSession(timeout=timeout, connector=connector, loop=loop)


class GroupApiResponse(TypedDict):
    id: int
    name: str
    members_count: int


async def fetch_group_info(group_id: int, access_token: str = ACCESS_TOKEN, api_version: str = "5.131") -> Tuple[Optional[int], Optional[GroupApiResponse]]:
    """Call VK API at https://api.vk.com/method/groups.getById for single group_id

    :param group_id: Integer VK group id (not the name from URL)
    :type group_id: int
    :param access_token: VK app service access token
    :type access_token: str
    :params api_version: VK API version
    :type api_version: str
    :returns: a tuple (error_code, response_data) where error_code is None if the request was successful
    :rtype: tuple
    """

    if not isinstance(group_id, int):
        raise TypeError('group_id must be an integer')

    params = {
        'access_token': access_token,
        'group_id': group_id,
        'fields': 'members_count',
        'v': api_version
    }

    await _init_session()

    async with session.get('https://api.vk.com/method/groups.getById', params=params) as response:
        response_data = await response.json()

        if 'error' in response_data or 'response' not in response_data:
            error_code = response_data.get('error', -1)
            return error_code, None

        response_data = response_data['response']
        return None, response_data[0]


def fetch_members_count_info(group_ids: List[int], access_token: str = ACCESS_TOKEN, api_version: str = '5.131') -> List[Tuple[int, int]]:
    """Fetch members count for multiple group (max 500)

    :param group_ids: list of VK group ids
    :type group_ids: list of integers
    :param access_token: VK app service access token
    :type access_token: str
    :params api_version: VK API version
    :type api_version: str
    :returns: list of tuples (error_code, response_data) where error_code is None if the request was successful
    :rtype: tuple
    """

    if not isinstance(group_ids, list):
        raise TypeError('group_ids must be a list of integers')

    if len(group_ids) > 500:
        raise TypeError("group_ids length must be not greater than 500")

    if len(group_ids) == 0:
        return []  # endpoint would return error when group_ids is blank

    params = {
        'access_token': access_token,
        'group_ids': ','.join(map(str, group_ids)),
        'fields': 'members_count',
        'v': api_version
    }

    response = requests.get('https://api.vk.com/method/groups.getById', params=params)
    response_data = response.json()

    if 'error' in response_data or 'response' not in response_data:
        raise KeyError('VK API response error')

    response_data = response_data['response']
    return [(group_info['id'], group_info.get('members_count', None)) for group_info in response_data]
