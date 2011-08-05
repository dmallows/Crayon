from multiprocessing import Pool

import tempfile 
import shutil
from hashlib import md5

import subprocess
import os

def _latex_render_worker_init(texsum, pretext, posttext, workdir, cachedir):
    from os import path

    """Set up initial state for each thread worker"""
    # Global state is usually a very bad thing. However, here it happens to save
    # writing our own pool. Therefore it stays!
    # TODO: Remove this global state.
    global PRETEXT, POSTTEXT, WORKDIR, CACHEDIR, TEXSUM

    PRETEXT  = pretext
    POSTTEXT = posttext
    WORKDIR  = workdir
    CACHEDIR = cachedir
    TEXSUM   = texsum

def _latex_render_helper(text):
    import os
    path = os.path

    # Generate the cachename
    cachename = md5(text).hexdigest()
    cachefile = path.join(CACHEDIR, '%s.svg' % cachename)

    # Check to see if svg exists in cache. If so, wonderful.
    if os.path.isfile(cachefile):
        return cachefile

    # Since the result is not cached, we must run latex.
    texfile = path.join(WORKDIR, '%s.tex' % cachename)

    # Generate the latex source file
    with open(texfile, 'w') as f:
        f.write('\n'.join((PRETEXT, text, POSTTEXT)))

    # Run latex, error if we get anything other than return code zero.
    print 'RUN latex'
    try:
        subprocess.check_call(
            ('latex','-interaction=batchmode','-fmt','preamble.fmt',texfile),
            cwd=WORKDIR, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception, e:
            print e

    # Now, we try convert from dvi to svg.
    dvifile = path.join(WORKDIR, '%s.dvi' % cachename)

    try:
        subprocess.check_call(
            ('dvisvgm', '-S', '-n', dvifile),
            cwd=WORKDIR, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception, e:
            print e

    # Then move into the cachedir, guaranteed atomically on POSIX.
    # Therefore, even if two process run, they cannot mess each other up!
    svgfile = path.join(WORKDIR, '%s.svg' % cachename)

    os.rename(svgfile, cachefile)
    return cachefile

class LatexRenderer(object):
    def __init__(self):
        self._tempdir = tempfile.mkdtemp(prefix='plotty.')
        self._cachedir = os.path.expanduser('~/.plotty/svgcache')

        if not os.path.exists(self._cachedir):
              os.makedirs(self._cachedir)

        self._results = {}

        # Open before and after
        with open('data/before.tex', 'r') as f:
            before = f.read()

        with open('data/after.tex', 'r') as f:
            after = f.read()

        with open('data/preamble.tex', 'r') as f:
            preamble = f.read()

        texsum = md5('\n'.join((preamble, before, after))).hexdigest()

        mkpre = subprocess.Popen((
            'latex','-interaction=batchmode','-output-directory=%s' %
            self._tempdir, '-ini', '&latex data/preamble.tex\dump'),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        self._pool = Pool(
            initializer=_latex_render_worker_init,
            initargs=(texsum, before, after, self._tempdir, self._cachedir))

        mkpre.communicate()

        if mkpre.returncode != 0:
            raise RuntimeError('Latex was unable to compile the preamble.')

    def close(self):
        shutil.rmtree(self._tempdir)
        self._pool.terminate()

    def render(self, text):
        # First check the svg cache. 

        try:
            result = self._results[text]
        except KeyError:
            result = self._pool.apply_async(_latex_render_helper, (text,))
            self._results[text] = result

        return result

    def __del__(self):
        self.close()

a = LatexRenderer()

for i in xrange(100):
    a.render('%03d' % i)
a._pool.close()
a._pool.join()
