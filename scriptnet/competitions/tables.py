import django_tables2 as tables
from .models import Submission

class TwoscoreTable(tables.Table):
    class Meta:
        attrs = {'class': 'paleblue'}
    name = tables.Column()
    method_info = tables.Column()
    submitter = tables.Column()
    affiliation = tables.Column()
    map = tables.Column()
    pat5 = tables.Column(verbose_name='p@5')

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