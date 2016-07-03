# This file contains all functions available to compute numerical results
# for user uploaded method results.
# Except: evaluator_worker . This is used as the thread that wraps calls 
# to evaluator_function in views.py .

from django.conf import settings
from random import random
from time import sleep
from os import system

def evaluator_worker(evaluator_function, submission_status_set):
    if not evaluator_function:
        for s in submission_status_set:
            s.status="ERROR_EVALUATOR"
            s.save()
        return
    else:
        try:
            for s in submission_status_set:
                s.status = "PROCESSING"
                s.save()
            result_dictionary = evaluator_function()
            for s in submission_status_set:
                benchname = s.benchmark.name
                print(benchname)
                if benchname in result_dictionary.keys():
                    s.status = "COMPLETE"
                    s.numericalresult = result_dictionary[benchname]
                    s.save()
                else:
                    s.status = "ERROR_UNSUPPORTED"
                    s.numericalresult = ''
                    s.save()
        except:
            for s in submission_status_set:
                s.status="ERROR_PROCESSING"
                s.save()
            return

def random_numbers():
    sleep(20)
    result = {
        'random_integer': int(random()*10000),
        'random_percentage': random()
    }
    return result

def icfhr14_kws_tool():
    executable_folder = '{}/competitions/executables/VCGEvalConsole.linux'.format(settings.BASE_DIR)
    executable = '{}/VCGEvalConsole.sh'.format(executable_folder)
    dummy_results = '{}/WordSpottingResultsSample.xml'.format(executable_folder)
    dummy_privatedata = '{}/GroundTruthRelevanceJudgementsSample.xml'.format(executable_folder)
    commandline = '{} {} {}'.format(executable, dummy_privatedata, dummy_results)
    system(commandline)
    result = {
        'map': 0.0,
        'p@5': 0.0
    }
    return result
