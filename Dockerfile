FROM python:3.9.4-alpine3.13

ARG SMTP_HOST_VAR=smtp.gmail.com
ENV SMTP_HOST=$SMTP_HOST_VAR

ARG SMTP_PORT_VAR=587
ENV SMTP_PORT=$SMTP_PORT_VAR

COPY . .

RUN pip install -r requirements.txt

RUN crontab crontab

CMD ["crond", "-f"]