#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 16:22:12 2020

Quality Projects: Code for Real-Time Auditing 

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
                    '[(][\s]*one-half[\s]+to[\s]+one[\s]*[)]', '[(][\s]*one[\s]+half[\s]+to[\s]+one[\s]*[)]', '[(][\s]*one[\s]+&[\s]+one-half[\s]+to[\s]+two[\s]*[)]', 
                    '[(][\s]*two[\s]+and[\s]+one[-|\s]?half[\s]*[)]', '[(][\s]*three[\s]+and[\s]+one[-|\s]?half[\s]*[)]',
                    '[(][\s]*one[\s]*[)]', '[(][\s]*two[\s]*[)]', '[(][\s]*three[\s]*[)]', '[(][\s]*four[\s]*[)]', '[(][\s]*five[\s]*[)]', '[(][\s]*six[\s]*[)]', 
                    '[(][\s]*seven[\s]*[)]', '[(][\s]*eight[\s]*[)]', '[(][\s]*nine[\s]*[)]', '[(][\s]*ten[\s]*[)]', '[(][\s]*twelve[\s]*[)]', '[(][\s]*fourteen[\s]*[)]', 
                    '[(][\s]*twenty-four[\s]*[)]', '[(][\s]*twenty-eight[\s]*[)]', '[(][\s]*thirty[\s]*[)]', 
                    '[(][\s]*[0-9|.|,|/|\s]+[)]', 
                    '[(][\s]*[0-9|.|,|/|\s]+to[\s]*[0-9|.|,|/|\s]+[)]', '[(][\s]*[0-9|.|,|/|\s]+-[\s]*[0-9|.|,|/|\s]+[)]', 
                    '[(][\s]*[0-9|.|,|/|\s]+and[\s]*[0-9|.|,|/|\s]+[)]', '[(][\s]*[0-9|.|,|/|\s]+&[\s]*[0-9|.|,|/|\s]+[)]',
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
WORD2CHANGE[' orally dissolving tablet '] = ['[\s|.|,|;|-]+odt '] 
WORD2CHANGE[' \\1 by mouth '] = [' ([0-9]+)p[.]?o[.]? ']
WORD2CHANGE[' \\1 daily '] = [' ([0-9]+)q[.]?d[.]? ']
WORD2CHANGE[' as needed ' ] = [' p[.]?r[.]?n[.]? ']
WORD2CHANGE[' as directed ' ] = [' as[\s]*dir ']
WORD2CHANGE[' by mouth '] = [' [b]?[y]?[\s]*oral[\s]*route ', ' oral ', ' orally ', ' p[.]?o[.]? '] # oral, orally, p.o.
WORD2CHANGE[' and '] = [' & ']
WORD2CHANGE[' before '] = [' prior to ']
WORD2CHANGE[' every '] = [' each ', ' ea', ' per ']
WORD2CHANGE[' through '] = [' thur ']
WORD2CHANGE[' without '] = [' w/o ']
WORD2CHANGE[' with '] = [' w/ ']
WORD2CHANGE[' - '] = ['-']
WORD2CHANGE[' subcutaneous '] = [' subcutaneously ', ' into the skin ', ' under the skin ']
WORD2CHANGE[' intramuscular '] = [' intramuscularly ', ' into the muscle ']
### Numbers (order matters!)
WORD2CHANGE[' \\1\\2 '] = [' ([0-9]+)[,]([0-9]{3}[.]?[0-9]*)'] # 1,000 --> 1000
WORD2CHANGE[' 0\\1 '] = [' ([.][0-9]*) '] # .5 --> 0.5
WORD2CHANGE[' 0.25 '] = [' 1/4 of a[n]? ', ' 1/4 ', ' one quarter of a[n]? ', ' one quarter ']
WORD2CHANGE[' 1.5 '] = [' one and half ', ' one[\s|-]+and[\s|-]+a[\s|-]+half ', ' one and one[\s|-]+half ', ' 1[&|\s]*1/2 ', ' 1 and 0.5 ', ' 1 and 1/2 ', ' 1[\s|-]+1/2 ']
WORD2CHANGE[' 2.5 '] = [' two and half ', ' two and a half ', ' two and one[\s|-]+half ', ' 2[&|\s]*1/2 ', ' 2 and 0.5 ', ' 2 and 1/2 ', ' 2[\s|-]+1/2 ']
WORD2CHANGE[' 3.5 '] = [' three and half ', ' three and a half ', ' three and one[\s|-]+half ', ' 3[&|\s]*1/2 ', ' 3 and 0.5 ', ' 3 and 1/2 ', ' 3[\s|-]+1/2 ']
WORD2CHANGE[' 4.5 '] = [' four and half ', ' four and a half ', ' four and one[\s|-]+half ', ' 4[&|\s]*1/2 ', ' 4 and 0.5 ', ' 4 and 1/2 ', ' 4[\s|-]+1/2 ']
WORD2CHANGE[' 5.5 '] = [' five and half ', ' five and a half ', ' five and one[\s|-]+half ', ' 5[&|\s]*1/2 ', ' 5 and 0.5 ', ' 5 and 1/2 ', ' 5[\s|-]+1/2 ']
WORD2CHANGE[' 0.5 '] = [' one[\s]*-[\s]*half ', ' one half ', ' a half ', ' half a ', ' half of a ', ' 0.5/half ', ' half ', ' 1/2 ']
WORD2CHANGE[' 1 '] = [' one ', ' 1 whole ', ' 0ne ']
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
                           ' table ', 'tabet ', ' tabl[.]? ', 'tabelet ', ' tabletd ', ' tbt ', ' tablelet ', ' tablyes '] # tablet, tablets, tablet(s), tab, tabs, tab(s)
WORD2CHANGE[' capsule '] = ['[\-]?[\s]*capsule[(]?[s]?[)]?[\s|.|,|;|-|/]+', 'cap[(]?[s]?[)]?[\s|.|,|;|-]+', ' c[(]?[s]?[)]? ', 
                            ' capsul ', ' cpaules ', ' capsulse '] # capsule, capsules, capsule(s), cap, caps, cap(s) 
WORD2CHANGE[' pill '] = ['pill[(]?[s]?[)]?[\s|.|,|;|-]+'] # pill, pills, pill(s)    
WORD2CHANGE[' puff '] = ['puff[(]?[s]?[)]?[\s|.|,|;|-]+', ' pufs ',
                         'inhalation[(]?[s]?[)]?[\s|.|,|;|-]+', 'inhaler[(]?[s]?[)]? ', 'inh[l]?[(]?[s]?[)]?[\s|.|,|;|-]+', ' aerosol[(]?[s]?[)]? '] # puff, puffs, puff(s)   
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
#WORD2CHANGE[' application '] = ['appliciation[(]?[s]?[)]?[\s|.|,|;|-]+', 'applicator[(]?[s]?[)]?[\s|.|,|;|-]+', 'app[l]?[(]?[s]?[)]?[\s|.|,|;|-]+'] # application(s), app(s)              
WORD2CHANGE[' ampule '] = ['amp[o]?ule[(]?[s]?[)]?[\s|.|,|;|-]+', 'ampul[(]?[s]?[)]?[\s|.|,|;|-]+'] # ampule(s), ampoule(s), ampul(s) 
WORD2CHANGE[' piece '] = ['piece[(]?[s]?[)]?[\s|.|,|;|-]+']
WORD2CHANGE[' needle '] = ['needle[(]?[s]?[)]?[\s|.|,|;|-]+']
WORD2CHANGE[' suppository '] = ['suppository[\s|.|,|;|-]+', 'suppositories[\s|.|,|;|-]+']
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
                               ' before midday ', ' every[\s]*a[.]?m[.]?[\s|.|,|;|-]+'] # morning(s), qam
WORD2CHANGE[' a.m. '] = ['[\s]*a[.]?m[.]?[\s|.|,|;|-]+', ' a..m '] # a.m.
WORD2CHANGE[' midday '] = [' noon[(]?[s]?[)]?[\s|.|,|;|-]+', ' midday[(]?[s]?[)]?[\s|.|,|;|-]+'] # noon(s), midday(s)
WORD2CHANGE[' in midday '] = [' q[.]?[\s]*noon[(]?[s]?[)]?[\s|.|,|;|-]+']
WORD2CHANGE[' afternoon '] = [' afternoon[(]?[s]?[)]?[\s|.|,|;|-]+']
WORD2CHANGE[' in afternoon '] = [' q[.]?[\s]*afternoon[(]?[s]?[)]?[\s|.|,|;|-]+', 
                                 ' after school[\s|.|,|;|-]+', ' mid afternoon[\s|.|,|;|-]+'] # afternoon(s)
WORD2CHANGE[' evening '] = [' evening[(]?[s]?[)]?[\s|.|,|;|-]+', ' night[(]?[s]?[)]?[\s|.|,|;|-]+', ' nighttime[\s|.|,|;|-]+', ' midnight[\s|.|,|;|-]+']
WORD2CHANGE[' in evening '] = [' q[.]?[\s]*evening[(]?[s]?[)]?[\s|.|,|;|-]+', ' q[.]?[\s]*night[(]?[s]?[)]?[\s|.|,|;|-]+', 
                               ' q[.]?[\s]*p[.]?m[.]?[\s|.|,|;|-]+', ' in[\s]*p[.]?m[.]?[\s|.|,|;|-]+', ' in[\s]*the[\s]*p[.]?m[.]?[\s|.|,|;|-]+',
                               ' nightly[\s|.|,|;|-]+', ' nighlty ', ' every[\s]*p[.]?m[.]?[\s|.|,|;|-]+'] # night(s), nightly, nighttime, qpm
WORD2CHANGE[' p.m. '] = ['[\s]*p[.]?m[.]?[\s|.|,|;|-]+', ' p..m '] # p.m.
WORD2CHANGE[' every \\1 \\2 '] = [' [.]?q[.]?[\s]*([0-9]+)[\s]*([a|p]{1}[.]?m[.]?)[\s|.|,|;|-]+'] # q6am    
# Special Time of Day
WORD2CHANGE[' breakfast '] = [' breakfast[(]?[s]?[)]?[\s|.|,|;|-]+', 'breakfst', 'brakfast', 'bkfst', 'morning meal[s]? '] # breakfast(s)
WORD2CHANGE[' before breakfast '] = [' a[.]?c[.]?[\s]*breakfast ', ' a[.]?c[.]?[\s]*bk ']
WORD2CHANGE[' with breakfast '] = [' w breakfast ']
WORD2CHANGE[' lunch '] = [' lunch[(]?[e|s]*[)]?[\s|.|,|;|-]+'] # lunch(es)
WORD2CHANGE[' before lunch '] = [' a[.]?c[.]?[\s]+lunch ' ]
WORD2CHANGE[' with lunch '] = [' w lunch ']
WORD2CHANGE[' dinner '] = [' dinner[(]?[s]?[)]?[\s|.|,|;|-]+', ' supper[(]?[s]?[)]?[\s|.|,|;|-]+', ' dinnertime ', ' evening meal[s]? '] # dinner(s), supper(s)
WORD2CHANGE[' before dinner '] = [' a[.]?c[.]?[\s]+dinner ']
WORD2CHANGE[' with dinner '] = [' w dinner ']
WORD2CHANGE[' bedtime '] = [' bed[(]?[s]?[)]?[\s|.|,|;|-]+', ' bedtime[\w]*[\s|.|,|;|-]+', ' bed[\s]*time[(]?[s]?[)]?[\s|.|,|;|-]+']
WORD2CHANGE[' at bedtime '] = [' at h[.]?s[.]?[\s|,|;|-]+', ' [.]?q[.]?[-|\s]*h[.]?s[.]?[\s|,|;|-]+', ' h[.]?s[.]?[\s|,|;|-]+', ' q[\s]*bedtime[\s|.|,|;|-]+', ' before[\s]+bedtime '] # bed(s), bedtime(s), bed time(s), h.s., qbedtime 
WORD2CHANGE[' meal '] = [' [a]?[\s]*meal[(]?[s]*[)]?[\s|.|,|;|-]+'] # meal(s)
WORD2CHANGE[' before meal '] = [' q[.]?a[.]?c[.]? ', ' a[.]?c[.]? ', ' before every meal ', ' before each meal ']
WORD2CHANGE[' with meal '] = [' w meal ', ' withmeal[s]? ', ' with every meal ', ' with each meal ']
WORD2CHANGE[' with food '] = [' w food ']
WORD2CHANGE[' shortness of breath '] = [' s[.]?o[.]?b[.]? ']
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
WORD2CHANGE[' every \\1 hours '] = [' [.]?q[.]?[\s]*([0-9]+)[\s|-]*h[o]?[u]?[r]?[(]?[s]?[)]?[\s|.|,|;|-]+'] # q12hour(s)    
WORD2CHANGE[' every \\1 to \\2 hours '] = [' [.]?q[.]?[\s]*([0-9]+)[\s]*to[\s]*([0-9]+)[\s]*h[o]?[u]?[r]?[(]?[s]?[)]?[\s|.|,|;|-]+', 
                                           ' [.]?q[.]?[\s]*([0-9]+)[\s]*-[\s]*([0-9]+)[\s]*h[o]?[u]?[r]?[(]?[s]?[)]?[\s|.|,|;|-]+'] # q1 to 2 h          
WORD2CHANGE[' daily '] = [' a[\s]*day ', ' [o|n|c|e]*[\s]*a[\s]*day ', ' [o|n|c|e]*[\s]*each[\s]*day ', ' [o|n|c|e]*[\s]*every[\s]*day ', ' [o|n|c|e]*[\s]*per[\s]*day ', 
                          ' once[\s]+daily ', ' 1 time[\s]+daily ', ' once[\s]*day ', ' 1 time[\s]+day ', ' every 1 day ', ' for 1 day', ' for a day ',
                          ' q[.]?[\s]*day[\s|.|,|;|-]+', ' q[.]?[\s]*d[.]?[\s|,|;|-]+', ' q[.]?[\s]*dly[.]?[\s|,|;|-]+', ' qd[\*] ', ' q[\s]+daily ', ' a[\s]+daily ',
                          '/[\s]*day ', '/[\s]*d ', ' d ',                           
                          ' dailly ', 'dily', ' dly ', ' daiy ', ' dialy ', ' daoily ', ' dail ', 'dail;y ', ' daild ', ' daiily ', ' daliy '] # typos
WORD2CHANGE[' every \\1 days '] = [' [.]?q[.]?[\s]*([0-9]+)[\s]*d[a]?[y]?[(]?[s]?[)]?[\s|.|,|;|\-]+'] # q2day(s)
WORD2CHANGE[' every other day '] = [' [.]?q[.]?[\s]*other[\s]*day[\s|.|,|;|\-]+', ' [.]?q[.]?od '] # qotherday, qod   
WORD2CHANGE[' weekly '] = [' [o|n|c|e]*[\s]*a[\s]*week ', ' [o|n|c|e]*[\s]*each[\s]*week ', ' [o|n|c|e]*[\s]*every[\s]*week ', ' [o|n|c|e]*[\s]*per[\s]*week ', 
                           ' once[\s]+weekly ', ' 1 time[\s]+weekly ', ' once[\s]week ', ' 1 time[\s]+week ', 
                           ' q[.]?[\s]*week[\s|.|,|;|-]+', ' q[.]?[\s]*w[.]?[\s|,|;|-]+', ' q[.]?[\s]*wk[l|y]*[.|\s|,|;|-]+', ' q[\s]*-[\s]*week ',
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
UNIT_LIST = ['tablet', 'capsule', 'pill', 'puff', 'pump', 'drop', 'spray', 'strip', 'scoop', 'needle',
             'ring', 'patch', 'packet', 'unit', 'ampule', 'syringe', 'vial', 'pen', 'piece', 'suppository',
             # 'application',
             'gr', 'mg', 'mcg', 'ml', 'meq']
PERI_LIST = ['breakfast','lunch','dinner','meal','food','snack','milk',
             'morning', 'midday','afternoon','evening','bedtime',
             'neuropathy', 'subcutaneous', 'intramuscular', 'stomach']
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
fp['117'] = [{'LOWER':'up'},{'LOWER':'to'}] + fp['111']
fp['118'] = [{'LOWER':'up'},{'LOWER':'to'}] + fp['112']
fp['119'] = [{'LOWER':'up'},{'LOWER':'to'}] + fp['113']
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
fp['304'] = [{'LOWER':'at'}] + fp['303'] # at 7 am
fp['305'] = fp['303'] + [{'LOWER':',','OP':'?'},{'LOWER':'and','OP':'?'}] + fp['303'] # 7 am and 12 pm
fp['306'] = [{'LOWER':'at'}] + fp['305'] # at 7 am and 12 pm
fp['307'] = fp['303'] + [{'LOWER':',','OP':'?'}] + fp['305'] # 7 am, 12 pm, and 6 pm
fp['308'] = [{'LOWER':'at'}] + fp['307'] # at 7 am, 12 pm, and 6 pm
fp['309'] = fp['303'] + [{'LOWER':',','OP':'?'}] + fp['307'] # 7 am, 12 pm, 6 pm, and 10 pm
fp['310'] = [{'LOWER':'at'}] + fp['307'] # at 7 am, 12 pm, 6 pm, and 10 pm
fp['311'] = [{'LOWER':'at'}] + NUM # at 1030
fp['312'] = fp['311'] + [{'LOWER':',','OP':'?'},{'LOWER':'and','OP':'?'}] + NUM # at 1030 and 2100
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
dp['105'] = [{'LOWER':'up'},{'LOWER':'to'}] + dp['101'] # up to 2 tablet
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
pp['106'] = [{'LOWER':'as'},{'LEMMA':{'IN':['direct','necessary','need']}}] # as needed
pp['107'] = [{'LOWER':'and'}] + pp['106'] # and as needed
pp['108'] = [{'LOWER':'if'},{'LEMMA':{'IN':['direct','necessary','need']}}] # if needed
pp['109'] = [{'LOWER':'shortness'},{'LOWER':'of'},{'LOWER':'breath'}]
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
def _MODIFY_FREQ(FREQ, STRENGTH):
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
        # hours
        for t in ['hour', 'hours']: # every 4 hours
            if t in f:
                info.add(f)
        # time
        times = re.findall('[0-9]?[0-9][:][0-9][0-9][\s]+[a|p]?.m.', f) # timestamps, 7:00 p.m., 10/09/2020
        for t in times:
            t = re.sub('[\s]+', ' ', t)
            info.add(t)
        if len(times) == 0:
            times = re.findall('[0-1]?[0-9][\s]+[a|p]?.m.', f) # timestamps, 7 p.m., 10/09/2020
            for t in times:
                t = re.sub('[\s]+', ' ', t)
                t = t[:-5]+':00'+t[-5:]
                info.add(t)        
        # military time
        military_times = re.findall('[0-9]{4}', f) # find military time, 10/09/2020
        for t in military_times:
            if int(t[:2]) >= 12:
                if int(t[2:]) > 0:
                    info.add(t[:2]+':'+t[2:]+' p.m.')
                else:
                    info.add(t[:2]+' p.m.')
                if int(t[:2]) == 12 and int(t[2:]) == 0:
                    noon =1
                else:
                    afternoon = 1
            else:
                if int(t[2:]) > 0:
                    info.add(t[:2]+':'+t[2:]+' a.m.')
                else:
                    info.add(t[:2]+' a.m.')                    
                morning = 1
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
        for d in [1,2,3,4,5,6]:
            for t in [str(d)+' time daily', str(d)+' times daily', str(d)+' time day', str(d)+' times day']:
                if t == f:
                    daily = max(d, daily)        
        for t in ['every 24 hours', 'every 24 hour', 
                  'every day', 'every 1 day','everyday', 'each day', 'day', 'days', 'daily']:
            if t in f:
                daily = max(1, daily)
        for t in ['every 2 days','every other day']:
            if t in f:
                daily = 0
                info.add('every 2 days')             
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
                daily = 0
                weekly = max(1, weekly)
        for t in ['every 14 days', 'every 2 weeks', 'every other week']:
            if t in f:
                daily = 0
                weekly = 0
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
    if len(info) == 0:
        info = FREQ
    return info    
###############################################################################

###############################################################################
# Modify Dose and Compare
def _MODIFY_DOSE(DOSE, STRENGTH):
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
    if len(info) == 0: # if no dose informaiton is found, then use strength information
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
def _MODIFY_PERI(PERI, STRENGTH):
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
        for i in ['morning','midday','afternoon','evening']:
            if i in p:
                info.add(i)
                find = True
        if find == False:
            info.add(p)
    if 'morning' in info and 'breakfast' in info: # remove words with similar meaning
        info.remove('morning')
    if 'evening' in info and 'dinner' in info: # remove words with similar meaning
        info.remove('evening')        
    if 'evening' in info and 'bedtime' in info: # remove words with similar meaning
        info.remove('evening')
    return info
###############################################################################

###############################################################################
def _DETECTION(DIRECTION, SIG_TEXT, TYPE, STRENGTH):
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
    result = 0
    print('******************************')
    print(TYPE+' Change Detection Starts...')
    # Step 2. 
    print('Step 2')
    NEW_DIRECTION = _EXTRACT(DIRECTION, MATCHER)
    NEW_SIG_TEXT = _EXTRACT(SIG_TEXT, MATCHER)
    if NEW_DIRECTION != NEW_SIG_TEXT or NEW_DIRECTION == set():
    # Step 3. 
        print('Step 3')
        NEW_DIRECTION = MODIFY(NEW_DIRECTION, STRENGTH)
        NEW_SIG_TEXT = MODIFY(NEW_SIG_TEXT, STRENGTH)
        if TYPE != 'PERIPHERAL': 
            if NEW_DIRECTION != NEW_SIG_TEXT or NEW_DIRECTION == set():
                result = 1
        else:
            if NEW_DIRECTION != NEW_SIG_TEXT:
                result = 1
    return result
###############################################################################

###############################################################################
def main(ESCRIBE_DIRECTION, SIG_TEXT, MEDICATION_DESCRIPTION):
    """
    Inputs: escribe text: ESCRIBE_DIRECTION
            sigline text: SIG_TEX
            medication description: MEDICATION_DESCRIPTON
    Outputs:
            if there is a frequency change
            if there is a dose change
            if there is a peripheral information change
    """
    
    # Extract Medication Strength Information
    print('******************************')
    print('Extracing Medication Strength Infromation')  
    NEW_MEDICATION_DESCRIPTION = _REWORD(MEDICATION_DESCRIPTION, remove_bracket=True)
    STRENGTH = _EXTRACT(NEW_MEDICATION_DESCRIPTION, matcher=dose_matcher)
    ### Step 0. Convert Original Directions and Sigline Texts and Extract Strength Inforamtion
    print('******************************')
    print('Step 0. Converting to Standard Format')
    # Convert Escribe Directions and Sigline Texts
    NEW_DIRECTION = _REWORD(ESCRIBE_DIRECTION)
    NEW_SIG_TEXT = _REWORD(SIG_TEXT)
    ### Step 1. Compare New Direcitons and Sigline Text
    print('******************************')
    print('Step 1')
    if NEW_DIRECTION == NEW_SIG_TEXT:
        result = 0
    else: 
    ### Step 2 and 3. Direction Change Detection
        result = {}
        for TYPE in ['DOSE','FREQUENCY','PERIPHERAL']: 
            result[TYPE] = _DETECTION(NEW_DIRECTION, NEW_SIG_TEXT, TYPE, STRENGTH)
    return result