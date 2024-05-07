import calendar
import datetime
import json
import os
import shutil
from report import ReportCreator
import tailadmin as ta
from config import WEEKDAYS, conf, colors, chart_base_color
from utils import getkeyssortedbyvaluekey, getkeyssortedbyvalues, getversion


class HTMLReportCreator(ReportCreator):
	def create(self, data, path):
		ReportCreator.create(self, data, path)
		self.title = data.projectname

		# copy static files. Looks in the binary directory, ../share/gitstats and /usr/share/gitstats
		binarypath = os.path.dirname(os.path.abspath(__file__))
		secondarypath = os.path.join(binarypath, '..', 'share', 'gitstats')
		basedirs = [binarypath, secondarypath, '/usr/share/gitstats']
		for file in (conf['style']):
			for base in basedirs:
				src = base + '/' + file
				if os.path.exists(src):
					shutil.copyfile(src, path + '/' + file)
					break
			else:
				print('Warning: "%s" not found, so not copied (searched: %s)' % (file, basedirs))
		##
		# index.html
		# General
		format = '%Y-%m-%d %H:%M:%S'

		general_html = ta.HTML(path=f'{path}/index.html', title=f"{data.projectname}'S STATS", version= getversion())

		general_html.add('<div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">')
		general_html.tilesItemStat(title='Project name', info=data.projectname, icon =ta.Icons.Trophy.value.format("w-7 h-7 fill-emerald-500"))
		general_html.tilesItemStat(title='Generated', info=datetime.datetime.now().strftime(format), icon =ta.Icons.CalendarCheck.value.format("w-7 h-7 fill-emerald-500"))
		general_html.tilesItemStat(title='Report Period', info=f'{data.getFirstCommitDate().strftime(format)} to {data.getLastCommitDate().strftime(format)}', icon =ta.Icons.CalendarWeek.value.format("w-7 h-7 fill-emerald-500"))
		general_html.add('</div>')

		
		general_html.add('<div class="grid grid-cols-1 gap-4 md:grid-cols-2 md:gap-6 xl:grid-cols-4 2xl:gap-7.5">')
		general_html.cardItemStat(title='Branches', count=data.total_branches, icon=ta.Icons.Branch.value.format('fill-primary dark:fill-white w-5 h-5'))
		general_html.cardItemStat(title='Tags', count=data.total_tags, icon=ta.Icons.Tags.value.format('fill-primary dark:fill-white w-5 h-5'))
		general_html.cardItemStat(title='Age', count=f'{data.getCommitDeltaDays():.1f} days', icon=ta.Icons.Calendar.value.format('fill-primary dark:fill-white w-5 h-5'))
		general_html.cardItemStat(title='Active days', count=f'{len(data.getActiveDays())}', stat=f'{(100.0 * len(data.getActiveDays()) / data.getCommitDeltaDays()):3.2f}%', arrow='up', icon=ta.Icons.CalendarCheck.value.format('fill-primary dark:fill-white w-5 h-5'))
		general_html.cardItemStat(title='Total files', count=data.getTotalFiles(), icon=ta.Icons.File.value.format('fill-primary dark:fill-white w-5 h-5'))
		general_html.cardItemStat(title='Total LOC', count=data.getTotalLOC(), icon=ta.Icons.Code.value.format('fill-primary dark:fill-white w-5 h-5'))
		general_html.cardItemStat(title='Total lines added', count=data.total_lines_added, stat=f'{((data.total_lines_added/data.getTotalLOC())*100):.2f}%', arrow='up', icon=ta.Icons.ArrowTrendUp.value.format('fill-primary dark:fill-white w-5 h-5'))
		general_html.cardItemStat(title='Total lines removed', count=data.total_lines_removed, stat=f'{((data.total_lines_removed/data.getTotalLOC())*100):.2f}%', arrow='up', icon=ta.Icons.ArrowTrendDown.value.format('fill-primary dark:fill-white w-5 h-5'))
		general_html.cardItemStat(title='Total commits', count=data.getTotalCommits(), stat=f'{(float(data.getTotalCommits()) / len(data.getActiveDays())):.1f}', arrow='up', icon=ta.Icons.CodeCommit.value.format('fill-primary dark:fill-white w-5 h-5'))
		general_html.cardItemStat(title='Authors', count=data.getTotalAuthors(), stat=f'{((1.0 * data.getTotalCommits()) / data.getTotalAuthors()):.1f}', arrow='up', icon=ta.Icons.Users.value.format('fill-primary dark:fill-white w-5 h-5'))
		general_html.add('</div>')

		# general_content.append('<div><div class="card-body"><dl>')
		# general_content.append('<dt>Project name</dt><dd>%s (%s branches, %s tags)</dd>' % (data.projectname, data.total_branches, data.total_tags))
		# general_content.append('<dt>Generated</dt><dd>%s (in %d seconds)</dd>' % (datetime.datetime.now().strftime(format), time.time() - data.getStampCreated()))
		# general_content.append('<dt>Generator</dt><dd><a href="http://gitstats.sourceforge.net/">GitStats</a> (version %s), %s, %s</dd>' % (getversion(), getgitversion(), getgnuplotversion()))
		# general_content.append('<dt>Report Period</dt><dd>%s to %s</dd>' % (data.getFirstCommitDate().strftime(format), data.getLastCommitDate().strftime(format)))
		# general_content.append('<dt>Age</dt><dd>%d days, %d active days (%3.2f%%)</dd>' % (data.getCommitDeltaDays(), len(data.getActiveDays()), (100.0 * len(data.getActiveDays()) / data.getCommitDeltaDays())))
		# general_content.append('<dt>Total Files</dt><dd>%s</dd>' % data.getTotalFiles())
		# general_content.append('<dt>Total Lines of Code</dt><dd>%s (%d added, %d removed)</dd>' % (data.getTotalLOC(), data.total_lines_added, data.total_lines_removed))
		# general_content.append('<dt>Total Commits</dt><dd>%s (average %.1f commits per active day, %.1f per all days)</dd>' % (data.getTotalCommits(), float(data.getTotalCommits()) / len(data.getActiveDays()), float(data.getTotalCommits()) / data.getCommitDeltaDays()))
		# general_content.append('<dt>Authors</dt><dd>%s (average %.1f commits per author)</dd>' % (data.getTotalAuthors(), (1.0 * data.getTotalCommits()) / data.getTotalAuthors()))
		# general_content.append('</dl></div></div>')

		general_html.create()


		chart_default_config = json.load(open('chart.json'))

		###
		# activity.html
		# Activity
		totalcommits = data.getTotalCommits()

		activity_html = ta.HTML(path=f'{path}/activity.html', title='Activity', version= getversion())

		activity_html.add('<div class="grid grid-cols-12 gap-4 md:gap-6 2xl:gap-7.5">')

		# Activity :: Last 30 days
		# Activity :: Last 12 month
		end_date = data.getLastCommitDate()
		start_date = end_date - datetime.timedelta(days=365)

		# print('data.getActivityByDate()', data.getActivityByDate())

		# Activity :: Weekly activity
		WEEKS = 32
		# generate weeks to show (previous N weeks from now)
		now = datetime.datetime.now()
		deltaweek = datetime.timedelta(7)
		weeks = []
		stampcur = now
		for i in range(0, WEEKS):
			weeks.insert(0, stampcur.strftime('%Y-%W'))
			stampcur -= deltaweek
		
		activity_per_weekly_series = [
			{"name": "Commits", "color": chart_base_color, "data": []},
			# {"name": "Percentage", "color": "#779EF1", "data": []},
		]
		for i in range(0, WEEKS):
			commits = data.activity_by_year_week[weeks[i]] if weeks[i] in data.activity_by_year_week else 0
			activity_per_weekly_series[0]['data'].append({"x": f'{WEEKS-i}', "y": commits})
			# activity_per_weekly_series[1]['data'].append({"x": f'{WEEKS-i}', "y": f'{((100.0 * commits) / totalcommits):.2f}'})
		
		activity_per_weekly_config = {
			**chart_default_config,
			"series": activity_per_weekly_series
		}

		activity_html.addChart(activity_per_weekly_config, name='chartWeeklyActivity', title=f'Weekly activity <span class="text-xs font-medium">Last {WEEKS} weeks</span>', className="")
		

		# Activity :: Hour of Day
		hour_of_day = data.getActivityByHourOfDay()

		activity_per_hours_day_series = [
			{"name": "Commits", "color": chart_base_color, "data": []},
			# {"name": "Percentage", "color": "#779EF1", "data": []},
		]

		for i in range(0, 24):
			commits = hour_of_day[i] if i in hour_of_day else 0
			activity_per_hours_day_series[0]["data"].append({"x": f'{i}', "y": commits})
			# activity_per_hours_day_series[1]["data"].append({"x": f'{i}', "y": f'{((100.0 * commits) / totalcommits):.2f}'})

		activity_per_hours_day_config = {
			**chart_default_config, 
			"series": activity_per_hours_day_series
		}
		
		activity_html.addChart(activity_per_hours_day_config, name='chartHourOfDay', title='Hour of Day', className="")


		# Activity :: Day of Week
		day_of_week = data.getActivityByDayOfWeek()

		activity_per_day_week_series = [
			{"name": "Commits", "color": chart_base_color, "data": []},
			# {"name": "Percentage", "color": "#779EF1", "data": []},
		]

		for d in range(0, 7):
			commits = day_of_week[d] if d in day_of_week else 0
			activity_per_day_week_series[0]["data"].append({"x": WEEKDAYS[d], "y": commits})
			# activity_per_day_week_series[1]["data"].append({"x": WEEKDAYS[d], "y": f'{((100.0 * commits) / totalcommits):.2f}'})

		activity_per_day_week_config = {
			**chart_default_config,
			"series": activity_per_day_week_series
		}
		
		activity_html.addChart(activity_per_day_week_config, name='chartDayofWeek', title='Day of Week', className="xl:col-span-4")

		# Activity :: Hour of Week
		activity_hour_of_week_series = []

		for weekday in range(0, 7):
			activity_hour_of_week_series.append({"name": WEEKDAYS[weekday], "data": []})
			for hour in range(0, 24):
				try:
					commits = data.activity_by_hour_of_week[weekday][hour]
				except KeyError:
					commits = 0
				
				activity_hour_of_week_series[weekday]["data"].append({"x": f'{hour}', "y": commits})

		activity_hour_of_week_series.reverse()

		activity_hour_of_week_config = {
			"series": activity_hour_of_week_series,
			"chart": {**chart_default_config["chart"], "type": 'heatmap'},
      		"dataLabels": chart_default_config["dataLabels"],
			"colors": ["#3C50E0"],
			"xaxis": chart_default_config["xaxis"],
			"yaxis": chart_default_config["yaxis"],
		}

		activity_html.addChart(activity_hour_of_week_config, name='chartHourOfWeek', title='Hour of Week', className="xl:col-span-8")
	
		# Activity :: Month of Year
		activity_per_month_of_year_series = [
			{"name": "Commits", "color": chart_base_color, "data": []},
			# {"name": "Percentage", "color": "#779EF1", "data": []},
		]
		for mm in range(1, 13):
			commits = data.activity_by_month_of_year[mm] if mm in data.activity_by_month_of_year else 0
			activity_per_month_of_year_series[0]["data"].append({"x": calendar.month_abbr[mm], "y": commits, "percentage": (100.0 * commits) /totalcommits})
			# activity_per_month_of_year_series[1]["data"].append({"x": calendar.month_abbr[mm], "y": f'{((100.0 * commits) /totalcommits):.2f}'})

		activity_per_month_of_year_config = {
			**chart_default_config,
			"series": activity_per_month_of_year_series
		}

		activity_html.addChart(activity_per_month_of_year_config, name='chartMonthOfYear', title='Month of Year', className="xl:col-span-5")


		# Activity :: Commits by year/month
		activity_per_year_month_serie = []
		for yymm in sorted(data.commits_by_month.keys()):
			activity_per_year_month_serie.append({"x": f'{yymm}', "y": data.commits_by_month.get(yymm,0), "lines_added": data.lines_added_by_month.get(yymm,0), "lines_removed": data.lines_removed_by_month.get(yymm,0), "percentage": (100.0 * data.commits_by_month.get(yymm,0)) /totalcommits})

		activity_per_year_month_config = {
			**chart_default_config,
			"series": [{
			"name": "Commits",
			"color": chart_base_color,
			"data": activity_per_year_month_serie}],
			"xaxis": {
				**chart_default_config["xaxis"], 
				"labels": {
					**chart_default_config["xaxis"]["labels"] , 
					"show" : False
					}}
		}

		activity_html.addChart(activity_per_year_month_config, name='chartCommitsByYearMonth', title='Commits by year/month', className="xl:col-span-7")


		# Activity :: Commits by year
		activity_by_year_series = [
			{"name": "Commits", "color": chart_base_color, "data": []},
			{"name": "Lines Added", "color": "#23961B","data": []},
			{"name": "Lines Removed", "color": "#DB1A1A","data": []},
			# {"name": "Percentage", "color": "#779EF1","data": []}
			]
		
		for yy in sorted(data.commits_by_year.keys()):
			activity_by_year_series[0]["data"].append({"x": f'{yy}', "y": data.commits_by_year.get(yy,0)})
			activity_by_year_series[1]["data"].append({"x": f'{yy}', "y": data.lines_added_by_year.get(yy,0)})
			activity_by_year_series[2]["data"].append({"x": f'{yy}', "y": data.lines_removed_by_year.get(yy,0)})
			# activity_by_year_series[3]["data"].append({"x": f'{yy}', "y": f'{((100.0 * data.commits_by_year.get(yy,0)) /totalcommits):.2f}'})

		activity_by_year_config = {
			**chart_default_config,
			"series": activity_by_year_series
			}

		activity_html.addChart(activity_by_year_config, name='chartCommitsByYear', title='Commits by Year', className="xl:col-span-6")

		# Activity :: Commits by timezone
		activity_by_timezone_series = [
			{"name": "Commits", "color": chart_base_color, "data": []},
			# {"name": "Percentage", "color": "#779EF1", "data": []},
		]
		max_commits_on_tz = max(data.commits_by_timezone.values())
		for i in sorted(data.commits_by_timezone.keys(), key = lambda n : int(n)):
			commits = data.commits_by_timezone.get(i, 0)
			activity_by_timezone_series[0]["data"].append({"x": f'{i}', "y": commits})
			# activity_by_timezone_series[1]["data"].append({"x": f'{i}', "y": f'{((100.0 * commits) /totalcommits):.2f}'})

		activity_by_timezone_config = {
			**chart_default_config,
			"series": activity_by_timezone_series
		}

		activity_html.addChart(activity_by_timezone_config, name='chartCommitsByTimezone', title='Commits by Timezone', className="xl:col-span-6")

		activity_html.add('</div>')

		activity_html.create()

		###
		# authors.html
		# Authors
		authors_html = ta.HTML(path=f'{path}/authors.html', title='Authors', version= getversion())
		authors_html.add('<div class="grid grid-cols-12 gap-4 md:gap-6 2xl:gap-7.5">')
		

		# Authors :: List of authors
		list_authors_table_data = []
		for author in data.getAuthors(conf['max_authors']):
			info = data.getAuthorInfo(author)
			list_authors_table_data.append({
				"author": author,
				"commits":'%d (<span class="text-sm">%.2f%%</span>)' % (info['commits'], info['commits_frac']),
				"lines_added": info['lines_added'],
				"lines_removed": info['lines_removed'],
				# "date_first": info['date_first'],
				# "date_last": info['date_last'],
				# "age": '%s' % info['timedelta'],
				"active_days": len(info['active_days']),
				"place_by_commits": info['place_by_commits'],
			})

		allauthors = data.getAuthors()
		if len(allauthors) > conf['max_authors']:
			rest = allauthors[conf['max_authors']:]
			# list_authors_content.append('<p class="moreauthors">These didn\'t make it to the top: %s</p>' % ', '.join(rest))
			
		authors_html.addSortableTable(
			# [('author', 'Author', False, False), ('commits', 'Commits (%)', False, True), ('lines_added', '+ lines', True, False), ('lines_removed', '- lines', True, False), ('date_first', '1st commit', True, False), ('date_last', 'Last commit', True, False), ('age', 'Age', True, False), ('active_days', 'Active days', True, False), ('place_by_commits', '# by commits', False, False)],
			[('author', 'Author', False, False), ('commits', 'Commits (%)', False, True), ('lines_added', '+ lines', True, False), ('lines_removed', '- lines', True, False), ('active_days', 'Active days', True, False), ('place_by_commits', '# by commits', False, False)],
			list_authors_table_data,
			name='authorsListTable',
			title='List of Authors')

		# Authors :: Commits
		author_disclaimer = ''
		max_authors = conf['max_authors']
		if len(allauthors) > max_authors:
			author_disclaimer =f'<span class="text-xs font-medium">Only top {max_authors} authors shown</span>'

		lines_by_authors = {} # cumulated added lines by
		# lines_removed_by_authors = {}
		# author. to save memory,
		# changes_by_date_by_author[stamp][author] is defined
		# only at points where author commits.
		# lines_by_authors allows us to generate all the
		# points in the .dat file.

		# Don't rely on getAuthors to give the same order each
		# time. Be robust and keep the list in a variable.
		commits_by_authors = {} # cumulated added lines by


		authors_cumulated_lines_added_series = {}
		# authors_cumulated_lines_removed_series = {}
		authors_commits_series = {}

		self.authors_to_plot = data.getAuthors(conf['max_authors'])
		for idx, author in enumerate(self.authors_to_plot):
			lines_by_authors[author] = 0
			# lines_removed_by_authors[author] = 0
			commits_by_authors[author] = 0

			authors_cumulated_lines_added_series[author]= {"name": author, "color": colors[idx], "data": []}
			# authors_cumulated_lines_removed_series[author]= {"name": author, "color": colors[idx], "data": []}
			authors_commits_series[author]= {"name": author, "color": colors[idx], "data": []}

		# for stamp in sorted(data.changes_by_date_by_author.keys()):
		# 	for author in self.authors_to_plot:
		# 		if author in data.changes_by_date_by_author[stamp].keys():
		# 			lines_by_authors[author] = data.changes_by_date_by_author[stamp][author]['lines_added']
		# 			commits_by_authors[author] = data.changes_by_date_by_author[stamp][author]['commits']
		# 		# authors_cumulated_commits_series[author]['data'].append({"x": stamp, "y": lines_by_authors[author]})
				
		# 		authors_cumulated_commits_series[author]['data'].append(lines_by_authors[author])
		# 		authors_commits_series[author]['data'].append(commits_by_authors[author])

		for yyMM in sorted(data.changes_by_month_by_author.keys()):
			for author in self.authors_to_plot:
				if author in data.changes_by_month_by_author[yyMM].keys():
					lines_by_authors[author] = lines_by_authors[author] + data.changes_by_month_by_author[yyMM][author]['lines_added']
					# lines_removed_by_authors[author] = lines_removed_by_authors[author] + data.changes_by_month_by_author[yyMM][author]['lines_removed']
					commits_by_authors[author] = commits_by_authors[author] + data.changes_by_month_by_author[yyMM][author]['commits']
				
				# authors_cumulated_commits_series[author]['data'].append(lines_by_authors[author])
				authors_cumulated_lines_added_series[author]['data'].append({"x": yyMM, "y": lines_by_authors[author]})
				# authors_cumulated_lines_removed_series[author]['data'].append({"x": yyMM, "y": lines_removed_by_authors[author]})
				authors_commits_series[author]['data'].append({"x": yyMM, "y": commits_by_authors[author]})
				# authors_commits_series[author]['data'].append(commits_by_authors[author])

		# Authors :: Cumulated added LoC per author
		authors_cumulated_commits_config = {
			**chart_default_config,
			"chart": {**chart_default_config["chart"], "type": 'line'},
			"series": list(authors_cumulated_lines_added_series.values()),
			"markers": {"size": 0,"hover": {"sizeOffset": 6}},
			"xaxis": {
				**chart_default_config["xaxis"], 
				"labels": {
					**chart_default_config["xaxis"]["labels"] , 
					"show" : False
					}}
		}

		authors_html.addChart(authors_cumulated_commits_config, name='chartCumulatedAddedLoCAuthor', title=f'Cumulated Added LoC per Author {author_disclaimer}', className="xl:col-span-6")

		# Authors :: Cumulated removed LoC per author
		# authors_cumulated_removed_loc_config = {
		# 	**chart_default_config,
		# 	"chart": {**chart_default_config["chart"], "type": 'line'},
		# 	"series": list(authors_cumulated_lines_removed_series.values()),
		# 	"markers": {"size": 0,"hover": {"sizeOffset": 6}},
		# 	"xaxis": {
		# 		**chart_default_config["xaxis"], 
		# 		"labels": {
		# 			**chart_default_config["xaxis"]["labels"] , 
		# 			"show" : False
		# 			}}
		# }

		# authors_html.addChart(authors_cumulated_removed_loc_config, name='chartCumulatedRemovedLoCAuthor', title=f'Cumulated removed LoC per Author {author_disclaimer}', className="xl:col-span-6")


		# Authors :: Commits per Author
		authors_commits_config = {
			**chart_default_config,
			"chart": {**chart_default_config["chart"], "type": 'line'},
			"series": list(authors_commits_series.values()),
			"markers": {"size": 0,"hover": {"sizeOffset": 6}},
			"xaxis": {
				**chart_default_config["xaxis"], 
				"labels": {
					**chart_default_config["xaxis"]["labels"] , 
					"show" : False
					}}
		}

		authors_html.addChart(authors_commits_config, name='chartCommitsPerAuthor', title=f'Commits per Author {author_disclaimer}', className="xl:col-span-6")


		# Authors :: Author of Month
		author_of_month_table_data = []
		for yymm in reversed(sorted(data.author_of_month.keys())):
			authordict = data.author_of_month[yymm]
			authors = getkeyssortedbyvalues(authordict)
			authors.reverse()
			commits = data.author_of_month[yymm][authors[0]]
			next = '<br/>'.join(authors[1:conf['authors_top']+1])
			author_of_month_table_data.append({
				"month": yymm,
				"author": authors[0],
				"commits":'%d (<span class="text-sm">%.2f%% of %d</span>)' % (commits, (100.0 * commits) / data.commits_by_month[yymm], data.commits_by_month[yymm]),
				"next_top": next,
				"number_of_authors": len(authors),
			})

		authors_html.addSortableTable(
			[('month', 'Month', False, False), ('author', 'Author', False, False), ('commits', 'Commits (%)', False, True), ('next_top', 'Next top 5', True, True), ('number_of_authors', 'Authors', True, False)],
			author_of_month_table_data,
			name='authorOfMonthTable',
			title='Author of Month')

		# Authors :: Author of Year
		author_of_year_table_data = []
		for yy in reversed(sorted(data.author_of_year.keys())):
			authordict = data.author_of_year[yy]
			authors = getkeyssortedbyvalues(authordict)
			authors.reverse()
			commits = data.author_of_year[yy][authors[0]]
			next = '<br/>'.join(authors[1:conf['authors_top']+1])
			
			author_of_year_table_data.append({
				"year": yy,
				"author": authors[0],
				"commits":'%d (<span class="text-sm">%.2f%% of %d</span>)' % (commits, (100.0 * commits) / data.commits_by_year[yy], data.commits_by_year[yy]),
				"next_top": next,
				"number_of_authors": len(authors),
			})

		authors_html.addSortableTable(
			[('year', 'Year', False, False), ('author', 'Author', False, False), ('commits', 'Commits (%)', False, True), ('next_top', 'Next top %d' % conf['authors_top'], True, True), ('number_of_authors', 'Authors', True, False)],
			author_of_year_table_data,
			name='authorOfYearTable',
			title='Author of Year')

		# Authors :: Domains
		domains_by_commits = getkeyssortedbyvaluekey(data.domains, 'commits')
		domains_by_commits.reverse() # most first

		authors_commits_by_domains_series = [{
			"name": "Commits",
			"color": chart_base_color,
			"data": []
		},{
			"name": "Percentage",
			"color": "#8FB0F6",
			"data": []
		}]
		n = 0
		for domain in domains_by_commits:
			if n == conf['max_domains']:
				break
			commits = 0
			n += 1
			info = data.getDomainInfo(domain)
			authors_commits_by_domains_series[0]['data'].append({"x": domain, "y": info['commits']})
			p = (100.0 * info['commits'] / totalcommits)
			authors_commits_by_domains_series[1]['data'].append({"x": domain, "y": f'{p:.2f}'})

		authors_commits_by_domains_config = {
			**chart_default_config,
			"series": authors_commits_by_domains_series,
		}

		authors_html.addChart(authors_commits_by_domains_config, name='chartCommitsbyDomains', title='Commits by Domains', className="xl:col-span-6")

		authors_html.add('</div>')

		authors_html.create()

		###
		# files.html
		# Files
		files_html = ta.HTML(path=f'{path}/files.html', title='Files', version= getversion())

		files_html.add('<div class="grid grid-cols-1 gap-4 md:grid-cols-2 md:gap-6 xl:grid-cols-4 2xl:gap-7.5 mb-6">')
		files_html.cardItemStat(title='Total files', count=data.getTotalFiles())
		files_html.cardItemStat(title='Total LoC', count=data.getTotalLOC())
		try:
			files_html.cardItemStat(title='Average file size', count=f'{(float(data.getTotalSize()) / data.getTotalFiles()):2f} bytes')
		except ZeroDivisionError:
			pass
		files_html.add('</div>')

		files_html.add('<div class="grid grid-cols-12 gap-4 md:gap-6 2xl:gap-7.5">')

		# Files :: File count by date
		files_by_month_series = {"name": 'Files', "color": "#3C50E0", "data": []}
		# # use set to get rid of duplicate/unnecessary entries
		# files_by_date = set()
		# for stamp in sorted(data.files_by_stamp.keys()):
		# 	files_by_date.add('%s %d' % (datetime.datetime.fromtimestamp(stamp).strftime('%Y-%m-%d'), data.files_by_stamp[stamp]))

		for yyMM in sorted(data.files_by_month.keys()):
			files_by_month_series["data"].append({"x": yyMM, "y": data.files_by_month[yyMM]})

		files_by_month_config = {
			**chart_default_config,
			"chart": {**chart_default_config["chart"], "type": 'line'},
			"series": [files_by_month_series],
			"markers": {"size": 0,"hover": {"sizeOffset": 6}},
			"xaxis": {
				**chart_default_config["xaxis"], 
				"labels": {
					**chart_default_config["xaxis"]["labels"] , 
					"show" : False
					}}
		}

		files_html.addChart(files_by_month_config, name='chartFilesByMonth', title='File count by month', className="xl:col-span-12")


		#files_content.append('<h2>Average file size by date</h2>')

		# Files :: Extensions
		files_extensions_series = {"name": 'Extensions', "color": "#3C50E0", "data": []}
		files_extensions_table_data = []
		for ext in sorted(data.extensions.keys()):
			files = data.extensions[ext]['files']
			lines = data.extensions[ext]['lines']
			try:
				loc_percentage = (100.0 * lines) / data.getTotalLOC()
			except ZeroDivisionError:
				loc_percentage = 0

			files_extensions_table_data.append({
				"extension": ext,
				'files': files,
				'files_percent': f'{((100.0 * files) / data.getTotalFiles()):.2f}',
				'lines': lines,
				'lines_percent': f'{loc_percentage:.2f}',
				'lines_per_file': f'{(lines / files):.2f}',

			})
			files_extensions_series["data"].append({"x": ext, "y": files})

		files_extensions_config = {
			"chart": {**chart_default_config["chart"], "type": 'treemap'},
			"series": [files_extensions_series],
		}

		files_html.addSortableTable(
			[('extension', 'Extension', False, False), ('files', 'Files', False, False), ('files_percent', '% Files', True, False), ('lines', 'Lines', False, False), ('lines_percent', '% Lines', True, False), ('lines_per_file', 'Lines/file', True, False)],
			files_extensions_table_data,
			name='filesExtensionsTableData',
			title='Extensions')

		files_html.addChart(files_extensions_config, name='chartFilesByExtensions', title='Extensions treemap')


		files_html.add('</div>')

		files_html.create()

		###
		# lines.html
		# Lines
		lines_content=[]
		lines_html = ta.HTML(path=f'{path}/lines.html', title='Lines', version= getversion())

		lines_html.add('<div class="grid grid-cols-1 gap-4 md:grid-cols-2 md:gap-6 xl:grid-cols-4 2xl:gap-7.5 mb-6">')
		lines_html.cardItemStat(title='Total LoC', count=data.getTotalLOC())
		lines_html.add('</div>')

		lines_html.add('<div class="grid grid-cols-12 gap-4 md:gap-6 2xl:gap-7.5">')


		lines_by_year_series = {"name": 'Lines', "color": "#3C50E0", "data": []}

		for year in sorted(data.changes_by_year.keys()):
			lines_by_year_series["data"].append({"x": year, "y": data.changes_by_year[year]['lines']})


		lines_by_year_config = {
			**chart_default_config,
			"chart": {**chart_default_config["chart"], "type": 'line'},
			"series": [lines_by_year_series],
			"markers": {"size": 0,"hover": {"sizeOffset": 6}},
			"xaxis": {
				**chart_default_config["xaxis"], 
				"labels": {
					**chart_default_config["xaxis"]["labels"] , 
					"show" : False
					}}
		}

		lines_html.addChart(lines_by_year_config, name='chartLinesOfCodeByYear', title='Lines of Code by Year', className="xl:col-span-6")

		lines_by_month_series = {"name": 'Lines', "color": "#3C50E0", "data": []}

		for yyMM in sorted(data.changes_by_month.keys()):
			lines_by_month_series["data"].append({"x": yyMM, "y": data.changes_by_month[yyMM]['lines']})

		lines_by_month_config = {
			**lines_by_year_config,
			"series": [lines_by_month_series],
		}

		lines_html.addChart(lines_by_month_config, name='chartLinesByMonth', title='Lines of Code by Month', className="xl:col-span-6")




		# Lines :: Weekly activity
		WEEKS = 32
		# lines_content.append(html_header(2, 'Weekly activity'))
		# lines_content.append('<p>Last %d weeks</p>' % WEEKS)

		# generate weeks to show (previous N weeks from now)
		now = datetime.datetime.now()
		deltaweek = datetime.timedelta(7)
		weeks = []
		stampcur = now
		for i in range(0, WEEKS):
			weeks.insert(0, stampcur.strftime('%Y-%W'))
			stampcur -= deltaweek

		lines_per_weekly_serie = {"name": "LoC", "color": chart_base_color, "data": []}
		for i in range(0, WEEKS):
			lines = data.lineactivity_by_year_week[weeks[i]] if weeks[i] in data.lineactivity_by_year_week else 0
			lines_per_weekly_serie['data'].append({"x": f'{WEEKS-i}', "y": lines})
		
		lines_per_weekly_config = {
			**chart_default_config,
			"series": [lines_per_weekly_serie]
		}

		lines_html.addChart(lines_per_weekly_config, name='chartLinesWeeklyActivity', title=f'Weekly activity <span class="text-xs font-medium">Last {WEEKS} weeks</span>', className="")		

		# Lines :: Hour of Day
		hour_of_day = data.getLineActivityByHourOfDay()

		lines_per_hours_day_serie = {"name": "LoC", "color": chart_base_color, "data": []}

		for i in range(0, 24):
			lines = hour_of_day[i] if i in hour_of_day else 0
			lines_per_hours_day_serie["data"].append({"x": f'{i}', "y": lines})

		lines_per_hours_day_config = {
			**chart_default_config, 
			"series": [lines_per_hours_day_serie]
		}
		
		lines_html.addChart(lines_per_hours_day_config, name='chartLinesHourOfDay', title='Hour of Day', className="")

		# Lines :: Day of Week
		day_of_week = data.getLineActivityByDayOfWeek()

		lines_per_day_week_serie= {"name": "LoC", "color": chart_base_color, "data": []}

		for d in range(0, 7):
			lines = day_of_week[d] if d in day_of_week else 0
			lines_per_day_week_serie["data"].append({"x": WEEKDAYS[d], "y": lines})

		lines_per_day_week_config = {
			**chart_default_config,
			"series": [lines_per_day_week_serie]
		}
		
		lines_html.addChart(lines_per_day_week_config, name='chartLinesDayofWeek', title='Day of Week', className="xl:col-span-4")


		# Lines :: Hour of Week
		lines_hour_of_week_series = []

		for weekday in range(0, 7):
			lines_hour_of_week_series.append({"name": WEEKDAYS[weekday], "data": []})
			for hour in range(0, 24):
				try:
					lines = data.lineactivity_by_hour_of_week[weekday][hour]
				except KeyError:
					lines = 0
				
				lines_hour_of_week_series[weekday]["data"].append({"x": f'{hour}', "y": lines})

		lines_hour_of_week_series.reverse()

		lines_hour_of_week_config = {
			"series": lines_hour_of_week_series,
			"chart": {**chart_default_config["chart"], "type": 'heatmap'},
      		"dataLabels": chart_default_config["dataLabels"],
			"colors": ["#3C50E0"],
			"xaxis": chart_default_config["xaxis"],
			"yaxis": chart_default_config["yaxis"],
		}

		lines_html.addChart(lines_hour_of_week_config, name='chartLinesHourOfWeek', title='Hour of Week', className="xl:col-span-8")
	


		# Lines :: Month of Year
		lines_per_month_of_year_series= {"name": "LoC", "color": chart_base_color, "data": []}
		
		for mm in range(1, 13):
			lines = data.lineactivity_by_month_of_year[mm] if mm in data.lineactivity_by_month_of_year else 0
			lines_per_month_of_year_series["data"].append({"x": f'{mm}', "y": lines, "percentage": (100.0 * lines) /data.getTotalLines()})

		lines_per_month_of_year_config = {
			**chart_default_config,
			"series": [lines_per_month_of_year_series]
		}

		lines_html.addChart(lines_per_month_of_year_config, name='chartLinesMonthOfYear', title='Month of Year', className="xl:col-span-5")


		# Lines :: Lines by year/month
		lines_per_year_month_serie = []
		
		for yymm in sorted(data.commits_by_month.keys()):
			lines_per_year_month_serie.append({"x": f'{yymm}', "y": data.lines_added_by_month.get(yymm, 0) + data.lines_removed_by_month.get(yymm, 0)})

		lines_per_year_month_config = {
			**chart_default_config,
			"series": [{
			"name": "Commits",
			"color": chart_base_color,
			"data": lines_per_year_month_serie}],
			"xaxis": {
				**chart_default_config["xaxis"], 
				"labels": {
					**activity_per_year_month_config["xaxis"]["labels"] , 
					"show" : False
					}}}

		lines_html.addChart(lines_per_year_month_config, name='chartCommitsByYearMonth', title='Lines by year/month', className="xl:col-span-7")


		# Lines :: Lines by year
		lines_by_year_serie= {"name": "Lines", "color": chart_base_color, "data": []}

		for yy in sorted(data.commits_by_year.keys()):
			lines_by_year_serie["data"].append({"x": f'{yy}', "y": data.lines_added_by_year.get(yy,0) - data.lines_removed_by_year.get(yy,0)})

		lines_by_year_config = {
			**chart_default_config,
			"series": [lines_by_year_serie]
			}

		lines_html.addChart(lines_by_year_config, name='chartLinesByYear', title='Lines by Year', className="xl:col-span-6")


		lines_html.add('</div>')

		lines_html.create(lines_content)

		###
		# tags.html
		tags_html = ta.HTML(path=f'{path}/tags.html', title='Tags', version= getversion())

		tags_html.add('<div class="grid grid-cols-1 gap-4 md:grid-cols-2 md:gap-6 xl:grid-cols-4 2xl:gap-7.5 mb-6">')
		tags_html.cardItemStat(title='Total tags', count=len(data.tags))
		tags_html.cardItemStat(title='Average commits per tag', count=f'{(1.0 * data.getTotalCommits() / len(data.tags)):.2f}')
		tags_html.add('</div>')

		tags_html.add('<div class="grid grid-cols-12 gap-4 md:gap-6 2xl:gap-7.5">')

		tags_table_data = []
		# sort the tags by date desc
		tags_sorted_by_date_desc = [el[1] for el in reversed(sorted([(el[1]['date'], el[0]) for el in list(data.tags.items())]))]
		previous_tag = None
		for tag in tags_sorted_by_date_desc:
			authorinfo = []		
			self.authors_by_commits = getkeyssortedbyvalues(data.tags[tag]['authors'])
			for i in reversed(self.authors_by_commits):
				authorinfo.append('%s <span class="text-xs">(%d commits)</span>' % (i, data.tags[tag]['authors'][i]))
			
			age = None
			if previous_tag is not None :
				age = (datetime.datetime.fromtimestamp(data.tags[previous_tag]['stamp']) - datetime.datetime.fromtimestamp(data.tags[tag]['stamp'])).days

			tags_table_data.append({
				"name": tag,
				"date": data.tags[tag]['date'],
				"age": '' if age is None else f'{age} days',
				"commits": data.tags[tag]['commits'],
				"authors": '<br/>'.join(authorinfo)
			})

			previous_tag = tag

		tags_html.addSortableTable(
			[('name', 'Name', False, False), ('date', 'Date', False, False), ('age', 'Age', False, False), ('commits', 'Commits', True, False), ('authors', 'Authors', True, True)],
			tags_table_data,
			name='tagsTnformation',
			title='Tags information')
		
		tags_html.add('</div>')
		tags_html.create()
	
	