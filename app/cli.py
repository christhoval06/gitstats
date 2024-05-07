#!/usr/bin/env python3
# Copyright (c) 2007-2014 Heikki Hokkanen <hoxu@users.sf.net> & others (see doc/AUTHOR)
# GPLv2 / GPLv3
import os
import sys
import time

from config import JSONFILE
from stats import GitStats
from locals import locals

if __name__=='__main__':
	g = GitStats()
	outputpath = g.run(sys.argv[1:])

	time_end = time.time()
	exectime_internal = time_end - locals.time_start
	print('Execution time %.5f secs, %.5f secs (%.2f %%) in external commands)' % (exectime_internal, locals.exectime_external, (100.0 * locals.exectime_external) / exectime_internal))
	if sys.stdin.isatty():
		print('You may now run:')
		print()
		print(f"open '{os.path.join(outputpath, 'index.html')}'")
		print(f"open '{os.path.join(outputpath, JSONFILE)}'")
		print()

