import os
import httpx
from typing import Tuple, Optional, List, TypedDict


ACCESS_TOKEN = os.environ.get('VK_API_SERVICE_ACCESS_TOKEN')
API_VERSION = os.environ.get('API_VERSION')


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

    params = {
        'access_token': access_token,
        'group_id': group_id,
        'fields': 'members_count',
        'v': api_version
    }

    async with httpx.AsyncClient() as client:
        response: httpx.Response = await client.get('https://api.vk.com/method/groups.getById', params=params)
        response_data = response.json()

        error_code = response_data['error']['error_code'] if 'error' in response_data else None
        response_data = response_data['response'][0] if error_code is None else response_data

        return (error_code, response_data)


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

    group_ids = [str(item) for item in group_ids]
    group_ids = ','.join(group_ids)

    params = {
        'access_token': access_token,
        'group_ids': group_ids,
        'fields': 'members_count',
        'v': api_version
    }

    response = httpx.get('https://api.vk.com/method/groups.getById', params=params)
    response = response.json()
    response = response['response']
    return [(group_info['id'], group_info.get('members_count')) for group_info in response]
