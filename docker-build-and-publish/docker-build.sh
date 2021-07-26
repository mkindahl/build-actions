#!/bin/bash

if [[ -z "$PLATFORM" ]]; then
   echo "PLATFORM not set" 1>&2
   exit 2
fi

if [[ -z "$TAGS" ]]; then
   echo "TAGS not set" 1>&2
   exit 2
else
    TAGS_FLAG="--tag=$TAGS"
fi

if [[ $PUSH = true ]]; then
    PUSH_FLAG=--push
else
    PUSH_FLAG=--load
fi

name=$(docker buildx create --platform $PLATFORM --use)
docker buildx inspect $name --bootstrap
docker buildx build --platform $PLATFORM --build-arg PG_VERSION=$PG_VERSION $TAGS_FLAG $PUSH_FLAG .
docker buildx rm $name
