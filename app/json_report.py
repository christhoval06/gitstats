import json
from collector import GitDataCollectorJSONEncoder
from report import ReportCreator


class JSONReportCreator(ReportCreator):
    def create(self, data, filename):
        f = open(filename, 'w')
        json.dump(data, f, indent=True,
                cls=GitDataCollectorJSONEncoder)
        f.close()
