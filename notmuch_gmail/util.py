# Copyright (c) 2018 Robin Jarry
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import logging.config
import os


#------------------------------------------------------------------------------
UNITS = ['B', 'K', 'M', 'G', 'T', 'P', 'E']
def human_size(size):
    try:
        if size < 1000:
            return str(size)
        else:
            u = 0
            while size >= 1000 and u < len(UNITS):
                size /= 1000
                u += 1
            return '%.1f%s' % (size, UNITS[u])
    except:
        return size

#------------------------------------------------------------------------------
def configure_logging(verbose=0, logfile=None):
    conf = {
        'version': 1,
        'reset_existing_loggers': True,
        'formatters': {
            'simple': {
                'format': '%(asctime)s %(levelname)s %(message)s',
                'datefmt': '%H:%M:%S',
            },
        },
        'root': {
            'level': 'DEBUG' if verbose > 0 else 'INFO',
        },
        'loggers': {
            'notmuch_gmail': {
                'level': 'DEBUG' if verbose > 0 else 'INFO',
            },
            'googleapiclient': {
                'level': 'DEBUG' if verbose > 1 else 'WARNING',
            },
        },
    }

    if logfile is not None:
        conf['handlers'] = {
            'file': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': logfile,
                'formatter': 'simple',
                'when': 'midnight',
                'delay': True,
                'backupCount': 2,
                'encoding': 'utf-8',
            },
        }
        conf['root']['handlers'] = ['file']

    else:
        conf['handlers'] = {
            'stdout': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',
                'formatter': 'simple',
                'level': 'DEBUG',
            },
        }
        conf['root']['handlers'] = ['stdout']
        logging.addLevelName(logging.ERROR, 'E')
        logging.addLevelName(logging.WARNING, 'W')
        logging.addLevelName(logging.INFO, 'I')
        logging.addLevelName(logging.DEBUG, 'D')

    logging.config.dictConfig(conf)

#------------------------------------------------------------------------------
class PIDFile(object):

    class AlreadyRunning(Exception):
        pass

    def __init__(self, config):
        self.filepath = os.path.join(config.status_dir, 'pidfile')

    def create(self):
        dirname = os.path.dirname(self.filepath)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)

        try:
            with open(self.filepath, 'r') as f:
                other_pid = int(f.readline().strip())
            os.kill(other_pid, 0)
        except:
            other_pid = None

        if other_pid is not None:
            raise self.AlreadyRunning('PID=%d' % other_pid)

        with open(self.filepath, 'w') as f:
            f.write('%d\n' % os.getpid())

    def close(self):
        if os.path.isfile(self.filepath):
            os.unlink(self.filepath)

    def __enter__(self):
        self.create()
        return self

    def __exit__(self, exc_type=None, exc_value=None, exc_tb=None):
        self.close()
