import os
import re
import subprocess
import sys
import time

from config import ON_LINUX, conf
from locals import locals

def getpipeoutput(cmds, quiet = False):
	start = time.time()
	if not quiet and ON_LINUX and os.isatty(1):
		print('>> ' + ' | '.join(cmds))
		sys.stdout.flush()
	p = subprocess.Popen(cmds[0], stdout = subprocess.PIPE, shell = True)
	processes=[p]
	for x in cmds[1:]:
		p = subprocess.Popen(x, stdin = p.stdout, stdout = subprocess.PIPE, shell = True)
		processes.append(p)
	output = (p.communicate()[0]).decode("utf-8")
	for p in processes:
		p.wait()
	end = time.time()
	if not quiet:
		if ON_LINUX and os.isatty(1):
			print('\r')
		print('[%.5f] >> %s' % (end - start, ' | '.join(cmds)))
	locals.exectime_external += (end - start)
	return output.rstrip('\n')

def getlogrange(defaultrange = 'HEAD', end_only = True):
	commit_range = getcommitrange(defaultrange, end_only)
	datesel = ''
	if len(conf['start_date']) > 0:
		datesel = '--since="%s" %s' % (conf['start_date'], datesel)
	if len(conf['end_date']) > 0:
		datesel = '--until="%s" %s' % (conf['end_date'], datesel)
    
	if (len(datesel) > 0):
		commit_range = '%s "%s"' % (datesel, commit_range)

	return commit_range

def getcommitrange(defaultrange = 'HEAD', end_only = False):
	if len(conf['commit_end']) > 0:
		if end_only or len(conf['commit_begin']) == 0:
			return conf['commit_end']
		return '%s..%s' % (conf['commit_begin'], conf['commit_end'])
	return defaultrange

def getkeyssortedbyvalues(dict):
	return [el[1] for el in sorted([(el[1], el[0]) for el in list(dict.items())])]

# dict['author'] = { 'commits': 512 } - ...key(dict, 'commits')
def getkeyssortedbyvaluekey(d, key):
	return [el[1] for el in sorted([(d[el][key], el) for el in list(d.keys())])]

def getstatsummarycounts(line):
	numbers = re.findall('\d+', line)
	if   len(numbers) == 1:
		# neither insertions nor deletions: may probably only happen for "0 files changed"
		numbers.append(0);
		numbers.append(0);
	elif len(numbers) == 2 and line.find('(+)') != -1:
		numbers.append(0);    # only insertions were printed on line
	elif len(numbers) == 2 and line.find('(-)') != -1:
		numbers.insert(1, 0); # only deletions were printed on line
	return numbers

VERSION = 0
def getversion():
	global VERSION
	if VERSION == 0:
		gitstats_repo = os.path.dirname(os.path.abspath(__file__))
		VERSION = getpipeoutput(["git --git-dir=%s/.git --work-tree=%s rev-parse --short %s" %
			(gitstats_repo, gitstats_repo, getcommitrange('HEAD').split('\n')[0])])
	return VERSION

def getgitversion():
	return getpipeoutput(['git --version']).split('\n')[0]

def getnumoffilesfromrev(time_rev):
	"""
	Get number of files changed in commit
	"""
	time, rev = time_rev
	return (int(time), rev, int(getpipeoutput(['git ls-tree -r --name-only "%s"' % rev, 'wc -l']).split('\n')[0]))

def getnumoflinesinblob(ext_blob):
	"""
	Get number of lines in blob
	"""
	ext, blob_id = ext_blob
	return (ext, blob_id, int(getpipeoutput(['git cat-file blob %s' % blob_id, 'wc -l']).split()[0]))



def usage():
	print(f"""
Usage: gitstats [options] <gitpath..> <outputpath>

Options:
-c key=value     Override configuration value

Default config values:
{conf}

Please see the manual page for more details.
""")