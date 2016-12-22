# ScriptNet Competitions

[![Build Status](https://travis-ci.org/Transkribus/competitions.svg?branch=develop)](https://travis-ci.org/Transkribus/competitions)

The competitions site for the [READ] project, written in [Python] / [Django].

### Requirements, installation & testing
[Python], [Django], [Django-Bootstrap3] and [Django-Tables2] need to be installed.

#### Python and Pip

* Install the latest release of [Python] 3.x.x
* Install [pip]

Follow the instructions on the links above to install on your system. Specifically for Ubuntu Linux, the command-line commands to install Python and Pip are
```sh
apt-get update && apt-get upgrade
apt-get install python3-pip python3-dev build-essential python3-setuptools
```

#### Django and plugins 
Install Django and the required plugins with
```sh
pip3 install django django-bootstrap3 django_tables2
```
#### Requirements of optional components

##### ICFHR'14 KWS
The benchmarks introduced in the ICFHR'14 KWS competition require the [Mono] library to run. In Ubuntu, install it by running the following as a privileged user:
```sh
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF
echo "deb http://download.mono-project.com/repo/debian wheezy main" | tee /etc/apt/sources.list.d/mono-xamarin.list
apt-get update
apt-get install mono-complete
```
Follow the [Mono] installation instructions to install the library in other platforms.

##### ICFHR'16 HTR - liblog4cxx, boost-filesystem
The benchmarks in the ICFHR'16 HTR competition require the liblog4cc and boost/filesystem libraries. In Ubuntu, install them by running
```
apt-get install liblog4cxx10
apt-get install libboost-filesystem1.54.0
apt-get install libopencv-dev
apt-get install uni2ascii
```

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

Switch to the ```develop``` branch, with
```sh
git checkout develop
```
and start the development server:
```sh
python3 manage.py runserver
```

The previous command will allow you to test the server on your local machine.
If you need to use the development server and be able to login from remote machines (note that security-wise this is not recommended), you can install the [django-sslserver] plugin for django, then start the server with:
```sh
python3 manage.py runsslserver 0.0.0.0:8000 --certificate /path/to/certificate.crt --key /path/to/key.key
```

If you need to access the django admin, you can always create a super-user account with
```sh
python3 manage.py createsuperuser
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
env = SYNTHIMA=<.....>

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
    location /media/ {
        #the difference btw alias+root is essentially that root adds the location argument as a suffix on the final URL        
        alias /home/sfikas/CODE/competitions/scriptnet/; 
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

#### Updating a live Django server on production

Supposing you need to update a competitions server to the latest repo version, you should:
```sh
git checkout master
git pull
service restart uwsgi
service restart nginx
```

Note that it is *very* important that you restart both uwsgi and nginx -- forgetting this can cause a server error (''Server Error 500'').

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

### Creating a new competition

In order to create a new competition, you'll need to follow these steps:

#### 1. Install the benchmarks that will be used for your competition.

* For this step you will need to make changes to the repo code. 
If you think that you can use only benchmarks that are already installed on the repo, you can skip this step.
You can check which benchmarks are installed by logging in the django administration page (step 2).
* Either you intend to use the new benchmark code on a copy cloned locally on your machine, or push this as a contribution to the current github repo,
please follow these guidelines:
    * Make your changes over code of the ```develop``` branch. Optionally create a new branch for your contributions as a branch of ```develop```.
    * Pay attention to the Travis CI tag for the latest commit of the ```develop``` branch. 
    * If you need to access the django administration page on your local repository clone, you can create a superuser account with ```python manage.py createsuperuser```. 
* There are two django models that are related to benchmarks: *evaluator function models* and *benchmark models*. 
    You will need to add at least one evaluator function model. 
        This will correspond to a function that you will have to add to [evaluators.py](https://github.com/Transkribus/competitions/blob/master/scriptnet/competitions/evaluators.py) .
        An example evaluator function is ```random_numbers```, found in the same file:
```python
def random_numbers(*args, **kwargs):
    sleep(20)
    result = {
        'random_integer': int(random()*10000),
        'random_percentage': random()
    }
    return result
```

You can use this as a template for a new evaluator function. Define a new function with ```(*args, **kwargs)``` arguments, and return a dictionary (here called 'result').
Each *key* of this dictionary will correspond to a different benchmark.
Note of course that ```random_numbers``` is not a real benchmark, in the sense that it simply computes and returns a random number.

Normally you will have to write some code to compute a value or values over the submitted results (more on this below). 

* You can define more than one evaluator function if you like, and define other benchmarks there. However, the norm should be that you define all your benchmarks under a single evaluator function

* You can use data that are attached to a competition/track/subtrack. This is the *private data*, defined as a field of each django *subtrack model* (see [models.py](https://github.com/Transkribus/competitions/blob/master/scriptnet/competitions/models.py)).
Pass private data, submitted results and other information through the python arguments. See for example how this is done in the ```icfhr14_kws_tool``` evaluator function: 

```python
resultdata = kwargs.pop('resultdata', '{}/WordSpottingResultsSample.xml'.format(executable_folder))
privatedata = kwargs.pop('privatedata', '{}/GroundTruthRelevanceJudgementsSample.xml'.format(executable_folder))
```

Here resultdata and privatedate refer to the XML files for the submitter's results and the private data. The second arguments are default values for these variables, here set to test data (this is optional).

* The processing required to compute benchmarks can be done using an external executable file. See how this is done in ```icfhr14_kws_tool```:

```python
executable = '{}/VCGEvalConsole.sh'.format(executable_folder)
commandline = '{} {} {}'.format(executable, privatedata, resultdata)
command_output = cmdline(commandline)
```

The output of the executable is saved in ```command_output```, then you'll have to parse this and use it to populate the dictionary you will return:

```python
rgx = r'ALL QUERIES\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)'
r = re.search(rgx, command_output) 
result = {
    'p@5':              r.group(1),
    'p@10':             r.group(2),
    'r-precision':      r.group(3),
    'map':              r.group(4),
    'ndcg-binary':      r.group(5),
    'ndcg':             r.group(6),
    'pr-curve':         dumps([r.group(7), r.group(8), r.group(9), r.group(10), r.group(11), r.group(12), r.group(13), r.group(14), r.group(15), r.group(16), r.group(17)])
}
```

* Keep note of the names of the evaluator functions you have defined, and the benchmark names you have used as keys on the dictionary your evaluator function returns.
You will need these to define corresponding django models.

* Create tests for your benchmark. Add code at [tests.py](https://github.com/Transkribus/competitions/blob/master/scriptnet/competitions/tests.py). Each test function should go under ```class EvaluatorTests```, or under a new class named ```class EvaluatorTests_***``` if you feel like using a lot of test functions. An example of a test function is:

```python
def test_icfhr14_kws_tool(self):
    res = icfhr14_kws_tool()
    self.assertEqual(res, {
        'pr-curve': '["1.0000", "1.0000", "1.0000", "1.0000", "1.0000", "0.6667", "0.0000", "0.0000", "0.0000", "0.0000", "0.0000"]',
        'p@5': '0.9000',
        'r-precision': '0.5000',
        'map': '0.5185',
        'ndcg': '0.6395',
        'p@10': '0.5000',
        'ndcg-binary': '0.6817'
        }
    )
```

At a minimum, tests should check that some result fixture should return specific benchmark values.

#### 2. Access the django administration page. 
    
* If you are the site administrator, simply login with your credentials. The administration site URL will normally be http://my.site.com/admin/
* If you are not the site administrator, you need to:
    1. Create an account if you don't have one. You can create one yourself on the Register tab of the site. 
    2. Ask the administrator to give your account _staff status_ .
    3. Ask the administrator to add your account to the 'Competitions organizers' group. This will give you access to manipulate all ORM models necessary to create and manage a competition.

#### 3. Create Evaluator function models.

* On the django administration page, add one ```Evaluator function``` model for each evaluator function model you have defined previously.
* Set the name of the new model to the name of the function you used on step 1.

#### 4. Create Benchmark models.

Create one benchmark models for each of the result keys you defined. Specifically, for each added model, fill-in the require fields:

* Name: Set its name to the resulting dictionary you specificed in step 1.
* Evaluator function: Set the evaluator function model you created in step 3.
* Benchmark info: Write a small description of this benchmark. 
* Subtracks: Leave this empty for now, since we haven't specified any subtracks yet.
* Count in scoreboard: Leave this empty for now, since we haven't specified any competitions yet.
* Is scalar: Tick this if the benchmark is defined as a scalar value. (for example, precision-recall is not scalar, but MAP is scalar)

#### 5. Create a Competition model.

Create a competition model, and fill in the fields with the required information. Most field requirements are self-explanatory.
Note that in the overview, newsfeed and important dates fields you can write HTML code.

On the field 'Benchmark-Competition relationships' add the benchmarks that you have defined on steps 1 and 4 below.

#### 6. Create one or more Track models.

Even if your competition does not distinguish between different tracks, you still have to create at least one track.

Ignore the ```percomp_uniqueid``` field -- this is an identifier that is automatically filled in.

Fill in the required fields:

* Name: The name of your track.
* Overview: A description of the track. You can use HTML here.
* Competition: Select the competition you created on step 5 here.

#### 7. Create one or more Subtrack models.

Even if your competition does not distinguish between different subtracks, you still have to create at least one subtrack.

Ignore the ```pertrack_uniqueid``` field -- this is an identifier that is automatically filled in.

Fill in the required fields:

* Name: The name of your subtrack.
* Track: Select a track you created on step 6 here.
* Public data / Public data external: Upload data that are meant to be downloaded by the competition participants. Alternatively, you can provide an external URL.
* Private data: Upload data that are not meant to be downloaded by the competition participants. If the uploaded file is a compressed tarball, ie a tar.gz or a tgz file, it will be decompressed and un-tarred automatically on the server, once the upload is completed. **This is useful if your private data is too large and/or it is comprised of multiple files.**

In Unix, you can create a compressed tarball by running:
```
tar cvfz privatedata.tgz privatedata/
```
where privatedata is a folder containing your data, and privatedata.tgz is the file that will be the result of this process.

The private data field is meant to be used as an argument to your evaluation benchmarks. In KWS for example, the private data is a file that contains the information about which query matches with which word.

Note that uploaded ```zip``` files will *not* be automatically decompressed. You are advised to use ```tar.gz``` files, after creating them with the process described above.

#### 8. Assign Benchmarks to the scoreboard.

For each competition there is a 'scoreboard', that is an ordered list of all competitors. Competitors are ordered from best performing (least points) to worst performing (most points).
The total points are calculated as a simple sum function over the rankings of the methods on benchmarks that are assigned as 'important' for the scoreboard.

You can choose which benchmarks are important for the scoreboard of which competition, by changing the appropriate benchmark model info (see Step 4, field 'Count in Scoreboard')

#### See also

Related discussion: <https://github.com/Transkribus/competitions/issues/18>

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
