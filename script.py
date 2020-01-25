#!/usr/bin/env python
#-*- coding: utf-8 -*-

from datetime import datetime
import requests
import pywikibot
from pywikibot.pagegenerators import PrefixingPageGenerator
import re
import mwparserfromhell

#RE_SIGNATURE = re.compile(r'-?-?\[\[(User|Wikipedista):([^|]+)\|([^]]+)\]\] \(\[\[(Diskuse s wikipedistou|User talk):\2\|diskuse\]\]\) ([0-9]+)\. ([0-9]+)\. ([0-9]+), ([0-9]+):([0-9]+) \(CES?T\)')
RE_SIGNATURE = re.compile(r'-?-?\[\[(User|Wikipedista):([^|]+)\|([^]]+)\]\]( \(|, )\[\[(Diskuse s wikipedistou|User talk):\2\|[dD]iskuse\]\](\) | )([0-9]+)\. ([0-9]+)\. ([0-9]+), ([0-9]+):([0-9]+) \(CES?T\)')

mentors = open('mentors.txt').read().split('\n')
mentors.pop()
site = pywikibot.Site()

f = open('activity.tsv', 'w')
f.write('Username\tAverage response time (seconds)\tNumber of unanswered questions\tAnswered questions\n')
for mentor in mentors:
	print('Processing %s' % mentor)
	user_talk = pywikibot.Page(site, mentor, ns=3)
	total_reaction = 0
	total_questions = 0
	unanswered_questions = 0
	for page in PrefixingPageGenerator(prefix=user_talk.title(), site=site):
		code = mwparserfromhell.parse(page.text)
		for section in code.get_sections(include_lead=False, matches=r'Otázka od wikipedisty \[\[User:([^|]+)\|\1\]\] \(([0-9]+)\. ([0-9]+)\. ([0-9]+), ([0-9]+):([0-9]+)\)'):
			matches = list(RE_SIGNATURE.finditer(str(section)))
			mentee_m = matches[0]
			mentee_d = datetime(int(mentee_m.group(9)), int(mentee_m.group(8)), int(mentee_m.group(7)), int(mentee_m.group(10)), int(mentee_m.group(11)))
			mentor_m = None
			for m in matches:
				if m.group(2) == mentor:
					mentor_m = m
			#mentor_m = matches[1] # not precise
			if mentor_m is None:
				unanswered_questions += 1
				continue
			mentor_d = datetime(int(mentor_m.group(9)), int(mentor_m.group(8)), int(mentor_m.group(7)), int(mentor_m.group(10)), int(mentor_m.group(11)))
			delta = mentor_d - mentee_d
			if delta.total_seconds() < 0:
				continue
			total_reaction += delta.total_seconds()
			total_questions += 1
	if total_questions == 0:
		print('%s has zero questions' % mentor)
		continue
	print('Average reaction for %s is %d seconds; %d unanswered questions' % (mentor, total_reaction/total_questions, unanswered_questions))
	f.write('%s\t%d\t%d\t%d\n' % (mentor, total_reaction/total_questions, unanswered_questions, total_questions))
