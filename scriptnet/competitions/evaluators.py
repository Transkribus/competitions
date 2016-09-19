# This file contains all functions available to compute numerical results
# for user uploaded method results.
# Except: evaluator_worker . This is used as the thread that wraps calls 
# to evaluator_function in views.py .

from django.conf import settings
from random import random
from time import sleep
from os import listdir, makedirs
from os.path import splitext, isdir, join,abspath,normpath,basename
from shutil import copyfile, rmtree
from subprocess import PIPE, Popen
from uuid import uuid4
from json import dumps
import re
import tarfile

temporary_folder = '/tmp/'

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

def transkribusBaseLineMetricTool(*args, **kwargs):
    executable_folder = '{}/competitions/executables/TranskribusBaseLineMetricTool'.format(settings.BASE_DIR)    
    #resultdata = kwargs.pop('resultdata', 'reco.lst')
    resultdata = kwargs.pop('resultdata', executable_folder)
    #privatedata = kwargs.pop('privatedata', 'truth.lst')
    privatedata = kwargs.pop('privatedata', executable_folder)

    executable_jar = 'baselineTool.jar'
    if(isdir(privatedata)):
        print(resultdata)
        print(privatedata)
        #This is the non-test scenario
        #Hence we have to create a temporary folder and copy everything there
        newfolder = '{}{}/'.format(temporary_folder, uuid4().hex)
        makedirs(newfolder)
        if(isdir(resultdata)):
            for filename in listdir(resultdata):
                full_filename = join(resultdata, filename)
                target_filename = join(newfolder, filename)
                copyfile(full_filename, target_filename)
        else:
            #If it is a file, it must be a tarball, or else raise an error 
            tar = tarfile.open(resultdata)
            tar.extractall(newfolder)
            tar.close()
        for filename in listdir(privatedata):
            full_filename = join(privatedata, filename)
            target_filename = join(newfolder, filename)
            copyfile(full_filename, target_filename)
        copyfile(join(executable_folder, executable_jar), join(newfolder, executable_jar))
        executable_folder = newfolder
        resultdata = '{}reco.lst'.format(newfolder)
        privatedata = '{}truth.lst'.format(newfolder)
   
    executable = 'java -jar {}'.format(executable_jar)
    commandline = '{} {} {}'.format(executable, privatedata, resultdata)
    command_output = cmdline(commandline, cwd=executable_folder)

    rmtree(newfolder)
    print(command_output)
    rgx = r'Avg \(over Pages\) Avg Precision: ([\d\.]+)\nAvg \(over Pages\) Avg Recall: ([\d\.]+)\nAvg \(over Pages\) Avg F-Measure: ([\d\.]+)'
    r = re.search(rgx, command_output)     
    result = {
        'bl-avg-precision': r.group(1),
        'bl-avg-recall':    r.group(2),
        'bl-avg-fmeasure':  r.group(3),
    }
    return result

def transkribusErrorRate(*args, **kwargs):
    #the method assumes the following parameters:
    # kwargs has to contain "privatedata" with the path to a tar-file.
    # The tar-file has to contain Page-xml-files without subfolders.
    # The TextEquiv of the lines have to be the ground truth for the competition.
    # kwargs also has to contain "resultdata",
    # which is the path to the tar-file containing the hypothesises of the competitor.
    # kwargs can contain a path "tmpfolder" - all temporary files and folder are created there.
    # the folder will be deleted afterwards, when it did not exist before.
    # Otherwise only the containing files and folders are deleted.

    folder_data =  kwargs.pop('tmpfolder',normpath(abspath(".")))
    folder_exec = join(settings.BASE_DIR,"competitions/executables/TranskribusBaseLineMetricTool")
    folder_exec = join(normpath(abspath(".")),"executables/TranskribusErrorRate")
    privatedata =  kwargs.pop('privatedata',"gt.tgz")
    print("privatedata is '"+privatedata+"'.")
    resultdata =  kwargs.pop('resultdata', "hyp.tgz")
    print("resultdata is '"+resultdata+"'.")
    file_exec = join(folder_exec,'TranskribusErrorRate.jar')

    data_lists = {}
    to_remove_folder = []
    to_remove_file = []
    deleteroot = False
    if not (isdir(folder_data)):
        print("folder have to be deleted")
        deleteroot = True
    for (file_tar,prefix) in [[privatedata,"gt"], [resultdata,"hyp"]]:
        print("execute '"+ file_tar + "' ...")
        folder_xmls = join(folder_data,prefix + '_dir')
        print(folder_xmls)
        if isdir(folder_xmls):
            rmtree(folder_xmls)
        makedirs(folder_xmls) #, exist_ok=True)
        to_remove_folder += [folder_xmls]
        print("unpack tar-file ...")
        obj_tar = tarfile.open(file_tar)
        obj_tar.extractall(folder_xmls)
        obj_tar.close()
        print("unpack tar-file ... [DONE]")
        print("save list ...")
        files_xml = sorted(listdir(folder_xmls))
        file_list_xml = join(folder_data,prefix + '.lst')
        to_remove_file+=[file_list_xml]
        data_lists[file_tar] = file_list_xml
        with open(file_list_xml, 'w') as tfFile:
            for file_xml in files_xml:
                tfFile.write(join(folder_xmls, file_xml)+"\n")
                #print(join(folder_xmls, file_xml), file=tfFile)
        print("save list ... [DONE] (to '"+file_list_xml+"')")
    if (deleteroot):
        to_remove_folder += [folder_data]

    executable = 'java -cp {} eu.transkribus.errorrate.ErrorRateParser'.format(file_exec)
    commandline = '{} {} {}'.format(executable, data_lists[privatedata], data_lists[resultdata])
    print(commandline)
    #command_output = "tryrun"
    command_output = cmdline(commandline)
    print("output of algorithm:")
    print(command_output)
    print("output of algorithm: [DONE]")
    for file in to_remove_file:
        print("remove '"+file+"'")
        os.remove(file)
    for folder in to_remove_folder:
        print("remove '"+folder+"'")
        rmtree(folder)
    rgx = r'.*SUB = ([\d\.]+).*\nDEL = ([\d\.]+).*\nINS = ([\d\.]+).*\nCER = ([\d\.]+).*'
    r = re.search(rgx, command_output)
    result = {
    'CER': r.group(4),
    'INS': r.group(3),
    'DEL': r.group(2),
    'SUB': r.group(1),
    }
    print(result)
    return result
