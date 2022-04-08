FROM alpine:latest
RUN apk add --no-cache python3

COPY librespot_handler.py /librespot_handler.py

COPY run.sh /run.sh
RUN chmod +x /run.sh

CMD [ "/run.sh" ]

