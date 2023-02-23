import re
import folium

from argparse import ArgumentParser
from pathlib import Path
from ticklist_mapper.mountainproject import get_route_info


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    with open(args.filename, "r") as f:
        climbs = f.readlines()

    output_filepath = str(Path("docs") / Path(Path(args.filename).stem + ".html"))

    m = folium.Map(location=[37.3352, -118.49894], zoom_start=12)

    all_routes = {}
    for i, climb in enumerate(climbs):
        route = get_route_info(f"{climb} bishop")
        print(i, route)

        # Group routes if they're on the same boulder
        key = str(route.coordinates)
        if all_routes.get(key):
            all_routes[key].append(route)
        else:
            all_routes[key] = [route]

    for coordinates, routes in all_routes.items():
        max_grade = 0
        tooltip = ""
        popup = f"{routes[0].area}<br><br>"
        for route in routes:
            text = f"{route.grade}, {route.name}<br>"
            tooltip += text
            popup += f"<a href={route.url} target='_blank'>{text}</a><br>"

            matches = re.search(r"v([0-9]+)", route.grade.lower())
            if matches and (grade := int(matches.group(1))) > max_grade:
                max_grade = grade

        # Show a different marker colour based on the boulder's max grade
        if max_grade <= 3:
            color = "green"
        elif max_grade <= 6:
            color = "blue"
        elif max_grade <= 9:
            color = "orange"
        else:
            color = "red"

        # Show a different icon if there are multiple routes on the boulder
        # https://fontawesome.com/v3/icons/
        if len(routes) > 1:
            icon = "plus-sign"
        else:
            icon = "info-sign"

        # https://python-visualization.github.io/folium/modules.html?highlight=marker#folium.map.Icon
        folium.Marker(
            eval(coordinates),
            popup=popup,
            tooltip=tooltip,
            icon=folium.Icon(color=color, icon=icon),
        ).add_to(m)

    m.save(output_filepath)
    print(f"Saved to {output_filepath}")
