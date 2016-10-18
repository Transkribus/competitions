from random import random
from time import sleep
import sys
import StringIO
from os import listdir, makedirs, remove
from os.path import splitext, isdir, join,abspath,normpath,basename
from shutil import copyfile, rmtree
from subprocess import PIPE, Popen
from uuid import uuid4
from json import dumps
import re
import tarfile

def cmdline(command, *args, **kwargs):
    # http://stackoverflow.com/questions/3503879/assign-output-of-os-system-to-a-variable-and-prevent-it-from-being-displayed-on
    # http://stackoverflow.com/questions/17615414/how-to-convert-binary-string-to-normal-string-in-python3
    # http://stackoverflow.com/questions/13744473/command-line-execution-in-different-folder
    cwd = kwargs.pop('cwd', None)
    process = Popen(
        command,
        stdout=PIPE,
        shell=True,
        cwd=cwd,
    )
    res = process.communicate()[0]
    return res.decode('utf-8')

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
    #folder_exec = join(settings.BASE_DIR,"competitions/executables/TranskribusBaseLineMetricTool")
    folder_exec = join(normpath(abspath(".")),"executables/TranskribusErrorRate")
    folder_exec = normpath(abspath(".."))
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
    out=sys.stdout
    #command_output = "tryrun"
    command_output = cmdline(commandline)
    print(out)
    print("output of algorithm:")
    print(command_output)
    print("output of algorithm: [DONE]")
    for file in to_remove_file:
        print("remove '"+file+"'")
#        os.remove(file)
    for folder in to_remove_folder:
        print("remove '"+folder+"'")
#        rmtree(folder)
    rgx = r'.*SUB = ([\d\.]+).*\nDEL = ([\d\.]+).*\nINS = ([\d\.]+).*\nCER = ([\d\.]+).*'
    r = re.search(rgx, command_output)
    result = {
    'CER': r.group(4),
    'INS': r.group(3),
    'DEL': r.group(2),
    'SUB': r.group(1),
    }
    return result

transkribusErrorRate()