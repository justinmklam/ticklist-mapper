# import pickle
import re
import statistics
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List

import folium

from ticklist_mapper.mountainproject import Route, get_route_info


def get_climbs(area, climb_list: List[str]) -> List[Route]:
    with ThreadPoolExecutor(max_workers=8) as executor:
        routes = executor.map(
            get_route_info, [f"{climb.strip()} {area}" for climb in climb_list]
        )

    return [route for route in routes if route is not None]


def generate_map(climbs: List[Route]) -> folium.Map:
    # import pickle
    # all_routes = pickle.load(open("bishop.pickle", "rb"))
    # centroid = [37.41588, -118.45133]

    # print("Requesting climbs...")
    # with ThreadPoolExecutor(max_workers=8) as executor:
    #     results = executor.map(
    #         get_route_info, [f"{climb.strip()} {area}" for climb in climbs]
    #     )

    # Find coordinates to center the map at
    all_coords = [[], []]
    all_routes = {}
    for route in climbs:
        print(route)
        # Group routes if they're on the same boulder
        key = str(route.coordinates)
        if all_routes.get(key):
            all_routes[key].append(route)
        else:
            all_routes[key] = [route]

        all_coords[0].append(route.coordinates[0])
        all_coords[1].append(route.coordinates[1])

    # Use median since there might be outliers which we wouldn't want to include in the avg
    centroid = [statistics.median(c) for c in all_coords]

    m = folium.Map(location=centroid, zoom_start=12)

    for coordinates, routes in all_routes.items():
        max_grade = 0
        tooltip = ""
        popup = (
            f"<a href={routes[0].area_url} target='_blank'>{routes[0].area}</a><br><br>"
        )
        for route in routes:
            text = f"{route.grade}, {route.name}<br>"
            tooltip += text
            popup += f"<a href={route.url} target='_blank'>{text}</a> <a href={route.youtube_beta_url} target='_blank'>(beta)</a><br>"

            matches = re.search(r"v([0-9]+)", route.grade.lower())
            if matches and (grade := int(matches.group(1))) > max_grade:
                max_grade = grade

        # Show a different marker colour based on the boulder's max grade
        if max_grade <= 3:
            color = "green"
        elif max_grade <= 5:
            color = "blue"
        elif max_grade <= 8:
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

    return m


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("filename")
    parser.add_argument("area")
    args = parser.parse_args()

    area = args.area

    with open(args.filename, "r") as f:
        climbs = f.readlines()

    output_filepath = str(Path("docs") / Path(Path(args.filename).stem + ".html"))
    routes = get_climbs(area, climbs)
    m = generate_map(args.area, routes)

    m.save(output_filepath)
    print(f"Saved to {output_filepath}")

    # pickle.dump(all_routes, open("bishop.pickle", "wb"))
