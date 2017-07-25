#!/usr/bin/env python
"""Evaluation Protocol for the ICDAR 2017 Writer Identification Competition on
Historical Data

This script evaluates the results submitted to ScriptNet

"""
import logging

__author__ = "Stefan Fiel"
__copyright__ = "Copyright 2017, Computer Vision Lab, TU Wien"
__credits__ = "Stefan Fiel"
__license__ = "GPLv3"
__version__ = "0.2"
__maintainer__ = "Stefan Fiel"
__email__ = "fiel@caa.tuwien.ac.at"
__status__ = "Production"

OUTPUT_NAME = "Historical-WI Evaluation"

logging.basicConfig(level=logging.INFO, format=OUTPUT_NAME +
                    ' %(levelname)s %(message)s')

logger = logging.getLogger()


def parse_gt_file(file):
    import re

    file = open(file, "r")

    gt = {}
    writer = {}
    writer_list = []
    for line in file:
        line = line.rstrip('\n')
        split = line.split('=')
        if len(split) != 2:
            print('syntax of GT file incorrect: ' + line)
            logger.error('syntax of GT file incorrect: ' + line)
            return 0, 0, 0
        gt[split[0]] = split[1]
        # w = re.split('_|-', s[1])
        w = re.split('[_-]', split[1])
        if len(w) == 0:
            print('syntax of GT file incorrect: ' + line)
            logger.error('syntax of GT file incorrect: ' + line)
            return 0, 0, 0

        writer[split[0]] = w[0]
        writer_list.append(w[0])
        
    file.close()

    uniq_writer = list(set(writer_list))
    writer_count = []
    for w in uniq_writer:
        writer_count.append(writer_list.count(w))

    if  len(list(set(writer_count))) != 1:
        print('writers in GT not equally distributed')
        logger.error('writers in GT not equally distributed')
        return 0,0
    return gt, writer, writer_count[0]


def evaluate(writer, result_file, pages_per_writer):
    file = open(result_file, "r")

    page_count = 0
    top1_count = 0

    soft_count = [0] * len(writer)
    hard_count = [0] * len(writer)
    perc_count = [0] * len(writer)

    average_precision = []
    line_count = 0
    for line in file:
        line_count += 1

        line = line.rstrip()
        imgs = line.split(',')

        ref_page = imgs.pop(0)

        if ref_page not in writer:
            print('filename \"' + ref_page + '\" unkown')
            logger.error('filename \"' + ref_page + '\" unkown')
            return 0, 0, 0, 0, 0


        ref_writer = writer[ref_page]
        logger.debug("ref_writer:" + ref_writer + " ref_page:" + ref_page)
        if ref_writer == writer[imgs[0]]:
            top1_count = top1_count + 1
        i_count = 0
        i_true = 0
        cur_sum = 0
        for i in imgs:
            i_count = i_count + 1
            if writer[i] == ref_writer:
                i_true = i_true + 1
                cur_sum = cur_sum + float(i_true)/i_count
            if i_true > 0:
                if i_count < len(soft_count):
                    soft_count[i_count] += 1
            if i_true == i_count:
                if i_count < len(hard_count):
                    hard_count[i_count] += 1
            if i_count < len(perc_count):
                perc_count[i_count] += i_true
        # +1 because reference page is not counted
        if i_count + 1 != len(writer):
            print('line %d contains %d pages, instead of %d' % (line_count, i_count + 1, len(writer)))
            logger.error('line %d contains %d pages, instead of %d' % (line_count, i_count + 1, len(writer)))
            return 0, 0, 0, 0, 0

        page_count = page_count + 1
        if i_true != 0:
            average_precision.append(float(cur_sum)/(pages_per_writer-1))
        else:
            average_precision.append(0)

    file.close()
    soft_eval = [x / len(writer) for x in soft_count]
    hard_eval = [x / len(writer) for x in hard_count]
    perc_eval = [0] * len(writer)
    for i,p in enumerate(perc_count):
        if i == 0:
            continue
        perc_eval[i] = p / (len(writer) * i)

    if line_count != len(writer):
        print('result file does not the correct line number (lines in result file: %d, lines in GT: %d' % (
            line_count, len(writer)))
        logger.error('result file does not the correct line number (lines in result file: %d, lines in GT: %d' % (
            line_count, len(writer)))
        return 0, 0, 0, 0, 0
    logger.debug("top1_count:" + str(top1_count))
    logger.debug("page_count:" + str(page_count))
    prec = float(top1_count)/len(writer)
    mean_ap = float(sum(average_precision))/float(len(writer))
    return prec, mean_ap, soft_eval, hard_eval, perc_eval

if __name__ == "__main__":
    import argparse
    import os.path
    import zipfile
    import tempfile
    import shutil

    logger.setLevel(logging.ERROR)
    logger.debug("starting")
    parser = argparse.ArgumentParser(
        description='evaluation the result files submitted via ScriptNet ' +
        'of the ICDAR 2017 Historic-WI')

    parser.add_argument('gtfile', metavar='[GT file]', help='' +
                        'GroundTruth file of the competition with mapping' +
                        '[obfuscated filename]=[real filename]. Real ' +
                        'Filename must look like [writerId]_....')
    parser.add_argument('resultfile', metavar='[result file]', help='' +
                        'Result file submitted for 2017 Historical-WI')

    args = parser.parse_args()

    cur_gt = None
    cur_writer = None
    writer_pages = 0

    if not os.path.isfile(args.gtfile):
        print('0\n0')
        print('GT file does not exist')
        logger.error("GT file does not exist!")
        exit(0)
    else:
        cur_gt, cur_writer, writer_pages = parse_gt_file(args.gtfile)

    if not os.path.isfile(args.resultfile):
        print('0\n0')
        print('result file does not exist!')
        logger.error("result file does not exist!")
        exit(0)
    else:
        res_file = args.resultfile
        tmp_dir = None
        if zipfile.is_zipfile(res_file):
            tmp_dir = tempfile.mkdtemp()
            with zipfile.ZipFile(args.resultfile) as fzip:
                files_in_zip = fzip.namelist()
                fzip.extract(files_in_zip[0], tmp_dir)
                res_file = os.path.join(tmp_dir, files_in_zip[0])

        precision, meanap, soft, hard, perc = evaluate(cur_writer, res_file, writer_pages)
        print('%.6f' % precision)
        print('%.6f' % meanap)

        logger.info("precision:" + str(precision))
        logger.info("map:" + str(meanap))

        if precision != 0 and meanap != 0:
            soft_output = [1, 2, 3, 4, 5, 6]
            out_str1 = ''
            out_str2 = ''
            for s in soft_output:
                out_str1 += 'Top %d\t' % s
                out_str2 += '%.3f\t' % soft[s]
            logger.info('soft evaluation')
            logger.info(out_str1)
            logger.info(out_str2)

            hard_output = [1, 2, 3, 4]
            out_str1 = ''
            out_str2 = ''
            for s in hard_output:
                out_str1 += 'Top %d\t' % s
                out_str2 += '%.3f\t' % hard[s]
            logger.info('hard evaluation')
            logger.info(out_str1)
            logger.info(out_str2)

            perc_output = [2, 3, 4]
            out_str1 = ''
            out_str2 = ''
            for s in perc_output:
                out_str1 += 'Top %d\t' % s
                out_str2 += '%.3f\t' % perc[s]
            logger.info('perc evaluation')
            logger.info(out_str1)
            logger.info(out_str2)

        if zipfile.is_zipfile(args.resultfile):
            shutil.rmtree(tmp_dir)
