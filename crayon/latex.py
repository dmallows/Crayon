#! /usr/bin/python
import hashlib
import Queue

import subprocess
import os
import re
import math
import shelve

import errno
import templite
import tempfile
import shutil


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

class Tex(object):
    def __init__(self, text, dvifile = None, extents = None):
        self.text = text
        self.hash = hashlib.md5(text).hexdigest()
        self.dvifile = dvifile
        self.extents = extents

class TexRunner(object):
    def __init__(self):

        ## todo: For templates: check cwd, then ~/.crayon, then system.
        self._templatedir = 'templates'

        ## Since there's potential to massively save time using caches, allow
        ## user to set directory (thus they can set /dev/null) or set minimal
        ## cacheing.
        base_cachedir = os.path.expanduser('~/.cache/crayon')

        preamble = self._template('preamble.tex')
        body = self._template('body.tpl')

        ## Compile the body template using templite (single file, < 50 line
        ## lightweight and fast templating engine)
        self._body_tpl = templite.Templite(preamble)

        ## Hash the template. This will form the directory for storage of cache
        ## files.
        h = hashlib.md5(preamble)
        h.update(body)
        templatehash = h.hexdigest()

        self._cachedir = os.path.join(base_cachedir, templatehash)

        ## Try and make the cachedir. This way avoids various race conditions
        ## and is more pythonic than Guido's suggestion.
        try:
            os.makedirs(self._cachedir)
        except OSError as exc:
            if exc.errno == errno.EEXIST:
                pass
            else:
                raise

        # Open the database
        self._db = shelve.open(os.path.join(templatehash, ''), protocol=1)

        ## Make a temp dir for running latex and dvipos in
        self._tempdir = tempfile.mkdtemp(prefix='crayon-')

        # Batch number, so we can build svgs separately
        # (Many pages of the dvi file will *not* be needed as SVG.)
        self._batchnumber = 0

    def close(self):
        shutil.rmtree(self._tempdir)
        self._db.close()

    def render(self, strings):
        """Batch latexing of a batch of strings"""
        self._batchnumber += 1

        texes = [Tex(s) for s in strings]

        self._render_latex()
        output = 'output-%x.tex' % self._batchnumber

    def _template(self, filename):
        with open(os.path.join(self._templatedir, filename),'r') as f:
            return f.read()

    def _cache(self, filename):
        return os.path.join(self._cachedir, filename)

    def _temp(self, filename):
        return os.path.join(self._tempdir, filename)

    def _render_latex(self, texes):
        self._write_latex(texes)

    def _make_preamble():
        pipe = subprocess.PIPE
        with open('preamble.tex', 'w') as f:
            f.write(preamble)

        self._pre = subprocess.Popen((
            'latex','-interaction=batchmode', '-ini',
            '&latex preamble.tex\dump'), cwd=self._tempdir,
            stderr=pipe, stdout=pipe)

    def _check_preamble(self):
        self._pre.communicate()

        if self._pre.returncode != 0:
            raise RuntimeError('Latex was unable to compile the preamble.')

    ## Write out tex
    def _write_tex(self, filename, texes):
        with open(filename, 'w') as f:
            f.write(self._body_tpl.render(t.text for t in texes))

    ## Call LaTeX on file
    def _run_latex(self, filename):
        return subprocess.check_call(
            ('latex','-interaction=batchmode','-fmt','preamble.fmt',filename),
            cwd=self._tempdir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    ## Run dvipos
    def _run_dvipos(dvifile):
        return subprocess.check_call(
            ('dvipos', '-b', dvifile), cwd= self._tempdir,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)


TexRunner()
