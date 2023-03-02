# Ticklist Mapper

Generates an interactive map based on a list of climbs. Useful for figuring out where climbs are relative to each other to make it easier to plan out climbing days during a trip.

Check it out at [ticklistmapper.fly.dev](https://ticklistmapper.fly.dev/)!

## Contributing

### Developing

```sh
# Install dependencies
make install

# Start the local server
make serve
```

Optionally, docker can be used:

```sh
# Build the image
make docker-build

# Run the container
make docker-run

# Start interactive shell
make docker-shell
```

### Deploying

```sh
make deploy
```
