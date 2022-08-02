FROM timescaledev/rust-pgx:testing

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get -qy install build-essential python3 lsb-release debhelper-compat

ADD entrypoint.py /entrypoint.py
RUN python3 -m py_compile /entrypoint.py

CMD ["python3", "/entrypoint.py"]
