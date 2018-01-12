# This file is part of notmuch-gmail-sync.
#
# It is released under the MIT license (see the LICENSE file for more details).

import io
import os
import datetime
import re
import subprocess


HERE = os.path.dirname(__file__)

#------------------------------------------------------------------------------
def _tag_to_pep440_version(tag):
    version = re.sub(r'^v', '', tag)

    git_tag_re = re.compile(r'''
        ^
        (?P<major>\d+)\.
        (?P<minor>\d+)\.
        (?P<patch>\d+)
        (\.post(?P<post>\d+))?
        (-(?P<dev>\d+))?
        (-g(?P<commit>.+))?
        $
        ''', re.VERBOSE)

    match = git_tag_re.match(version)
    if match:
        d = match.groupdict()
        fmt = '{major}.{minor}.{patch}'
        if d.get('post'):
            fmt += '.post.{post}'
        if d.get('dev'):
            d['patch'] = int(d['patch']) + 1
            fmt += '.dev.{dev}'
        return fmt.format(**d)

    return datetime.datetime.now().strftime('%Y.%m.%d')

#------------------------------------------------------------------------------
def _tag_from_git_describe():
    if not os.path.isdir(os.path.join(HERE, '../.git')):
        raise ValueError('not in git repo')

    out = subprocess.check_output(['git', 'describe', '--always'],
                                  cwd=HERE, stderr=subprocess.STDOUT)
    return out.strip().decode('utf-8')

#------------------------------------------------------------------------------
def _version_from_git_archive_id(git_archive_id='$Format:%ct %d$'):
    if git_archive_id.startswith('$For''mat:'):
        raise ValueError('not a git archive')

    match = re.search(r'tag:\s*v([^,)]+)', git_archive_id)
    if match:
        # archived revision is tagged, use the tag
        return _tag_to_pep440_version(match.group(1))

    # archived revision is not tagged, use the commit date
    tstamp = git_archive_id.strip().split()[0]
    d = datetime.datetime.fromtimestamp(int(tstamp))
    return d.strftime('%Y.%m.%d')

#------------------------------------------------------------------------------
def _version():
    try:
        tag = _tag_from_git_describe()
        version = _tag_to_pep440_version(tag)
        with io.open(os.path.join(HERE, 'VERSION'), 'w') as f:
            f.write(version)
        return version
    except:
        pass
    try:
        with io.open(os.path.join(HERE, 'VERSION'), 'r') as f:
            version = f.read()
        return version.strip()
    except:
        pass
    try:
        return _version_from_git_archive_id()
    except:
        pass

    return 'latest'

VERSION = _version()