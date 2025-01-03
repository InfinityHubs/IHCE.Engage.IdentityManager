FROM ubuntu:latest
LABEL authors="rajendra"

ENTRYPOINT ["top", "-b"]