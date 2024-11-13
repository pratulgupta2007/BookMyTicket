set url_var=0
docker-compose up -d --build
docker-compose exec web python manage.py migrate --noinput
set url_var=1
docker-compose up -d --build
docker-compose exec web python manage.py migrate --noinput
py ticketbooking/manage.py runserver 7000