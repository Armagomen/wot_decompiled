# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/bw_site.py
from __future__ import print_function
import __builtin__
import os
import traceback
import sys
import pydoc
import fnmatch
import logging
import BigWorld
import BWLogging
import BWUtil
import ResMgr
import bwdeprecations
from bwdebug import NOTICE_MSG
DEFAULT_ENCODING = 'utf-8'
PLATFORM_SUFFIX = BWUtil.getPlatformSuffix()

class _Helper(object):

    def __repr__(self):
        pass

    def __call__(self, *args, **kwds):
        return pydoc.help(*args, **kwds)


def set_helper():
    __builtin__.help = _Helper()


def set_default_encoding():
    if hasattr(sys, 'setdefaultencoding'):
        sys.setdefaultencoding(DEFAULT_ENCODING)
        del sys.setdefaultencoding
        configLog = logging.getLogger('Config')
        configLog.info('Default encoding set to %s', sys.getdefaultencoding())


def resMgrListDir(path, fnpat=None):
    dir = ResMgr.openSection(path)
    if dir is None:
        return
    elif not fnpat:
        return dir.keys()
    else:
        return [ n for n in dir.keys() if fnmatch.fnmatch(n, fnpat) ]


def resMgrDirExists(path):
    return ResMgr.openSection(path) != None


def getsitepackages():
    sitepackages = []
    seen = set()
    from soft_exception import SoftException
    if not PLATFORM_SUFFIX:
        raise SoftException('Unable to determine platform suffix')
    for prefix in sys.path:
        if not prefix or prefix in seen:
            continue
        seen.add(prefix)
        if prefix.endswith('scripts/server_common'):
            fullPath = os.path.join(prefix, 'site-packages') + '/' + PLATFORM_SUFFIX
            sitepackages.append(fullPath)
        sitepackages.append(os.path.join(prefix, 'site-packages'))

    return sitepackages


def _init_pathinfo():
    return set(sys.path)


def addpackage(sitedir, name, known_paths):
    if known_paths is None:
        _init_pathinfo()
        reset = 1
    else:
        reset = 0
    fullname = os.path.join(sitedir, name)
    try:
        f = open(fullname, 'rU')
    except IOError as e:
        print('ioerror', e, fullname, file=sys.stderr)
        return

    with f:
        resolveToAbs = False
        for n, line in enumerate(f):
            if line.startswith('#'):
                continue
            if line.startswith('@'):
                resolveToAbs = True
                continue
            try:
                if line.startswith(('import ', 'import\t')):
                    exec line
                    continue
                line = line.rstrip()
                relativeDir = os.path.join(sitedir, line)
                if resolveToAbs:
                    dir = ResMgr.resolveToAbsolutePath(relativeDir)
                else:
                    dir = relativeDir
                if dir not in known_paths and resMgrDirExists(relativeDir):
                    sys.path.append(dir)
                    known_paths.add(dir)
            except Exception as err:
                print('Error processing line {:d} of {}:\n'.format(n + 1, fullname), file=sys.stderr)
                for record in traceback.format_exception(*sys.exc_info()):
                    for line in record.splitlines():
                        print('  ' + line, file=sys.stderr)

                print('\nRemainder of file ignored', file=sys.stderr)
                break

    if reset:
        known_paths = None
    return known_paths


def addsitedir(sitedir, known_paths=None):
    if known_paths is None:
        known_paths = _init_pathinfo()
        reset = 1
    else:
        reset = 0
    if sitedir not in known_paths:
        sys.path.append(sitedir)
    names = resMgrListDir(sitedir, '*.pth')
    if names is None or len(names) == 0:
        return
    else:
        for name in sorted(names):
            addpackage(sitedir, name, known_paths)

        if reset:
            known_paths = None
        return known_paths


def addsitepackages(known_paths):
    for sitedir in getsitepackages():
        if resMgrDirExists(sitedir):
            addsitedir(sitedir, known_paths)

    return known_paths


def setup_paths():
    known_paths = set(sys.path)
    addsitepackages(known_paths)
    sys.path = [ p.replace('\\', '/') for p in sys.path ]


@BWUtil.if_only_component('base', 'service', 'cell', 'database')
def set_twisted_reactor():
    import BWTwistedReactor
    import twisted.internet.default
    twisted.internet.default = BWTwistedReactor


def set_builtin_open_patch():
    BWUtil.monkeyPatchOpen(full_replace=BigWorld.component in ('client', 'bot'))


@BWUtil.if_only_component('client', 'bot')
def revert_builtin_open_patch():
    BWUtil.revertPatchedOpen()


@BWUtil.if_only_not_component('process_defs')
def set_threading_bootstrap():
    import threading
    orig_bootstrap = threading.Thread._Thread__bootstrap

    def hooked_bootstrap(self):
        BigWorld.__onThreadStart(self.name)
        orig_bootstrap(self)
        BigWorld.__onThreadEnd()

    threading.Thread._Thread__bootstrap = hooked_bootstrap


def main():
    BWLogging.init()
    set_builtin_open_patch()
    set_threading_bootstrap()
    set_helper()
    set_default_encoding()
    setup_paths()
    revert_builtin_open_patch()
    set_twisted_reactor()
    import bwpydevd
    bwpydevd.startDebug(isStartUp=True)


main()
try:
    import BWAutoImport
except ImportError as e:
    NOTICE_MSG('bw_site.py failed to import BWAutoImport: %s\n' % (e,))
