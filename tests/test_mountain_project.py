import pytest

import ticklist_mapper.mountainproject as mp


@pytest.mark.parametrize("query", ["show of hands moe's valley", "evilution bishop"])
def test_get_route(query):
    route = mp.get_route_info(query)
    assert route is not None
    assert route.url is not None
    assert route.area_url is not None
    assert isinstance(route.dict(), dict)
