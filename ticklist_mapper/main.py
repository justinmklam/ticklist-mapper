import folium

from argparse import ArgumentParser
from ticklist_mapper.mountainproject import get_route_info


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    with open(args.filename, "r") as f:
        climbs = f.readlines()

    m = folium.Map(location=[37.3352, -118.49894], zoom_start=12)

    for i, climb in enumerate(climbs):
        route = get_route_info(f"{climb} bishop")
        print(i, route)

        tooltip = f"{route.grade}, {route.name}"
        popup = f"{tooltip}<br><a href={route.url} target='_blank'>(MP)</a>"

        folium.Marker(
            route.coordinates, popup=popup, tooltip=tooltip
        ).add_to(m)

        # if i > 2:
        #     break

    m.save("index.html")
