# This file contains all functions available to compute numerical results
# for user uploaded method results.
# Except: evaluator_worker . This is used as the thread that wraps calls
# to evaluator_function in views.py .

from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from random import random
from time import sleep
from os import listdir, makedirs, remove
from os.path import splitext, isdir, join, abspath, normpath, basename
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

def send_feedback(status, logfile, individu):
    uname = individu.user.username
    #TODO: Maybe all cosubmitters should be notified
    #TODO: Maybe add more info about the submission
    uemail = individu.user.email
    if status == "COMPLETE":
        status_final = 'Evaluation finished succesfully.'
    elif status == "ERROR_EVALUATOR":
        status_final = 'Evaluation internal error; evaluator not found.'
    elif status == "ERROR_UNSUPPORTED":
        status_final = 'Evaluation internal error; benchmark unsupported.'
    elif status == "ERROR_PROCESSING":
        status_final = 'Evaluation error; an error occured while processing your file.'
    else:
        status_final = 'Unknown error.'
    email = EmailMessage(
        'Submission to Scriptnet',
        """
This email is sent as feedback because you have submitted a result file to the ScriptNet Competitions Site.
Username: {}
{} (return code: {})

Evaluator log (if any:)
{}

ScriptNet is hosted by the National Centre of Scientific Research Demokritos and co-financed by the H2020 Project READ (Recognition and Enrichment of Archival Documents):
http://read.transkribus.eu/
        """.format(uname, status_final, status, logfile),
        settings.EMAIL_HOST_USER,
        [uemail],
        [settings.EMAIL_ADMINISTRATOR],
    )
    email.send(fail_silently=False)


def evaluator_worker(evaluator_function, submission_status_set, individu):
    logfile = ''
    if not evaluator_function:
        for s in submission_status_set:
            s.status = "ERROR_EVALUATOR"
            s.save()
        send_feedback(s.status, logfile, individu)
        return
    else:
        try:
            for s in submission_status_set:
                # ugly; works because submission should be the same for all
                submission = s.submission
                s.status = "PROCESSING"
                s.save()
            res = evaluator_function(
                privatedata=submission.subtrack.private_data_unpacked_folder(),
                resultdata=submission.resultfile.name,
                )
            if(isinstance(res, dict)):
                result_dictionary = res
            else:
                (result_dictionary, logfile) = res
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
            send_feedback(s.status, logfile, individu)
        except:
            for s in submission_status_set:
                s.status = "ERROR_PROCESSING"
                s.save()
            send_feedback(s.status, logfile, individu)
            return


def random_numbers(*args, **kwargs):
    sleep(20)
    result = {
        'random_integer': int(random()*10000),
        'random_percentage': random()
    }
    return result


def icfhr14_kws_tool(*args, **kwargs):
    executable_folder = \
        '{}/competitions/executables/VCGEvalConsole.linux'\
        .format(settings.BASE_DIR)
    resultdata = kwargs.pop('resultdata',
                            '{}/WordSpottingResultsSample.xml'
                            .format(executable_folder))
    privatedata = kwargs.pop('privatedata',
                             '{}/GroundTruthRelevanceJudgementsSample.xml'.
                             format(executable_folder))
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
        raise IOError('The private data folder does not contain exactly ' +
                      'one ground-truth file')

    executable = '{}/VCGEvalConsole.sh'.format(executable_folder)
    commandline = '{} {} {}'.format(executable, privatedata, resultdata)
    command_output = cmdline(commandline)

    rgx = r'ALL QUERIES\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)'\
        '\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)'\
        '\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)'\
        '\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)'
    r = re.search(rgx, command_output)
    result = {
        'p@5':              r.group(1),
        'p@10':             r.group(2),
        'r-precision':      r.group(3),
        'map':              r.group(4),
        'ndcg-binary':      r.group(5),
        'ndcg':             r.group(6),
        'pr-curve':         dumps([r.group(7), r.group(8), r.group(9),
                                   r.group(10), r.group(11), r.group(12),
                                   r.group(13), r.group(14), r.group(15),
                                   r.group(16), r.group(17)])
    }
    return (result, command_output)


def transkribusBaseLineMetricTool(*args, **kwargs):
    executable_folder =\
        '{}/competitions/executables/TranskribusBaseLineMetricTool'\
        .format(settings.BASE_DIR)
    # resultdata = kwargs.pop('resultdata', 'reco.lst')
    resultdata = kwargs.pop('resultdata', executable_folder + '/HYPO.tar')
    # privatedata = kwargs.pop('privatedata', 'truth.lst')
    privatedata = kwargs.pop('privatedata', executable_folder + '/GT')

    executable_jar = 'baselineTool.jar'
    if(isdir(privatedata)):
        print(resultdata)
        print(privatedata)
        # This is the non-test scenario
        # Hence we have to create a temporary folder and copy everything there
        newfolder = '{}{}/'.format(temporary_folder, uuid4().hex)
        makedirs(newfolder)
        # Since truth and hypo could be named equally we have to create two folders
        hypofolder = join(newfolder, 'hypo')
        makedirs(hypofolder)
        truthfolder = join(newfolder, 'truth')
        makedirs(truthfolder)
        if(isdir(resultdata)):
            cmdline('cp -r '+resultdata+' '+hypofolder, cwd=newfolder)
        else:
            # If it is a file, it must be a tarball, or else raise an error
            tar = tarfile.open(resultdata)
            tar.extractall(hypofolder)
            tar.close()
        cmdline('cp -r '+privatedata+' '+truthfolder)
        # Resultdata contains the folder structure of the result files

        cmdline('find '+hypofolder+' -name "*.txt" > tmp.lst', cwd=newfolder)
        cmdline('find '+hypofolder+' -name "*.xml" >> tmp.lst', cwd=newfolder)
        cmdline('cat tmp.lst | sort > reco.lst', cwd=newfolder)
        cmdline('rm tmp.lst', cwd=newfolder)
        cmdline('find '+truthfolder+' -name "*.txt" > tmp.lst', cwd=newfolder)
        cmdline('find '+truthfolder+' -name "*.xml" >> tmp.lst', cwd=newfolder)
        cmdline('cat tmp.lst | sort > truth.lst', cwd=newfolder)
        cmdline('rm tmp.lst', cwd=newfolder)

        copyfile(join(executable_folder, executable_jar), join(newfolder,
                                                               executable_jar))
        executable_folder = newfolder
        resultdata = '{}reco.lst'.format(newfolder)
        privatedata = '{}truth.lst'.format(newfolder)

    executable = 'java -jar {}'.format(executable_jar)
    commandline = '{} {} {}'.format(executable, privatedata, resultdata)
    command_output = cmdline(commandline, cwd=executable_folder)

    rmtree(newfolder)
    print(command_output)
    rgx = r'Avg \(over pages\) P value: ([\d\.]+)\nAvg \(over pages\) '\
        'R value: ([\d\.]+)\nResulting F_1 value: ([\d\.]+)'
    r = re.search(rgx, command_output)
    result = {
        'bl-avg-P-value': r.group(1),
        'bl-avg-R-value':    r.group(2),
        'bl-F_1-value':  r.group(3),
    }
    return (result, command_output)


def transkribusErrorRate(*args, **kwargs):
    # the method assumes the following parameters:
    # kwargs has to contain "privatedata" with the path to a tar-file.
    # The tar-file has to contain Page-xml-files without subfolders.
    # The TextEquiv of the lines have to be the ground truth for the
    # competition.
    # kwargs also has to contain "resultdata",
    # which is the path to the tar-file containing the hypothesises of the
    # competitor.
    # kwargs can contain a path "tmpfolder" - all temporary files and folder
    # are created there.
    # the folder will be deleted afterwards, when it did not exist before.
    # Otherwise only the containing files and folders are deleted.

    folder_data = kwargs.pop('tmpfolder', normpath(abspath(".")))
    folder_exec = kwargs.pop("execpath",
                             join(normpath(abspath(".")),
                                  "executables/TranskribusErrorRate"))
    privatedata = kwargs.pop('privatedata', "gt.tgz")
    resultdata = kwargs.pop('resultdata', "hyp.tgz")
    print("privatedata is '"+privatedata+"'.")
    print("resultdata is '" + resultdata+"'.")
    print("folder_exec is '" + folder_exec+"'.")
    params = kwargs.pop("params", "")
    file_exec = join(folder_exec, 'TranskribusErrorRate.jar')

    data_lists = {}
    to_remove_folder = []
    to_remove_file = []
    deleteroot = False
    if not (isdir(folder_data)):
        print("folder have to be deleted")
        deleteroot = True
    for (file_tar, prefix) in [[privatedata, "gt"], [resultdata, "hyp"]]:
        print("execute '" + file_tar + "' ...")
        folder_xmls = join(folder_data, prefix + '_dir')
        print(folder_xmls)
        if isdir(folder_xmls):
            rmtree(folder_xmls)
        makedirs(folder_xmls)  # , exist_ok=True)
        to_remove_folder += [folder_xmls]
        print("unpack tar-file ...")
        obj_tar = tarfile.open(file_tar)
        obj_tar.extractall(folder_xmls)
        obj_tar.close()
        print("unpack tar-file ... [DONE]")
        print("save list ...")
        files_xml = sorted(listdir(folder_xmls))
        file_list_xml = join(folder_data, prefix + '.lst')
        to_remove_file += [file_list_xml]
        data_lists[file_tar] = file_list_xml
        with open(file_list_xml, 'w') as tfFile:
            for file_xml in files_xml:
                tfFile.write(join(folder_xmls, file_xml)+"\n")
#                print(join(folder_xmls, file_xml), file=tfFile)
        print("save list ... [DONE] (to '"+file_list_xml+"')")
    if (deleteroot):
        to_remove_folder += [folder_data]

    executable = 'java -cp {} eu.transkribus.errorrate.ErrorRateParser'.format(
        file_exec)
    commandline = '{} {} {} {}'.format(
        executable, params, data_lists[privatedata], data_lists[resultdata])
    print(commandline)
#    command_output = "tryrun"
    command_output = cmdline(commandline)
    print("output of algorithm:")
    print(command_output)
    print("output of algorithm: [DONE]")
    for file in to_remove_file:
        print("remove '"+file+"'")
        remove(file)
    for folder in to_remove_folder:
        print("remove '"+folder+"'")
        rmtree(folder)
    rgx = r'.*SUB = ([\d\.]+).*\nDEL = ([\d\.]+).*\nINS '\
        '= ([\d\.]+).*\nERR = ([\d\.]+).*'
    r = re.search(rgx, command_output)
    result = {
        'ERR': r.group(4).encode("utf-8"),
        'INS': r.group(3).encode("utf-8"),
        'DEL': r.group(2).encode("utf-8"),
        'SUB': r.group(1).encode("utf-8"),
    }
    return result


def icfhr16_HTR_tool(*args, **kwargs):
    print("icfhr16_HTR_tool")
    executable_folder = '{}/competitions/executables/'\
        'EvaluationCERandWER'.format(settings.BASE_DIR)
    resultdata = kwargs.pop('resultdata', executable_folder)
    privatedata = kwargs.pop('privatedata',
                             '{}/gt.zip'.format(executable_folder))

    print(resultdata)
    print(privatedata)

    executable = '{}/Create_WER-PAGE.sh'.format(executable_folder)
    commandline = '{} {} {}'.format(executable, resultdata, privatedata)
    print(commandline)

    command_output = cmdline(commandline)

    rgx = r'([\d\.]+)\n+([\d\.]+)'
    r = re.search(rgx, command_output)
    result = {
        'CER':             r.group(1),
        'WER':             r.group(2),
    }
    print(result)
    return result


def icdar2017_writer_identification(*args, **kwargs):
    print("ICDAR 2017 Writer Identification")
    print(str(kwargs))
    executable_folder = \
        '{}/competitions/executables/ICDAR2017WriterIdentification'\
        .format(settings.BASE_DIR)
    resultdata = kwargs.pop('resultdata', executable_folder)
    privatedata = kwargs.pop('privatedata',
                             '{}/gtfile.txt'.format(executable_folder))

    print(resultdata)
    print(privatedata)

    executable = '{}/evaluation.py'.format(executable_folder)
    commandline = '{} {} {}'.format(executable, privatedata +
                                    '/gtfile.csv', resultdata)
    print(commandline)

    command_output = cmdline(commandline)

    rgx = r'([\d\.]+)\n+([\d\.]+)'
    r = re.search(rgx, command_output)
    result = {
        'WI-precision': r.group(1),
        'WI-map': r.group(2),
    }
    command_output = re.sub(rgx, "", command_output)
    print(result)
    return (result, command_output)


def icdar17_BLEU_tool(*args, **kwargs):
    print("icdar17_BLEU_tool")
    executable_folder = '{}/competitions/executables/'\
        'EvaluationBLEU'.format(settings.BASE_DIR)
    resultdata = kwargs.pop('resultdata', executable_folder)
    privatedata = kwargs.pop('privatedata',
                             '{}/gt.zip'.format(executable_folder))

    print(resultdata)
    print(privatedata)

    executable = '{}/Create_BLEU-PAGE.sh'.format(executable_folder)
    commandline = '{} {} {}'.format(executable, resultdata, privatedata)
    print(commandline)

    command_output = cmdline(commandline)

    print("output of algorithm:")
    print(command_output)
    print("output of algorithm: [DONE]")

    rgx = r'BLEU = ([\d\.]+), .*'

    r = re.search(rgx, command_output)
    result = {
        'BLEU':             r.group(1),
    }
    print(result)
    return result


