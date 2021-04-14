# vaccine-appt-alert

## Usage

Here are some example snippets to help you get started creating a container.

### docker-compose

```yaml
---
version: "3"
services:
  code-server:
    image: afeldman1/vaccine-appt-alert
    container_name: vaccine-appt-alert
    environment:
      - SMTP_HOST=smtp.gmail.com
      - SMTP_PORT=587
      - SENDER_USERNAME=
      - SENDER_PASSWORD=
      - RECIPIENTS=
    volumes:
      - /path/to/appdata:/logs
    network_mode: host
    restart: unless-stopped
```

### docker cli

```
docker run -d \
    --name vaccine-appt-alert \
    --network host \
    -e SMTP_HOST=smtp.gmail.com \
    -e SMTP_PORT=587 \
    -e SENDER_USERNAME= \
    -e SENDER_PASSWORD= \
    -e RECIPIENTS= \
    -v /path/to/appdata:/logs \
    --restart unless-stopped \
    afeldman1/vaccine-appt-alert:latest
```


## Parameters

Container images are configured using parameters passed at runtime and environmental variables.

| Parameter | Function |
| :----: | --- |
| `-e SMTP_HOST=smtp.gmail.com` | SMTP server address |
| `-e SMTP_PORT=587` | SMTP server port |
| `-e SENDER_USERNAME=` | Username for SMTP server |
| `-e SENDER_PASSWORD=` | Password for SMTP server |
| `-e RECIPIENTS=` | Comma seperated list of alert email address recipients|
