FROM python:3.11

WORKDIR /code

COPY . .

RUN chmod +x /code/populate_db.sh
ENTRYPOINT [ "/code/populate_db.sh" ]