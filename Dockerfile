FROM python:3.9-alpine
WORKDIR /app
COPY requirements.txt .
RUN apk add --no-cache --virtual .build-deps build-base \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps build-base
COPY addNew.py createDb.py functions.py main.py /app/
CMD ["python", "main.py"]