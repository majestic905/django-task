import pytest
from groups.vk_api import fetch_members_count_info, fetch_group_info


@pytest.mark.asyncio
async def test_fetch_group_info_success():
    (error_code, response_data) = await fetch_group_info(1)
    assert error_code is None
    assert response_data.get('id') == 1
    assert 'name' in response_data
    assert 'members_count' in response_data


@pytest.mark.asyncio
async def test_fetch_group_info_error():
    (error_code, response_data) = await fetch_group_info(-1212327)
    assert error_code is not None
    assert 'error' in response_data


def test_fetch_members_count_info_error_group_ids_not_list():
    with pytest.raises(TypeError):
        response = fetch_members_count_info('foo')


def test_fetch_members_count_info_error_group_ids_len_gt_500():
    with pytest.raises(TypeError):
        group_ids = list(range(501))
        response = fetch_members_count_info(group_ids)


def test_fetch_members_count_info_empty_response_on_empty_group_ids():
    response = fetch_members_count_info([])
    assert len(response) == 0


def test_fetch_members_count_info_empty_success():
    response = fetch_members_count_info([1])
    assert len(response) == 1
    assert response[0][1] > 0
