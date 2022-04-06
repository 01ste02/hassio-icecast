FROM alpine:latest
RUN apk add --no-cache icecast2 ices2

RUN apk -U add build-base curl cargo portaudio-dev protobuf-dev \
 && cd /root \
 && curl -LO https://github.com/librespot-org/librespot/archive/refs/tags/v0.3.1.zip \
 && unzip v0.3.1.zip \
 && cd librespot-0.3.1 \
 && cargo build --jobs $(grep -c ^processor /proc/cpuinfo) --release --no-default-features \
 && mv target/release/librespot /usr/local/bin \
 && cd / \
 && apk --purge del curl cargo portaudio-dev protobuf-dev \
 && apk add llvm-libunwind \
 && rm -rf /etc/ssl /var/cache/apk/* /lib/apk/db/* /root/v0.1.3.zip /root/librespot-0.3.1 /root/.cargo

COPY ices.xml
COPY icecast.xml

COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]

