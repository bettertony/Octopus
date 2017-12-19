FROM debian:8

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

ENV DEBIAN_FRONTEND noninteractive
ENV PIPELINEDB_DATA /var/lib/octopus/data

# ---------------------------------------------------------------------------
# Locales
# ---------------------------------------------------------------------------

RUN apt-get update \
    && apt-get install -y locales \
    && rm -rf /var/lib/apt/lists/* \
    && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8
ENV LANGUAGE en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8

# ---------------------------------------------------------------------------
# Gosu
# ---------------------------------------------------------------------------

ENV GOSU_VERSION 1.9
RUN set -x \
    && apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates wget \
    && rm -rf /var/lib/apt/lists/* \
    && dpkgArch="$(dpkg --print-architecture | awk -F- '{ print $NF }')" \
    && wget -O /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch" \
    && wget -O /usr/local/bin/gosu.asc "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch.asc" \
    && export GNUPGHOME="$(mktemp -d)" \
    && gpg --keyserver ha.pool.sks-keyservers.net --recv-keys B42F6819007F00F88E364FD4036A9C25BF357DD4 \
    && gpg --batch --verify /usr/local/bin/gosu.asc /usr/local/bin/gosu \
    && rm -r "${GNUPGHOME}" /usr/local/bin/gosu.asc \
    && chmod +x /usr/local/bin/gosu \
    && gosu nobody true \
    && apt-get purge -y --auto-remove ca-certificates wget

# ---------------------------------------------------------------------------
# Octopus
# ---------------------------------------------------------------------------

ARG PIPELINEDB_VERSION=
RUN mkdir -p /tmp/octopus \
    && apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates wget \
    && wget -O /tmp/octopus/debian.deb "https://www.octopus.com/download/${PIPELINEDB_VERSION}/debian8" \
    && dpkg --install /tmp/octopus/debian.deb \
    && rm -r /tmp/octopus \
    && apt-get purge -y --auto-remove ca-certificates wget

# ---------------------------------------------------------------------------
# Extras
# ---------------------------------------------------------------------------

ARG WITH_CONTRIB_MODULES=
ENV POSTGRES_CONTRIB_VERSION 9.5.0
RUN test -z "${WITH_CONTRIB_MODULES}" \
    || (set -x \
        && apt-get update \
        && apt-get install -y --no-install-recommends ca-certificates wget build-essential \
        && mkdir -p /tmp/pg_contrib \
        && wget -O - "https://ftp.postgresql.org/pub/source/v${POSTGRES_CONTRIB_VERSION}/postgresql-${POSTGRES_CONTRIB_VERSION}.tar.gz" \
            | tar xzf - -C /tmp/pg_contrib --strip-components=1 \
        && export USE_PGXS=1 \
        && export PG_CONFIG=/usr/lib/octopus/bin/pg_config \
        && for CONTRIB in ${WITH_CONTRIB_MODULES}; do make -C /tmp/pg_contrib/contrib/${CONTRIB} install; done \
        && rm -rf /tmp/pg_contrib \
        && apt-get purge -y --auto-remove ca-certificates wget build-essential)

ARG WITH_CSTORE=
ENV CSTORE_VERSION 1.4.1
RUN test -z "${WITH_CSTORE}" \
    || (set -x \
        && apt-get update \
        && apt-get install -y --no-install-recommends ca-certificates wget build-essential protobuf-c-compiler libprotobuf-c0-dev \
        && mkdir -p /tmp/cstore \
        && wget -O - "https://github.com/citusdata/cstore_fdw/archive/v${CSTORE_VERSION}.tar.gz" \
            | tar xzf - -C /tmp/cstore --strip-components=1 \
        && export PG_CONFIG=/usr/lib/octopus/bin/pg_config \
        && make -C /tmp/cstore \
        && make -C /tmp/cstore install \
        && rm -rf /tmp/cstore \
        && apt-get purge -y --auto-remove ca-certificates wget build-essential)

ARG WITH_KAFKA=
ENV PIPELINEDB_KAFKA_VERSION 0.9.5
ENV RDKAFKA_VERSION 0.9.2
RUN test -z "${WITH_KAFKA}" \
    || (set -x \
        && apt-get update \
        && apt-get install -y --no-install-recommends ca-certificates wget make gcc g++ python \
            protobuf-c-compiler libprotobuf-c0-dev libssl-dev zlib1g-dev \
        && mkdir -p /tmp/octopus_kafka /tmp/rdkafka \
        && wget -O - "https://github.com/edenhill/librdkafka/archive/v${RDKAFKA_VERSION}.tar.gz" \
            | tar xzf - -C /tmp/rdkafka --strip-components=1 \
        && wget -O - "https://github.com/octopus/octopus_kafka/archive/${PIPELINEDB_KAFKA_VERSION}.tar.gz" \
            | tar xzf - -C /tmp/octopus_kafka --strip-components=1 \
        && export PG_CONFIG=/usr/lib/octopus/bin/pg_config \
        && cd /tmp/rdkafka \
        && ./configure --CFLAGS="-fPIC" --prefix=/usr --disable-ssl --disable-sasl \
        && make \
        && make install \
        && cd /tmp/octopus_kafka \
        && ./configure \
        && make \
        && make install \
        && cd / \
        && rm -rf /tmp/rdkafka /tmp/octopus_kafka \
        && apt-get purge -y --auto-remove ca-certificates wget make gcc g++ python)

ARG WITH_KINESIS=
ENV PIPELINEDB_KINESIS_VERSION 0.9.0
ENV AWS_SDK_VERSION 0.10.9
RUN test -z "${WITH_KINESIS}" \
    || (set -x \
        && apt-get update \
        && apt-get install -y --no-install-recommends ca-certificates wget make gcc g++ \
            zlib1g-dev libssl-dev libcurl4-openssl-dev uuid-dev \
        && mkdir -p /tmp/cmake /tmp/aws_sdk /tmp/octopus_kinesis \
        && wget -O - "https://cmake.org/files/v3.7/cmake-3.7.0-Linux-x86_64.tar.gz" \
            | tar xzf - -C /tmp/cmake --strip-components=1 \
        && wget -O - "https://github.com/aws/aws-sdk-cpp/archive/${AWS_SDK_VERSION}.tar.gz" \
            | tar xzf - -C /tmp/aws_sdk --strip-components=1 \
        && wget -O - "https://github.com/octopus/octopus_kinesis/archive/${PIPELINEDB_KINESIS_VERSION}.tar.gz" \
            | tar xzf - -C /tmp/octopus_kinesis --strip-components=1 \
        && mkdir -p /tmp/aws_sdk/build \
        && /tmp/cmake/bin/cmake -B/tmp/aws_sdk/build -H/tmp/aws_sdk/ -DBUILD_ONLY=aws-cpp-sdk-kinesis -DCMAKE_BUILD_TYPE=Release \
        && make -C /tmp/aws_sdk/build \
        && make -C /tmp/aws_sdk/build install \
        && ln -s /usr/local/lib/linux/intel64/Release/libaws-cpp-sdk-core.so /usr/lib/libaws-cpp-sdk-core.so \
        && ln -s /usr/local/lib/linux/intel64/Release/libaws-cpp-sdk-kinesis.so /usr/lib/libaws-cpp-sdk-kinesis.so \
        && ldconfig \
        && make -C /tmp/octopus_kinesis \
        && make -C /tmp/octopus_kinesis install \
        && rm -rf /tmp/cmake /tmp/aws_sdk /tmp/octopus_kinesis \
        && apt-get purge -y --auto-remove ca-certificates wget make gcc g++)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

VOLUME /var/lib/octopus/data
EXPOSE 5432

RUN addgroup --system octopus \
    && adduser \
        --system \
        --no-create-home \
        --disabled-login \
        --ingroup octopus \
        octopus

COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["octopus"]

