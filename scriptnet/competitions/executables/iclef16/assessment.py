#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import argparse
import math
import re
import sys

from osgeo import ogr

BB_RE=r'(?:\d+:\d+x\d+\+\d+\+\d+)'
MATCHES_RE=r'(?:(%s)(?:\/(%s))?)' % (BB_RE, BB_RE)
FLOAT_RE=r'[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?'


class MultiBoundingBox(object):
    @staticmethod
    def _box2polygon(box):
        assert isinstance(box, tuple) and len(box) == 5
        w, h, x, y = box[1:]
        return 'POLYGON ((%f %f, %f %f, %f %f, %f %f, %f %f))' % (
            x, y,           # left-top
            x + w, y,       # right-top
            x + w, y + h,   # right-bottom
            x, y + h,       # left-bottom
            x, y)           # left-top (CLOSE)

    def __init__(self, parent_match, *args):
        assert parent_match is not None
        assert len(args) >= 1
        self._pm = parent_match
        self._boxes = {}
        for box in args:
            assert box is not None
            geo = ogr.CreateGeometryFromWkt(MultiBoundingBox._box2polygon(box))
            if box[0] in self._boxes:
                self._boxes[box[0]] = self._boxes[box[0]].Union(geo)
            else:
                self._boxes[box[0]] = geo

    @property
    def qid(self):
        return self._pm.qid

    @property
    def sid(self):
        return self._pm.sid

    @property
    def score(self):
        return self._pm.score

    @property
    def area(self):
        return sum(box.GetArea() for box in self._boxes.itervalues())

    def intersection_area(self, other):
        '''Area of the intersection of two multiboxes.'''
        area = 0.0
        pages = set(self._boxes.keys() + other._boxes.keys())
        for page in pages:
            s_boxes = self._boxes.get(page, None)
            o_boxes = other._boxes.get(page, None)
            if s_boxes and o_boxes:
                area += s_boxes.Intersection(o_boxes).GetArea()
        return area

    def union_area(self, other):
        '''Area of the union of two multiboxes. Takes into account that the
        multibox can be splitted into multiple pages.'''
        area = 0.0
        pages = set(self._boxes.keys() + other._boxes.keys())
        for page in pages:
            s_boxes = self._boxes.get(page, None)
            o_boxes = other._boxes.get(page, None)
            if s_boxes and o_boxes:
                area += s_boxes.Union(o_boxes).GetArea()
            elif s_boxes:
                area += s_boxes.GetArea()
            else:
                area += o_boxes.GetArea()
        return area


class WordMatch(object):
    def __init__(self, parent_match):
        assert parent_match is not None
        self._pm = parent_match
        self._boxes = []

    @property
    def qid(self):
        return self._pm.qid

    @property
    def sid(self):
        return self._pm.sid

    @property
    def score(self):
        return self._pm.score

    def add_splitted_box(self, box1, box2):
        assert box1 is not None
        if box2 is None:
            self._boxes.append(MultiBoundingBox(self, box1))
        else:
            self._boxes.append(MultiBoundingBox(self, box1, box2))

    def __iter__(self):
        for x in self._boxes:
            yield x

    def __len__(self):
        return len(self._boxes)


class QueryMatch(object):
    def __init__(self, qid, sid, score):
        assert isinstance(qid, int)
        assert isinstance(sid, int)
        assert isinstance(score, float)
        self._qid = qid
        self._sid = sid
        self._score = score
        self._words = []

    @property
    def qid(self):
        return self._qid

    @property
    def sid(self):
        return self._sid

    @property
    def score(self):
        return self._score

    def add_word_match(self):
        self._words.append(WordMatch(self))
        return self._words[-1]

    def __lt__(self, other):
        assert isinstance(other, QueryMatch)
        return (self._score, self._qid, self._sid) < \
            (other._score, other._qid, other._sid)

    def __le__(self, other):
        assert isinstance(other, QueryMatch)
        return (self._score, self._qid, self._sid) <= \
            (other._score, other._qid, other._sid)

    def __gt__(self, other):
        assert isinstance(other, QueryMatch)
        return (self._score, self._qid, self._sid) > \
            (other._score, other._qid, other._sid)

    def __ge__(self, other):
        assert isinstance(other, QueryMatch)
        return (self._score, self._qid, self._sid) >= \
            (other._score, other._qid, other._sid)

    def __iter__(self):
        for x in self._words:
            yield x

    def __len__(self):
        return len(self._words)

    def __getitem__(self, i):
        return self._words[i]


class Solution(object):
    '''Class representing a solution file (including the reference solution,
    a.k.a. the ground-truth).

    It reads a text file formated as specified in the task webpage
    (http://www.imageclef.org/2016/handwritten). Performs basic validations
    and will raise an exception if any error is found in the solution file.
    '''
    def __init__(self, line2page, f=None):
        assert line2page is not None
        self._line2page = line2page
        self._file = None
        self._lnum = None
        self._line = None
        self._matches = []
        self._matches_by_qid_sid = {}
        if f is not None:
            self.read(f)

    def _next(self):
        assert self._file is not None
        self._line = self._file.readline()
        if self._line == '':
            return False
        else:
            self._lnum += 1
            return True

    def _err(self, msg):
        return '%s, see line %s:%d' % (msg, self._file.name, self._lnum)

    def read(self, f):
        if isinstance(f, str) or isinstance(f, unicode):
            f = open(f, 'r')
        self._file, self._lnum = f, 0
        seen_splitted_words = False
        while self._next():
            line = self._line.strip()
            # Skip comments
            if line[0] == '#': continue
            line = line.split()
            assert len(line) >= 4, \
                self._err('Missing fields (%d vs 4)' % len(line))
            assert re.match(r'^\d+$', line[0]), \
                self._err('Query ID must be an integer')
            assert re.match(r'^\d+$', line[1]), \
                self._err('Segment ID must be an integer')
            assert re.match('^(?:%s|-)$' % FLOAT_RE, line[2]), \
                self._err('Score must be a valid floating point number')
            qid, sid = int(line[0]), int(line[1])
            score = float('-inf') if line[2] == '-' else float(line[2])
            query_match = QueryMatch(qid, sid, score)
            for item_matches in line[3:]:
                word_match = query_match.add_word_match()
                bb_matches = item_matches.split(',')
                for bb in bb_matches:
                    m = re.match(r'^%s$' % MATCHES_RE, bb)
                    assert m, self._err('Invalid bounding box')
                    b1, b2 = m.groups()
                    b1 = map(lambda x: int(x), re.match(
                        '^(\d+):(\d+)x(\d+)\+(\d+)\+(\d+)$', b1).groups())
                    assert b1[0] >= sid and b1[0] <= sid+5, \
                        self._err('Line of bounding box %d outside ' \
                                  'corresponding segment %d' % (b1[0], sid))
                    assert b1[0] in self._line2page, \
                        self._err('Line image not found %d' % b1[0])
                    b1[0] = self._line2page[b1[0]]
                    b1 = tuple(b1)
                    if b2:
                        b2 = map(lambda x: int(x), re.match(
                            '^(\d+):(\d+)x(\d+)\+(\d+)\+(\d+)$', b2).groups())
                        assert b2[0] >= sid and b2[0] <= sid+5, \
                            self._err('Line of bounding box %d outside ' \
                                      'corresponding segment %d' % (b2[0], sid))
                        assert b2[0] in self._line2page, \
                            self._err('Line image not found %d' % b2[0])
                        b2[0] = self._line2page[b2[0]]
                        b2 = tuple(b2)
                        seen_splitted_words = True
                    word_match.add_splitted_box(b1, b2)
            self._matches.append(query_match)
            self._matches_by_qid_sid[(query_match.qid, query_match.sid)] = \
                query_match

        if not seen_splitted_words:
            sys.stderr.write('WARNING: The solution file %s does not ' \
                             'contain any hyphened word!\n' % self._file.name)
        self._file.close()
        self._matches.sort(reverse=True)
        self._file, self._lnum, self._line = None, None, None

    def __iter__(self):
        for x in self._matches:
            yield x

    def __contains__(self, x):
        return x in self._matches_by_qid_sid

    def __getitem__(self, x):
        if isinstance(x, int):
            return self._matches[x]
        else:
            return self._matches_by_qid_sid[x]

    def iteritems(self):
        for x in self._matches_by_qid_sid.iteritems():
            yield x

    def iterkeys(self):
        for x in self._matches_by_qid_sid.iterkeys():
            yield x

    def itervalues(self):
        for x in self._matches_by_qid_sid.itervalues():
            yield x


class Assessment(object):
    '''Class that computes different metrics using a reference and hypothesis
    solutions.

    All the computation is carried in the constructor, and then the different
    metrics can be accessed by properties of the object.
    '''
    def __init__(self, refs, hyps, interpolate=True, trapezoid=True):
        assert isinstance(refs, Solution)
        assert isinstance(hyps, Solution)
        # Collect stats about true positives, false positives, false negatives,
        # etc at different score thresholds.
        segment_stats, boxes_stats, segment_stats_query, boxes_stats_query = \
            self._collect_stats(refs, hyps)
        # Compute segment-level Global Precision-Recall curve and AP
        self._segment_prc, self._segment_ap = \
            self._compute_pr_curve_and_ap(segment_stats, interpolate, trapezoid)
        # Compute segment-level Global NDCG
        self._segment_ndcg = self._compute_ndcg(segment_stats)
        # Compute box-level Global Precision-Recall curve and AP
        self._boxes_prc, self._boxes_ap = \
            self._compute_pr_curve_and_ap(boxes_stats, interpolate, trapezoid)
        # Compute box-level Global NDCG
        self._boxes_ndcg = self._compute_ndcg(boxes_stats)
        # Compute segment-level Mean Precision-Recall curve and AP
        self._segment_mean_prc, self._segment_mean_ap = \
            self._compute_mean_pr_curve_and_ap(segment_stats_query,
                                               interpolate, trapezoid)
        # Compute segment-level Mean NDCG
        self._segment_mean_ndcg = self._compute_mean_ndcg(segment_stats_query)
        # Compute boxes-level Mean Precision-Recall curve and AP
        self._boxes_mean_prc, self._boxes_mean_ap = \
            self._compute_mean_pr_curve_and_ap(boxes_stats_query,
                                               interpolate, trapezoid)
        # Compute segment-level Mean NDCG
        self._boxes_mean_ndcg = self._compute_mean_ndcg(boxes_stats_query)

    @property
    def segment_global_ap(self):
        return self._segment_ap

    @property
    def segment_mean_ap(self):
        return self._segment_mean_ap

    @property
    def segment_global_ndcg(self):
        return self._segment_ndcg

    @property
    def segment_mean_ndcg(self):
        return self._segment_mean_ndcg

    @property
    def boxes_global_ap(self):
        return self._boxes_ap

    @property
    def boxes_mean_ap(self):
        return self._boxes_mean_ap

    @property
    def boxes_global_ndcg(self):
        return self._boxes_ndcg

    @property
    def boxes_mean_ndcg(self):
        return self._boxes_mean_ndcg

    @staticmethod
    def _add_to_dict_list(d, k, v):
        l = d.get(k, None)
        if l is None:
            d[k] = [v]
        else:
            l.append(v)

    @staticmethod
    def _collect_stats(refs, hyps):
        segment_stats, boxes_stats = [], []
        segment_stats_query, boxes_stats_query = {}, {}
        unmatched_ref_segments = set(refs.iterkeys())
        unmatched_ref_boxes = []
        for k, hyp in enumerate(hyps):
            # If the score has changed respect the previous hypothesis, add a
            # new bin to accumulate statistics.
            if k == 0 or hyp.score != hyps[k - 1].score:
                segment_stats.append([0.0, 0.0, 0.0])
                boxes_stats.append([0.0, 0.0, 0.0])
                if hyp.qid in segment_stats_query:
                    segment_stats_query[hyp.qid].append([0.0, 0.0, 0.0])
                    boxes_stats_query[hyp.qid].append([0.0, 0.0, 0.0])
                else:
                    segment_stats_query[hyp.qid] = [[0.0, 0.0, 0.0]]
                    boxes_stats_query[hyp.qid] = [[0.0, 0.0, 0.0]]

            # Check whether the hypothesis is in the reference (TP) or not (FP)
            if (hyp.qid, hyp.sid) in unmatched_ref_segments:
                ref = refs[(hyp.qid, hyp.sid)]
                # Segment-level true positive
                segment_stats[-1][0] += 1.0
                if hyp.qid in segment_stats_query:
                    segment_stats_query[hyp.qid][-1][0] += 1
                else:
                    segment_stats_query[hyp.qid] = [[1.0, 0, 0]]
                # References can only be matched once
                unmatched_ref_segments.remove((hyp.qid, hyp.sid))
                # The number of words in the query must be the same as the
                # the reference.
                assert len(hyp) == len(ref), \
                    ('There is a mismatch in the number of words of query ' + \
                     '%d in segment %d: %d vs. %d (hyp vs. ref)') % (
                         hyp.qid, hyp.sid, len(hyp), len(ref))
                for i in xrange(len(hyp)):
                    pending_ref_boxes = set(ref[i])
                    pending_hyp_boxes = set(hyp[i])
                    overlaps = [(hb.intersection_area(rb), hb.union_area(rb),
                                 hb, rb) for hb in hyp[i] for rb in ref[i]]
                    overlaps.sort(cmp=lambda x, y: \
                                  (x[0] / x[1]) > (y[0] / y[1]))
                    for inter_area, union_area, hyp_box, ref_box in overlaps:
                        # Skip matched boxes
                        if ref_box not in pending_ref_boxes: continue
                        if hyp_box not in pending_hyp_boxes: continue
                        tp = inter_area / union_area
                        fp = 1.0 - inter_area / hyp_box.area
                        fn = 1.0 - inter_area / ref_box.area
                        if tp > 0.0:
                            # If there is some overlapping between the two
                            # boxes, remove these from the pending sets and
                            # compute the True Positive, False Positive and
                            # False Negative ratios. These ratios are used to
                            # avoid dealing with a threshold to determine a
                            # how much overlapping is required.
                            pending_ref_boxes.remove(ref_box)
                            pending_hyp_boxes.remove(hyp_box)
                            boxes_stats[-1][0] += tp
                            boxes_stats[-1][1] += fp
                            boxes_stats[-1][2] += fn
                            if hyp.qid in boxes_stats_query:
                                boxes_stats_query[hyp.qid][-1][0] += tp
                                boxes_stats_query[hyp.qid][-1][1] += fp
                                boxes_stats_query[hyp.qid][-1][2] += fn
                            else:
                                boxes_stats_query[hyp.qid]=[[tp, fp, fn]]
                        else:
                            # If the overlaping area is 0.0, we are done, since
                            # the next iterations the overlapping area will be
                            # 0.0 as well.
                            break
                    for box in pending_hyp_boxes:
                        # Box-level false positives
                        boxes_stats[-1][1] += 1.0
                        if box.qid in boxes_stats_query:
                            boxes_stats_query[box.qid][-1][1] += fn
                        else:
                            boxes_stats_query[box.qid] = [[0, 1.0, 0]]
                    for box in pending_ref_boxes:
                        # Box-level false negatives
                        unmatched_ref_boxes.append(box)
            else:
                # Segment-level False Positive
                segment_stats[-1][1] += 1.0
                if hyp.qid in segment_stats_query:
                    segment_stats_query[hyp.qid][-1][1] += 1.0
                else:
                    segment_stats_query[hyp.qid] = [[0.0, 1.0, 0.0]]
                # Box-level False Positives
                for word_match in hyp:
                    for box in word_match:
                        boxes_stats[-1][1] += 1.0
                        if box.qid in boxes_stats_query:
                            boxes_stats_query[box.qid][-1][1] += 1.0
                        else:
                            boxes_stats_query[box.qid] = [[0, 1.0, 0]]
        # Process the set of pending reference segments and its respective
        # reference boxes.
        for qid, sid in unmatched_ref_segments:
            ref = refs[(qid, sid)]
            # Segment-level false negatives
            segment_stats[-1][2] += 1.0
            if ref.qid in segment_stats_query:
                segment_stats_query[ref.qid][-1][2] += 1.0
            else:
                segment_stats_query[ref.qid] = [[0.0, 0.0, 1.0]]
            # Box-level false negatives
            for word_match in ref:
                for box in word_match:
                    boxes_stats[-1][2] += 1.0
                    if box.qid in boxes_stats_query:
                        boxes_stats_query[box.qid][-1][2] += 1.0
                    else:
                        boxes_stats_query[box.qid] = [[0.0, 0.0, 1.0]]
        # Process the set of unmatched boxes from reference segments that were
        # matched correctly.
        for box in unmatched_ref_boxes:
            boxes_stats[-1][2] += 1.0
            if box.qid in boxes_stats_query:
                boxes_stats_query[box.qid][-1][2] += 1.0
            else:
                boxes_stats_query[box.qid] = [[0.0, 0.0, 1.0]]
        # Return collected stats
        return segment_stats, boxes_stats, segment_stats_query, \
            boxes_stats_query

    @staticmethod
    def _compute_pr_curve_and_ap(events, interpolate=True, trapezoid=True):
        '''Use this function to compute the Recall-Precision curve and the
        area under it (average precision) from a set of events.

        It can compute the interpolated precision instead of plain-precision,
        and compute the average precision using the trapezoidal approximation
        to the integral of the Recall-Precision curve.

        As a base case, if the number of detected elements is zero, or the
        number of relevant events (in the reference) is zero, AP is defined to
        be 0.0 (notice that in this case precision and/or recall are not
        well-defined).'''
        assert isinstance(events, list) and len(events) > 0
        # Accumulate events stats
        acc_events = [ tuple(events[0]) ]
        for (tp, fp, fn) in events[1:]:
            acc_events.append((tp + acc_events[-1][0],
                               fp + acc_events[-1][1],
                               fn + acc_events[-1][2]))
        # Total number of detected events (TP + FP)
        ND = acc_events[-1][0] + acc_events[-1][1]
        # Total number of relevant events (TP + FN)
        NR = acc_events[-1][0] + acc_events[-1][2]
        if ND == 0.0 or NR == 0.0:
            # Base case, if total number of detected events or the total number
            # of relevant events is 0.0, then return P=0.0 and R=0.0.
            # Note: observe that it is not possible that both ND and NR are 0
            return [(0.0, 0.0)], 0.0
        else:
            # Compute precision and recall curves
            PR = []
            for acc_tp, acc_fp, _ in acc_events:
                PR.append((acc_tp / (acc_tp + acc_fp), acc_tp / NR))
            # Interpolate precision curve
            if interpolate:
                for i in xrange(len(PR) - 1, 0, -1):
                    PR[i - 1] = (max(PR[i][0], PR[i - 1][0]), PR[i][1])
            # Compute average precision
            sAP = 0.0
            for i in xrange(len(events)):
                tp = events[i][0]
                p0, p1 = (PR[i - 1][0] if i > 0 else PR[i][0], PR[i][0])
                sAP += tp * ((0.5 * (p0 + p1)) if trapezoid else p1)
            return PR, sAP / NR

    @staticmethod
    def _test_compute_pr_curve_and_ap(tol=1E-6):
        events = [(2.0, 1.0, 0.0), (1.0, 0.0, 0.0),
                  (1.0, 2.0, 0.0), (0.0, 1.0, 0.0),
                  (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)]
        # No interpolation, no trapezoid integral
        ex_ap = 223.0 / 420.0
        _, ap = Assessment._compute_pr_curve_and_ap(events, False, False)
        assert math.fabs(ap - ex_ap) < tol, \
            'Expected AP = %g, Computed AP = %g' % (ex_ap, ap)
        # No interpolation, trapezoid integral
        ex_ap = 227.0 / 420.0
        _, ap = Assessment._compute_pr_curve_and_ap(events, False, True)
        assert math.fabs(ap - ex_ap) < tol, \
            'Expected AP = 0.55, Computed AP = %g' % (exp_ap, ap)
        # Interpolation, no trapezoid integral
        ex_ap = 237.0 / 420.0
        _, ap = Assessment._compute_pr_curve_and_ap(events, True, False)
        assert math.fabs(ap - ex_ap) < tol, \
            'Expected AP = %g, Computed AP = %g' % (ex_ap, ap)
        # Interpolation, trapezoid integral
        ex_ap = 163.0 / 280.0
        _, ap = Assessment._compute_pr_curve_and_ap(events, True, True)
        assert math.fabs(ap - ex_ap) < tol, \
            'Expected AP = %g, Computed AP = %g' % (ex_ap, ap)

    @staticmethod
    def _compute_mean_pr_curve_and_ap(events_by_qid, interpolate=True,
                                      trapezoid=True):
        assert isinstance(events_by_qid, dict) and len(events_by_qid) > 0
        # Compute Precision-Recall curve and AP for each query
        aux = { q : Assessment._compute_pr_curve_and_ap(e, interpolate,
                                                        trapezoid) \
                for q, e in events_by_qid.iteritems() }
        mAP = sum([ap for (_, ap) in aux.itervalues()]) / len(events_by_qid)
        return None, mAP

    @staticmethod
    def _compute_ndcg(events):
        '''Use this function to compute the Normalized Discounted Cumulative
        Gain over a set of events.

        It uses an extension of the traditional definition of NDCG that behaves
        deterministically when some subset of the events has the same score.
        In the traditional formulation, depending on the order, the NDCG would
        differ, even if the score is the same.

        As a base case, if the number of detected elements is zero, or the
        number of relevant events (in the reference) is zero, NDCG is defined
        to be 0.0 (notice that in this case the original formulation is not
        well-defined).'''
        assert isinstance(events, list) and len(events) > 0
        NR, dcg, k = 0.0, 0.0, 0
        for tp, fp, fn in events:
            NR += tp + fn
            for i in xrange(int(tp + fp)):
                k += 1
                p = tp / (tp + fp)
                dcg += (math.pow(2.0, p) - 1.0) / math.log(k + 1, 2)
        if NR > 0.0:
            idcg = sum([1.0 / math.log(k + 1, 2) \
                        for k in xrange(1, int(NR) + 1)])
            return dcg / idcg
        else:
            return 0.0

    @staticmethod
    def _test_compute_ndcg(tol=1E-6):
        events = [(2.0, 1.0, 0.0), (1.0, 0.0, 0.0),
                  (1.0, 2.0, 0.0), (0.0, 1.0, 0.0),
                  (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)]
        ex_ndcg = 1.9621642208209584 / 2.948459118879392
        ndcg = Assessment._compute_ndcg(events)
        assert math.fabs(ndcg - ex_ndcg) < tol, \
            'Expected NDCG = %g, Computed NDCG = %g' % (ex_ndcg, ndcg)

    @staticmethod
    def _compute_mean_ndcg(events_by_qid):
        assert isinstance(events_by_qid, dict) and len(events_by_qid) > 0
        sNDCG = sum([Assessment._compute_ndcg(e) \
                     for e in events_by_qid.itervalues()])
        return sNDCG / len(events_by_qid)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Run quality assessment (or validation) of a submission ' +
        'file for the ImageCLEF-2016 Handwritten Scanned Document Retrieval ' +
        'Task. The tool will show different assessment metrics at different ' +
        'levels of granularity. If no reference file is specified, the ' +
        'submission file will only be validated. See the task webpage ' +
        '(http://www.imageclef.org/2016/handwritten) for additional help.')
    parser.add_argument('--query-list', '-q', type=argparse.FileType('r'),
                        help='file containing the list of queries (used only '
                        'during validation)')
    parser.add_argument('line2page', type=argparse.FileType('r'),
                        help='file containing a mapping from lines to pages')
    parser.add_argument('submission', type=argparse.FileType('r'),
                        help='file containing the submission solution')
    parser.add_argument('reference', type=argparse.FileType('r'), nargs='?',
                        help='file containing the reference solution')
    args = parser.parse_args()

    # Run tests to make sure that there are no bugs in the AP and NDCG
    # computation.
    Assessment._test_compute_pr_curve_and_ap()
    Assessment._test_compute_ndcg()

    # Read line2page document
    line2page = {}
    for l in args.line2page:
        l = l.split()
        assert len(l) == 2
        line2page[int(l[0])] = l[1]

    if args.reference is None:
        sys.stderr.write('WARNING: You did not specify a reference file. ' +
                         'The submission file will only be validated.\n')
        hyp = Solution(line2page, args.submission)
        # Optionally, check that the number of words in each query of the
        # solution file is the expected.
        if args.query_list:
            num_words_in_query = []
            for query in args.query_list:
                words = query.split()
                assert len(words) > 0, 'Wrong query, see line %d:%s' % (
                    len(num_words_in_query) + 1, args.query_list.name)
                num_words_in_query.append(len(words))
            for match in hyp:
                assert len(match) == num_words_in_query[match.qid - 1], \
                    'Your match of query %d in segment %d does not have the ' \
                    'same number of words as the query (actual: %d, ' \
                    'expected: %d)' % (match.qid, match.sid, len(match),
                                       num_words_in_query[match.qid - 1])
    else:
        # Perform evaluation
        hyp = Solution(line2page, args.submission)
        ref = Solution(line2page, args.reference)
        assessment = Assessment(ref, hyp)
        print 'Segment-Level Global AP = %f' % assessment.segment_global_ap
        print 'Segment-Level Mean AP = %f' % assessment.segment_mean_ap
        print 'Segment-Level Global NDCG = %f' % assessment.segment_global_ndcg
        print 'Segment-Level Mean NDCG = %f' % assessment.segment_mean_ndcg
        print 'Box-Level Global AP = %f' % assessment.boxes_global_ap
        print 'Box-Level Mean AP = %f' % assessment.boxes_mean_ap
        print 'Box-Level Global NDCG = %f' % assessment.boxes_global_ndcg
        print 'Box-Level Mean NDCG = %f' % assessment.boxes_mean_ndcg
