# This file contains all functions available to compute numerical results
# for user uploaded method results.
# Except: evaluator_worker . This is used as the thread that wraps calls 
# to evaluator_function in views.py .

from django.conf import settings
from random import random
from time import sleep
from os import listdir
from os.path import splitext, isdir
from subprocess import PIPE, Popen
from json import dumps
import re


def cmdline(command, *args, **kwargs):
    # http://stackoverflow.com/questions/3503879/assign-output-of-os-system-to-a-variable-and-prevent-it-from-being-displayed-on    
    # http://stackoverflow.com/questions/17615414/how-to-convert-binary-string-to-normal-string-in-python3 
    # http://stackoverflow.com/questions/13744473/command-line-execution-in-different-folder
    cwd = kwargs.pop('cwd', None)
    process = Popen(
        args=command,
        stdout=PIPE,
        shell=True,
        cwd=cwd,
    )
    res = process.communicate()[0]
    return res.decode('utf-8')


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
    privatedata = kwargs.pop('privatedata', '{}/GroundTruthRelevanceJudgementsSample.xml'.format(executable_folder))
    n_xml = 0
    if isdir(privatedata):
        for fn in listdir(privatedata):
            fn_base, fn_ext = splitext(fn)
            if(fn_ext.lower() == '.xml'):
                n_xml = n_xml + 1
                privatedata = '{}{}'.format(privatedata, fn)
    else:
        n_xml = 1

    if(n_xml != 1):
        raise IOError('The private data folder does not contain exactly one ground-truth file')

    executable = '{}/VCGEvalConsole.sh'.format(executable_folder)
    commandline = '{} {} {}'.format(executable, privatedata, resultdata)
    command_output = cmdline(commandline)

    rgx = r'ALL QUERIES\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)'
    r = re.search(rgx, command_output) 
    result = {
        'p@5':              r.group(1),
        'p@10':             r.group(2),
        'r-precision':      r.group(3),
        'map':              r.group(4),
        'ndcg-binary':      r.group(5),
        'ndcg':             r.group(6),
        'pr-curve':         dumps([r.group(7), r.group(8), r.group(9), r.group(10), r.group(11), r.group(12), r.group(13), r.group(14), r.group(15), r.group(16), r.group(17)])
    }
    return result

def transkribusBaselineMetricTool(*args, **kwargs):
    executable_folder = '{}/competitions/executables/TranskribusBaseLineMetricTool'.format(settings.BASE_DIR)    
    resultdata = kwargs.pop('resultdata', 'reco.lst')
    privatedata = kwargs.pop('privatedata', 'truth.lst')

    executable = 'java -jar baselineTool.jar'
    commandline = '{} {} {}'.format(executable, privatedata, resultdata)
    command_output = cmdline(commandline)

    print(command_output)
    result = {
        'bl-avg-precision': 0,
        'bl-avg-recall': 0,
        'bl-avg-fmeasure': 0,
    }
    return result