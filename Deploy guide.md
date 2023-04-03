# Deploy project in the vps

This file contains of two deploy case
* Deploy to update patch
* Deploy new folder (Just in case & Educational purpose)

## Deploy to update patch

First we will update package in os system after we ssh in the vps
``` bash
$ sudo apt-get update
$ sudo apt-get upgrade
```

Then we will move to the project folder

``` bash
$ cd MVISGuidance/
```
We will pull from the repsitory

``` bash
$ git pull https://github.com/MVISGuidance/production
```

We will restart the gunicorn

``` bash
$ sudo systemctl daemon-reload
$ sudo systemctl restart gunicorn
```
 And all set! Don't remember to check if it is updated!

## Deploy new folder

It is recommended to pull from the existing repository. In this file we will focus on how to set up the vps.

### Diagam of nginx, gunicorn and django
![alt](https://djangocentral.com/media/uploads/django_nginx_gunicorn.png)

### Basic setup

First, it is recommended to use virtual environment. Create it with **virtualenv** and activate it.
``` bash
$ virtualenv env
$ source myprojectenv/bin/activate
```

 Don't forget to:
 * Add **203.170.190.60** in ALLOWED_HOSTS in project setting
 * Collect static content by command: '~/myproject/manage.py collectstatic'
 * Migrate the database
 * change to DEBUG =  False

### Create a Gunicorn system
sudo nano /etc/systemd/system/gunicorn.service
``` bash
$ sudo nano /etc/systemd/system/gunicorn.service
```

Put this in the file
``` text
[Unit]
Description=gunicorn daemon
After=network.target


[Service]
User=root
Group=www-data
WorkingDirectory=/home/myproject
ExecStart=/home/myproject/myprojectenv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/home/myproject/myproject.sock myproject.wsgi:application

[Install]
WantedBy=multi-user.target
```
Don't forget to adapt the path to your project!
Then we will enable the gunicorn and check its status.

``` bash
$ sudo systemctl start gunicorn
$ sudo systemctl enable gunicorn
$ sudo systemctl status gunicorn
```

Next we will configure the nginx part.
``` bash
$ sudo nano /etc/nginx/sites-available/myproject
```

Type in this code:
``` bash
server {
    listen 80;
    server_name '203.170.190.60';

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /home/myproject;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/myproject/myproject.sock;
    }
}
```

We will link it to the sites-enabled directory with this command:
``` bash
$ sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled
```
Also check the status with this command:
``` bash
$ sudo nginx -t
```
Restart the nginx and open up the firewall to normal traffic on port 80
``` bash
$ sudo systemctl restart nginx
$ sudo ufw allow 'Nginx Full'
```
And it is done to deploy the app. Check the ip address to view the result.

If you face any problems, please refer to:
* https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-16-04
* https://djangocentral.com/deploy-django-with-nginx-gunicorn-postgresql-and-lets-encrypt-ssl-on-ubuntu/
* https://www.askpython.com/django/deploying-django-project-on-vps