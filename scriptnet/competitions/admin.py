from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Competition, Individual, Affiliation, Submission, Track, Subtrack, PublicLink
from .models import Benchmark, EvaluatorFunction, SubmissionStatus

class IndividualInline(admin.StackedInline):
    model = Individual
    can_delete = False
    filter_horizontal = ('affiliations', )    

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (IndividualInline, )

#class BenchmarkInline(admin.TabularInline):
    #model = Competition.count_in_scoreboard.through
#    extra = 3

#class CompetitionAdmin(admin.ModelAdmin):
#    inlines = (BenchmarkInline, )

class PubliclinkInline(admin.TabularInline):
    model = PublicLink
    can_delete = False
    extra = 0

class SubtrackAdmin(admin.ModelAdmin):
    inlines = (PubliclinkInline, )

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Individual)
admin.site.register(Affiliation)
admin.site.register(Competition)
admin.site.register(Track)
admin.site.register(Subtrack, SubtrackAdmin)
admin.site.register(Submission)
admin.site.register(Benchmark)
admin.site.register(EvaluatorFunction)
admin.site.register(SubmissionStatus)
admin.site.register(PublicLink)
