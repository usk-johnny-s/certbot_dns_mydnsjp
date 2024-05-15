FROM certbot/certbot:latest

WORKDIR /opt/certbot_dns_mydnsjp

COPY . .
RUN apk add git
RUN pip install -r requirements.txt
RUN pip install .
