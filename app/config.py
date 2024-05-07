import multiprocessing
import os
import platform

os.environ['LC_ALL'] = 'C'

ON_LINUX = (platform.system() == 'Linux')
WEEKDAYS = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
JSONFILE = 'gitstats.json'


conf = {
	'max_domains': 10,
	'max_ext_length': 10,
	'style': 'gitstats.css',
	'max_authors': 20,
	'authors_top': 5,
	'commit_begin': '',
	'commit_end': 'HEAD',
	'linear_linestats': 1,
	'project_name': '',
	'processes': multiprocessing.cpu_count(),
	'start_date': '',
	'end_date': '',
	'excluded_authors': [],
	'excluded_prefixes': []
}

chart_base_color = "#1A56DB"

colors = [
		"#4B0082",
		"#2E8B57",
		"#7B68EE",
		"#BA55D3",
		"#DB7093",
		"#FFD700",
		"#006400",
		"#008080",
		"#191970",
		"#0000CD",
		"#CD5C5C",
		"#FAFAD2",
		"#7FFF00",
		"#9966CC",
		"#D2B48C",
		"#000080",
		"#AFEEEE",
		"#8B008B",
		"#008000",
		"#6A5ACD"]