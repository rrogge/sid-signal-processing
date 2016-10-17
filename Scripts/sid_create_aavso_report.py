#!/usr/bin/env python

"""
Copyright 2011	Gary A. Richardson	garyr@fidalgo.net

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to
deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

"""
A PROGRAM TO GENERATE AN AAVSO SUDDEN IONOSPHERIC DISTURBANCE REPORT

Input data is supplied in a text file having the following format:

The observer, station, frequency, year and month must be specified at the
beginning of the file. Each value is identified by a keyword and the value
separated by at least one space. The station keyword must be followed by the
three-letter station code and the frequency in KHz.

The event data then follows consisting of the day of the event, start time,
max time, end time and definition, in that order. These values must be
separated by at least one space.
	
	Day of event may be 1 or 2 digits and must be between 1 and 31.
	
	Start, Max and End time must be 4 digits in the range 0000 to 2359.
	The times may also have an additional character appended: E, U or
	(D or U) respectively.
	
	Definition must be one digit in the range 1 to 5.

The entries do not need to be in order by date.

The event data for more than one station may be contained in a single file.
If so, the end of each group of event data must be indicated by an ENDGROUP
keyword followed by the new STATION keyword.

Lines beginning with # and blank lines are ignored.

For example, the following data:

OBSERVER A128
YEAR 11
MONTH 3

STATION NPM 21.4
13   0300    0310U   0400        3
 01   1234E   1250    1255        5		Comment text OK here
14   0240    0250    0310D       4
08   0226    0230    0315        5
ENDGROUP

STATION NAA 24.8
13   0300    0400U   0410        3
 01   1234E   1350    1355        5
14   0340    0350    0410D       4
09   0226    0230    0315        5
ENDGROUP

will generate the following files:

============= A128NPM.DAT =========================
AAVSO Sudden Ionospheric Disturbance Report
Observer: A128    11/03

40   110301  1234E1255 1250                 1     5PM21              A128

40   110308  0226 0315 0230                 2+    5PM21              A128

40   110313  0300 0400 0310U                2+    3PM21              A128

40   110314  0240 0310D0250                 1+    4PM21              A128

============= A128NAA.DAT ==========================
AAVSO Sudden Ionospheric Disturbance Report
Observer: A128    11/03

40   110301  1234E1355 1350                 2+    5AA25              A128

40   110309  0226 0315 0230                 2+    5AA25              A128

40   110313  0300 0410 0400U                2+    3AA25              A128

40   110314  0340 0410D0350                 1+    4AA25              A128

-- end report --

RUN THIS PROGRAM FROM A COMMAND PROMPT. A dialog window will be displayed
from which you can specify the file containing the source data. The source data
file can reside in any directory; the result files are created in the directory
containing the source data.

"""
import sys, string, os.path, re, exceptions, datetime, os

class ReportException(exceptions.Exception):
	pass

OBSERVERMASK = 1
STATIONMASK = 2
YEARMASK = 4
MONTHMASK = 8
HEADERMASK = OBSERVERMASK | STATIONMASK | YEARMASK | MONTHMASK
DATAMASK = 0X10

class Report:
	def __init__(self, filename):
		self.infile = file(filename)
		observerPat = re.compile(r'OBSERVER *(A\d{2,3})', re.IGNORECASE)
		stationPat = re.compile(r'STATION *([A-Z]{3}) *(\d+.\d+)', re.IGNORECASE)
		yearPat = re.compile(r'YEAR *(\d{2,3})', re.IGNORECASE)
		monthPat = re.compile(r'MONTH *(\d{1,2})', re.IGNORECASE)
		dataPat = re.compile(r'(\d{1,2}) *(\d{4}[DEU]?) *(\d{4}[DEU]?) *(\d{4}[DEU]?) *(\d+)')
		endgroupPat = re.compile(r'ENDGROUP', re.IGNORECASE)
		self.patterns = (observerPat, stationPat, yearPat, monthPat, dataPat, endgroupPat)
		self.hmPat = re.compile('(\d\d) *(\d\d)')
		self.state = 0
	
	def validateEntry(self, event, line):
		date = int(event[0])
		if (date < 1) or (date > 31):
			raise ReportException, 'Invalid date in line "%s" ' % (line,)
		
		t = []
		for k in range(1, 4):
			h, m = self.hmPat.findall(event[k])[0]
			h, m = int(h), int(m)
			if h > 23:
				raise ReportException, 'Invalid hour in line "%s" ' % (line,)
			if m > 59:
				raise ReportException, 'Invalid minute in line "%s" ' % (line,)
			t.append(h*60 + m)	# time in minutes
		
		# t contains startTime, maxTime, endTime
		if t[0] > t[1] or t[1] > t[2]:
			raise ReportException, 'Invalid time values in line "%s" ' % (line,)
		
		definition = int(event[4])
		if definition not in (1, 2,3,4,5):
			raise ReportException, 'Invalid definition in line "%s" ' % (line,)
	
	def processGroup(self):
		events = []
		N = len(self.patterns)
		while 1:
			try:
				line =  self.infile.next().strip()
				if (not line) or (line[0] == '#'):
					continue
				match = False
				for k in range(N):
					mo = re.match(self.patterns[k], line)
					if mo:
						if k == 5:
							# New group encountered
							self.state &= ~(STATIONMASK | DATAMASK)
							return events
						if k == 0:
							self.observer = mo.groups()[0]
							self.state |= OBSERVERMASK
							match = True
						elif k == 1:
							if self.state & STATIONMASK:
								# New station keyword encountered.
								raise ReportException, 'ENDGROUP keyword missing'
							self.station = mo.groups()[0]
							self.frequency = mo.groups()[1]
							self.state |= STATIONMASK
							match = True
						elif k == 2:
							self.year = mo.groups()[0]
							self.state |= YEARMASK
							match = True
						elif k == 3:
							month =  mo.groups()[0]
							if 0 < int(month) and int(month) < 13:
								self.month = month
								self.state |= MONTHMASK
								match = True
							else:
								raise ReportException, 'Invalid month in line "%s"' % (line,)
						else:
							if (self.state & HEADERMASK) != HEADERMASK:
								missing = self.state ^ HEADERMASK
								dirx = {OBSERVERMASK : 'Observer', STATIONMASK : 'Station', YEARMASK : 'Year', MONTHMASK : 'Month'}
								mask = 1
								tmp = ''
								while missing:
									if mask & missing:
										tmp = '%s, %s' % (tmp, dirx[mask])
										missing &= ~mask
									mask <<= 1
								raise ReportException,  'Missing or incorrect keyword information: %s' % (tmp[1:],)
							self.validateEntry( mo.groups(), line)
							events.append(mo.groups())
							self.state |= DATAMASK
							match = True
				if not match:
					raise ReportException, 'Invalid or missing data in line: %s' % (line, )
			except StopIteration:
				return events
		raise StopIteration
	
	def computeImportance(self, startTime, endTime):
		g = re.findall(r'(\d\d)(\d\d)', startTime)[0]
		h = g[0]
		m = g[1]
		tstart = datetime.time(hour=int(h), minute=int(m))
		g = re.findall(r'(\d\d)(\d\d)', endTime)[0]
		h = g[0]
		m = g[1]
		tend = datetime.time(hour=int(h), minute=int(m))
		now = datetime.datetime.now()
		dstart = datetime.datetime.combine(now, tstart)
		dend = datetime.datetime.combine(now, tend)
		duration = (dend - dstart).seconds / 60
		for r, durCode in ((19, '1-'), (26, '1 '), (33, '1+'), (46, '2 '), (86, '2+'), (125, '3 '), (sys.maxint, '3+')):
			if duration < r:
				break
		return durCode
	
	def sortEvents(self, events):
		# Sort events by date and start time
		def eventCompare(e1, e2):
			d, h, min = e1[0], e1[1][:2], e1[1][2:]
			if len(min) > 2:
				min = min[:2]
			date1 = datetime.datetime(1, 1, int(d), int(h), int(min))
			d, h, min = e2[0], e2[1][:2], e2[1][2:]
			if len(min) > 2:
				min = min[:2]
			date2 = datetime.datetime(1, 1, int(d), int(h), int(min))
			if date1 < date2:
				return -1
			elif date1 > date2:
				return 1
			else:
				return 0
		
		events.sort(eventCompare)
		return events
	
	def generateReport(self, events, filename):
		
		def insertText(s, loc, text):
			for k in range(len(text)):
				s[loc + k - 1] = text[k]
			return s
		fn = self.observer + self.station + '.dat'
		pathname= os.path.join(os.path.dirname(filename), fn)
		outfile = file(pathname, 'w')
		header = 'AAVSO Sudden Ionospheric Disturbance Report\n'
		outfile.write(header)
		print
		print header[:-1]
		
		line = [' ' for k in range(80)]
		L = 'Observer: ' + self.observer + ' '*30
		insertText(line, 1, L)
		date = '%02d/%02d' % (int(self.year), int(self.month))
		insertText(line, 19, date)
		line1 =string.join(line, '').strip() + '\n\n'
		outfile.write(line1)
		print line1[:-1]
		
		stationCode = self.station[1:] + str(int(round(float(self.frequency))))
		date = '%02d%02d' % (int(self.year), int(self.month))
		for s in events:
			if not s:
				continue
			line = [' ' for j in range(80)]
			line[0] = '4'; line[1] = '0'
			insertText(line, 6, date+s[0])			# date
			insertText(line, 14, s[1])				# start time
			insertText(line, 24, s[2])				# max time
			insertText(line, 19, s[3])				# end time
			imp = self.computeImportance(s[1], s[3])
			insertText(line, 45, imp)				# importance
			x = s[4] + stationCode
			insertText(line, 51, x)					# definition + station code
			insertText(line, 70, self.observer+'\n')
			line = string.join(line, '') + '\n'
			outfile.write(line)
			print line[:-2]
		tmp = '-- end report --\n'
		outfile.write(tmp)
		print tmp[:-2]
		outfile.flush()
		outfile.close()

def main(argv):
    if (len(argv) != 2):
        print "usage: ", argv[0], " file"
        return
    filename = argv[1]
    r = Report(filename)
    try:
		while 1:
			events = r.processGroup()
			if events:
				events = r.sortEvents(events)
				r.generateReport(events, filename)
			else:
				break
    except ReportException, msg:
        print msg
    r.infile.close()
    return r

if __name__ == '__main__':
	main(sys.argv)
