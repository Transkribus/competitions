from __future__ import unicode_literals
from django.apps import AppConfig
import os


class CompetitionsConfig(AppConfig):
    name = 'competitions'
    def ready(self):
        # startup code here        
        print("""
##############################################################
#                                                            #
#           ScriptNet Competitions - booting!                #
#                                                            #
##############################################################        
# Environment:                                               #
# SYNTHIMA={}
#
        """.format(os.environ.get('SYNTHIMA'))
        )