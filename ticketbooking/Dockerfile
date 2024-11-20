FROM python:3.11.4-slim-buster

WORKDIR /usr/src/ticketbooking

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y netcat

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /usr/src/ticketbooking/entrypoint.sh
RUN chmod +x /usr/src/ticketbooking/entrypoint.sh

COPY . .

CMD ["/usr/src/ticketbooking/entrypoint.sh"]