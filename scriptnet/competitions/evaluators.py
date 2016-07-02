# This file contains all functions available to compute numerical results
# for user uploaded method results.
# Except: evaluator_worker . This is used as the thread that wraps calls 
# to evaluator_function in views.py .

from django.conf import settings
from random import random
from time import sleep
from os import system

def evaluator_worker(evaluator_function, submission_status):
    if not evaluator_function:
        submission_status.status="ERROR_EVALUATOR"
        submission_status.save()
        return
    else:
        try:
            submission_status.status="PROCESSING"
            submission_status.save()
            submission_status.numericalresult = evaluator_function()
        except:
            submission_status.status="ERROR_PROCESSING"
            submission_status.save()
            return
    submission_status.status = "COMPLETE"
    submission_status.save()


def random_integer_slow():
    print('random_integer_slow has been called!')
    sleep(20)
    return int(random()*100)

def random_scalar():
    print('random_scalar has been called!')
    return random()

def icfhr14tool_check():
    executable_folder = '{}/competitions/executables/VCGEvalConsole.linux'.format(settings.BASE_DIR)
    executable = '{}/VCGEvalConsole.sh'.format(executable_folder)
    dummy_results = '{}/WordSpottingResultsSample.xml'.format(executable_folder)
    dummy_privatedata = '{}/GroundTruthRelevanceJudgementsSample.xml'.format(executable_folder)
    commandline = '{} {} {}'.format(executable, dummy_privatedata, dummy_results)
    system(commandline)
    result = 0.0
    return result
