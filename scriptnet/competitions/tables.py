import django_tables2 as tables
from .models import Submission

class SubmissionTable(tables.Table):
    class Meta:
        model = Submission
        attrs = {'class': 'paleblue'}
