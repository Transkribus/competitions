import django_tables2 as tables
from .models import Submission
from .models import Subtrack

class ScalarscoreTable(tables.Table):
    class Meta:
        attrs = {
            'class': 'paleblue', 
            'orderable': 'True',
        }
    name = tables.Column()
    method_info = tables.Column()
    submitter = tables.Column()
    affiliation = tables.Column()

def expandedScalarscoreTable(extracolumn_names):
    #adapted idea from http://stackoverflow.com/questions/16696066/django-tables2-dynamically-adding-columns-to-table-not-adding-attrs-to-table
    attrs = dict((r, tables.Column()) for r in extracolumn_names)
    attrs['Meta'] = type('Meta', (), dict( attrs = ScalarscoreTable.Meta.attrs) )
    expanded_class = type('DynamicScalarscoreTable', (ScalarscoreTable,), attrs)    
    return expanded_class

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

class ManipulateMethodsTable(tables.Table):
    class Meta:
        attrs = {
            'class': 'paleblue', 
            'orderable': 'False',
        }
    name = tables.Column()
    method_info = tables.Column()
    submitter = tables.Column()
    subtracks = tables.Column()
    selection = tables.CheckBoxColumn(verbose_name=('Select'), accessor='pk')