# This file contains all functions available to compute numerical results
# for user uploaded method results.
# Except: evaluator_worker . This is used as the thread that wraps calls 
# to evaluator_function in views.py .

from django.conf import settings
from random import random
from time import sleep
from os import system, listdir
from os.path import splitext

def evaluator_worker(evaluator_function, submission_status_set):
    if not evaluator_function:
        for s in submission_status_set:
            s.status="ERROR_EVALUATOR"
            s.save()
        return
    else:
        try:
            for s in submission_status_set:
                submission = s.submission #ugly; works because submission should be the same for all
                s.status = "PROCESSING"
                s.save()
            result_dictionary = evaluator_function(
                privatedata = submission.subtrack.private_data_unpacked_folder(), 
                resultdata = submission.resultfile.name,
                )
            for s in submission_status_set:
                benchname = s.benchmark.name
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

def random_numbers(*args, **kwargs):
    sleep(20)
    result = {
        'random_integer': int(random()*10000),
        'random_percentage': random()
    }
    return result

def icfhr14_kws_tool(*args, **kwargs):
    executable_folder = '{}/competitions/executables/VCGEvalConsole.linux'.format(settings.BASE_DIR)    
    resultdata = kwargs.pop('resultdata', '{}/WordSpottingResultsSample.xml'.format(executable_folder))
    privatedatafolder = kwargs.pop('privatedata', '{}/GroundTruthRelevanceJudgementsSample.xml'.format(executable_folder))
    n_xml = 0
    for fn in listdir(privatedatafolder):
        print(fn)
        fn_base, fn_ext = splitext(fn)
        print(fn_base)
        print(fn_ext)
        if(fn_ext.lower() == '.xml'):
            n_xml = n_xml + 1
            privatedata = '{}{}'.format(privatedatafolder, fn)
    print(privatedata)
    print(resultdata)    
            
    if(n_xml != 1):
        raise IOError('The private data folder does not contain exactly one ground-truth file')

    executable = '{}/VCGEvalConsole.sh'.format(executable_folder)
    commandline = '{} {} {}'.format(executable, privatedata, resultdata)
    system(commandline)
    result = {
        'map': 0.0,
        'p@5': 0.0
    }
    return result
