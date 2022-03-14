""" Python classes and functions that unpack and parse Benchmark Scan PDF files.

    the idea is to parse each section and retreive some params for a match object


    #Extract table of contents
    # string toc => (Recommendations - Appendix)


    Main idea:
    # Section
    #  name
    #  number
    # SubSection(s), may have several iterations so use list? (maybe dict or set)
    # LeafSection
    # Name
    # Profile L1 or L2
    # Controls v8
    # Controls v7
    # Controls v6
"""
import pdfminer.high_level as ex
import io
import re

# for future use.
from string import whitespace
import threading as th
import time


class TextIterator(io.StringIO):
    done = False
    cursor = None

    def init(self, text):
        super(text)
        self.done = False

    def _is_done(self):
        if self.read(1) == '':
            self.done = True
        else:
            self.seek(self.tell() - 1)

    def next(self):
        self._is_done()
        self.cursor = self.read(1)
        return self.cursor

    def rewind_cur(self, i):
        cur = self.tell() - i
        if cur <= 0:
            self.seek(0)
        else:
            self.seek(cur)

    def event(self, keyword, lookahead=False):
        """
         Returns boolean True when a particular string is found.
         If the string is found the cursor will remain at the point of match
         completion. Iterates until a match is found or the stream is exhausted,
         unless lookahead flag is set to True

        :param keyword: The string to match
        :param lookahead: Only search the stream far enough to match the keyword. Else, search until steam is exhausted
        :return: returns true
        """

        if lookahead:
            limit = len(keyword)
            self.rewind_cur(1)
        else:
            limit = None

        place = self.tell()
        value = ''
        match = True
        j = 1

        while not self.done:

            cur = self.next()

            if value == keyword[0:i]:
                j += 1
                value += cur

            elif cur == keyword[0:1]:
                value += cur

            else:
                j = 1
                value = ''
                match = False

            if len(value) == len(keyword):
                if value == keyword:
                    return True

            if limit is not None:
                if limit > 0 and match:
                    limit -= 1
                else:
                    self.seek(place+1)
                    break

        return False


def get_toc(txt):
    # find and extract the table of contents from a CIS Benchmark file.
    # return two lists, the list of oids and list of sections
    event_start = "Recommendations"
    event_end = "Appendix"
    toc = []
    itr = TextIterator(txt)
    start = False
    end = False
    while not itr.done:

        if end:
            break
        elif start:
            c = itr.next()
            toc.append(c)
            if c == event_end[0:1]:
                end = itr.event(event_end, lookahead=True)
        else:
            start = itr.event(event_start)

    # clean up the odd form-feed character
    [toc.pop(k) for k, char in enumerate(toc) if char == ""]

    c1, c2 = "", " "
    toc = c1.join(toc[:-1]).split("\n")

    # capture a bunch of periods (.) followed by some numbers, or page numbers
    # removes all those pesky periods and page numbers from the found text.
    ex_rem = re.compile(r'([. ][.]{3,}.[0-9]{,4})|([.]{,2} [0-9]{2,3})|([0-9]{,2} [|] P a g e..)')
    m = []
    [m.append(ex_rem.sub('', line)) for line in toc]

    [m.pop(k) for k, line in enumerate(m) if line == c2 or line == c1]

    if m[-1] == '':
        m.pop(-1)

    # capture the oid of the item
    ex_oid = re.compile(r'([0-9.]{3,}[ (]{2}[LBNG0-9]{2}\))')
    ex_sec = re.compile(r'([0-9]{1,2} )|([0-9.]{3,12} [^(])')

    toc = []
    sec = []
    is_oid = False
    is_se = False
    oid_ = ''
    se_ = ''

    x = iter(m)
    elem = next(x, '____')
    while True:
        # gather info
        oid = ex_oid.match(elem)
        se = ex_sec.match(elem)
        test_se = isinstance(se, re.Match)
        test_oid = isinstance(oid, re.Match)

        # check for regex match
        if test_oid or test_se:
            # if oid
            if test_oid:
                oid_ = oid.string.strip()
                is_oid = True
            # if section
            elif test_se:
                se_ = se.string.strip()
                is_se = True

        # get and test next element
        elem = next(x, '____')

        if elem == "____":
            if test_oid:
                toc.append(oid_)
            elif test_se:
                sec.append(se_)
            break

        oid = ex_oid.match(elem)
        se = ex_sec.match(elem)
        # check if new oid of sec
        test_se = isinstance(se, re.Match)
        test_oid = isinstance(oid, re.Match)

        # if an oid was detected in the previous element
        if is_oid:
            # if new oid or sec
            if test_se or test_oid:
                toc.append(oid_)
                # add in logging
                is_oid = False
            # if part of the same oid
            else:
                oid_ += " " + elem.strip()

        # if a section was detected in the previous element
        elif is_se:
            # if new oid or sec
            if test_se or test_oid:
                # add in logging

                sec.append(se_)
                is_se = False
            # if part the same se
            else:
                se_ += " " + elem.strip()

    return toc, sec


def extract_text(fp):
    return ex.extract_text(fp)


def write_text(fp, op):

    pdf_text = extract_text(fp)
    with open(op, "w", encoding='utf-8') as o_file:
        o_file.write(pdf_text)


if __name__ == "__main__":

    op = "CIS_Win10E_20H2.txt"
    with open(op, 'r', encoding='utf-8') as f:
        doc = f.read()

    contents, section = get_toc(doc)

    new = contents + section
    new.sort()
    input(len(new))
    input(len(section))
    input(len(contents))
    for i, item in enumerate(contents):
        print(item)
        if i % 25 == 0:
            input()










