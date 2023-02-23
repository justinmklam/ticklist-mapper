# Ticklist Mapper

Generates an interactive map based on a list of climbs. Useful for figuring out where climbs are relative to each other to make it easier to plan out climbing days during a trip.

Uses data from [Mountain Project](https://www.mountainproject.com/).

## Getting Started

```sh
poetry install
```

## Usage

If you have a file named `ticklist.csv` with the following contents:

```
Birthday Direct
Smooth Shrimp
...
Cocktail Sauce
High Plains Drifter
```

Then run the following command to generate a map in the `docs/` directory:

```sh
poetry run python ticklist_mapper/main.py ticklist.csv
```

View the generated page in your web browser:

```sh
open docs/ticklist.html
```
