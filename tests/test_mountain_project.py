import ticklist_mapper.mountainproject as mp


def test_get_route():
    route = mp.get_route_info("gription moe's valley")

    assert route is not None
    assert route.name == "Gription"
    assert route.grade == "V9"
    assert route.area == "Monkey Boy Area"
    assert route.url is not None
    assert route.area_url is not None
    assert isinstance(route.dict(), dict)
