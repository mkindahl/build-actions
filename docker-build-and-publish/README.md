# Action for building and publishing Docker image

This action is based on the existing Docker image building that we
already use.

There are already actions available for building and publishing docker
images under https://github.com/docker/build-push-action and we might
transition to them over time.

## Inputs

### `postgresql_version`

PostgreSQL version that will be used to create the Docker image. Required.

### `tags`

Tags to use for the docker image when published, for example
`timescale/timescaledb:nightly-pg12`. Required.

### `platform`

Platform for the docker image, for example `linux/amd64`.

## Examples

### Building and publishing a nightly Docker image

To build and publish the nightly Docker image, we could use this job definition

```yaml
  timescaledb:
    name: PG${{ matrix.pg_ver }}
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        pg_ver: [12, 13 ]

    steps:
    - uses: actions/checkout@v2
    - name: Set up Docker Buildx
      id: buildx
      uses: docker/setup-buildx-action@v1
    - name: Login to Docker Hub
      uses: docker/login-action@v1
      with:
        username: ${{ secrets.DOCKERHUB_USER }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}
    - name: Build and push nightly Docker image for TimescaleDB
	  uses: timescale/build-actions/docker-build-and-publish
	  with:
          previous_timescaledb_version: 2.3.0
          timescaledb_version: 2.3.1
		  postgresql_version: ${{ matrix.pg_version }}
		  platform: linux/amd64
		  push: true
		  tags: timescaledev/timescaledb:nightly-pg${{ matrix.pg_version }}
```
