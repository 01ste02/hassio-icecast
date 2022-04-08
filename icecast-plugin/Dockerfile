FROM alpine:latest
RUN apk add --no-cache icecast ices

COPY ices.xml /ices.xml
COPY icecast.xml /icecast.xml

RUN apk -U add build-base curl cargo portaudio-dev protobuf-dev pwgen \
 && cd /root \
 && curl -LO https://github.com/librespot-org/librespot/archive/refs/tags/v0.3.1.zip \
 && unzip v0.3.1.zip \
 && cd librespot-0.3.1 \
 && cargo build --jobs $(grep -c ^processor /proc/cpuinfo) --release --no-default-features \
 && mv target/release/librespot /usr/local/bin \
 && cd / \
 && apk --purge del curl cargo portaudio-dev protobuf-dev \
 && apk add llvm-libunwind \
 && rm -rf /etc/ssl /var/cache/apk/* /lib/apk/db/* /root/v0.1.3.zip /root/librespot-0.3.1 /root/.cargo \
 && pass=$(pwgen -ns 64 1) \
 && sed "s/thisisnopassword/$pass/g" /ices.xml \
 && sed "s/thisisnopassword/$pass/g" /icecast.xml

ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3
COPY librespot_handler.py /librespot_handler.py

COPY run.sh /run.sh
RUN chmod +x /run.sh

CMD [ "/run.sh" ]

