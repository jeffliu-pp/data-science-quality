#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 16:22:12 2020

Quality Projects: Code for High-Frequency Auditing 

@author: liujianf
"""

import os
import sys
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
WORD2CHANGE[' mg '] = ['[\s]*mg[(]?[s]?[)]?[\s|.|,|;]+', '[\s]*milligram[(]?[s]?[)]?[\s|.|,|;]+'] # mg(s), milligram(s)
WORD2CHANGE[' mcg / '] = [' mcg/']
WORD2CHANGE[' mcg '] = ['[\s]*mcg[(]?[s]?[)]?[\s|.|,|;]+', '[\s]*microgram[(]?[s]?[)]?[\s|.|,|;]+'] # mcg(s), microgram(s)
WORD2CHANGE[' \\1 gr '] = ['([0-9]+)g[\s|.|,|;]+']
WORD2CHANGE[' gr '] = ['[\s]*gr[(]?[s]?[)]?[\s|.|,|;]+', '[\s]*gram[(]?[s]?[)]?[\s|.|,|;]+', ' g[\s|.|,|;]+', ' gm[\s|.|,|;]+'] # gr(s), gram(s)
WORD2CHANGE[' ml '] = ['[\s]*ml[(]?[s]?[)]?[\s|.|,|;]+', '[\s]*milliliter[(]?[s]?[)]?[\s|.|,|;]+'] # ml(s), milliliter(s)
WORD2CHANGE[' meq '] = [' milliequivalent[(]?[s]?[)]?[\s|.|,|;]+', ' meq[(]?[s]?[)]?[\s|.|,|;]+'] 
WORD2CHANGE[' po \\1 '] = [' p[.]?o[.]?(q[a-z]{2})', ' p[.]?o[.]?(q[d|w]{1})', ' p[.]?o[.]?([b|t]{1}id)'] # poqam, poqhs, poqid, poqd, poqw, pobid, potid
WORD2CHANGE[' ac hs '] = [' a[.]?c[.]?h[.]?s[.]? ']
WORD2CHANGE[' \\1 ac '] = [' ([b|t|q]{1}id)ac ', ' (qd)ac ', ' (qday)ac ' ]
WORD2CHANGE[' orally dissolving tablet '] = ['[\s|.|,|;|-]+odt '] 
WORD2CHANGE[' \\1 by mouth '] = [' ([0-9]+)p[.]?o[.]? ']
WORD2CHANGE[' \\1 daily '] = [' ([0-9]+)q[.]?d[.]? ']
WORD2CHANGE[' as needed ' ] = ['[\s|.|,|;]+p[.]?r[.]?n[\s|.|,|;|:]+', ' s needed ', '[.|,|;]+as needed ']
WORD2CHANGE[' as directed ' ] = [' as[\s]*dir ', ' tad ', ' ud ', ' ut ', ' utd ', ' dict ', ' uad ', ' as instructed '] 
WORD2CHANGE[' by mouth '] = [' [b]?[y]?[\s]*oral[\s]*route ', ' oral ', ' orally ', ' p[.]?o[.]? '] # oral, orally, p.o.
WORD2CHANGE[' and '] = [' & ']
WORD2CHANGE[' before '] = [' prior to ']
WORD2CHANGE[' every '] = [' each ', ' ea ', ' per ', 'evey ', '.every ']
WORD2CHANGE[' through '] = [' thur ']
WORD2CHANGE[' without '] = [' w/o ']
WORD2CHANGE[' with '] = [' w/ ']
WORD2CHANGE[' up to '] = [' upto ']
WORD2CHANGE[' - '] = ['-']
WORD2CHANGE[' subcutaneous '] = [' subcutaneously ', ' into the skin ', ' into skin ', ' under the skin ', ' under skin ', ' below the skin ', ' below skin ', 
                                 ' s[/|\s]?q[\s|.|,|;]+', ' s[/|\s]?c[\s|.|,|;]+', ' subq ', ' subcut ', ' sub q route ', ' subcutan ']
WORD2CHANGE[' intramuscular '] = [' intramuscularly ', ' into the muscle ', ' im[\s|.|,|;]+']
### Numbers (order matters!)
WORD2CHANGE[' \\1\\2 '] = [' ([0-9]+)[,]([0-9]{3}[.]?[0-9]*)'] # 1,000 --> 1000
WORD2CHANGE[' 0\\1 '] = [' ([.][0-9]+) '] # .5 --> 0.5
WORD2CHANGE[' 0.25 '] = [' 1/4 of a[n]? ', ' 1/4 ', ' one quarter of a[n]? ', ' one quarter ', ' a quarter ', ' quarter ']
WORD2CHANGE[' 1.5 '] = [' one and half ', ' one[\s|-]+and[\s|-]+a[\s|-]+half ', ' one and one[\s|-]+half ', ' 1[&|\s]*1/2 ', ' 1 and 0.5 ', ' 1 and 1/2 ', ' 1[\s|-]+1/2 ']
WORD2CHANGE[' 2.5 '] = [' two and half ', ' two and a half ', ' two and one[\s|-]+half ', ' 2[&|\s]*1/2 ', ' 2 and 0.5 ', ' 2 and 1/2 ', ' 2[\s|-]+1/2 ']
WORD2CHANGE[' 3.5 '] = [' three and half ', ' three and a half ', ' three and one[\s|-]+half ', ' 3[&|\s]*1/2 ', ' 3 and 0.5 ', ' 3 and 1/2 ', ' 3[\s|-]+1/2 ']
WORD2CHANGE[' 4.5 '] = [' four and half ', ' four and a half ', ' four and one[\s|-]+half ', ' 4[&|\s]*1/2 ', ' 4 and 0.5 ', ' 4 and 1/2 ', ' 4[\s|-]+1/2 ']
WORD2CHANGE[' 5.5 '] = [' five and half ', ' five and a half ', ' five and one[\s|-]+half ', ' 5[&|\s]*1/2 ', ' 5 and 0.5 ', ' 5 and 1/2 ', ' 5[\s|-]+1/2 ']
WORD2CHANGE[' 0.5 '] = [' one[\s]*-[\s]*half ', ' one half ', ' a half ', ' half a ', ' half of a ', ' 0.5/half ', ' half ', ' 1/2 ']
WORD2CHANGE[' 24 '] = [' twenty[\s|-]+four ']
WORD2CHANGE[' 24=8 '] = [' twenty[\s|-]+eight ']
WORD2CHANGE[' 36 '] = [' thirty[\s|-]+six ']
WORD2CHANGE[' 48 '] = [' forty[\s|-]+eight ']
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
WORD2CHANGE[' 40 '] = [' forty ']
WORD2CHANGE[' 0.5 to \\1 '] = [' 1/2[\s]*-[\s]*([0-9]*)', ' 1/2[\s]+or[\s]+([0-9]*)']
WORD2CHANGE[' \\1 to \\2 '] = ['([0-9]+[.]?[0-9]*)[\s]*-[\s]*([0-9]+[.]?[0-9]*)', '([0-9]+[.]?[0-9]*)[\s]+or[\s]+([0-9]+[.]?[0-9]*)']
### Medication Units
WORD2CHANGE[' \\1 tablet '] = ['([0-9]+)t ']
WORD2CHANGE[' tablet '] = ['[\-]?[\s]*tablet[(]?[s]?[)]?[\s|.|,|;|-|/]+', 'tab[(]?[s]?[)]?[\s|.|,|;|-]+', ' t[(]?[s]?[)]? ', ' tb[(]?[s]?[)]? ', 
                           ' table[s]? ', 'tabet ', ' tabl[.]? ', 'tabelet ', ' tabletd ', ' tbt ', ' tablelet ', ' tablyes ', ' tabletby ', ' tableta ', ' of[\s]+tablet '] # tablet, tablets, tablet(s), tab, tabs, tab(s)
WORD2CHANGE[' capsule '] = ['[\-]?[\s]*capsule[(]?[s]?[)]?[\s|.|,|;|-|/]+', 'cap[(]?[s]?[)]?[\s|.|,|;|-]+', ' c[(]?[s]?[)]? ', 
                            ' capsul ', ' cpaules ', ' capsulse ', ' delayed release capsule[(]?[s]?[)]? ', ' of[\s]+capsule '] # capsule, capsules, capsule(s), cap, caps, cap(s) 
WORD2CHANGE[' pill '] = ['pill[(]?[s]?[)]?[\s|.|,|;|-]+'] # pill, pills, pill(s)    
WORD2CHANGE[' puff '] = ['puff[(]?[s]?[)]?[\s|.|,|;|-]+', ' pufs ',
                         'inhalation[(]?[s]?[)]?[\s|.|,|;|-]+', 'inhaler[(]?[s]?[)]? ', 'inh[l]?[(]?[s]?[)]?[\s|.|,|;|-]+', ' aerosol[(]?[s]?[)]? '] # puff, puffs, puff(s)   
WORD2CHANGE[' pump '] = ['pump[(]?[s]?[)]?[\s|.|,|;|-]+'] # pump, pumps, pump(s)           
WORD2CHANGE[' drop '] = ['drop[(]?[s]?[)]?[\s|.|,|;|-]+', 'gtt[(]?[s]?[)]?[\s|.|,|;|-]+'] # drop, drops, drop(s)    
WORD2CHANGE[' spray '] = ['spray[(]?[s]?[)]?[\s|.|,|;|-]+', 'spr[(]?[s]?[)]?[\s|.|,|;|-]+', 'squirt[(]?[s]?[)]?[\s|.|,|;|-]+'] # spray, sparys, spray(s)   
WORD2CHANGE[' strip '] = ['strip[(]?[s]?[)]?[\s|.|,|;|-]+'] # strip(s)
WORD2CHANGE[' scoop '] = ['scoop[(]?[s]?[)]?[\s|.|,|;|-]+'] # scoop(s)
WORD2CHANGE[' syringe '] = ['syringe[(]?[s]?[)]?[\s|.|,|;|-]+'] # syringe(s)
WORD2CHANGE[' ring '] = ['vaginal ring[(]?[s]?[)]?[\s|.|,|;|-]+', 'vag ring[(]?[s]?[)]?[\s|.|,|;|-]+', 'ring[(]?[s]?[)]?[\s|.|,|;|-]+'] # ring(s)      
WORD2CHANGE[' patch '] = ['patch[(]?[e|s]*[)]?[\s|.|,|;|-]+'] # patch(es)   
WORD2CHANGE[' packet '] = ['packet[(]?[e|s]*[)]?[\s|.|,|;|-]+'] # packet(s)
WORD2CHANGE[' \\1 unit '] = ['([0-9]+)u[n]? ']
WORD2CHANGE[' unit '] = ['unit[(]?[s]?[)]?[\s|.|,|;|-|:]+', ' u[(]?[s]?[)]?[\s|.|,|;|-]+', ' iu ', ' unis '] # unit, units, unit(s) 
WORD2CHANGE[' vial '] = ['vial[(]?[s]?[)]?[\s|.|,|;|-]+'] # vial(s)
WORD2CHANGE[' pen '] = ['pen[(]?[s]?[)]?[\s|.|,|;|-]+', 'injection[(]?[s]?[)]?[\s|.|,|;|-]+', 'solution[(]?[s]?[)]?[\s|.|,|;|-]+'] # pen(s), injection(s), solution(s)
WORD2CHANGE[' teaspoon '] = ['teaspoon[(]?[s]?[)]?[\s|.|,|;|-]+', 'tsp[(]?[s]?[)]?[\s|.|,|;|-]+'] # teaspoon(s), tsp(s)
WORD2CHANGE[' application '] = ['appliciation[(]?[s]?[)]?[\s|.|,|;|-]+', 'applicator[(]?[s]?[)]?[\s|.|,|;|-]+', 'app[l]?[(]?[s]?[)]?[\s|.|,|;|-]+'] # application(s), app(s)              
WORD2CHANGE[' ampule '] = ['amp[o]?ule[(]?[s]?[)]?[\s|.|,|;|-]+', 'ampul[(]?[s]?[)]?[\s|.|,|;|-]+'] # ampule(s), ampoule(s), ampul(s) 
WORD2CHANGE[' piece '] = ['piece[(]?[s]?[)]?[\s|.|,|;|-]+']
WORD2CHANGE[' needle '] = ['needle[(]?[s]?[)]?[\s|.|,|;|-]+']
WORD2CHANGE[' suppository '] = ['suppository[\s|.|,|;|-]+', 'suppositories[\s|.|,|;|-]+', ' supp[(]?s[)]? ']
### Time-Related Words
# Day of Week (DOW)
WORD2CHANGE[' monday '] = [' [q]?[\s]*mon[\s|.|,|;|-]+', '[q]?[\s]*monday[(]?[s]?[)]?[\s|.|,|;|-]+'] # mon, monday(s), qmonday(s)
WORD2CHANGE[' tuesday '] = [' [q]?[\s]*tue[s]?[\s|.|,|;|-]+', '[q]?[\s]*tuesday[(]?[s]?[)]?[\s|.|,|;|-]+'] # tue, tuesday(s)
WORD2CHANGE[' wednesday '] = [' [q]?[\s]*wed[\s|.|,|;|-]+', '[q]?[\s]*wednesday[(]?[s]?[)]?[\s|.|,|;|-]+'] # wed, wednesday(s)
WORD2CHANGE[' thursday '] = [' [q]?[\s]*thu[r]?[s]?[\s|.|,|;|-]+', '[q]?[\s]*thursday[(]?[s]?[)]?[\s|.|,|;|-]+'] # thu, thursday(s)
WORD2CHANGE[' friday '] = [' [q]?[\s]*fri[\s|.|,|;|-]+', '[q]?[\s]*friday[(]?[s]?[)]?[\s|.|,|;|-]+'] # fri, friday(s)
WORD2CHANGE[' saturday '] = [' [q]?[\s]*sat[\s|.|,|;|-]+', '[q]?[\s]*saturday[(]?[s]?[)]?[\s|.|,|;|-]+'] # sat, saturday(s)
WORD2CHANGE[' sunday '] = [' [q]?[\s]*sun[\s|.|,|;|-]+', '[q]?[\s]*sunday[[(]?[s]?[)]?[\s|.|,|;|-]+'] # sun, sunday(s)
# Time of Day (TOD)
WORD2CHANGE[' day in morning '] = [' day[s]?[\s]+a[.]?m[.]?[\s|.|,|;|-]+']
WORD2CHANGE[' daily in morning '] = [' daily[\s]+a[.]?m[.]?[\s|.|,|;|-]+']
WORD2CHANGE[' tablet in morning '] = [' tablet a[.]?m[.]?[\s|.|,|;|-]+']
WORD2CHANGE[' capsule in morning '] = [' capsule a[.]?m[.]?[\s|.|,|;|-]+']
WORD2CHANGE[' by mouth in morning '] = [' by mouth a[.]?m[.]?[\s|.|,|;|-]+']
WORD2CHANGE[' day in evening '] = [' day[s]?[\s]+p[.]?m[.]?[\s|.|,|;|-]+']
WORD2CHANGE[' daily in evening '] = [' daily[\s]+p[.]?m[.]?[\s|.|,|;|-]+']
WORD2CHANGE[' tablet in evening '] = [' tablet p[.]?m[.]?[\s|.|,|;|-]+']
WORD2CHANGE[' capsule in evening '] = [' capsule p[.]?m[.]?[\s|.|,|;|-]+']
WORD2CHANGE[' by mouth in evening '] = [' by mouth p[.]?m[.]?[\s|.|,|;|-]+']
WORD2CHANGE[' in moring and in evening '] = [' a[.]?m[.]? and p[.]m[.]? ']
WORD2CHANGE[' morning '] = [' morning[(]?[s]?[)]?[\s|.|,|;|-]+', ' mornng ', ' themorning ', ' morinng']
WORD2CHANGE[' in morning '] = [' q[.]?[\s]*morning[(]?[s]?[)]?[\s|.|,|;|-]+', ' q[.]?[\s]*a[.]?m[.]?[\s|.|,|;|-]+', 
                               ' in[\s]*a[.]?m[.]?[\s|.|,|;|-]+', ' in[\s]*the[\s]*a[.]*m[.]?[\s|.|,|;|-]+',
                               ' before midday ', ' every[\s]*a[.]?m[.]?[\s|.|,|;|-]+', ' first[\s]*a[.]?m[.]?[\s|.|,|;|-]+'] # morning(s), qam
WORD2CHANGE['\\1 a.m. '] = ['([0-9]+)[\s]*a[.]?m[.]?[\s|.|,|;|-]+']
WORD2CHANGE[' a.m. '] = ['[\s]+a[.]?m[.]?[\s|.|,|;|-]+', ' a..m[\s|.|,|;|-]+'] # a.m.
WORD2CHANGE[' midday '] = [' noon[(]?[s]?[)]?[\s|.|,|;|-]+', ' midday[(]?[s]?[)]?[\s|.|,|;|-]+'] # noon(s), midday(s)
WORD2CHANGE[' in midday '] = [' q[.]?[\s]*noon[(]?[s]?[)]?[\s|.|,|;|-]+', ' q[.]?[\s]*midday[\s|.|,|;|-]+']
WORD2CHANGE[' afternoon '] = [' afternoon[(]?[s]?[)]?[\s|.|,|;|-]+', ' afernoon ']
WORD2CHANGE[' in afternoon '] = [' q[.]?[\s]*afternoon[(]?[s]?[)]?[\s|.|,|;|-]+', 
                                 ' after school[\s|.|,|;|-]+', ' mid afternoon[\s|.|,|;|-]+'] # afternoon(s)
WORD2CHANGE[' evening '] = [' evening[(]?[s]?[)]?[\s|.|,|;|-]+', ' night[(]?[s]?[)]?[\s|.|,|;|-]+', ' night[t]?ime[\s|.|,|;|-]+', ' midnight[\s|.|,|;|-]+']
WORD2CHANGE[' in evening '] = [' q[.]?[\s]*evening[(]?[s]?[)]?[\s|.|,|;|-]+', ' q[.]?[\s]*night[(]?[s]?[)]?[\s|.|,|;|-]+', 
                               ' q[.]?[\s]*p[.]?m[.]?[\s|.|,|;|-]+', ' in[\s]*p[.]*m[.]?[\s|.|,|;|-]+', ' in[\s]*the[\s]*p[.]*m[.]?[\s|.|,|;|-]+',
                               ' nightly[\s|.|,|;|-]+', ' nighlty ', ' every[\s]*p[.]?m[.]?[\s|.|,|;|-]+'] # night(s), nightly, nighttime, qpm
WORD2CHANGE['\\1 p.m. '] = ['([0-9]+)[\s]*p[.]?m[.]?[\s|.|,|;|-]+']
WORD2CHANGE[' p.m. '] = ['[\s]+p[.]?m[.]?[\s|.|,|;|-]+', ' p..m '] # p.m.
WORD2CHANGE[' every \\1 \\2 '] = [' [.]?q[.]?[\s]*([0-9]+)[\s]*([a|p]{1}[.]?m[.]?)[\s|.|,|;|-]+'] # q6am    
# Special Time of Day
WORD2CHANGE[' breakfast and dinner '] = [' morning[\s]*and[\s]*evening[\s]*meal[s]?']
WORD2CHANGE[' breakfast '] = [' breakfast[(]?[s]?[)]?[\s|.|,|;|-]+', 'breakfst', 'brakfast', 'bkfst', 'breakfase', 
                              ' morning[\s]*meal[s]?[\s|.|,|;|-]+', ' the morning[\s]*meal[s]?[\s|.|,|;|-]+', ' meal in the morning ', ' a[.]?m[.]? meal[s]? '] # breakfast(s)
WORD2CHANGE[' before breakfast '] = [' a[.]?c[.]?[\s]*breakfast ', ' a[.]?c[.]?[\s]*bk ']
WORD2CHANGE[' with breakfast '] = [' w breakfast ']
WORD2CHANGE[' lunch '] = [' lunch[(]?[e|s]*[)]?[\s|.|,|;|-]+', ' [a][\s]*meal[s]? at lunch[\s]*time[\s|.|,|;]'] # lunch(es)
WORD2CHANGE[' before lunch '] = [' a[.]?c[.]?[\s]+lunch ' ]
WORD2CHANGE[' with lunch '] = [' w lunch ']
WORD2CHANGE[' dinner '] = [' dinner[(]?[s]?[)]?[\s|.|,|;|-]+', ' supper[(]?[s]?[)]?[\s|.|,|;|-]+', ' dinnertime ', ' evening[\s]*meal[s]?[\s|.|,|;|-]+', ' meal in the eveninng ', ' p[.]?m[.]? meal[s]? '] # dinner(s), supper(s)
WORD2CHANGE[' before dinner '] = [' a[.]?c[.]?[\s]+dinner ']
WORD2CHANGE[' with dinner '] = [' w dinner ']
WORD2CHANGE[' bedtime '] = [' bed[(]?[s]?[)]?[\s|.|,|;|-]+', ' bedtime[\w]*[\s|.|,|;|-]+', ' bed[\s]*time[(]?[s]?[)]?[\s|.|,|;|-]+', ' beditime ']
WORD2CHANGE[' at bedtime '] = [' at h[.]?s[.]?[\s|,|;|-]+', ' [.]?q[.]?[-|\s]*h[.]?s[.]?[\s|,|;|-]+', ' h[.]?s[.]?[\s|,|;|-]+', ' q[\s]*bedtime[\s|.|,|;|-]+'] # bed(s), bedtime(s), bed time(s), h.s., qbedtime 
WORD2CHANGE[' before bedtime '] = [' before[\s]+bedtime '] 
WORD2CHANGE[' meal '] = [' [a]?[\s]*meal[(]?[s]*[)]?[\s|.|,|;|-]+', ' mieal '] # meal(s)
WORD2CHANGE[' before meal '] = [' q[.]?a[.]?c[.]? ', ' a[.]?c[.]? ', ' before every meal ', ' before each meal ', ' pre[-|\s]?meal[s]? ']
WORD2CHANGE[' with meal '] = [' w meal ', ' withmeal[s]? ', ' with every meal ', ' with each meal ']
WORD2CHANGE[' after meal '] = [' p[.]?c[.]? ', ' after every meal ', ' after each meal ']
WORD2CHANGE[' before food '] = [' before eating food ']
WORD2CHANGE[' with food '] = [' w food ']
WORD2CHANGE[' shortness of breath '] = [' s[.]?o[.]?b[.]?[\s|.|,|;]+']
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
WORD2CHANGE[' \\1 minute '] = [' ([0-9]+)min[(]?[s]?[)]?[\s|.|,|;]+', ' ([0-9]+)minute[(]?[s]?[)]?[\s|.|,|;]+']
WORD2CHANGE[' minute '] = [' minute[(]?[s]?[)]?[\s|.|,|;]+', ' min[(]?[s]?[)]?[\s|.|,|;]+']
WORD2CHANGE[' hour '] = ['hour[.|,|;]+', 'hr[\s|.|,|;]+', 'hrs[\s|.|,|;]+', 'hurs[\s|.|,|;]+']
WORD2CHANGE['day '] = ['day[.|,|;]+']
WORD2CHANGE[' week '] = ['week[.|,|;]+', 'wk[\s|.|,|;|(]+', 'wks[\s|.|,|;|(]+ ']
WORD2CHANGE[' month '] = ['month[.|,|;|-]+']
WORD2CHANGE[' hourly '] = [' a[\s]*hour ', ' each[\s]*hour[\s|.|,|;]+', ' every[\s]*hour[\s|.|,|;]+', ' per[\s]*hour[\s|.|,|;]+', 
                           '/[\s]*hour[\s|.|,|;]+', '/[\s]*hr[\s|.|,|;|-]+', '/[\s]*h[\s|.|,|;]+']
WORD2CHANGE[' every \\1 hours '] = [' [.]?q[.]?[\s]*([0-9]+)[\s|-]*[h]?[o]?[u]?[r]?[(]?[s]?[)]?[\s|.|,|;]+', ' every[\s]+([0-9]+)[\s]+hour[s]?[\s]+daily'] # q12hour(s)    
WORD2CHANGE[' every \\1 to \\2 hours '] = [' [.]?q[.]?[\s]*([0-9]+)[\s]*to[\s]*([0-9]+)[\s]*h[o]?[u]?[r]?[(]?[s]?[)]?[\s|.|,|;|-]+', 
                                           ' [.]?q[.]?[\s]*([0-9]+)[\s]*-[\s]*([0-9]+)[\s]*h[o]?[u]?[r]?[(]?[s]?[)]?[\s|.|,|;|-]+',
                                           ' every ([0-9]+)[\s]*h[o]?[u]?[r]?[(]?[s]?[)]?[\s]*-[\s]*([0-9]+)[\s]*h[o]?[u]?[r]?[(]?[s]?[)]? ',
                                           ' every ([0-9]+)[\s]*h[o]?[u]?[r]?[(]?[s]?[)]?[\s]*to[\s]*([0-9]+)[\s]*h[o]?[u]?[r]?[(]?[s]?[)]? '] # q1 to 2 h          
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
AT_LIST = ['at','in','on','before','after','during','with','without']
TIME_LIST = ['minute','hour','day','week','month']
TIMELY_LIST = ['hourly', 'daily', 'weekly', 'monthly']
DOW_LIST =['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
TOD_LIST = ['morning','a.m.','breakfast',
            'midday','lunch',
            'afternoon','p.m.',
            'evening', 'dinner','bedtime'] # time of day
UNIT_LIST = ['tablet', 'capsule', 'pill', 'puff', 'pump', 'drop', 'spray', 'strip', 'scoop', 'needle', 
             'ring', 'patch', 'packet', 'unit', 'ampule', 'syringe', 'vial', 'pen', 'piece', 'suppository',
             'teaspoon', 'application',
             'gr', 'mg', 'mcg', 'ml', 'meq']
PERI_LIST = ['breakfast','lunch','dinner','meal','food','snack','milk',
             'morning', 'midday','afternoon','evening','bedtime']
             #'neuropathy', 'subcutaneous', 'intramuscular', 'stomach']
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
dp['215'] = [{'LEMMA':'take'}] + NUM + [{'LOWER':{'IN':['as','if']},'OP':'?'},{'LEMMA':{'IN':['direct','necessary','need']}}] # take 1 as needed
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
pp['110'] = [{'LOWER':'empty'},{'LOWER':'stomach'}] # empty stomach
pp['111'] = [{'LOWER':{'IN':['neuropathy', 'subcutaneous', 'intramuscular']}}] # route information
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
        # hours
        for t in ['hour', 'hours']: # every 4 hours
            if t in f and '24' not in f:
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
                if int(t[:2]) == 12 and int(t[2:]) > 0: # 12XX
                    info.add(t[:2]+':'+t[2:]+' p.m.')
                elif int(t[:2]) > 12 and int(t[2:]) > 0:# 13XX
                    info.add(str(int(t[:2])-12)+':'+t[2:]+' p.m.')
                elif int(t[:2]) > 12 and int(t[2:]) == 0: # 1300
                    info.add(str(int(t[:2])-12)+':00 p.m.')
                else: # 1200 
                    info.add(t[:2]+':00 p.m.')
                if int(t[:2]) == 12 and int(t[2:]) == 0:
                    noon =1
                else:
                    afternoon = 1
            else:
                if int(t[2:]) > 0:
                    if int(t[:2]) >= 10:
                        info.add(t[:2]+':'+t[2:]+' a.m.')
                    else:
                        info.add(t[1:2]+':'+t[2:]+' a.m.')
                else:
                    if int(t[:2]) >= 10:
                        info.add(t[:2]+':00 a.m.')
                    else:
                        info.add(t[1:2]+':00 a.m.')
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
        for d in DOW_LIST:
            if d in f:
                dow[d] = 1
        for t in ['every 24 hours', 'every 24 hour', 
                  'every day', 'every 1 day','everyday', 'each day', ' day', ' days', 'daily']:
            if t in f and 'weekly' not in f and 'time' not in f:
                daily = max(1, daily) 
        for t in ['every 7 days', 'every 7 day', 
                  'every week', 'every 1 week','everyweek', 'each week', 'week', 'weeks', 'weekly']:
            if t in f:
                daily = 0
                weekly = max(1, weekly)        
        for d in [1,2,3,4,5,6]:
            for t in [str(d)+' time daily', str(d)+' times daily', str(d)+' time day', str(d)+' times day']:
                if t == f:
                    daily = max(d, daily)        
        for t in ['every 2 days','every 2 day','every other day']:
            if t in f:
                daily = 0
                info.add('every 2 days')             
        for d in [1,2,3,4,5,6,7]:
            for t in [str(d)+' time weekly', str(d)+' times weekly', str(d)+' day weekly', str(d)+' days weekly',
                      str(d)+' time week', str(d)+' times week', str(d)+' day week', str(d)+' days week']:
                if t == f:
                    daily = 0
                    weekly = max(d, weekly)
        for t in ['every 14 days', 'every 14 day', 'every 2 weeks', 'every 2 week', 'every other week']:
            if t in f:
                daily = 0
                weekly = 0
                info.add('every 2 weeks')        
        for t in ['every 28 days', 'every 28 day', 'every 4 weeks', 'every 4 week']:
            if t in f:
                daily = 0
                weekly = 0
                info.add('every 4 weeks') 
        for d in [3,4,5,6,8,9,10]:
            for t in ['every '+str(d)+' day', 'every '+str(d)+' days']:
                if t in f:
                    daily = 0
                    info.add('every '+str(d)+' days')
    daily = max(daily, morning + noon + max(afternoon,evening)) # use max(afternoon and evening) 12/20/2020
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
    if len(info) == 0: # if no tablet informaiton is found, then use strength information
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
        for i in ['at','with']:
            for j in ['breakfast','lunch','dinner','meal','food','snack','milk']:
                if i + ' ' + j in p:
                    info.add(j)
                    find = True
                for k in ['breakfast', 'lunch', 'dinner']:
                    if j + ' and ' + k in p and 'before' not in p and 'after' not in p:
                        info.add(j)
                        info.add(k)
                        find = True
        for i in ['in','at']:
            for j in ['morning','midday','afternoon','evening']:
                if i + ' ' + j in p:
                    info.add(j)
                    find = True
                for k in ['morning','midday','afternoon','evening']:
                    if j + ' and ' + k in p:
                        info.add(j)
                        info.add(k)      
                        find = True
        for i in ['at', 'before']:
            if i + ' bedtime' == p:
                info.add('bedtime')
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
    if len(DATA) == 0:
        return pd.DataFrame(columns=['DOCUPACK_URL','CURRENT_QUEUE','ID','PRESCRIPTION_ID','MEDICATION_DESCRIPTION',\
                                     'ESCRIBE_DIRECTIONS','SIG_TEXT','LINE_NUMBER','TOTAL_LINE_COUNT','ESCRIBE_QUANTITY','ESCRIBE_NOTES',\
                                     TYPE+'_DIRECTIONS',TYPE+'_SIG_TEXT','NEW_'+TYPE+'_DIRECTIONS','NEW_'+TYPE+'_SIG_TEXT',TYPE+'_CHANGE'])
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
                 'ESCRIBE_DIRECTIONS','SIG_TEXT','LINE_NUMBER','TOTAL_LINE_COUNT','ESCRIBE_QUANTITY','ESCRIBE_NOTES',\
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

def _RISK_QUERY(TIME_INTERVAL):
    RISK_QUERY = """SELECT id,
                       prescription_id,
                       medication_description,
                       predicted_risk
                FROM analytics_core.drug_dir_pv1_rx_risk
                WHERE sf_updated_at >= CURRENT_TIMESTAMP() - interval '{0}'""".format(TIME_INTERVAL)
    return RISK_QUERY           
                
def _DIRECTION_QUERY(TIME_INTERVAL):
    DIRECTION_QUERY = """SELECT  ('https://admin.pillpack.com/admin/docupack/#/' || docs.id) docupack_url,
                     docs.queue current_queue,
                     doc_pres.id id,
                     sig.prescription_id,
                     sig.id sig_id,
                     sig.line_number,
                     sig.text sig_text,
                     esc.message_json:MedicationPrescribed.SigText::string ESCRIBE_DIRECTIONS,  -- Updated 2020-10-15 due to new doucpack_escribes table
                     esc.message_json:MedicationPrescribed.Quantity.Value ESCRIBE_QUANTITY,     -- Updated 2020-10-15 due to new doucpack_escribes table
                     esc.message_json:MedicationPrescribed.Note::string ESCRIBE_NOTES,           -- Updated 2020-10-15 due to new doucpack_escribes table
                     esc.message_json:MedicationPrescribed.NDC NDC,                             -- Updated 2020-10-15 due to new doucpack_escribes table
                     sig.quantity_per_dose,
                     sig.units,
                     sig.hoa_times,
                     sig.quantity_per_day,
                     sig.schedule_type,
                     sig.period,
                     sig.dow,
                     doc_pres.med_name medication_description,
                     CURRENT_TIMESTAMP() current_time
                     FROM source_pillpack_core.docupack_prescriptions doc_pres
                     LEFT JOIN source_pillpack_core.docupack_documents docs ON doc_pres.document_id = docs.id
                     LEFT JOIN source_pillpack_core.prescriptions pres ON doc_pres.app_prescription_id = pres.id
                     LEFT JOIN source_pillpack_core.sig_lines sig ON doc_pres.app_prescription_id = sig.prescription_id
                     LEFT JOIN source_pillpack_core.docupack_escribes esc ON esc.id= doc_pres.INBOUND_ESCRIBE_ID          -- Updated 2020-10-15 due to new doucpack_escribes table
                     WHERE pres.created_at >= CURRENT_TIMESTAMP() - interval '{0}' -- Use for prediction. Intentionally 0.5 minute is added in case the code runs with some delays, we do not want to miss any prescription
                     AND pres.created_at < CURRENT_TIMESTAMP()
                     AND sig.id IS NOT NULL
                     AND pres.rx_number IS NOT NULL
                     AND doc_pres.self_prescribed = false
                     AND docs.source = 'Escribe'
                     AND ESCRIBE_DIRECTIONS is NOT NULL""".format(TIME_INTERVAL)
    return DIRECTION_QUERY
###############################################################################

###############################################################################
# Send email from SES that the job failed to run
import boto3
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

EMAIL_LIST = ['jeff.liu@pillpack.com'] #, 'cetinkay@amazon.com', 'mohsen.bayati@pillpack.com', 'ipshita.jain@pillpack.com', 'olivia@pillpack.com', 'colin.hayward@pillpack.com']

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
def main(TIME_INTERVAL):
    # Path and Filename
    PATH = os.path.abspath(os.getcwd())#+'/Data/'
    TIME = pd.to_datetime('now').isoformat() # nearly real-time
    TIME = TIME[:13]+TIME[14:16]
    OUTPUT = '/NRT_Results/nrt_results_'+TIME+'.csv'    

    print('******************************')
    print('Running SQL to pull predicted risk from Snowflake...') 
    risk = _SQL(_RISK_QUERY(TIME_INTERVAL))
    risk.columns = risk.columns.str.upper()
    print('Running SQL to pull directions from Snowflake...') 
    data = _SQL(_DIRECTION_QUERY(TIME_INTERVAL))                      
    ### Handeling Empty Data
    if len(data) == 0:
        return 0
    data.columns = data.columns.str.upper()
    data = data.drop_duplicates()  # remove duplicated records   
    data['TOTAL_LINE_COUNT'] = data.groupby('ID')['LINE_NUMBER'].transform('count') # total sigline count
    data = data.sort_values(by=['ID','LINE_NUMBER'], ascending=[True,True], na_position='last')
    data.to_csv(PATH+'/NRT_Results/snapshots_'+TIME+'.csv', index=False)
    data['SIG_TEXT'] = data.groupby(['ID'])['SIG_TEXT'].transform(lambda x: ' '.join(x)) # combine sig_text in multi-line prescriptions, 10/09/2020
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
    ### Handeling Empty Data
    if len(data) == 0:
        return 0
    ### Step 2 and 3. Direction Change Detection
    results = pd.DataFrame()
    for TYPE in ['DOSE','FREQUENCY','PERIPHERAL']: 
        result = _DETECTION(data.loc[:], TYPE, medications).copy()
        if len(results) == 0:
            results =  result.copy()
        else:
            results = results.merge(result, on=['DOCUPACK_URL','CURRENT_QUEUE','ID','PRESCRIPTION_ID','MEDICATION_DESCRIPTION',\
                                                'ESCRIBE_DIRECTIONS','SIG_TEXT','LINE_NUMBER','TOTAL_LINE_COUNT','ESCRIBE_QUANTITY','ESCRIBE_NOTES'], how='outer')
    ### Save and Return
    results = results.merge(medications, on=['MEDICATION_DESCRIPTION'], how='left')
    results = results.merge(risk, on=['ID','PRESCRIPTION_ID','MEDICATION_DESCRIPTION'], how='left')
    results = results.sort_values(by=['TOTAL_LINE_COUNT','CURRENT_QUEUE','PREDICTED_RISK'], ascending=[True,True,False], na_position='last') # sort by predicated risk from higher to lower and put NAs last
    # Remove Lines with 'pen needle' in ESCRIBE_DIRECTIONS and 'topical' in SIG_TEXT while only missing does information, this is requested by Colin on 09/18/2020 to reduce false positives
    results = results[~((results.ESCRIBE_DIRECTIONS.str.contains(pat='pen needle',case=False))&(results.DOSE_CHANGE==False)&(results.FREQUENCY_CHANGE.isnull())&(results.PERIPHERAL_CHANGE.isnull()))]
    results = results[~((results.SIG_TEXT.str.contains(pat='topical',case=False))&(results.DOSE_CHANGE==False)&(results.FREQUENCY_CHANGE.isnull())&(results.PERIPHERAL_CHANGE.isnull()))]
    # Save as a Local File
    results.to_csv(PATH+OUTPUT, index=False)
#    email = EmailClient()
#    email.send_email(EMAIL_LIST,
#       'Direction Changes ' + TIME,
#       'Hey team, <br><br>\
#       Attached please find the direction changes on {0}. If you have any questions please contact Jeff Liu: jeff.liu@pillpack.com. <br><br> \
#       Key Columns: <br> \
#       DOCUPACK_URL: link to document <br> \
#       CURRENT_QUEUE: Archive, ExistingPatients <br> \
#       ID: docupack prescriptions id <br> \
#       PRESCRIPTION_ID <br> \
#       MEDICATION_DESCRIPTION <br> \
#       ESCRIBE_DIRECTIONS <br> \
#       SIG_TEXT <br> \
#       LINE_NUMBER: sigline number <br> \
#       TOTAL_LINE_COUNT: total number of siglines; if a prescription has more than one siglines, it is likely to be detected since information is saved in different siglines <br> \
#       ESCRIBE_QUANTITY <br> \
#       ESCRIBE_NOTES <br> \
#       DOSE_CHANGE: if Ture, there are changes; if False, dose info is missing <br> \
#       FREQUENCY_CHANGE: if Ture, there are changes; if False, frequency info is missing <br> \
#       PERIPHERAL_CHANGE: if Ture, there are changes <br> \
#       PREDICTED_RISK: risk of direction changes from ML model, high value means high risk <br><br>\
#       Best, <br>data_science_bot'.format(TIME),
#       PATH+OUTPUT)
    return results

if __name__ == "__main__":
    TIME_INTERVAL = str(' '.join(sys.argv[1:]))
    results = main(TIME_INTERVAL)
    
    
## Post-processing: NRT results
#import os
#import pandas as pd
#PATH = os.path.abspath(os.getcwd())+'/Results/NRT_Results_012203082021/'
#s_list = [] # snapshot list
#r_list = [] # result list
#for d in ['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15',
#          '16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31']:
#    for h in ['00','01','02','03','04','05','06','07','08','09',\
#              '10','11','12','13','14','15','16','17','18','19',\
#              '20','21','22','23']:
#        for m in ['00','30']:
#            for mn in ['01','02','03']:
#                try:
#                    s = pd.read_csv(PATH+'snapshots_2021-'+mn+'-'+d+'T'+h+m+'.csv')
#                    r = pd.read_csv(PATH+'nrt_results_2021-'+mn+'-'+d+'T'+h+m+'.csv')
#                except:
#                    continue
#                s['TIME'] = '2021-'+mn+'-'+d+' '+h+':'+m+':00'
#                r['TIME'] = '2021-'+mn+'-'+d+' '+h+':'+m+':00'
#                s_list.append(s)
#                r_list.append(r)
#s = pd.concat(s_list, axis=0, ignore_index=True)[['CURRENT_QUEUE','ID','PRESCRIPTION_ID','LINE_NUMBER','ESCRIBE_DIRECTIONS','SIG_TEXT','TIME']]
#s = s.sort_values('TIME').drop_duplicates(['CURRENT_QUEUE','ID','PRESCRIPTION_ID','LINE_NUMBER','ESCRIBE_DIRECTIONS'], keep='first')
#s = s.rename(columns={'TIME':'FIRST_OBSERVED_AT'})
#r = pd.concat(r_list, axis=0, ignore_index=True).drop_duplicates()#.fillna(0)
#r = r.sort_values('TIME').drop_duplicates(['CURRENT_QUEUE','ID','PRESCRIPTION_ID','LINE_NUMBER','ESCRIBE_DIRECTIONS'], keep='first')
#r = r.rename(columns={'TIME':'FIRST_CAPTURED_AT'})
#x = pd.merge(s,r, on=list(s.columns)[:-1], how='left').drop_duplicates().rename(columns={'SIG_TEXT':'ORIGINAL_SIG_TEXT'})
## Read NME Results
#k = pd.read_csv(PATH+'KPI_NRT.csv')#[['ID','PRESCRIPTION_ID','LINE_NUMBER','SIG_TEXT']]
#k['CREATED_AT'] = k['CREATED_AT'].str[:19]
#k['FIRST_ENTERED_RPH_AT'] = k['FIRST_ENTERED_RPH_AT'].str[:19]
#k['FIRST_RETURNED_TO_DE_AT'] = k['FIRST_RETURNED_TO_DE_AT'].str[:19]
## Merge Results
#x = pd.merge(x,k,on=['ID','PRESCRIPTION_ID','LINE_NUMBER'], how='left').drop_duplicates().rename(columns={'SIG_TEXT':'NEW_SIG_TEXT'})
#x['CAPTURED'] = pd.notna(x['FIRST_CAPTURED_AT'])
#x['EXCLUDE'] = (x['FIRST_OBSERVED_AT'] >= x['FIRST_RETURNED_TO_DE_AT']) | pd.isna(x['CREATED_AT'])
#x['EXCLUDE'] = x['EXCLUDE'] | (x['CREATED_AT'] > x['FIRST_ENTERED_RPH_AT'])
#x.to_csv(PATH+'all_cases.csv', index=False)

#x['NME'] = pd.notna(x['CLASS1_WRONG_DIRECTIONS'])
#print('Total Cases: ', len(x[['ID','PRESCRIPTION_ID']].drop_duplicates()))
#print('Total NMEs: ', len(x[x.NME==True][['ID','PRESCRIPTION_ID']].drop_duplicates()))
#print('Total Direction NMEs: ', len(x[x.CLASS1_WRONG_DIRECTIONS==1][['ID','PRESCRIPTION_ID']].drop_duplicates()))
#print('Total Captured: ', len(x[x.CAPTURE==True][['ID','PRESCRIPTION_ID']].drop_duplicates()))
#print('Total NMEs and Captured: ', len(x[(x.NME==True)&(x.CAPTURE==True)][['ID','PRESCRIPTION_ID']].drop_duplicates()))
#print('Total Direction NMEs and Captured: ', len(x[(x.CLASS1_WRONG_DIRECTIONS==1)&(x.CAPTURE==True)][['ID','PRESCRIPTION_ID']].drop_duplicates()))
