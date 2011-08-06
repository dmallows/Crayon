from Queue import Queue
from threading import Thread
from hashlib import md5

import tempfile 
import shutil

import subprocess
import os
path = os.path

class LatexProxy(object):
    def __init__(self):
        self._tempdir = tempfile.mkdtemp(prefix='plotty.')
        self._cachedir = os.path.expanduser('~/.plotty/svgcache')

        if not os.path.exists(self._cachedir):
              os.makedirs(self._cachedir)

        # Open preamble, pretext and posttext
        with open('data/preamble.tex', 'r') as f:
            preamble = f.read()

        with open('data/before.tex', 'r') as f:
            before = f.read()

        with open('data/after.tex', 'r') as f:
            after = f.read()

        with open(os.path.join(self._tempdir, 'preamble.tex'),'w') as f:
            f.write(preamble)

        self.make_preamble() 
        self._md5 = md5('\n'.join((preamble, before, after)))

        self.pre = before
        self.post = after
        self.check_preamble()

    def make_preamble(self):
        pipe = subprocess.PIPE
        self._mkpre = subprocess.Popen((
            'latex','-interaction=batchmode', '-ini',
            '&latex preamble.tex\dump'),
            stdout=pipe,stderr=pipe, cwd=self._tempdir)

    def check_preamble(self):
        self._mkpre.communicate()

        if self._mkpre.returncode != 0:
            raise RuntimeError('Latex was unable to compile the preamble.')

    def make_tex_file(self, text, texfile):
        with open(texfile, 'w') as f:
            f.write('\n'.join((self.pre, text, self.post)))

    def run_latex(self, texfile):
        subprocess.check_call(
            ('latex','-interaction=batchmode','-fmt','preamble.fmt',texfile),
            cwd=self._tempdir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def run_dvisvgm(self, dvifile):
        subprocess.check_call(
            ('dvisvgm', '-S', '-n', dvifile),
            cwd=self._tempdir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def get_hash(self, text):
        hash = self._md5.copy()
        hash.update(text)
        return hash.hexdigest()

    def render(self, text):
        """Render given latex, returning the filename of the svg"""
        # Generate the cached base name
        cachename = self.get_hash(text)

        # Generate filename of cached svg file
        cachefile = path.join(self._cachedir, '%s.svg' % cachename)

        # Check to see if svg exists in cache. If so, wonderful.
        if not os.path.isfile(cachefile):
            # Since the result is not cached, we must run latex.
            texfile = path.join(self._tempdir, '%s.tex' % cachename)

            # Generate the latex source file
            self.make_tex_file(text, texfile)

            # Run latex to make a dvi file
            self.run_latex(texfile)

            # Now, we try convert from dvi to svg.
            dvifile = path.join(self._tempdir, '%s.dvi' % cachename)
            self.run_dvisvgm(dvifile)

            # Then move into the cachedir, guaranteed atomically on POSIX.
            # Therefore, even if two process run, they cannot mess each other
            # up!
            svgfile = path.join(self._tempdir, '%s.svg' % cachename)

            os.rename(svgfile, cachefile)
            
        return cachefile

class Result(object):
    def __init__(self):
        self.value = None


class Worker(Thread):
    """Thread for rendering latex"""
    def __init__(self, tasks, latexproxy):
        Thread.__init__(self)
        self.latexproxy = latexproxy
        self.tasks = tasks
        self.daemon = True
        self.start()
    
    def run(self):
        while True:
            try:
                (result, text) = self.tasks.get()
                result.value = self.latexproxy.render(text)
                self.tasks.task_done()
            except Exception, e:
                print e

class LatexPool(object):
    def __init__(self, num_threads=4, latexproxy = None):
        self._latexproxy = LatexProxy() if latexproxy is None else latexproxy
        self._tasks = Queue()
        self._results = {}
        for _ in xrange(num_threads):
            Worker(self._tasks, self._latexproxy)

    def render(self, text):
        try:
            return self._results[text]
        except KeyError:
            # Create a 'thunk' - a result that will be later.
            result = Result()
            self._tasks.put((result, text))
            self._results[text] = result
            return result 

if __name__=='__main__':
    a = LatexPool()
    results = [a.render('%03d' % i) for i in xrange(100)]
        
    print "Waiting..."
    a._tasks.join()
    for r in results:
        print r.value
