#! /usr/bin/python
import hashlib
import Queue

import atexit
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
    def __init__(self, text, dvifile = None, dvipath = None, extents = None):
        self.text = text
        self.hash = hashlib.md5(text).hexdigest()
        self.dvifile = dvifile
        self.dvipath = dvipath
        self.extents = extents

class TexRunner(object):
    def __init__(self):
        self._errorparser = re.compile(r'^! (.*)$', re.MULTILINE)
        self._progressparser = re.compile(r'^((?:\[\d+\]\s?)+):$', re.MULTILINE)
        self._preamble_checked = False

        ## todo: For templates: check cwd, then ~/.crayon, then system.
        self._templatedir = 'templates'

        ## Since there's potential to massively save time using caches, allow
        ## user to set directory (thus they can set /dev/null) or set minimal
        ## cacheing.
        base_cachedir = os.path.expanduser('~/.cache/crayon')

        ## Make a temp dir for running latex and dvipos in
        self._tempdir = tempfile.mkdtemp(prefix='crayon-')

        preamble = self._template('preamble.tex')
        self._make_preamble(preamble)

        body = self._template('body.tpl')

        ## Compile the body template using templite (single file, < 50 line
        ## lightweight and fast templating engine)
        self._body_tpl = templite.Templite(body)

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
        self._db = shelve.open(self._cache('extents.db'), protocol=1)

        self._posparser = PosParser()


        # Batch number, so we can build svgs separately
        # (Many pages of the dvi file will *not* be needed as SVG.)
        self._batchnumber = 0
        self._tex_cache = {}

    def close(self):
        shutil.rmtree(self._tempdir)
        self._db.close()

    def __del__(self):
        try:
            close()
        except:
            pass

    def render(self, strings):
        """Batch latexing of a batch of strings"""
        self._batchnumber += 1

        basefile = 'output-%d' % self._batchnumber
        texfile  = basefile + '.tex'

        ## Create a list of mutable containers
        texes = [self._get_tex(s) for s in strings]

        self._check_preamble()

        unknowns = [t for t in texes if t.extents is None]

        # Quit now if we don't need to run latex
        if not unknowns:
            return texes

        self._write_latex(self._temp(texfile), unknowns)

        dvifile = basefile + '.dvi'

        self._run_latex(texfile)

        self._run_dvipos(dvifile)

        posfile = basefile + '.pos'

        extents = self._posparser.parse(self._temp(posfile))

        for tex, ext in zip(unknowns, extents):
            tex.extents = ext
            self._db[tex.text] = ext
            tex.dvifile = dvifile
            tex.dvipath = self._tempdir

        return texes

    def _get_tex(self, string):
        t = None
        try:
            t = self._tex_cache[string]
        except KeyError:
            t = Tex(string)
            self._tex_cache[string] = t
            try:
                t.extents = self._db[string]
            except KeyError, e:
                print "Couldn't look up", e
                pass
        return t

    def _template(self, filename):
        with open(os.path.join(self._templatedir, filename),'r') as f:
            return f.read()

    def _cache(self, filename):
        return os.path.join(self._cachedir, filename)

    def _temp(self, filename):
        return os.path.join(self._tempdir, filename)

    def _make_preamble(self, preamble):
        pipe = subprocess.PIPE
        with open(self._temp('preamble.tex'), 'w') as f:
            f.write(preamble)

        self._pre = subprocess.Popen((
            'latex','-interaction=batchmode', '-ini',
            '&latex preamble.tex\dump'), cwd=self._tempdir,
            stderr=pipe, stdout=pipe)

    def _check_preamble(self):
        if self._preamble_checked:
            return

        self._pre.communicate()

        if self._pre.returncode != 0:
            raise RuntimeError('Latex was unable to compile the preamble.')
            self._preamble_checked = True
        del self._pre
        self._preamble_checked = True

    ## Write out latex
    def _write_latex(self, filename, texes):
        with open(filename, 'w') as f:
            f.write(self._body_tpl.render(texes = (t.text for t in texes)))

    ## Call LaTeX on file
    def _run_latex(self, filename):
        result = subprocess.Popen(
            ('latex','-interaction=nonstopmode','-fmt','preamble.fmt',filename),
            stdout=subprocess.PIPE, cwd=self._tempdir)
        ## This is stupid. It will throw an exception if there's an error.
        ## This sounds at first like a good assumption
        ## but it's not!!! We really need to find a way to work out which page
        ## the error occurred on and give some kind of feedback in the TeX
        ## objects. This would be *REALLY* handy for GUI. It would also be handy
        ## to check that all the pages are being made.
        stdout, _ = result.communicate()

    ## Run dvipos
    def _run_dvipos(self, dvifile):
        subprocess.check_call(
            ('dvipos', '-b', dvifile), cwd = self._tempdir,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

import contextlib
t = TexRunner()
t.render(['hello $world', 'bugger', 'what the fuck', r'\tortoise', 'next one',
          r'food and \arseholes sit tight!'])
t2 = t.render(['hello $world', 'bugger', 'what the fuck', r'\tortoise', 'next one',
          r'food and \arseholes sit tight!'])
t.close()
