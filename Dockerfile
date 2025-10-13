# Note that this image build ok with the AWS Lambda base image as well.
# FROM public.ecr.aws/lambda/python:3.12
FROM amazonlinux:2023

ARG PIP_INDEX_URL
ARG DOCMA_VERSION

COPY dist/docma-${DOCMA_VERSION}.tar.gz /tmp/docma.tar.gz

RUN \
    os=$(uname -s) ; \
    [ "$os" != Linux ] && echo "Unknown O/S: $os" && exit 1 ; \
    arch=$(uname -m) ; \
    case "$arch" in \
        x86_64 | amd64)     dist=linux-amd64 ;; \
        aarch64 | arm64)    dist=linux-arm64 ;; \
        *)  echo "Unkown architecture: $arch"; exit 1 ;; \
    esac ; \
    set -e ; \
    dnf update -y ; \
    dnf install -y python3.12 python3.12-pip pango zip ; \
    duckdb_ver=$(curl -s https://duckdb.org/data/latest_stable_version.txt) ; \
    curl -L -o /tmp/duckdb.zip "https://github.com/duckdb/duckdb/releases/download/v${duckdb_ver}/duckdb_cli-${dist}.zip" ; \
    unzip -d /usr/local/bin /tmp/duckdb.zip duckdb ; \
    python3.12 -m pip install --no-cache-dir '/tmp/docma.tar.gz[duckdb]' ; \
    /bin/rm -f /tmp/docma.tar.gz /tmp/duckdb.zip ; \
    dnf clean all ; \
    /bin/rm -rf /var/cache/dnf /var/cache/yum ; \
    /bin/rm -rf /root/.cache ; \
    docma --version

ENTRYPOINT ["docma"]
WORKDIR /docma
