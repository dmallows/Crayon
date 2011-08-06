from multiprocessing import Pool

import tempfile 
import shutil

import subprocess
import os

class logErrors(object):
    def __init__(self, f):
        self.f = f 
        
    def __call__(self, *args, **kwargs):
        try:
            return self.f(*args, **kwargs)
        except Exception, e:
            print e
            return e

def _latex_render_worker_init(preamble, pretext, posttext, workdir, cachedir):
    """A function called on each worker process in the pool."""
    from os import path

    """Set up initial state for each thread worker"""
    # Global state is usually a very bad thing. However, here it happens to save
    # writing our own pool. Therefore it stays!  TODO: Remove this global state,
    # if a sensible way ever arises!
    global PREAMBLE, PRETEXT, POSTTEXT,WORKDIR, CACHEDIR

    PRETEXT  = pretext
    POSTTEXT = posttext
    WORKDIR  = workdir
    CACHEDIR = cachedir
    PREAMBLE = preamble

_latex_render_worker_init = logErrors(_latex_render_worker_init)

def _latex_render_helper(text):
    try:
        import os
        from hashlib import md5
        path = os.path

        # Generate the cachename
        fulltex = '\n'.join((PREAMBLE, PRETEXT, text, POSTTEXT))

        cachename = md5(fulltex).hexdigest()

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

    except Exception, e:
        print e
        return e

class LatexRenderer(object):
    def __init__(self):
        self._tempdir = tempfile.mkdtemp(prefix='plotty.')
        self._cachedir = os.path.expanduser('~/.plotty/svgcache')

        if not os.path.exists(self._cachedir):
              os.makedirs(self._cachedir)

        self._results = {}

        # Open preamble, pretext and posttext
        with open('data/preamble.tex', 'r') as f:
            preamble = f.read()

        with open('data/before.tex', 'r') as f:
            before = f.read()

        with open('data/after.tex', 'r') as f:
            after = f.read()

        with open(os.path.join(self._tempdir, 'preamble.tex'),'w') as f:
            f.write(preamble)

        pipe = subprocess.PIPE
        mkpre = subprocess.Popen((
            'latex','-interaction=batchmode', '-ini',
            '&latex preamble.tex\dump'),
            stdout=pipe,stderr=pipe, cwd=self._tempdir)

        self._pool = Pool(
            initializer=_latex_render_worker_init,
            initargs=(preamble, before, after, self._tempdir, self._cachedir))

        mkpre.communicate()

        if mkpre.returncode != 0:
            raise RuntimeError('Latex was unable to compile the preamble.')

    def close(self):
        self._pool.terminate()

        try:
            shutil.rmtree(self._tempdir)
        except OSError:
            pass

    def render(self, text):
        # First check the svg cache. 

        try:
            result = self._results[text]
        except KeyError:
            result = self._pool.apply_async(_latex_render_helper, (text,))
            self._results[text] = result

        return result

    def batch_render(self, texts):
        return self._pool.map_async(_latex_render_helper, texts)

    def __del__(self):
        self.close()

if __name__=='__main__':
    a = LatexRenderer()

    try:
        results = a.batch_render('%03d' % i for i in xrange(100)).get(20)
        #for r in results:
            #print r
    except KeyboardInterrupt, e:
        print "Keyboard interrupt... closing threads"
    finally:
        a.close()
