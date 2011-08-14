#! /usr/bin/python
import hashlib
import Queue

import subprocess
import os
import re
import math
import shelve

data = shelve.open('foo.db', protocol=1)

class PosParser(object):
    """Parser for dvipos bounding box output"""
    def __init__(self):
        self.bbline = re.compile('^pagebb & (\d+) & (.*)')
        self.numbers = re.compile(r'[0-9.A-F-]+')

    def parse(self, filename):
        with open(filename, 'r') as file:
            matches = (self.bbline.match(line) for line in file)
            return [self._parse_line(match.group(2))
                    for match in matches if match]

    def _parse_hex(self, hex):
        a, b = hex.split('.')
        a, b = int(a), int(b, 16)
        return a + math.copysign(b,a)/65536.0

    def _parse_line(self, line):
        return tuple (self._parse_hex(i.group(0))
                      for i in self.numbers.finditer(line))


## Obtain list of strings to pass through tex

texes = ['Hello World %d' % i for i in xrange(100)]

## Generate hash of templates

def read(file):
    with open(file) as f:
        return f.read().strip()

preamble, pre_doc, pre_tex, post_tex, post_doc = (
    read(os.path.join('templates',i)+'.tex') for i in 
    ('preamble', 'pre_doc', 'pre_tex', 'post_tex', 'post_doc'))

md5sum = hashlib.md5('\n'.join((preamble, pre_doc, pre_tex, post_tex, post_doc)))

## Hash each individual piece of TeX

def calc_md5(text):
    md5 = md5sum.copy()
    md5.update(text)
    return md5.hexdigest()

md5sums = map(calc_md5, texes)

## See if each hash is in the database

pass

## If the hash is in the database, return the corresponding deferred result
## object.

pass

## Otherwise append to the list of unmade files.

pass

## Pass unmade files onto batch process

def write_pre(f):
    f.writelines('\n'.join((pre_doc, '', '')))

def write_page(f, tex):
    f.write('\n'.join((pre_tex, tex, post_tex, '', '')))

def write_post(f):
    f.write(post_doc)

def make_preamble():
    pipe = subprocess.PIPE
    with open('preamble.tex', 'w') as f:
        f.write(preamble)

    return subprocess.Popen((
        'latex','-interaction=batchmode', '-ini',
        '&latex preamble.tex\dump'), stderr=pipe, stdout=pipe)

def check_preamble(p):
    p.communicate()

    if p.returncode != 0:
        raise RuntimeError('Latex was unable to compile the preamble.')

p = make_preamble()
check_preamble(p)

with open('myoutput.tex', 'w') as f:
    write_pre(f)
    for t in texes:
        write_page(f, t)
    write_post(f)

## Call latex on file
def run_latex(texfile):
    return subprocess.check_call(
        ('latex','-interaction=batchmode','-fmt','preamble.fmt',texfile),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)

run_latex('myoutput.tex')

## Run dvipos
def run_dvipos(dvifile):
    return subprocess.check_call(
        ('dvipos', '-b', dvifile),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)

run_dvipos('myoutput.dvi')

p = PosParser()
stats = p.parse('myoutput.pos')

## Output dimension stats

for text, stats in zip(texes, stats):
    data[text] = stats

def run_dvisvgm(dvifile):
    """Convert all pages of dvi file to svgs"""
    subprocess.check_call(
        ('dvisvgm', '-b', 'none', '-p', '0-', '-S','-z', '-n', dvifile),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)

run_dvisvgm('myoutput.dvi')

data.close()
