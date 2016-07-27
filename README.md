# ScriptNet Competitions

[![Build Status](https://travis-ci.org/Transkribus/competitions.svg?branch=master)](https://travis-ci.org/Transkribus/competitions)

The competitions site for the [READ] project, written in [Python] / [Django].

### Requirements, installation & testing
[Python], [Django], [Django-Bootstrap3] and [Django-Tables2] need to be installed.

#### Python and Pip

* Install the latest release of [Python] 3.x.x
* Install [pip]

Follow the instructions on the links above to install on your system. Specifically for Ubuntu Linux, the command-line commands to install Python and Pip are
```sh
apt-get update && apt-get upgrade
apt-get install python3-pip python3-dev build-essential
```

#### Django and plugins 
Install Django and the required plugins with
```sh
pip3 install django django-bootstrap3 django_tables2
```
#### Requirements of optional components

##### Mono
The benchmarks introduced in the ICFHR'14 KWS competition require the [Mono] library to run. In Ubuntu, install it by running the following as a privileged user:
```sh
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF
echo "deb http://download.mono-project.com/repo/debian wheezy main" | tee /etc/apt/sources.list.d/mono-xamarin.list
apt-get update
apt-get install mono-complete
```
Follow the [Mono] installation instructions to install the library in other platforms.

##### p7zip
Private test data / ground-truth can be uploaded in the form of a zipped file. Gzipped tarballs are handled with Python builtins, but 7z files require the p7zip package to be installed. In Ubuntu, install it with
```sh
apt-get install p7zip
```

#### Testing
Run the tests to make sure everything is ok with
```sh
python3 manage.py test competitions
git clean -df
```

### Running

#### Running on development

Start the development server:
```sh
python3 manage.py runserver
```

The previous command will allow you to test the server on your local machine.
If you need to use the development server and be able to login from remote machines (note that security-wise this is not recommended), you can install the [django-sslserver] plugin for django, then start the server with:
```sh
python3 manage.py runsslserver 0.0.0.0:8000 --certificate /path/to/certificate.crt --key /path/to/key.key
```

#### Running on production

To run the production server, you'll need to install [uWSGI] and [nginx].
Follow the [links] to find tutorials on how to use each one with the rest of the Django+uWSGI+nginx stack.

The configuration files you'll need before running uWSGI/nginx are:

###### /etc/uwsgi/sites/scriptnet.ini
```sh
[uwsgi]
project = scriptnet
base = /home/sfikas/CODE/competitions

chdir = %(base)/%(project)
module = %(project).wsgi:application

master = true
processes = 5

socket = %(base)/%(project)/%(project)/%(project).sock
chmod-socket = 664
vacuum = true

daemonize = /var/log/uwsgi/%(project).log
```
Note that your non-privileged user will need to have write permission in ```/var/log/uwsgi/```.

###### /etc/init/uwsgi.conf
```sh
description "uWSGI application server in Emperor mode"

start on runlevel [2345]
stop on runlevel [!2345]

setuid sfikas
setgid www-data

exec /usr/local/bin/uwsgi --emperor /etc/uwsgi/sites
```

###### /etc/nginx/sites-available/scriptnet

```sh
server {
    listen          0.0.0.0:8000 ssl;
    server_name     www.example.com;
    access_log      /var/log/nginx/portoheli.iit.demokritos.gr_access.log combined;
    error_log       /var/log/nginx/portoheli.iit.demokritos.gr_error.log error;

    ssl_certificate         /etc/nginx/ssl/x.crt;
    ssl_certificate_key     /etc/nginx/ssl/x.key;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        root /home/sfikas/CODE/competitions/scriptnet;
    }

    location / {
        include         /etc/nginx/uwsgi_params;
        uwsgi_pass      unix:/home/sfikas/CODE/competitions/scriptnet/scriptnet/scriptnet.sock;
        uwsgi_param Host $host;
        uwsgi_param X-Real-IP $remote_addr;
        uwsgi_param X-Forwarded-For $proxy_add_x_forwarded_for;
        uwsgi_param X-Forwarded-Proto $http_x_forwarded_proto;
    }

}
```

For this file, you'll need to create a symbolic link with
```sh
cd /etc/nginx/sites-enabled
ln -s /etc/nginx/sites-available/scriptnet
```

Be sure to replace names, files and paths in the above with the respective values for your system.
For example, change ```sfikas``` to whatever is the name of your non-admin user.
Change the respective lines in ```settings.py``` to read as:
```sh
DEBUG = False
ALLOWED_HOSTS = ['*']
```

Finally, after making sure that everything is in place, copy static files to ```STATIC_ROOT``` with
```sh
python3 manage.py collectstatic
```
and start the server with
```sh
service start uwsgi
service start nginx
```


### Internationalisation

#### Code
* templates need to ```{% load i18n %}```
* then anything in ```{% trans "some phrase" %}``` will be translated if a translation is available
* .py files need to ```from django.utils.translation import ugettext_lazy as _```
* then anything in _("some phrase") will be translated, if a translation is available

#### Translate
To make translations available:
* find the appropriate .po file ```locale/[lang_code]/LC_MESSAGES/django.po```
* In this file you will see msgid's that correspond to the phrases in ```{% trans "..." %}``` or ```_("...")```
* Simply fill in the msgstr with the correct translation, e.g.:
```
#: library/forms.py:7
msgid "Given Name"
msgstr ""
```
* commit the changes to the .po files

#### Adding new phrases

If you have added a new phrase to a template or .py file there are a couple of things to do on the host afterwards. First the new phrases need to be added to the .po files. This is done with the following command:

* ```django-admin makemessages -l [lang_code] (or -a for all languages)```

Then (once the translations have been made in the .po files) the phrases must be recompiled with:

* ```django-admin compilemessages```


### Links

* [Competitions] READ discussion about competitions
* [Minutes] READ Minutes of the Valencia 2016 meeting regarding the competitions site
* [WebInterfaces] READ WebInterfaces Working group minutes
* [Architecture] READ Architecture Working group minutes
* [READ]
* [Django]

[Competitions]: <https://read02.uibk.ac.at/wiki/index.php/Competitions>
[Minutes]: <https://read02.uibk.ac.at/wiki/index.php/Technical_Meetings:Valencia_Meeting_Minutes#Competitions_site>
[WebInterfaces]: <https://read02.uibk.ac.at/wiki/index.php/Technical_Meetings:WebinterfacesWG>
[Architecture]: <https://read02.uibk.ac.at/wiki/index.php/Technical_Meetings:ArchitectureWG>
[READ]: <http://read.transkribus.eu>
[Django]: <https://www.djangoproject.com/>
[Django-Bootstrap3]: <http://github.com/dyve/django-bootstrap3>
[Django-Tables2]: <http://github.com/bradleyayers/django-tables2>
[Mono]: <http://www.mono-project.com/>
[Python]: <https://www.python.org>
[Pip]: <https://pip.pypa.io/en/stable/installing/>
[django-sslserver]: <https://github.com/teddziuba/django-sslserver>
[uWSGI]: <http://uwsgi-docs.readthedocs.io/en/latest/tutorials/Django_and_nginx.html>
[nginx]: <https://www.nginx.com/resources/admin-guide/gateway-uwsgi-django/>
[links]: <https://www.digitalocean.com/community/tutorials/how-to-serve-django-applications-with-uwsgi-and-nginx-on-ubuntu-14-04>
