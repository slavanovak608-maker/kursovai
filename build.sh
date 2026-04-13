д хаб #!/usr/bin/env bash
# Сборка на Render (Linux). Локально на Windows не запускайте — используйте команды вручную.
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput
