FROM python:3.7.3-alpine
ENV DIR /opt/bot/
ENV DEBUG=False \
  BOT_TOKEN=new_token \
  MIN_UPDATE_PERIOD=60 \
  DB_PORT=27017 \
  DB_MAX_POOL_SIZE=300

COPY requirements.txt ${DIR}/requirements.txt
RUN apk add --no-cache openssl build-base git\
  && pip install -r /opt/bot/requirements.txt\
  && apk del build-base git

COPY . ${DIR}
WORKDIR ${DIR}
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["python", "-m", "bot"]