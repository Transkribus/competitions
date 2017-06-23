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


def parseGTFile(gtfile):
    import re

    file = open(gtfile, "r")

    gt = {}
    writer = {}
    for line in file:
        line = line.rstrip('\n')
        s = line.split('=')
        if len(s) != 2:
            print('syntax of GT file incorrect: ' + line)
            logger.error('syntax of GT file incorrect: ' + line)
            return 0, 0
        gt[s[0]] = s[1]
        w = re.split('_|-', s[1])
        if len(w) == 0:
            print('syntax of GT file incorrect: ' + line)
            logger.error('syntax of GT file incorrect: ' + line)
            return 0, 0

        writer[s[0]] = w[0]
    file.close()
    return gt, writer


def evaluate(writer, resultfile):
    file = open(resultfile, "r")

    page_count = 0
    top1_count = 0

    average_precision = []
    for line in file:

        line = line.rstrip()
        imgs = line.split(',')

        ref_page = imgs.pop(0)

        if ref_page not in writer:
            print('filename \"' + ref_page + '\" unkown')
            logger.error('filename \"' + ref_page + '\" unkown')
            return 0, 0

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
                cur_sum = cur_sum + (float)(i_true)/i_count

        page_count = page_count + 1
        if i_true != 0:
            average_precision.append((float)(cur_sum)/i_true)
        else:
            average_precision.append(0)

    file.close()
    logger.debug("top1_count:" + str(top1_count))
    logger.debug("page_count:" + str(page_count))
    precision = (float)(top1_count)/len(writer)
    meanap = float(sum(average_precision))/float(len(writer))
    return precision, meanap

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

    if not os.path.isfile(args.gtfile):
        print('0\n0')
        print('GT file does not exist')
        logger.error("GT file does not exist!")
        exit(0)
    else:
        gt, writer = parseGTFile(args.gtfile)

    if not os.path.isfile(args.resultfile):
        print('0\n0')
        print('result file does not exist!')
        logger.error("result file does not exist!")
        exit(0)
    else:
        res_file = args.resultfile
        if zipfile.is_zipfile(res_file):
            tmp_dir = tempfile.mkdtemp()
            with zipfile.ZipFile(args.resultfile) as fzip:
                files_in_zip = fzip.namelist()
                fzip.extract(files_in_zip[0], tmp_dir)
                res_file = os.path.join(tmp_dir, files_in_zip[0])

        precision, meanap = evaluate(writer, res_file)
        logger.info("precision:" + str(precision))
        logger.info("map:" + str(meanap))
        print('%.6f' % precision)
        print('%.6f' % meanap)
        if zipfile.is_zipfile(args.resultfile):
            shutil.rmtree(tmp_dir)
