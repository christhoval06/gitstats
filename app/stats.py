import getopt
import os
import sys

from collector import GitDataCollector
from config import JSONFILE, conf
from html_report import HTMLReportCreator
from json_report import JSONReportCreator
from utils import usage


class GitStats:
    def run(self, args_orig):
        optlist, args = getopt.getopt(args_orig, 'hc:', ["help"])
        for o, v in optlist:
            if o == '-c':
                key, value = v.split('=', 1)
                if key not in conf:
                    raise KeyError('no such key "%s" in config' % key)
                if isinstance(conf[key], int):
                    conf[key] = int(value)
                elif isinstance(conf[key], list):
                    conf[key].append(value)
                else:
                    conf[key] = value
            elif o in ('-h', '--help'):
                usage()
                sys.exit()

        if len(args) < 2:
            usage()
            sys.exit(0)

        outputpath = os.path.abspath(args[-1])
        rundir = os.getcwd()

        try:
            os.makedirs(outputpath)
        except OSError:
            pass
        if not os.path.isdir(outputpath):
            print('FATAL: Output path is not a directory or does not exist')
            sys.exit(1)

        print('Output path: %s' % outputpath)
        cachefile = os.path.join(outputpath, 'gitstats.cache')

        data = GitDataCollector()
        data.loadCache(cachefile)

        for gitpath in args[0:-1]:
            print('Git path: %s' % gitpath)

            prevdir = os.getcwd()
            os.chdir(gitpath)

            print('Collecting data...')
            data.collect(gitpath)

            os.chdir(prevdir)

        print('Refining data...')
        data.saveCache(cachefile)
        data.refine()

        os.chdir(rundir)

        print('Generating HTML report...')
        report = HTMLReportCreator()
        report.create(data, outputpath)

        print('Generating JSON report...')
        report = JSONReportCreator()
        report.create(data, os.path.join(outputpath, JSONFILE))
        
        return outputpath
