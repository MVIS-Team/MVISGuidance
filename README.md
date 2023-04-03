# MVISGuidance

## Usage

### Administration

#### Set user(s) as teacher

1. Login to Django's administration page.
2. Select `Authentication and Authorization` › `Users`.
3. Select users using checkbox.
4. Select Action `Set user as teacher`.
5. Click `Go`.

## Deployment

### Installation

1. Clone the repository

   ```bash
   git clone https://github.com/MVISGuidance/production MVISGuidance
   cd MVISGuidance/
   ```

2. Setup environment variables (`.env`) if necessary.

   ```bash
   DJANGO_SETTINGS_MODULE = "main.setting.production"
   DJANGO_SECRET_KEY = "<django secret key>"
   DJANGO_HOSTNAME = "<deployment url>"
   EMAIL_HOST = "<email host>"
   EMAIL_HOST_USER = "<username for email host>"
   EMAIL_HOST_PASSWORD = "<password for email host>"
   ```

3. Setup and activate virtual environment with [`virtualenv`](https://virtualenv.pypa.io/en/latest/).

   ```bash
   python -m virtualenv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. Setup Django

   ```bash
   python manage.py collectstatic
   python manage.py migrate
   ```

5. Setup gunicorn service (`/etc/systemd/system/MVISGuidance.service`).

   ```text
   [Unit]
   Description=gunicorn daemon
   After=network.target


   [Service]
   User=root
   Group=www-data
   WorkingDirectory=<path to project>/backend
   ExecStart=<path to project>/venv/bin/gunicorn \
             --access-logfile - \
             --workers 3 \
             --bind unix:/run/MVISGuidance.sock \
             main.wsgi:application

   [Install]
   WantedBy=multi-user.target
   ```

6. Setup gunicorn socket (`/etc/systemd/system/MVISGuidance.socket`).

   ```text
    [Unit]
    Description=gunicorn socket

    [Socket]
    ListenStream=/run/MVISGuidance.sock

    [Install]
    WantedBy=sockets.target
   ```

7. Enable the gunicorn and check its status.

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl start MVISGuidance
   sudo systemctl enable MVISGuidance
   sudo systemctl status MVISGuidance
   ```

8. Setup nginx (`/etc/nginx/sites-available/MVISGuidance`).

   ```nginx
   server {
       listen 80;
       server_name '<server's IP address>';

       location = /favicon.ico { access_log off; log_not_found off; }
       location /static/ {
           root /var/www/MVISGuidance;
       }
       location /media/ {
           root /var/www/MVISGuidance;
       }

       location / {
           include proxy_params;
           proxy_pass http://unix:/run/MVISGuidance.sock;
       }
   }
   ```

9. Enable nginx and check status.

   ```bash
   sudo ln -s /etc/nginx/sites-available/MVISGuidance /etc/nginx/sites-enabled
   sudo nginx -t
   ```

10. Restart nginx and open up the firewall to normal traffic on port 80

    ```bash
    sudo systemctl restart nginx
    sudo ufw allow 'Nginx Full'
    ```

### Update

1. Update packages.

   ```bash
   sudo apt-get update
   sudo apt-get upgrade
   ```

2. Move to the project folder and activate virtual environment.

   ```bash
   cd MVISGuidance/
   source venv/bin/activate
   ```

3. Pull the update.

   ```bash
   git pull https://github.com/MVISGuidance/production
   ```

4. Setup environment variables (`.env`) if necessary.

5. Update requirements and setup django.

   ```bash
   pip install -r requirements.txt
   python backend/manage.py collectstatic
   python backend/manage.py migrate
   ```

6. Restart gunicorn

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl restart MVISGuidance
   ```

### Additional Resources

- <https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-16-04>
- <https://djangocentral.com/deploy-django-with-nginx-gunicorn-postgresql-and-lets-encrypt-ssl-on-ubuntu/>
- <https://www.askpython.com/django/deploying-django-project-on-vps>

## Contributing

See [Contributing Guideline](CONTRIBUTING.md) for more details.
