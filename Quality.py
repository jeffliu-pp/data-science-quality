#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 16:22:12 2020

Quality Projects

@author: liujianf
"""

import os
import pandas as pd
#import numpy as np
#import ast # use to split string to list
import re # use to precess string
import spacy
from spacy.matcher import Matcher
nlp = spacy.load("en_core_web_sm")

###############################################################################
WORD2CHANGE = {}
### Others
WORD2CHANGE[' '] = ['\*\*', '[(][\s]*s[\s]*[)]', '[(][\s]*es[\s]*[)]', '[(][\s]*each[\s]*[)]', '[(][\s]*half[\s]*[)]',
                    '[(][\s]*one[\s|-]?half[\s]*[)]', '[(][\s]*one[\s]+and[\s]+one[-|\s]?half[\s]*[)]', '[(][\s]*one[\s]+&[\s]+one[-|\s]?half[\s]*[)]', '[(][\s]*one[\s]+and[\s]+a[-|\s]?half[\s]*[)]',
                    '[(][\s]*one[\s]+half[\s]+to[\s]+one[\s]*[)]', 
                    '[(][\s]*two[\s]+and[\s]+one[-|\s]?half[\s]*[)]', '[(][\s]*three[\s]+and[\s]+one[-|\s]?half[\s]*[)]',
                    '[(][\s]*one[\s]*[)]', '[(][\s]*two[\s]*[)]', '[(][\s]*three[\s]*[)]', '[(][\s]*four[\s]*[)]', '[(][\s]*five[\s]*[)]', '[(][\s]*six[\s]*[)]', 
                    '[(][\s]*seven[\s]*[)]', '[(][\s]*eight[\s]*[)]', '[(][\s]*nine[\s]*[)]', '[(][\s]*ten[\s]*[)]', '[(][\s]*twelve[\s]*[)]', '[(][\s]*fourteen[\s]*[)]', 
                    '[(][\s]*twenty-four[\s]*[)]', '[(][\s]*twenty-eight[\s]*[)]', '[(][\s]*thirty[\s]*[)]', 
                    '[(][\s]*[0-9|.|,|/|\s]+[)]', '[(][\s]*[0-9|.|,|/|\s]+to[\s]*[0-9|.|,|/|\s]+[)]',
                    '[(][0-9|/|.|\s|x]+m[c]?[g|l][\s]*[)]', '[(][0-9|/|.|\s|x]+m[c]?[g|l][\s]*total[\s]*[)]']
WORD2CHANGE[' ( \\1 ) '] = ['[(]([a-zA-Z0-9]+[a-zA-Z0-9|\s|.|,|;]*)[)]']
WORD2CHANGE[' \\1 times '] = [' ([0-9]+)times ']
WORD2CHANGE[' mg / '] = [' mg/']
WORD2CHANGE[' mg '] = ['[\s]*mg[(]?[s]?[)]? ', '[\s]*milligram[(]?[s]?[)]? '] # mg(s), milligram(s)
WORD2CHANGE[' mcg / '] = [' mcg/']
WORD2CHANGE[' mcg '] = ['[\s]*mcg[(]?[s]?[)]? ', '[\s]*microgram[(]?[s]?[)]? '] # mcg(s), microgram(s)
WORD2CHANGE[' gr '] = ['[\s]*gr[(]?[s]?[)]? ', '[\s]*gram[(]?[s]?[)]? ', ' g ', ' gm '] # gr(s), gram(s)
WORD2CHANGE[' ml '] = ['[\s]*ml[(]?[s]?[)]? ', '[\s]*milliliter[(]?[s]?[)]? '] # ml(s), milliliter(s)
WORD2CHANGE[' meq '] = [' milliequivalent[(]?[s]?[)]? ', ' meq[(]?[s]?[)]? '] 
WORD2CHANGE[' po \\1 '] = ['po(q[a-z]{2})', 'po(q[d|w]{1})', 'po([b|t|q]{1}id)'] # poqam, poqhs, poqd, poqw, pobid, potid, poqid
WORD2CHANGE[' ac hs '] = [' a[.]?c[.]?h[.]?s[.]? '] 
WORD2CHANGE[' \\1 by mouth '] = [' ([0-9]+)p[.]?o[.]? ']
WORD2CHANGE[' \\1 daily '] = [' ([0-9]+)q[.]?d[.]? ']
WORD2CHANGE[' as needed ' ] = [' p[.]?r[.]?n[.]? ']
WORD2CHANGE[' by mouth '] = [' [b]?[y]?[\s]*oral[\s]*route ', ' oral ', ' orally ', ' p[.]?o[.]? '] # oral, orally, p.o.
WORD2CHANGE[' and '] = [' & ']
WORD2CHANGE[' before '] = [' prior to ']
WORD2CHANGE[' every '] = [' each ', ' ea', ' per ']
WORD2CHANGE[' through '] = [' thur ']
WORD2CHANGE[' without '] = [' w/o ']
WORD2CHANGE[' with '] = [' w/ ']
WORD2CHANGE[' - '] = ['-']
### Numbers (order matters!)
WORD2CHANGE[' \\1\\2 '] = [' ([0-9]+)[,]([0-9]{3}[.]?[0-9]*)'] # 1,000 --> 1000
WORD2CHANGE[' 0\\1 '] = [' ([.][0-9]*) '] # .5 --> 0.5
WORD2CHANGE[' 0.25 '] = [' 1/4 of a[n]? ', ' 1/4 ', ' one quarter of a[n]? ', ' one quarter ']
WORD2CHANGE[' 1.5 '] = [' one and half ', ' one[\s|-]+and[\s|-]+a[\s|-]+half ', ' one and one[\s|-]+half ', ' 1[&|\s]*1/2 ', ' 1 and 0.5 ', ' 1 and 1/2 ', ' 1[\s|-]+1/2 ']
WORD2CHANGE[' 2.5 '] = [' two and half ', ' two and a half ', ' two and one[\s|-]+half ', ' 2[&|\s]*1/2 ', ' 2 and 0.5 ', ' 2 and 1/2 ', ' 2[\s|-]+1/2 ']
WORD2CHANGE[' 3.5 '] = [' three and half ', ' three and a half ', ' three and one[\s|-]+half ', ' 3[&|\s]*1/2 ', ' 3 and 0.5 ', ' 3 and 1/2 ', ' 3[\s|-]+1/2 ']
WORD2CHANGE[' 4.5 '] = [' four and half ', ' four and a half ', ' four and one[\s|-]+half ', ' 4[&|\s]*1/2 ', ' 4 and 0.5 ', ' 4 and 1/2 ', ' 4[\s|-]+1/2 ']
WORD2CHANGE[' 5.5 '] = [' five and half ', ' five and a half ', ' five and one[\s|-]+half ', ' 5[&|\s]*1/2 ', ' 5 and 0.5 ', ' 5 and 1/2 ', ' 5[\s|-]+1/2 ']
WORD2CHANGE[' 0.5 '] = [' one[\s]*-[\s]*half ', ' one half ', ' a half ', ' half a ', ' half of a ', ' 0.5/half ', ' half ', ' 1/2 a ', ' 1/2 ']
WORD2CHANGE[' 1 '] = [' one ', ' 1 whole ']
WORD2CHANGE[' 2 '] = [' two ']
WORD2CHANGE[' 3 '] = [' three ']
WORD2CHANGE[' 4 '] = [' four ']
WORD2CHANGE[' 5 '] = [' five ']
WORD2CHANGE[' 6 '] = [' six ']
WORD2CHANGE[' 7 '] = [' seven ']
WORD2CHANGE[' 8 '] = [' eight ']
WORD2CHANGE[' 9 '] = [' nine ']
WORD2CHANGE[' 10 '] = [' ten ']
WORD2CHANGE[' 12 '] = [' twelve ']
WORD2CHANGE[' 14 '] = [' fourteen ']
WORD2CHANGE[' 30 '] = [' thirty ']
WORD2CHANGE[' 0.5 to \\1 '] = [' 1/2[\s]*-[\s]*([0-9]*)', ' 1/2[\s]+or[\s]+([0-9]*)']
WORD2CHANGE[' \\1 to \\2 '] = ['([0-9]+[.]?[0-9]*)[\s]*-[\s]*([0-9]+[.]?[0-9]*)', '([0-9]+[.]?[0-9]*)[\s]+or[\s]+([0-9]+[.]?[0-9]*)']
### Medication Units
WORD2CHANGE[' \\1 tablet '] = ['([0-9]+)t ']
WORD2CHANGE[' tablet '] = ['[\-]?[\s]*tablet[(]?[s]?[)]?[\s|.|,|;|-|/]+', 'tab[(]?[s]?[)]?[\s|.|,|;|-]+', ' t[(]?[s]?[)]? ', ' tb[(]?[s]?[)]? ', 
                           ' table ', 'tabet ', ' tabl[.]? ', 'tabelet ', ' tabletd ', ' tbt '] # tablet, tablets, tablet(s), tab, tabs, tab(s)
WORD2CHANGE[' capsule '] = ['[\-]?[\s]*capsule[(]?[s]?[)]?[\s|.|,|;|-|/]+', 'cap[(]?[s]?[)]?[\s|.|,|;|-]+', ' c[(]?[s]?[)]? ', ' capsul '] # capsule, capsules, capsule(s), cap, caps, cap(s) 
WORD2CHANGE[' pill '] = ['pill[(]?[s]?[)]?[\s|.|,|;|-]+'] # pill, pills, pill(s)    
WORD2CHANGE[' puff '] = ['puff[(]?[s]?[)]?[\s|.|,|;|-]+', 'inhalation[(]?[s]?[)]?[\s|.|,|;|-]+', ' inhaler[(]?[s]?[)]? ', 'inh[l]?[(]?[s]?[)]?[\s|.|,|;|-]+', ' aerosol[(]?[s]?[)]? '] # puff, puffs, puff(s)   
WORD2CHANGE[' pump '] = ['pump[(]?[s]?[)]?[\s|.|,|;|-]+'] # pump, pumps, pump(s)           
WORD2CHANGE[' drop '] = ['drop[(]?[s]?[)]?[\s|.|,|;|-]+', 'gtt[(]?[s]?[)]?[\s|.|,|;|-]+'] # drop, drops, drop(s)    
WORD2CHANGE[' spray '] = ['spray[(]?[s]?[)]?[\s|.|,|;|-]+', 'spr[(]?[s]?[)]?[\s|.|,|;|-]+', 'squirt[(]?[s]?[)]?[\s|.|,|;|-]+'] # spray, sparys, spray(s)   
WORD2CHANGE[' strip '] = ['strip[(]?[s]?[)]?[\s|.|,|;|-]+'] # strip(s)
WORD2CHANGE[' scoop '] = ['scoop[(]?[s]?[)]?[\s|.|,|;|-]+'] # scoop(s)
WORD2CHANGE[' syringe '] = ['syringe[(]?[s]?[)]?[\s|.|,|;|-]+'] # syringe(s)
WORD2CHANGE[' ring '] = ['ring[(]?[s]?[)]?[\s|.|,|;|-]+'] # ring(s)      
WORD2CHANGE[' patch '] = ['patch[(]?[e|s]*[)]?[\s|.|,|;|-]+'] # patch(es)   
WORD2CHANGE[' packet '] = ['packet[(]?[e|s]*[)]?[\s|.|,|;|-]+'] # packet(s)
WORD2CHANGE[' unit '] = ['unit[(]?[s]?[)]?[\s|.|,|;|-|:]+', ' u[(]?[s]?[)]?[\s|.|,|;|-]+', ' iu ', ' unis '] # unit, units, unit(s) 
WORD2CHANGE[' vial '] = ['vial[(]?[s]?[)]?[\s|.|,|;|-]+'] # vial(s)
WORD2CHANGE[' pen '] = ['pen[(]?[s]?[)]?[\s|.|,|;|-]+'] # pen(s)
WORD2CHANGE[' application '] = ['appliciation[(]?[s]?[)]?[\s|.|,|;|-]+', 'applicator[(]?[s]?[)]?[\s|.|,|;|-]+', 'app[l]?[(]?[s]?[)]?[\s|.|,|;|-]+'] # application(s), app(s)              
WORD2CHANGE[' ampule '] = ['amp[o]?ule[(]?[s]?[)]?[\s|.|,|;|-]+', 'ampul[(]?[s]?[)]?[\s|.|,|;|-]+'] # ampule(s), ampoule(s), ampul(s) 
### Time-Related Words
# Day of Week (DOW)
WORD2CHANGE[' monday '] = [' [q]?[\s]*mon[\s|.|,|;|-]+', '[q]?[\s]*monday[(]?[s]?[)]?[\s|.|,|;|-]+'] # mon, monday(s), qmonday(s)
WORD2CHANGE[' tuesday '] = [' [q]?[\s]*tue[\s|.|,|;|-]+', '[q]?[\s]*tuesday[(]?[s]?[)]?[\s|.|,|;|-]+'] # tue, tuesday(s)
WORD2CHANGE[' wednesday '] = [' [q]?[\s]*wed[\s|.|,|;|-]+', '[q]?[\s]*wednesday[(]?[s]?[)]?[\s|.|,|;|-]+'] # wed, wednesday(s)
WORD2CHANGE[' thursday '] = [' [q]?[\s]*thu[r]?[s]?[\s|.|,|;|-]+', '[q]?[\s]*thursday[(]?[s]?[)]?[\s|.|,|;|-]+'] # thu, thursday(s)
WORD2CHANGE[' friday '] = [' [q]?[\s]*fri[\s|.|,|;|-]+', '[q]?[\s]*friday[(]?[s]?[)]?[\s|.|,|;|-]+'] # fri, friday(s)
WORD2CHANGE[' saturday '] = [' [q]?[\s]*sat[\s|.|,|;|-]+', '[q]?[\s]*saturday[(]?[s]?[)]?[\s|.|,|;|-]+'] # sat, saturday(s)
WORD2CHANGE[' sunday '] = [' [q]?[\s]*sun[\s|.|,|;|-]+', '[q]?[\s]*sunday[[(]?[s]?[)]?[\s|.|,|;|-]+'] # sun, sunday(s)
# Time of Day (TOD)
WORD2CHANGE[' morning '] = [' morning[(]?[s]?[)]?[\s|.|,|;|-]+', ' mornng ']
WORD2CHANGE[' in morning '] = [' q[.]?[\s]*morning[(]?[s]?[)]?[\s|.|,|;|-]+', ' q[.]?[\s]*a[.]?m[.]?[\s|.|,|;|-]+', 
                               ' in[\s]*a[.]?m[.]?[\s|.|,|;|-]+', ' in[\s]*the[\s]*a[.]?m[.]?[\s|.|,|;|-]+',
                               ' before midday '] # morning(s), qam
WORD2CHANGE[' a.m. '] = ['[\s]*a[.]?m[.]?[\s|.|,|;|-]+', ' a..m '] # a.m.
WORD2CHANGE[' midday '] = [' noon[(]?[s]?[)]?[\s|.|,|;|-]+', ' midday[(]?[s]?[)]?[\s|.|,|;|-]+'] # noon(s), midday(s)
WORD2CHANGE[' in midday '] = [' q[.]?[\s]*noon[(]?[s]?[)]?[\s|.|,|;|-]+']
WORD2CHANGE[' afternoon '] = [' afternoon[(]?[s]?[)]?[\s|.|,|;|-]+']
WORD2CHANGE[' in afternoon '] = [' q[.]?[\s]*afternoon[(]?[s]?[)]?[\s|.|,|;|-]+', ' q[.]?[\s]*p[.]?m[.]?[\s|.|,|;|-]+', 
                                 ' in[\s]*p[.]?m[.]?[\s|.|,|;|-]+', ' in[\s]*the[\s]*p[.]?m[.]?[\s|.|,|;|-]+'
                                 ' after school[\s|.|,|;|-]+', ' mid afternoon[\s|.|,|;|-]+'] # afternoon(s), qpm
WORD2CHANGE[' p.m. '] = ['[\s]*p[.]?m[.]?[\s|.|,|;|-]+', ' p..m '] # p.m.
WORD2CHANGE[' evening '] = [' evening[(]?[s]?[)]?[\s|.|,|;|-]+', ' night[(]?[s]?[)]?[\s|.|,|;|-]+', ' nighttime[\s|.|,|;|-]+', ' midnight[\s|.|,|;|-]+']
WORD2CHANGE[' in evening '] = [' q[.]?[\s]*evening[(]?[s]?[)]?[\s|.|,|;|-]+', ' q[.]?[\s]*night[(]?[s]?[)]?[\s|.|,|;|-]+',
                               ' nightly[\s|.|,|;|-]+', ' nighlty '] # night(s), nightly, nighttime
WORD2CHANGE[' every \\1 \\2 '] = [' [.]?q[.]?[\s]*([0-9]+)[\s]*([a|p]{1}[.]?m[.]?)[\s|.|,|;|-]+'] # q6am    
# Special Time of Day
WORD2CHANGE[' breakfast '] = [' breakfast[(]?[s]?[)]?[\s|.|,|;|-]+', 'breakfst', 'brakfast', 'bkfst'] # breakfast(s)
WORD2CHANGE[' before breakfast '] = [' a[.]?c[.]?[\s]*breakfast ', ' a[.]?c[.]?[\s]*bk ']
WORD2CHANGE[' with breakfast '] = [' w breakfast ']
WORD2CHANGE[' lunch '] = [' lunch[(]?[e|s]*[)]?[\s|.|,|;|-]+'] # lunch(es)
WORD2CHANGE[' before lunch '] = [' a[.]?c[.]?[\s]+lunch ' ]
WORD2CHANGE[' with lunch '] = [' w lunch ']
WORD2CHANGE[' dinner '] = [' dinner[(]?[s]?[)]?[\s|.|,|;|-]+', ' supper[(]?[s]?[)]?[\s|.|,|;|-]+', ' dinnertime '] # dinner(s), supper(s)
WORD2CHANGE[' before dinner '] = [' a[.]?c[.]?[\s]+dinner ']
WORD2CHANGE[' with dinner '] = [' w dinner ']
WORD2CHANGE[' bedtime '] = [' bed[(]?[s]?[)]?[\s|.|,|;|-]+', ' bedtime[\w]*[\s|.|,|;|-]+', ' bed[\s]*time[(]?[s]?[)]?[\s|.|,|;|-]+']
WORD2CHANGE[' at bedtime '] = [' at h[.]?s[.]?[\s|,|;|-]+', ' [.]?q[.]?[-|\s]*h[.]?s[.]?[\s|,|;|-]+', ' h[.]?s[.]?[\s|,|;|-]+', ' q[\s]*bedtime[\s|.|,|;|-]+', ' before[\s]+bedtime '] # bed(s), bedtime(s), bed time(s), h.s., qbedtime 
WORD2CHANGE[' meal '] = [' [a]?[\s]*meal[(]?[s]*[)]?[\s|.|,|;|-]+'] # meal(s)
WORD2CHANGE[' before meal '] = [' q[.]?a[.]?c[.]? ', ' a[.]?c[.]? ']
WORD2CHANGE[' with meal '] = [' w meal ']
WORD2CHANGE[' with food '] = [' w food ']
# Time(s)
WORD2CHANGE[' 1 time '] = [' once ']
WORD2CHANGE[' 2 times '] = [' twice times ', ' twice ']
WORD2CHANGE[' 2 times daily '] = ['[\s|\(]?b[.]?i[.]?d[.]?[\s|,|;|\-|\)]+']
WORD2CHANGE[' 3 times daily '] = ['[\s|\(]?t[.]?i[.]?d[.]?[\s|,|;|\-|\)]+']
WORD2CHANGE[' 4 times daily '] = ['[\s|\(]?q[.]?i[.]?d[.]?[\s|,|;|\-|\)]+']
WORD2CHANGE[' 2 times weekly '] = ['[\s|\(]?b[.]?i[.]?w[.]?[\s|,|;|\-|\)]+']
WORD2CHANGE[' 3 times weekly '] = ['[\s|\(]?t[.]?i[.]?w[.]?[\s|,|;|\-|\)]+']
WORD2CHANGE[' 4 times weekly '] = ['[\s|\(]?q[.]?i[.]?w[.]?[\s|,|;|\-|\)]+']
WORD2CHANGE[' \\1 times '] = [' ([0-9]+)[\s]*x' ]
WORD2CHANGE[' \\1 minute '] = [' ([0-9]+)min[(]?[s]?[)]? ', ' ([0-9]+)minute[(]?[s]?[)]? ']
WORD2CHANGE[' minute '] = [' minute[(]?[s]?[)]?', ' min[(]?[s]?[)]? ']
WORD2CHANGE[' hour '] = ['hour[.|,|;|-]+', 'hr[\s|.|,|;|-]+', 'hrs[\s|.|,|;|-]+', 'hurs[\s|.|,|;|-]+']
WORD2CHANGE['day '] = ['day[.|,|;|-]+']
WORD2CHANGE[' week '] = ['week[.|,|;|-]+', 'wk[\s|.|,|;|-]+', 'wks[\s|.|,|;|-]+ ']
WORD2CHANGE[' month '] = ['month[.|,|;|-]+']
WORD2CHANGE[' hourly '] = [' a[\s]*hour ', ' each[\s]*hour[\s|.|,|;|-]+', ' every[\s]*hour[\s|.|,|;|-]+', ' per[\s]*hour[\s|.|,|;|-]+', 
                           '/[\s]*hour[\s|.|,|;|-]+', '/[\s]*hr[\s|.|,|;|-]+', '/[\s]*h[\s|.|,|;|-]+']
WORD2CHANGE[' every \\1 hours '] = [' [.]?q[.]?[\s]*([0-9]+)[\s]*h[o]?[u]?[r]?[(]?[s]?[)]?[\s|.|,|;|-]+'] # q12hour(s)    
WORD2CHANGE[' every \\1 to \\2 hours '] = [' [.]?q[.]?[\s]*([0-9]+)[\s]*to[\s]*([0-9]+)[\s]*h[o]?[u]?[r]?[(]?[s]?[)]?[\s|.|,|;|-]+', 
                                           ' [.]?q[.]?[\s]*([0-9]+)[\s]*-[\s]*([0-9]+)[\s]*h[o]?[u]?[r]?[(]?[s]?[)]?[\s|.|,|;|-]+'] # q1 to 2 h          
WORD2CHANGE[' daily '] = [' [o|n|c|e]*[\s]*a[\s]*day ', ' [o|n|c|e]*[\s]*each[\s]*day ', ' [o|n|c|e]*[\s]*every[\s]*day ', ' [o|n|c|e]*[\s]*per[\s]*day ', 
                          ' once[\s]+daily ', ' 1 time[\s]+daily ', ' once[\s]*day ', ' 1 time[\s]+day ', ' every 1 day ', ' for 1 day', ' for a day ',
                          ' q[.]?[\s]*day[\s|.|,|;|-]+', ' q[.]?[\s]*d[.]?[\s|,|;|-]+', ' q[.]?[\s]*dly[.]?[\s|,|;|-]+', ' qd[\*] ', ' q[\s]+daily ',
                          '/[\s]*day ', '/[\s]*d ', ' d ',                           
                          ' dailly ', 'dily', ' dly ', ' daiy ', ' dialy ', ' daoily ', ' dail ', 'dail;y ', ' daild ', ' daiily ', ' daliy '] # typos
WORD2CHANGE[' every \\1 days '] = [' [.]?q[.]?[\s]*([0-9]+)[\s]*d[a]?[y]?[(]?[s]?[)]?[\s|.|,|;|\-]+'] # q2day(s)
WORD2CHANGE[' every other day '] = [' [.]?q[.]?[\s]*other[\s]*day[\s|.|,|;|\-]+', ' [.]?q[.]?od '] # qotherday, qod   
WORD2CHANGE[' weekly '] = [' [o|n|c|e]*[\s]*a[\s]*week ', ' [o|n|c|e]*[\s]*each[\s]*week ', ' [o|n|c|e]*[\s]*every[\s]*week ', ' [o|n|c|e]*[\s]*per[\s]*week ', 
                           ' once[\s]+weekly ', ' 1 time[\s]+weekly ', ' once[\s]week ', ' 1 time[\s]+week ', 
                           ' q[.]?[\s]*week[\s|.|,|;|-]+', ' q[.]?[\s]*w[.]?[\s|,|;|-]+', ' q[.]?[\s]*wk[l|y]*[.|\s|,|;|-]+',
                           '/[\s]*week ', '/[\s]*wk ', '/[\s]*w ', ' w ', ' wkly ', ' weely ']
WORD2CHANGE[' every \\1 weeks '] = [' [.]?q[.]?[\s]*([0-9]+)[\s]*w[e]*[k]?[(]?[s]?[)]?[\s|.|,|;|-]+'] # q2week(s) 
WORD2CHANGE[' monthly '] = [' [o|n|c|e]*[\s]*a[\s]*month ', ' [o|n|c|e]*[\s]*each[\s]*month ', ' [o|n|c|e]*[\s]*every[\s]*month ', ' [o|n|c|e]*[\s]*pre[\s]*month ', 
                            ' once[\s]+monthly ', ' 1 time[\s]+monthly ', ' once[\s]*month ',  '1 time[\s]+month ', 
                            ' q[.]?[\s]*month[\s|.|,|;|-]+', ' q[.]?[\s]*mo[.]?[\s|,|;|-]+ ', 
                            '/[\s]*month ', '/[\s]*mo', '/[\s]*m ']
###############################################################################

###############################################################################
### List of Basic Components
EVERY_LIST = ['a','each','every','per','one']
AT_LIST = ['at','in','on','before','after','during','with']
TIME_LIST = ['minute','hour','day','week','month']
TIMELY_LIST = ['hourly', 'daily', 'weekly', 'monthly']
DOW_LIST =['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
TOD_LIST = ['morning','a.m.','breakfast',
            'midday','lunch',
            'afternoon','p.m.',
            'evening', 'dinner','bedtime'] # time of day
UNIT_LIST = ['tablet', 'capsule', 'pill', 'puff', 'pump', 'drop', 'spray', 'strip', 'scoop', 
             'ring', 'patch', 'packet', 'unit', 'application', 'ampule', 'syringe', 'vial', 'pen',
             'gr', 'mg', 'mcg', 'ml', 'meq']
PERI_LIST = ['breakfast','lunch','dinner','meal','food','snack','milk','bedtime']
             #'need','necessary','direct']
### Generate Patters for Frequency Information
# Pattern Components
NUM = [{'POS':'NUM'}]
EVERY = [{'LOWER':{'IN':EVERY_LIST}}]
AT = [{'LOWER':{'IN':AT_LIST}}]
TO = [{'LOWER':{'IN':['to', 'or']}}]
NOT = [{'LOWER':{'IN':['not','except']}}]
THROUGH = [{'LOWER':{'IN':['through','to']}}]
OTHER = [{'LOWER':'other'}]
TIME = [{'LEMMA':{'IN':TIME_LIST}}]
TIMELY = [{'LOWER':{'IN':TIMELY_LIST}}]
DOW = [{'LEMMA':{'IN':DOW_LIST}}]
TOD = [{'LEMMA':{'IN':TOD_LIST}}] 
UNIT = [{'LEMMA':{'IN':UNIT_LIST}}]
PERI = [{'LEMMA':{'IN':PERI_LIST}}]
###############################################################################

###############################################################################
# FREQUENCY
freq_matcher = Matcher(nlp.vocab)
# Dictionary of Patterns
fp = {}
# Normal Patterns
fp['101'] = TIMELY # weekly
fp['102'] = EVERY + TIME # every week
fp['103'] = EVERY + NUM + TIME # every 2 weeks
fp['104'] = EVERY + OTHER + TIME # every other week
fp['105'] = EVERY + NUM + TO + NUM + TIME # every 2 to 3 weeks
fp['111'] = NUM + [{'LEMMA':{'IN':['time','times']+TIME_LIST}}] + TIMELY # 2 times weekly
fp['112'] = NUM + [{'LEMMA':{'IN':['time','times']+TIME_LIST}}] + TIME # 2 times week 
fp['113'] = NUM + [{'LEMMA':{'IN':['time','times']+TIME_LIST}}] + EVERY + TIME # 2 times every week 
fp['114'] = NUM + [{'LEMMA':{'IN':['time','times']+TIME_LIST},'OP':'?'}] + TO + fp['111'] # 2 (times) to 3 times weekly
fp['115'] = NUM + [{'LEMMA':{'IN':['time','times']+TIME_LIST},'OP':'?'}] + TO + fp['112'] # 2 (times) to 3 times week
fp['116'] = NUM + [{'LEMMA':{'IN':['time','times']+TIME_LIST},'OP':'?'}] + TO + fp['113'] # 2 (times) to 3 times every week
## DOW Patterns
fp['201'] = DOW + [{'LOWER':',','OP':'?'}] + [{'LEMMA':{'IN':DOW_LIST},'OP':'?'},{'LOWER':',','OP':'?'}]*5 + \
            [{'LOWER':'and','OP':'?'},{'LEMMA':{'IN':DOW_LIST},'OP':'?'}] # monday (,tuseday, and wednesday)
fp['202'] = EVERY + fp['201'] # every monday     
fp['203'] = EVERY + NUM + fp['201'] # every two monday
fp['204'] = EVERY + OTHER + fp['201'] # every other monday
fp['205'] = DOW + THROUGH + DOW # monday through firday
fp['206'] = NOT + fp['205'] # not monday to friday
fp['207'] = NOT + fp['201'] # not monday
fp['208'] = NOT + AT + fp['201'] # except (on) monday
## TOD Patterns
fp['301'] = TOD + [{'LOWER':',','OP':'?'}] + [{'LEMMA':{'IN':TOD_LIST},'OP':'?'},{'LOWER':',','OP':'?'}]*5 + \
            [{'LOWER':'and','OP':'?'},{'LEMMA':{'IN':TOD_LIST},'OP':'?'}] # morning (, afternoon, and bedtime)
fp['302'] = EVERY + fp['301'] # every morning
fp['303'] = NUM + [{'LOWER':{'IN':['a.m.','p.m.']}}] # 7 am
fp['304'] = fp['303'] + [{'LOWER':',','OP':'?'},{'LOWER':'and','OP':'?'}] + fp['303'] # 7 am and 12 pm
fp['305'] = fp['303'] + [{'LOWER':',','OP':'?'}] + fp['304'] # 7 am, 12 pm, and 6 pm
fp['306'] = fp['303'] + [{'LOWER':',','OP':'?'}] + fp['305'] # 7 am, 12 pm, 6 pm and 10 pm
# Add Patterns
for i in fp:
    freq_matcher.add('FREQUENCY', None, fp[i])
###############################################################################

###############################################################################
# DOSE
dose_matcher = Matcher(nlp.vocab)
# Dictionary of Patterns
dp = {}
# Normal Patterns
dp['101'] = NUM + UNIT # 2 tablet
dp['102'] = NUM + TO + dp['101'] # 1 to 2 tablet
dp['103'] = dp['101'] + TO + dp['101'] # 1 tablet to 2 tablet
dp['104'] = NUM + [{'LOWER':'and'}] + NUM + UNIT # 1 and 0.5 tablet
# Special Patterns
dp['200'] = NUM + [{'LOWER':'every'},{'LOWER':'by'},{'LOWER':'mouth'}] # 1 every by mouth
dp['201'] = NUM + [{'LOWER':'by'},{'LOWER':'mouth'}] # 2 by mouth
dp['301'] = NUM + TO + dp['201'] # 1 to 2 by mouth
dp['202'] = NUM + EVERY + NUM + TIME # 2 every 12 hour
dp['302'] = NUM + TO + dp['202'] # 1 to 2 every 12 hour
dp['203'] = NUM + NUM + TIME # 2 30 minute
dp['303'] = NUM + TO + dp['203'] # 1 to 2 30 minute
dp['204'] = NUM + TIMELY # 1 daily
dp['304'] = NUM + TO + dp['204'] # 1 to 2 daily
dp['205'] = NUM + EVERY + TIMELY # 1 every daily
dp['305'] = NUM + TO + dp['205'] # 1 to 2 every daily
dp['206'] = NUM + EVERY + [{'LEMMA':'other','OP':'?'}] + TIME # 1 every other day
dp['306'] = NUM + TO + dp['206'] # 1 to 2 every other day
dp['207'] = NUM + EVERY + [{'LEMMA':'other','OP':'?'}] + DOW # 1 every other monday
dp['307'] = NUM + TO + dp['207'] # 1 to 2 every other monday
dp['208'] = NUM + EVERY + DOW # 1 every monday
dp['308'] = NUM + TO + dp['208'] # 1 to 2 every monday
dp['209'] = NUM + AT + DOW # 1 on monday
dp['309'] = NUM + TO + dp['209'] # 1 to 2 on monday
dp['210'] = NUM + EVERY + TOD # 1 every morning
dp['310'] = NUM + TO + dp['210'] # 1 to 2 every morning
dp['211'] = NUM + AT + [{'LOWER':'the','OP':'?'}] + TOD # 1 in morning
dp['311'] = NUM + TO + dp['211'] # 1 to 2 in morning
dp['212'] = NUM + [{'LOWER':'bedtime'}] # 1 bedtime
dp['312'] = NUM + TO + dp['212'] # 1 to 2 bedtime
dp['213'] = NUM + NUM + [{'LOWER':{'IN':['time','times']}}] # 1 2 times
dp['313'] = NUM + TO + dp['213'] # 1 to 2 2 times
dp['214'] = NUM + [{'LOWER':'as'},{'LEMMA':{'IN':['direct','necessary','need']}}] # 1 as directed
# Add Patterns
for i in dp:
    dose_matcher.add('DOSE', None, dp[i])
###############################################################################

###############################################################################
# PERIPHERAL 
peri_matcher = Matcher(nlp.vocab)
# Dictionary of Patterns
pp = {}
# Patterns
pp['101'] = PERI + [{'LOWER':',','OP':'?'}] + [{'LEMMA':{'IN':PERI_LIST},'OP':'?'},{'LOWER':',','OP':'?'}]*2 + \
            [{'LOWER':'and','OP':'?'},{'LEMMA':{'IN':PERI_LIST},'OP':'?'}] # breakfast (, lunch, and bedtime)
pp['102'] = AT + pp['101'] # before breakfast
pp['103'] = NUM + TIME + pp['102'] # 1 hour before breakfast
pp['104'] = NUM + TO + pp['103'] # one to two hours before breakfast
pp['105'] = NUM + TIME + TO + pp['104'] # 30 minutes to one hour before breakfast
pp['106'] = [{'LOWER':'as'}] + pp['101'] # as needed
#fp['401'] = [{'LOWER:':'for','POS':'ADP'}] + NUM + TIME # for two weeks, keyword 'for' is not working!!!
# Add Patterns
for i in pp:
    peri_matcher.add('PERIPHERAL', None, pp[i])
###############################################################################

###############################################################################
# Reword Text, Convert to Lower Case, and Remove White Spaces
def _REWORD(text, remove_bracket=False):
    text = str(text).lower()
    text = text.strip() # remove whitespaces from the beginning and end of text
    if remove_bracket:
        text = re.sub('[(][0-9a-z|,|.|\s]*[)]', ' ', text) # remove anything in a bracket
    if len(text) > 0:
        while text[-1] == '.':
            text = text[:-1] # remove period at the end
            if len(text) == 0:
                break
    text = ' ' + text + ' ' # add a space at the beginning and end of text, this is a necessary step in converting words
    for t in ['hourly', 'daily', 'weekly','monthly']: # extra space around times
        text = text.replace(t, ' '+t+' ')
    for k in WORD2CHANGE: # change words
        for i in WORD2CHANGE[k]: 
            text = re.sub(i,k,text)
    return " " + " ".join(text.split()) # split words into a list of words, add space in the beginning (this is useful when a sentence beginning with a number, we want to ensure the number is detected as POS: 'NUM')
###############################################################################

###############################################################################
# Extract Information from Text
def _EXTRACT(text, matcher):
    info = set()
    if type(text) == str:
        text = nlp(text)
        phrase_matches = matcher(text)
        result = set()
        for match_id, start, end in phrase_matches:
            span = text[start:end]
            while span[-1].text.lower() in [',','and']: # remove comma and 'and' at the end
                span = span[:-1]
            result.add(" ".join([token.lemma_ for token in span]))
        for i, e in enumerate(result):
            count = 0
            for j in result:
                if e in j:
                    count += 1
            if count == 1:
                info.add(e)
    return info    
###############################################################################

###############################################################################
# Modify Frequency and Compare
def _MODIFY_FREQ(ROW, NAME, MEDICATIONS):
    FREQ = ROW[NAME]
    morning = 0
    noon = 0
    afternoon = 0
    evening = 0
    daily = 0
    dow = {}
    info = set()
    for d in DOW_LIST:
        dow[d] = 0
    weekly = 0
    for f in FREQ:
        for t in ['morning', 'breakfast', 'a.m.']:
            if t in f:
                morning = 1
        for t in ['lunch', 'midday']:
            if t in f:
                noon = 1        
        for t in ['afternoon', 'p.m.']:
            if t in f:
                afternoon = 1       
        for t in ['evening', 'dinner', 'bedtime']: 
            if t in f:
                evening = 1        
        for d in [1,2,3,4]:
            for t in [str(d)+' time daily', str(d)+' times daily', str(d)+' time day', str(d)+' times day']:
                if t == f:
                    daily = max(d, daily)        
        for t in ['every 24 hours', 'every 24 hour', 
                  'every day', 'every 1 day','everyday', 'each day', 'day', 'days', 'daily']:
            if t in f:
                daily = max(1, daily)
        for d in DOW_LIST:
            if d in f:
                dow[d] = 1
        for d in [1,2,3,4,5,6,7]:
            for t in [str(d)+' time weekly', str(d)+' times weekly', str(d)+' day weekly', str(d)+' days weekly',
                      str(d)+' time week', str(d)+' times week', str(d)+' day week', str(d)+' days week']:
                if t == f:
                    weekly = max(d, weekly)
        for t in ['every 7 days', 'every 7 day', 
                  'every week', 'every 1 week','everyweek', 'each week', 'week', 'weeks', 'weekly']:
            if t in f:
                weekly = max(1, weekly)
                daily = 0
        for t in ['every 14 days', 'every 2 weeks', 'every other week']:
            if t in f:
                daily = 0
                info.add('every 2 weeks')                              
    daily = max(daily, morning + noon + afternoon + evening)
    if daily == 1:
        info.add('1 time daily')
    elif daily > 1:
        info.add(str(daily) + ' times daily')
    weekly = max(sum(dow[d] for d in DOW_LIST), weekly)    
    if weekly == 1:
        info.add('1 time weekly')
    elif weekly > 1:
        info.add(str(weekly) + ' times weekly')
    return info    
###############################################################################

###############################################################################
# Modify Dose and Compare
def _MODIFY_DOSE(ROW, NAME, MEDICATIONS):
    DOSE = ROW[NAME]
    info = set()
    a = []
    b = []
    for d in DOSE:
        for i in [1,2,3,4,5,6]: # combine
            if str(i) + ' and 0.5 ' in d:
                d = re.sub(str(i)+' and 0.5', str(i+0.5),d)
        if 'gr' not in d and 'mg' not in d and 'mcg' not in d and 'ml' not in d and 'meq' not in d and 'unit' not in d:
            a = re.findall('[0-9]+[.]?[0-9]*', d) # dose in tablet/capsule
            if len(a) > 0:       
                count = 1
                if (' to ' in d or ' or ' in d) and len(a) > 1:
                    count = 2
                for j in range(count):
                    if float(a[j]).is_integer():
                        a[j] = int(float(a[j]))
                    else:
                        a[j] = float(a[j])
                    info.add(a[j])
    if len(info) == 0: # if no table informaiton is found, then use strength information
        INDEX = MEDICATIONS.loc[MEDICATIONS.MEDICATION_DESCRIPTION==ROW['MEDICATION_DESCRIPTION']].index
        if len(INDEX) == 1:
            STRENGTH = MEDICATIONS.loc[INDEX[0],'STRENGTH']
            if len(STRENGTH) > 0:
                for s in STRENGTH:
                    for d in DOSE:
                        if ('gr' in s and 'gr' in d) or ('mg' in s and 'mg' in d) or \
                        ('mcg' in s and 'mcg' in d) or ('ml' in s and 'ml' in d) or \
                        ('meq' in s and 'meq' in d) or ('unit' in s and 'unit' in d):
                            a = re.findall('[0-9]+[.]?[0-9]*',d) # dose in gr/mg/mcg/ml
                            b = re.findall('[0-9]+[.]?[0-9]*',s) # strength in gr/mg/mcg/ml
                        if len(a) > 0 and len(b) == 1:
                            for i in range(len(a)):            
                                c = float(a[i])/float(b[0]) # count
                                if c.is_integer():
                                    c = int(c) # convert float to integer
                                info.add(c)
    return info
###############################################################################    

############################################################################### 
# Modify Peripheral and Compare
def _MODIFY_PERI(ROW, NAME, MEDICATIONS):
    PERI = ROW[NAME]
    info = set()
    for p in PERI:
        find = False
        for i in ['at','as','with']:
            for j in PERI_LIST:
                if i + ' ' + j == p:
                    if j == 'food':
                        j = 'meal'
                    info.add(j)
                    find = True
                    break
            if find == True:
                break
        if find == False:
            info.add(p)
    return info
###############################################################################

###############################################################################
def _DETECTION(DATA, TYPE, MEDICATIONS):
    if TYPE == 'DOSE':
        MATCHER = dose_matcher
        MODIFY = _MODIFY_DOSE
    elif TYPE == 'FREQUENCY':
        MATCHER = freq_matcher
        MODIFY = _MODIFY_FREQ
    elif TYPE == 'PERIPHERAL':
        MATCHER = peri_matcher
        MODIFY = _MODIFY_PERI
    else:
        print('Incorrect Type: ', TYPE)
        exit(1)         
    print('******************************')
    print(TYPE+' Change Detection Starts...')
    # Step 2. 
    print('Step 2. Input Lines: ', len(DATA))
    DATA[TYPE+'_DIRECTIONS'] = DATA['NEW_DIRECTIONS'].apply(_EXTRACT, matcher=MATCHER)
    DATA[TYPE+'_SIG_TEXT'] = DATA['NEW_SIG_TEXT'].apply(_EXTRACT, matcher=MATCHER)
    DATA = DATA.loc[(DATA[TYPE+'_DIRECTIONS'] != DATA[TYPE+'_SIG_TEXT'])|(DATA[TYPE+'_DIRECTIONS']==set())].copy()
    # Step 3. 
    print('Step 3. Input Lines: ', len(DATA))
    DATA['NEW_'+TYPE+'_DIRECTIONS'] = DATA.apply(MODIFY, axis=1, NAME=TYPE+'_DIRECTIONS', MEDICATIONS=MEDICATIONS)
    DATA['NEW_'+TYPE+'_SIG_TEXT'] = DATA.apply(MODIFY, axis=1, NAME=TYPE+'_SIG_TEXT', MEDICATIONS=MEDICATIONS)
    DATA[TYPE+'_CHANGE'] = (DATA['NEW_'+TYPE+'_DIRECTIONS'] != DATA['NEW_'+TYPE+'_SIG_TEXT'])
    if TYPE != 'PERIPHERAL':
        DATA = DATA.loc[(DATA[TYPE+'_CHANGE']==True)|(DATA['NEW_'+TYPE+'_DIRECTIONS']==set())].copy()
    else:
        DATA = DATA.loc[DATA[TYPE+'_CHANGE']==True].copy()
    print(TYPE+' Change Detection Ends')
    print('Detect ' + str(len(DATA)) + ' ' + TYPE + ' Changes')
    # Return
    return DATA[['DOCUPACK_URL','CURRENT_QUEUE','ID','PRESCRIPTION_ID','MEDICATION_DESCRIPTION',\
                 'ESCRIBE_DIRECTIONS','SIG_TEXT','LINE_NUMBER','TOTAL_LINE_COUNT',\
                 #'NEW_DIRECTIONS', 'NEW_SIG_TEXT', TYPE+'_DIRECTIONS', TYPE+'_SIG_TEXT',\
                TYPE+'_DIRECTIONS',TYPE+'_SIG_TEXT','NEW_'+TYPE+'_DIRECTIONS','NEW_'+TYPE+'_SIG_TEXT',TYPE+'_CHANGE']]
###############################################################################

###############################################################################
# SQL
def _SQL(QUERY):
    import data_science_tools as dst
    snow_eng = dst.snowflake_prod
    snow_conn = snow_eng.connect()
    data = pd.read_sql(QUERY, con=snow_conn)
    snow_conn.close()
    snow_eng.dispose()
    return data

RISK_QUERY = """SELECT id,
                       prescription_id,
                       medication_description,
                       predicted_risk
                FROM analytics_core.drug_dir_pv1_rx_risk
                WHERE sf_updated_at >= CURRENT_TIMESTAMP() - interval '24.5 hour'"""
DIRECTION_QUERY = """SELECT   ('https://admin.pillpack.com/admin/docupack/#/' || docs.id) docupack_url,
                              docs.queue current_queue,
                              doc_pres.id id,
                              sig.prescription_id,
                              sig.id sig_id,
                              sig.line_number,
                              sig.text sig_text,
                              esc.directions escribe_directions,  
                              esc.ndc,
                              sig.quantity_per_dose,
                              sig.units,
                              sig.hoa_times,
                              sig.quantity_per_day,
                              sig.schedule_type,
                              sig.period,
                              sig.dow,
                              doc_pres.med_name medication_description
                     FROM source_pillpack_core.docupack_prescriptions doc_pres
                     LEFT JOIN source_pillpack_core.docupack_documents docs ON doc_pres.document_id = docs.id
                     LEFT JOIN source_pillpack_core.prescriptions pres ON doc_pres.app_prescription_id = pres.id
                     LEFT JOIN source_pillpack_core.sig_lines sig ON doc_pres.app_prescription_id = sig.prescription_id
                     LEFT JOIN source_pillpack_core.escribes esc ON esc.docupack_prescription_id= doc_pres.id
                     WHERE docs.created_at >= CURRENT_TIMESTAMP() - interval '24.5 hour' -- Use for prediction. Intentionally a half hour is added in case the code runs with some delays, we do not want to miss any prescription
                     AND sig.id IS NOT NULL
                     AND pres.rx_number IS NOT NULL
                     AND doc_pres.self_prescribed = false
                     AND docs.source = 'Escribe'
                     AND esc.id is NOT NULL"""
###############################################################################

###############################################################################
# Send email from SES that the job failed to run
import boto3
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

EMAIL_LIST = ['jeff.liu@pillpack.com'] #, 'cetinkay@amazon.com', 'mohsen.bayati@pillpack.com', \
              #'ipshita.jain@pillpack.com', 'olivia@pillpack.com', 'dane@pillpack.com', 'colin.hayward@pillpack.com']

class EmailClient:
    def __init__(self, sender="data_science_bot@pillpack.com", region="us-east-1"):
        self.sender = sender
        self.client = boto3.client('ses',region_name=region)

    def construct_email(self, subject, body):
        body_html = """
        <html>
        <head></head>
        <body>
          <h1>{0}</h1>
          <p>{1}</p>
        </body>
        </html>
        """.format(subject, body)
        return body_html

    def send_email(self, recipients, subject, body, attachment=None, charset="utf-8"):
        body_html = self.construct_email(subject, body)
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = self.sender
        msg['To'] = ', '.join(recipients)
        # message body
        part = MIMEText(body_html.encode(charset), 'html', charset)
        msg.attach(part)
        if attachment:
            # attachment
            part = MIMEApplication(open(attachment, 'rb').read())
            part.add_header('Content-Disposition', 'attachment', filename='Direction_Changes_'+pd.to_datetime('now').date().isoformat()+'.csv')
            msg.attach(part)
        response = self.client.send_raw_email(
            Source=msg['From'],
            Destinations=recipients,
            RawMessage={'Data': msg.as_string()}
        )
###############################################################################

###############################################################################
#import datetime as dt
#def KPI(DAYS=7):
#    PATH = os.path.abspath(os.getcwd())+'/Results/'
#    TIME = pd.to_datetime('now').date()
#    data_list = []
#    for i in range(DAYS):
#        TIME = TIME - dt.timedelta(days=1)
#        data = pd.read_csv(PATH+'Direction_Changes_'+TIME.isoformat()+'.csv')\
#        [['ID','PRESCRIPTION_ID','ESCRIBE_DIRECTIONS','SIG_TEXT','MEDICATION_DESCRIPTION','LINE_NUMBER','TOTAL_LINE_COUNT','DOSE_CHANGE','FREQUENCY_CHANGE','PERIPHERAL_CHANGE']]
#        data_list.append(data)
#    data = pd.concat(data_list, axis=0, ignore_index=True).drop_duplicates()   
#    del(data_list)        
###############################################################################

###############################################################################
def main():
    # Path and Filename
    PATH = os.path.abspath(os.getcwd())#+'/Data/'
    #TIME = '08272020'
    TIME = pd.to_datetime('now').date().isoformat()
    INPUT_RISK = '/Data/predicted_risk_'+TIME+'.csv'
    INPUT_DIRECTION = '/Data/direction_sigline_'+TIME+'.csv'
    OUTPUT = '/Results/results_'+TIME+'.csv'    
    ### Load Data
    print('******************************')
    print('Loading Predicted Risk')
    try:    
        risk = pd.read_csv(PATH+INPUT_RISK) # NDC in string type, some NDCs start with 0's
    except:
        print('Running SQL to pull predicted risk from Snowflake...') 
        risk = _SQL(RISK_QUERY)
    risk.columns = risk.columns.str.upper()
    print('Loading Directions')
    try:    
        data = pd.read_csv(PATH+INPUT_DIRECTION) # NDC in string type, some NDCs start with 0's
    except:
        print('Running SQL to pull directions from Snowflake...') 
        data = _SQL(DIRECTION_QUERY)                         
    data.columns = data.columns.str.upper()
    data = data.drop_duplicates()  # remove duplicated records   
    data['TOTAL_LINE_COUNT'] = data.groupby('ID')['LINE_NUMBER'].transform('count') # total sigline count
    data.to_csv(PATH+'/Results/snapshopts_'+TIME+'.csv', index=False)
    # Extract Medication Strength Information
    print('******************************')
    print('Extracing Medication Strength Infromation')
    medications = data[['MEDICATION_DESCRIPTION']].fillna('') ### Some NDC is incorrect!!! 'supply!!!'
    medications = medications.drop_duplicates()
    medications['NEW_MEDICATION_DESCRIPTION'] = medications['MEDICATION_DESCRIPTION'].apply(_REWORD, remove_bracket=True)
    medications['STRENGTH'] = medications['NEW_MEDICATION_DESCRIPTION'].apply(_EXTRACT, matcher=dose_matcher)
    ### Step 0. Convert Original Directions and Sigline Texts and Extract Strength Inforamtion
    print('******************************')
    print('Step 0. Converting to Standard Format')
    # Convert Escribe Directions and Sigline Texts
    data['NEW_DIRECTIONS'] = data['ESCRIBE_DIRECTIONS'].apply(_REWORD)
    data['NEW_SIG_TEXT'] = data['SIG_TEXT'].apply(_REWORD)
    ### Step 1. Compare New Direcitons and Sigline Text
    print('******************************')
    print('Step 1. Input Lines: ', len(data))
    data['SAME_DIRECTIONS'] = (data['NEW_DIRECTIONS'] == data['NEW_SIG_TEXT'])
    data = data[data['SAME_DIRECTIONS']==False]
    print('Detect ' + str(len(data)) + ' Direction Changes')    
    ### Step 2 and 3. Direction Change Detection
    results = pd.DataFrame()
    for TYPE in ['DOSE','FREQUENCY','PERIPHERAL']: 
        result = _DETECTION(data.loc[:], TYPE, medications).copy()
        if len(results) == 0:
            results =  result.copy()
        else:
            results = results.merge(result, on=['DOCUPACK_URL','CURRENT_QUEUE','ID','PRESCRIPTION_ID','MEDICATION_DESCRIPTION',\
                                                'ESCRIBE_DIRECTIONS','SIG_TEXT','LINE_NUMBER','TOTAL_LINE_COUNT'], how='outer')
    ### Save and Return
    results = results.merge(medications, on=['MEDICATION_DESCRIPTION'], how='left')
    results = results.merge(risk, on=['ID','PRESCRIPTION_ID','MEDICATION_DESCRIPTION'], how='left')
    results = results.sort_values(by=['TOTAL_LINE_COUNT','CURRENT_QUEUE','PREDICTED_RISK'], ascending=[True,True,False], na_position='last') # sort by predicated risk from higher to lower and put NAs last
    results.to_csv(PATH+OUTPUT, index=False)
    email = EmailClient()
    email.send_email(EMAIL_LIST,
       'Direction Changes ' + TIME,
       'Hey team, <br><br>\
       Attached please find the direction changes on {0}. If you have any questions please contact Jeff Liu: jeff.liu@pillpack.com. <br><br> \
       Key Columns: <br> \
       DOCUPACK_URL: link to document <br> \
       CURRENT_QUEUE: Archive, ExistingPatients <br> \
       ID: docupack prescriptions id <br> \
       PRESCRIPTION_ID <br> \
       MEDICATION_DESCRIPTION <br> \
       ESCRIBE_DIRECTIONS <br> \
       SIG_TEXT <br> \
       LINE_NUMBER: sigline number <br> \
       TOTAL_LINE_COUNT: total number of siglines; if a prescription has more than one siglines, it is likely to be detected since information is saved in different siglines <br> \
       FREQUENCY_CHANGE: if Ture, there are changes; if False, frequency info is missing <br> \
       DOSE_CHANGE: if Ture, there are changes; if False, dose info is missing <br> \
       PERIPHERAL_CHANGE: if Ture, there are changes <br> \
       PREDICTED_RISK: risk of direction changes from ML model, high value means high risk <br><br>\
       Best, <br>data_science_bot'.format(TIME),
       PATH+OUTPUT)
    #results[['ID','PRESCRIPTION_ID','DIRECTIONS','SIG_TEXT','MEDICATION_DESCRIPTION',DOSE_CHANGE','FREQUENCY_CHANGE','PERIPHERAL_CHANGE','LINE_NUMBER','TOTAL_LINE_COUNT']].to_csv(PATH+OUTPUT, index=False)
    return results

if __name__ == "__main__":
    results = main()



#import datetime as dt
#PATH = os.path.abspath(os.getcwd())+'/Results/'
#TIME = pd.to_datetime('now').date()
#data_list = []
#for i in range(DAYS):
#    TIME = TIME - dt.timedelta(days=1)
#    data = pd.read_csv(PATH+'Direction_Changes_'+TIME.isoformat()+'.csv')\
#        [['ID','PRESCRIPTION_ID','ESCRIBE_DIRECTIONS','SIG_TEXT','MEDICATION_DESCRIPTION','LINE_NUMBER','TOTAL_LINE_COUNT','DOSE_CHANGE','FREQUENCY_CHANGE','PERIPHERAL_CHANGE']]
#    data_list.append(data)
#data = pd.concat(data_list, axis=0, ignore_index=True).drop_duplicates()   
#
#
#nm_list = []
#for i in range(1,10):
#    nm = pd.read_csv(PATH+'Near_Misses_2020-09-0'+str(i)+'.csv')
#    nm_list.append(nm)
#nm = pd.concat(nm_list, axis=0, ignore_index=True).drop_duplicates()  
#
#
#new = nm.merge(data, on=['ID','PRESCRIPTION_ID'], how='left')
#print(len(nm), len(new[new.TOTAL_LINE_COUNT.notnull()]))
#
#new.to_csv(PATH+'KPI_0901-0908.csv',index=False)



#    ### Load Medication
#    try:
#        medications = pd.read_csv(PATH+'medications_new.csv', dtype={'ndc':str}) # NDC in string type, some NDCs start with 0's
#    except:
#        print('Running SQL to pull medications from Snowflake...')
#        medications = _SQL(MEDICATION_QUERY)        
#    medications.columns = medications.columns.str.upper()
#    medications = medications.fillna('')
##    medications = medications.groupby('NDC').max().reset_index()
#    def _DESC(ROW):
#        return str(ROW['DESCRIPTION']) + ' ' + str(ROW['GSDD_DESC']) # combine two columns related to drug descriptions
#    if 'STRENGTH' in medications.columns:
#        medications.loc[medications.STRENGTH=='set()','STRENGTH'] = "{}"
#        medications['STRENGTH'] = medications['STRENGTH'].apply(ast.literal_eval)
#    else:
#        medications['DRUG_DESCRIPTION'] = medications.apply(_DESC, axis=1)
#        medications['DRUG_DESCRIPTION'] = medications['DRUG_DESCRIPTION'].apply(_REWORD)
#        medications['STRENGTH'] = medications['DRUG_DESCRIPTION'].apply(_EXTRACT, matcher=dose_matcher)

###############################################################################
## Dose Change Detection
# Step D-2. Get Frequency and Compare
#print('Step 2: ', len(data))
#data['DOSE_DIRECTIONS'] = data['NEW_DIRECTIONS'].apply(_EXTRACT, matcher=dose_matcher)
#data['DOSE_SIG_TEXT'] = data['NEW_SIG_TEXT'].apply(_EXTRACT, matcher=dose_matcher)
#data['SAME_DOSE'] = (data['DOSE_DIRECTIONS'] == data['DOSE_SIG_TEXT'])
#data = data[(data['SAME_DOSE']==False)|(data['DOSE_DIRECTIONS']==set())]

# Step D-3. Compare Modified 
#print('Step 3: ', len(data))
#data['NEW_DOSE_DIRECTIONS'] = data.apply(_MODIFY_DOSE, axis=1, NAME='DOSE_DIRECTIONS')
#data['NEW_DOSE_SIG_TEXT'] = data.apply(_MODIFY_DOSE, axis=1, NAME='DOSE_SIG_TEXT')
#data['SAME_NEW_DOSE'] = (data['NEW_DOSE_DIRECTIONS'] == data['NEW_DOSE_SIG_TEXT'])
#data = data[(data['SAME_NEW_DOSE']==False)|(data['NEW_DOSE_DIRECTIONS']==set())]

# Save
#print('Changes/Missings: ', len(data))
#x = data[['NEW_DIRECTIONS','DIRECTIONS','NEW_SIG_TEXT','SIG_TEXT','DOSE_DIRECTIONS','DOSE_SIG_TEXT','SAME_DOSE',
#          'NEW_DOSE_DIRECTIONS','NEW_DOSE_SIG_TEXT','SAME_NEW_DOSE']]
#x.to_csv(OUTPUT, index=False)
###############################################################################

################################################################################
#### FREQUENCY
## Step 2. Get Frequency and Compare
#print('Step 2: ', len(data))
#data['FREQ_DIRECTIONS'] = data['NEW_DIRECTIONS'].apply(_EXTRACT, matcher=freq_matcher)
#data['FREQ_SIG_TEXT'] = data['NEW_SIG_TEXT'].apply(_EXTRACT, matcher=freq_matcher)
#data['SAME_FREQ'] = (data['FREQ_DIRECTIONS'] == data['FREQ_SIG_TEXT'])
#data = data[(data['SAME_FREQ']==False)|(data['FREQ_DIRECTIONS']==set())]
#
## Step 3. Compare Modified 
#print('Step 3: ', len(data))
#data['NEW_FREQ_DIRECTIONS'] = data['FREQ_DIRECTIONS'].apply(_MODIFY_FREQ)
#data['NEW_FREQ_SIG_TEXT'] = data['FREQ_SIG_TEXT'].apply(_MODIFY_FREQ)
#data['SAME_NEW_FREQ'] = (data['NEW_FREQ_DIRECTIONS'] == data['NEW_FREQ_SIG_TEXT'])
#data = data[(data['SAME_NEW_FREQ']==False)|(data['NEW_FREQ_DIRECTIONS']==set())]

#x = data[data.TOTAL_LINE_COUNT==1]
#y = x[(x.PERI_DIRECTIONS != set())|(x.PERI_SIG_TEXT != set())]

#data.to_csv(PATH+'direction_sigline_500K_PS3.csv',index=False)
#
## Save Results
#print('Changes/Missings: ', len(data))
#x = data[['NEW_DIRECTIONS','DIRECTIONS','NEW_SIG_TEXT','SIG_TEXT','FREQ_DIRECTIONS','FREQ_SIG_TEXT','SAME_FREQ',
#          'NEW_FREQ_DIRECTIONS','NEW_FREQ_SIG_TEXT','SAME_NEW_FREQ']]
#x.to_csv(OUTPUT, index=False)
################################################################################

################################################################################
#### PERIPHERAL
## Step 2. Get Peripheral and Compare
#print('Step 2: ', len(data))
#data['PERI_DIRECTIONS'] = data['NEW_DIRECTIONS'].apply(_EXTRACT, matcher=peri_matcher)
#data['PERI_SIG_TEXT'] = data['NEW_SIG_TEXT'].apply(_EXTRACT, matcher=peri_matcher)
#data['SAME_PERI'] = (data['PERI_DIRECTIONS'] == data['PERI_SIG_TEXT'])
#data = data[(data['SAME_PERI']==False)|(data['PERI_DIRECTIONS']==set())]
#
## Step 3. Compare Modified 
#print('Step 3: ', len(data))
#data['NEW_PERI_DIRECTIONS'] = data['PERI_DIRECTIONS'].apply(_MODIFY_PERI)
#data['NEW_PERI_SIG_TEXT'] = data['PERI_SIG_TEXT'].apply(_MODIFY_PERI)
#data['SAME_NEW_PERI'] = (data['NEW_PERI_DIRECTIONS'] == data['NEW_PERI_SIG_TEXT'])
#data = data[(data['SAME_NEW_PERI']==False)|(data['NEW_PERI_DIRECTIONS']==set())]
#
## Save Results
#print('Changes/Missings: ', len(data))
#x = data[['NEW_DIRECTIONS','DIRECTIONS','NEW_SIG_TEXT','SIG_TEXT','PERI_DIRECTIONS','PERI_SIG_TEXT','SAME_PERI',
#          'NEW_PERI_DIRECTIONS','NEW_PERI_SIG_TEXT','SAME_NEW_PERI']]
#x.to_csv(OUTPUT, index=False)
################################################################################



###############################################################################
# Patterns for Dose
#dp1 = [{'POS':'NUM'},{'LOWER':{'IN':['tablets','tablet']},'POS':'NOUN'}] # 1 tablet
#dp2 = [{'POS':'VERB'}]+dp1 # take 1 tablet
#dp3 = [{'POS':'NUM'},{'LOWER':{'IN':['to', 'or']}}]+dp1 # 1 to 2 tablets
#dp4 = [{'POS':'VERB'}]+dp3 # take 1 to 2 tablets
#m_tool.add('DOSE', None, dp1, dp2, dp3, dp4)
###############################################################################


#
#if 'DOSE_DIRECTIONS' in data.columns and 'DOSE_SIG_TEXT' in data.columns:
#    data.loc[data.DOSE_DIRECTIONS=='set()','DOSE_DIRECTIONS'] = "{}"
#    data.loc[data.DOSE_SIG_TEXT=='set()','DOSE_SIG_TEXT'] = "{}"
#    data['DOSE_DIRECTIONS'] = data['DOSE_DIRECTIONS'].apply(ast.literal_eval)
#    data['DOSE_SIG_TEXT'] = data['DOSE_SIG_TEXT'].apply(ast.literal_eval)
#else:
#





#direction = nlp("on monday, tuesday, wednesday, thursday and friday, tablet, monday through saturday, except tuesday")
#direction = nlp("take one and a half tablet by mouth twice daily")
#direction = nlp("1 tab po qbedtime 6 days per week")
#print('POS:',[token.pos_ for token in direction])
#print('LEMMA:',[token.lemma_ for token in direction])
#print(direction.text)
#print('')








#
#PATH = 'Data/'
#FILENAME = 'direction_sigline_100K_hard.csv'

#
## Read File
#data = pd.read_csv(PATH+FILENAME)
#
## Convert Original Directions
#data['NEW_DIRECTIONS'] = data['DIRECTIONS'].apply(_REWORD)
#data['NEW_SIG_TEXT'] = data['SIG_TEXT'].apply(_REWORD)
#data['SAME_DIRECTIONS'] = (data['NEW_DIRECTIONS'] == data['NEW_SIG_TEXT'])
#
#
## Get Frequency
#data['FREQ_DIRECTIONS'] = data['NEW_DIRECTIONS'].apply(_FREQ)
#data['FREQ_SIG_TEXT'] = data['NEW_SIG_TEXT'].apply(_FREQ)
#data['SAME_FREQ'] = (data['FREQ_DIRECTIONS'] == data['FREQ_SIG_TEXT'])
#
## Save Results
##x = data[data['FREQ'] == set()][['NEW_DIRECTIONS','DIRECTIONS','FREQ']]
#x = data[['NEW_DIRECTIONS','DIRECTIONS','NEW_SIG_TEXT','SIG_TEXT','SAME_DIRECTIONS','FREQ_DIRECTIONS','FREQ_SIG_TEXT','SAME_FREQ']]
#x.to_csv('results_100K.csv', index=False)
#
#y = x.loc[:,'FREQ_DIRECTIONS'].value_counts(normalize=True)


#TABLET = ' tablet '
#MOUTH = ' mouth '
#MORNING = ' morning '
#EVENING = ' evening '
#HOURLY = ' hourly '
#DAILY = ' daily '
#WEEKLY = ' weekly '
#MONTHLY = ' monthly '
#
#WORD2NUM = {'one-half': '0.5', 'one and half': '0.5', 'half': '0.5', '1/2': '0.5',  '1/4': '0.25',
##               'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5', 'six': '6',
##               'seven': '7', 'eight': '8', 'nine': '9', 'ten': '10', 'eleven': '11',
##               'twelve': '12', 'thirteen': '13', 'fourteen': '14', 'fifteen': '15',
##               'sixteen': '16', 'seventeen': '17', 'eighteen': '18', 'nineteen': '19',
##               'twenty:': '20', 'thirty': '30', 'forty': '40', 'fifty': '50', 'sixty': '60',
##               'seventy': '70', 'eighty': '80', 'ninety': '90', 'hundred': '100', 'thousand': '1000',
#               'once': ' 1 times ', 'twice': ' 2 times ', 'bid': '2 times daily', 'tid': '3 times daily', 'qid': '4 times daily',
#               ' mg': 'mg', ' milligram': 'mg', ' ml': 'ml', ' milliliter': 'ml',
#               ',': ' ', '+': ' and ', ' to ': ' or ', '-': ' or ', ' thru ': ' through '}
#for i in range(1,97):
#    WORD2NUM['q'+str(i)+'h'] = 'every '+str(i)+' hours'
#WORD2CHANGE = {}
#WORD2CHANGE[TABLET] = ['tablet[\w|(|)]*[\s]', 'tab(s)', 'tabs ', 'tab ', 
#                          'capsule[\w|(|)]*[\s]', 'cap(s)', 'caps ', 'cap ',   
#                          'puff(s)', 'puffs ', 'puff ',
#                          'drop(s)', 'drops ', 'drop ',
#                          'spray(s)', 'sprays ', 'spray ',
#                          'pill(s)', 'pills ', 'pill ',
#                          'strip(s)', 'strips ', 'strip ',
#                          'ring(s)', 'rings ', 'ring ',
#                          'patch(es)', 'patches ', 'patch ']
#WORD2CHANGE[MOUTH] = ['by mouth', 'oral ', 'orally', 'p[.]*o[.]*']
#WORD2CHANGE[MORNING] = ['am']
#WORD2CHANGE[EVENING] = ['pm', 'night', ' hs'] # hs: at bedtime
#WORD2CHANGE[HOURLY] = ['a[\s]*hour', 'each[\s]*hour', 'every[\s]*hour', 'per[\s]*hour', 'hour[\w]*', ' qhs']
#WORD2CHANGE[DAILY] = ['a[\s]*day', 'each[\s]*day', 'every[\s]*day', 'per[\s]*day', 'daily', ' qd']
#WORD2CHANGE[WEEKLY] = ['a[\s]*week', 'each[\s]*week', 'every[\s]*week', 'per[\s]*week', 'weekly']
#WORD2CHANGE[MONTHLY] = ['a[\s]*month', 'each[\s]*month', 'every[\s]*month', 'pre[\s]*month', 'monthly']
#WORD2CHANGE[' monday '] = [' mon ', 'monday[(|)|s]*']
#WORD2CHANGE[' tuesday '] = [' tues ', 'tuesday[(|)|s]*']
#WORD2CHANGE[' wednesday '] = [' wed ', 'wednesday[(|)|s]*']
#WORD2CHANGE[' thursday '] = [' thu ', 'thursday[(|)|s]*']
#WORD2CHANGE[' friday '] = [' fir ', 'friday[(|)|s]*']
#WORD2CHANGE[' saturday '] = [' sat ', 'saturday[(|)|s]*']
#WORD2CHANGE[' sunday '] = [' sun ', 'sunday[(|)|s]*']
##
#
#
#for k in WORD2CHANGE:
#    WORD2CHANGE[k] = [re.compile(i) for i in WORD2CHANGE[k]]
#
#DOW = ['sunday','monday','tuesday','wednesday','thursday','friday','saturday'] # Day of week
#TOD = ['morning', 'breakfast', 'noon', 'lunch', 'afternoon', 'evening', 'dinner', 'supper', 'bedtime'] # time of day





#
#PATH = 'Data/'
#FILENAME = 'direction_sigline.csv'
#
#
#
## Read File
#data = pd.read_csv(PATH+FILENAME)
## Convert Columns
#data['HOA_TIMES'] = data['HOA_TIMES'].apply(ast.literal_eval) # Convert HOA_times
#def _DOW(dow): 
#    return dow[1:-1].split(',')
#data['DOW'] = data['DOW'].apply(_DOW) # Convert DOW
## Add Column
#data['FREQUENCY'] = data['HOA_TIMES'].apply(len) # Add frequency
#def _DAYS(dow):
#    return [i for i, e in enumerate(dow) if e=='true']
#data['DAYS'] = data['DOW'].apply(_DAYS) # Add days, 0: Sunday, 1: Monday, ..., 6: Saturday
#
## Reword a sentence
#def _REWORD(text):
#    text = str(text).lower()
#    while text[-1] == '.':
#        text = text[:-1] # Remove period at the end
#    text = text + ' ' # Add a space at the end
#    for k in WORD2CHANGE: # Change words
#        for i in WORD2CHANGE[k]: 
#            text = re.sub(i,k,text)
#    for k, i in WORD2NUM.items(): # Covert words to numbers
#        text = text.replace(k,i) 
#    return " ".join(text.split()) # split words into a list of words
#data['NEW_DIRECTIONS'] = data['DIRECTIONS'].apply(_REWORD)
#data['NEW_SIG_TEXT'] = data['SIG_TEXT'].apply(_REWORD)
## Compare
#data['SAMETEXT'] = (data['NEW_DIRECTIONS']==data['NEW_SIG_TEXT'])
#
#
## Get Information
#def _FIND(text,targets):
#    info = set()
#    for i in targets:
#        if len(re.findall(i,text)) > 0:
#            info.add(i)
#    return info
#data['D_TOD'] = data['NEW_DIRECTIONS'].apply(_FIND, args=(TOD,))
#
#
#def _DOW(text, DOW):
#    info = []
#    x = re.findall('[\w]+day[\s]*through[\s]*[\w]+day',text)
#    if len(x) > 0:
#        info.append(x)
#    x = re.findall('except*[o|n|a|t|\s]*[\w]+day[a|n|d|\s]*[\w]+day',text)
#    if len(x) > 0:
#        info.append(x)
#    else:
#        x = re.findall('except*[o|n|a|t|\s]*[\w]+day',text)
#        if len(x) > 0:
#            info.append(x)
#    for d in DOW:
#        if len(re.findall(d,text)) > 0:
#            info.append([d])
#    return info
#data['D_DOW'] = data['NEW_DIRECTIONS'].apply(_DOW, args=(DOW,))
#
#
## Get Frequency
#def _FREQ(text):
#    freq = []
#    # Get special        
#    for f in ['day','week']:
#        for i in ['every', 'pre', 'each']:
#            for j in ['other','[0-9]+']:
#                pattern = i+'[\s]*'+j+'[\s]*'+f
#                x = re.findall(pattern, text)
#                if len(x) > 0:
#                    freq.append(x)
#    x = re.findall('[0-9]+[\s]*days*[\s]*weekly', text)
#    if len(x) > 0:
#        freq.append(x)
#    # Get structured
#    for f in [HOURLY[1:-1], DAILY[1:-1],WEEKLY[1:-1],MONTHLY[1:-1]]:
#        if f == HOURLY[1:-1]:
#            pattern = 'every[\s]*[0-9]+[\s|-|o|r|(|)|0-9]*[\s]*'+f
#        else:
#            pattern = '[0-9|.]+[\s]*times*[\s]*'+f
#        x = re.findall(f, text)
#        if len(x) > 0:
#            x = re.findall(pattern, text)
#            if len(x) > 0:
#                freq.append(x)
#            elif f != HOURLY[1:-1] and len(freq)==0:
#                freq.append([f])
#    return freq
#data['FREQ'] = data['NEW_DIRECTIONS'].apply(_FREQ)





#x = data[['NEW_DIRECTIONS','DIRECTIONS','FREQ','D_DOW','D_TOD']]
#
#
#
#
#
#
##simple_data = data[['QUANTITY_PER_DOSE','UNITS','DOSE_QUAN','NEW_DIRECTIONS','DIRECTIONS','NEW_SIG_TEXT','CHECK','SAME']]    
###simple_data.loc[:,'len'] = simple_data.loc[:,'DOSE_QUAN'].apply(len)
##x = simple_data[simple_data['CHECK']==False]
#x.to_csv('results.csv', index=False)
##



## Get Quantity per Dose
#def _DOSE_QUAN(words):
#    dose_quan = [] 
#    start_index = 0
#    for i, e in enumerate(words):
#        if (e==TABLET[1:-1] or e==MOUTH[1:-1]) and i > 0:
#            count = 0
#            for j in range(i-1, start_index-1, -1):
#                if words[j]=='or':
#                    if count > 0:
#                        dose_quan.append(count)
#                        count = 0
#                    continue
#                elif words[j]=='and':
#                    continue
#                elif 'ml' in words[j] or 'mg' in words[j]: # '1 5mg tablet'
#                    continue
#                elif '(' in words[j] or ')' in words[j]: # '1 (one) tablet by mouth daily'
#                    continue
#                else:
#                    try :  
#                        float(words[j]) 
#                        count += float(words[j])
#                    except:         
#                        break
#            if count > 0:
#                dose_quan.append(count)    
#            start_index = i        
#    return dose_quan                            
#data['DOSE_QUAN'] = data['NEW_DIRECTIONS'].apply(_DOSE_QUAN)       
#
#
#
## Check Dose Quantity
#def _CHECK(row):
#    if row['QUANTITY_PER_DOSE'] in row['DOSE_QUAN']:
#        return True
#    else:
#        return False
#data['CHECK'] = data.apply(_CHECK, axis=1)



    


# need separate words? is there anything like that? 
# any rule-based detecting
# replace letter by something
# want to learn rule-based algorithm that is currenlty being used for data entry

# remove space between number of mg/ml