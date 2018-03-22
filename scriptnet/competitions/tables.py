import django_tables2 as tables
from .models import Submission
from .models import Subtrack

class ScoreboardTable(tables.Table):
    class Meta:
        attrs = {
            'class': 'paleblue', 
            'orderable': 'False',
        }
    position = tables.Column()
    name = tables.Column()
    method_info = tables.Column()
    submitter = tables.Column()
    affiliation = tables.Column()
    before_deadline = tables.BooleanColumn(verbose_name=('Submitted before deadline'))
    score = tables.Column()
        

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
    publishable = tables.BooleanColumn(verbose_name=('Result is public'), accessor='publishable')

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
    name = tables.Column(verbose_name=('Name'), accessor='name')
    method_info = tables.Column(verbose_name=('Method info'))
    date_published = tables.DateTimeColumn(verbose_name=('Date published'), accessor='timestamp')
    submitter = tables.Column(verbose_name=('Submitter'), accessor='submitter.all')
    subtracks = tables.Column(verbose_name=('Submitted to'), accessor='subtrack')
    publishable = tables.BooleanColumn(verbose_name=('Public'), accessor='publishable')
    #http://stackoverflow.com/a/10860711/5615276    
    selection = tables.CheckBoxColumn(verbose_name=('Select'), accessor='pk')