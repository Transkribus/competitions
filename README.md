# ScriptNet Competitions

The competitions site for the [READ] project, written in Python / [Django].

### Requirements & Installation
Python, [Django], [Django-Bootstrap3] and [Django-Tables2] need to be installed.

##### Linux (Ubuntu)
Run the following as a privileged user:
```sh
apt-get update && sudo apt-get upgrade
apt-get install python3-pip python3-dev build-essential
```
##### Windows
* Install the latest release of [Python 3.x.x]
* Install [pip]

#### All platforms
Finally, install Django and the required plugins with
```sh
pip3 install django django-bootstrap3 django_tables2
```



#### Requirements of optional components

The benchmarks related the ICFHR'14 KWS competition require the [Mono] library to run. In Ubuntu, install it with
```sh
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF
echo "deb http://download.mono-project.com/repo/debian wheezy main" | sudo tee /etc/apt/sources.list.d/mono-xamarin.list
sudo apt-get update
sudo apt-get install mono-complete
```

### Running

Start the development server:
```sh
python manage.py runserver
```

### Internationalisation

#### Code
* templates need to ```{% load i18n %}```
* then anything in ```{% trans "some phrase" %}``` will be translated if a translation is available
* .py files need to ```from django.utils.translation import ugettext_lazy as _```
* then anything in _("some phrase") will be translated if a translation is available

#### Translate
To make translations available:
* find the appropriate .po file ```locale/[lang_code]/LC_MESSAGES/django.po```
* In this file you will see msgid's that correspond to the phrases in ```{% trans "..." %}``` or ```_("...")```
* Simply fill in the msgstr with the correct translation eg:
```
#: library/forms.py:7
msgid "Given Name"
msgstr ""
```
* commit the changes to the .po files

#### Adding new phrases

If you have added a new phrase to a template or .py file there are a couple of things to do on the host afterwards. First the new phrases need to be added to the .po files. This is done with the following command:

* ```django-admin makemessages -l [lang_code] (or -a for all languages)```

Then (once the translations have been made in the .po files) the phrases must be be recompiled with:

* ```django-admin compilemessages```


### Links

* [Competitions] READ discussion about competitions
* [Minutes] READ Minutes of the Valencia 2016 meeting regarding the competitions site
* [WebInterfaces] READ WebInterfaces Working group minutes
* [READ]
* [Django]

[Competitions]: <https://read02.uibk.ac.at/wiki/index.php/Competitions>
[Minutes]: <https://read02.uibk.ac.at/wiki/index.php/Technical_Meetings:Valencia_Meeting_Minutes#Competitions_site>
[WebInterfaces]: <https://read02.uibk.ac.at/wiki/index.php/Technical_Meetings:WebinterfacesWG>
[READ]: <http://read.transkribus.eu>
[Django]: <https://www.djangoproject.com/>
[Django-Bootstrap3]: <http://github.com/dyve/django-bootstrap3>
[Django-Tables2]: <http://github.com/bradleyayers/django-tables2>
[Mono]: <http://www.mono-project.com/>
