import django_tables2 as tables
from .models import Submission
from .models import Subtrack

def expandedScalarscoreTable(scores):
    #adapted idea from http://stackoverflow.com/questions/16696066/django-tables2-dynamically-adding-columns-to-table-not-adding-attrs-to-table
    attrs = dict((r.name, tables.Column()) for r in scores)
    attrs['Meta'] = type('Meta', (), dict(attrs={"class":"paleblue"}) )
    expanded_class = type('DynamicScalarscoreTable', (ScalarscoreTable,), attrs)    
    return expanded_class

class ScalarscoreTable(tables.Table):
    class Meta:
        attrs = {'class': 'paleblue'}
    name = tables.Column()
    method_info = tables.Column()
    submitter = tables.Column()
    affiliation = tables.Column()

class SubmissionTable(tables.Table):
    class Meta:
        model = Submission
        fields = {'name', 'method_info', 'submitter'}
        attrs = {'class': 'paleblue'}
        
    SubmissionStatus_set = tables.Column()        
    submitter = tables.Column()
    def render_submitter(self, value):
        if value is not None:
            return ', '.join(['{} {}'.format(s.user.first_name, s.user.last_name) for s in value.all()])
        return '-'

    def render_SubmissionStatus_set(self, value):
        if value is not None:
            return ', '.join(['{} {}'.format(s.benchmark.name, s.numericalresult) for s in value.all()])
        return '-'        