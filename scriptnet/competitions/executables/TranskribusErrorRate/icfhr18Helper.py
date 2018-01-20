from os import listdir, makedirs, remove
from os.path import isdir, isfile, join, basename
from shutil import rmtree
import re
import tarfile
from competitions.evaluators import cmdline


def calc_error_rates(folder_data, folder_exec, privatedata, resultdata):
    print("privatedata is '" + privatedata + "'.")
    print("resultdata is '" + resultdata + "'.")
    print("folder_exec is '" + folder_exec + "'.")
    file_exec = join(folder_exec, 'TranskribusErrorRate-2.2.3-with-dependencies.jar')

    to_remove_folder = []
    to_remove_file = []
    delete_root = False
    if not (isdir(folder_data)):
        print("folder have to be deleted")
        delete_root = True
    (gt_dict, to_remove_folder) = fill_dict(privatedata, "gt", folder_data, to_remove_folder)
    (hyp_dict, to_remove_folder) = fill_dict(resultdata, "hyp", folder_data, to_remove_folder)

    doc_ids = []
    pages = []
    command_output = ""

    # parse dicts
    for file_id in gt_dict:
        split = file_id.replace('.', '_').split("_")
        num_of_pages = split[1]
        doc_id = split[0]
        if doc_id not in doc_ids:
            doc_ids.append(doc_id)
        if num_of_pages not in pages:
            pages.append(num_of_pages)

        gt_file_name_did = join(folder_data, "tmp_gt_doc_" + doc_id + ".txt")
        hyp_file_name_did = join(folder_data, "tmp_hyp_doc_" + doc_id + ".txt")
        gt_file_name_pages = join(folder_data, "tmp_gt_" + num_of_pages + ".txt")
        hyp_file_name_pages = join(folder_data, "tmp_hyp_" + num_of_pages + ".txt")
        gt_file_name_total = join(folder_data, "tmp_gt.txt")
        hyp_file_name_total = join(folder_data, "tmp_hyp.txt")

        for file in [gt_file_name_did, gt_file_name_pages, gt_file_name_total, hyp_file_name_did, hyp_file_name_pages,
                     hyp_file_name_total]:
            if file not in to_remove_file:
                to_remove_file.append(file)

        cur_gt_dict = gt_dict[file_id]
        cur_hyp_dict = hyp_dict[file_id]

        with open(gt_file_name_did, 'a') as gtDocFile, open(hyp_file_name_did, 'a') as hypDocFile, open(
                gt_file_name_pages, 'a') as gtPagesFile, \
                open(hyp_file_name_pages, 'a') as hypPagesFile, open(gt_file_name_total, 'a') as gtFile, open(
            hyp_file_name_total, 'a') as hypFile:
            for key in cur_gt_dict.keys():
                text_gt = cur_gt_dict[key]
                text_hyp = ""
                if key not in cur_hyp_dict:
                    cur_hyp_dict.update({key: ""})
                    text_hyp = "\n"
                else:
                    text_hyp = cur_hyp_dict[key]

                gtDocFile.write(text_gt)
                hypDocFile.write(text_hyp)
                gtPagesFile.write(text_gt)
                hypPagesFile.write(text_hyp)
                gtFile.write(text_gt)
                hypFile.write(text_hyp)
        if len(cur_gt_dict) != len(cur_hyp_dict):
            message = "WARNING: Some line ids in hypotheses of file {} are not in ground truth.\n".format(file_id)
            print(message)
            command_output += message

    command_output += "\nResults per additional specific training pages:\n"
    for page in sorted([int(x) for x in pages]):
        gt_file_name = join(folder_data, "tmp_gt_" + str(page) + ".txt")
        hyp_file_name = join(folder_data, "tmp_hyp_" + str(page) + ".txt")
        r, command_output = get_result(file_exec, gt_file_name, hyp_file_name, command_output, False)
        command_output += "{:<11d}: {:.6f} \n".format(page, float(r.group(1)))

    command_output += "\nResults per test collection:\n"
    for doc_id in sorted(doc_ids):
        gt_file_name = join(folder_data, "tmp_gt_doc_" + doc_id + ".txt")
        hyp_file_name = join(folder_data, "tmp_hyp_doc_" + doc_id + ".txt")
        r, command_output = get_result(file_exec, gt_file_name, hyp_file_name, command_output, False)
        command_output += "{:11s}: {:.6f} \n".format(doc_id, float(r.group(1)))

    gt_file_name = join(folder_data, "tmp_gt.txt")
    hyp_file_name = join(folder_data, "tmp_hyp.txt")
    r, command_output = get_result(file_exec, gt_file_name, hyp_file_name, command_output, True)
    command_output += "\n{:11s}: {:.6f} \n".format("total error", float(r.group(1)))

    print("output of algorithm:")
    print(command_output)
    print("output of algorithm: [DONE]")

    # tidy up everything
    if delete_root:
        to_remove_folder += [folder_data]
    for file in to_remove_file:
        print("remove '" + file + "'")
        remove(file)
    for folder in to_remove_folder:
        print("remove '" + folder + "'")
        rmtree(folder)

    result = {
        'CER': r.group(1),
        'INS': r.group(3),
        'DEL': r.group(2),
        'SUB': r.group(4),
    }
    return result, command_output


def get_result(file_exec, gt_file_name, hyp_file_name, command_output, addToOutput):
    executable = 'java -cp {} eu.transkribus.errorrate.HtrErrorTxt -n -d'.format(
        file_exec)
    commandline = '{} {} {}'.format(executable, gt_file_name, hyp_file_name)

    # print(commandline)
    tmp_output = cmdline(commandline)
    if addToOutput:
        command_output = "Detailed confusion map: \n{}\n{}".format(tmp_output, command_output)

    rgx = r'.*ERR=([\d\.E+-]+).*\nDEL=([\d\.E+-]+).*\nINS=([\d\.E+-]+).*\nSUB=([\d\.E+-]+).*\n.*'
    r = re.search(rgx, tmp_output)

    return r, command_output


def fill_dict(file_tar, prefix, folder_data, to_remove_folder):
    # helper function for icfhr18_atr_tool
    print("execute '" + file_tar + "' ...")
    folder_txt = join(folder_data, prefix + '_dir')
    print(folder_txt)
    if isdir(folder_txt):
        rmtree(folder_txt)
    makedirs(folder_txt)  # , exist_ok=True)
    to_remove_folder += [folder_txt]
    print("unpack tar-file ...")
    obj_tar = tarfile.open(file_tar)
    obj_tar.extractall(folder_txt)
    obj_tar.close()
    print("unpack tar-file ... [DONE]")
    print("fill dict ...")
    files_txt = sorted(listdir(folder_txt))
    dictionary = {}
    for file_txt in files_txt:
        texts = []
        line_ids = []
        # print(join(folder_txt, file_txt))
        # print(path.isfile(join(folder_txt, file_txt)))
        with open(join(folder_txt, file_txt), 'r+') as tfFile:
            for line in tfFile:
                split = line.split(" ", 1)
                line_id = split[0]
                text = split[1]
                line_ids.append(line_id)
                texts.append(text)
        d = dict(zip(line_ids, texts))
        dictionary[basename(file_txt)] = d
    return dictionary, to_remove_folder
