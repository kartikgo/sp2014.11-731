#!/usr/bin/env python
import argparse
import sys
import models
import heapq
from collections import namedtuple
from collections import defaultdict
from itertools import product
from collections import Counter
import cPickle
parser = argparse.ArgumentParser(description='Simple phrase based decoder.')
parser.add_argument('-i', '--input', dest='input', default='data/input', help='File containing sentences to translate (default=data/input)')
parser.add_argument('-t', '--translation-model', dest='tm', default='data/tm', help='File containing translation model (default=data/tm)')
parser.add_argument('-s', '--stack-size', dest='s', default=1, type=int, help='Maximum stack size (default=1)')
parser.add_argument('-n', '--num_sentences', dest='num_sents', default=sys.maxint, type=int, help='Number of sentences to decode (default=no limit)')
parser.add_argument('-l', '--language-model', dest='lm', default='data/lm', help='File containing ARPA-format language model (default=data/lm)')
parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', default=False,  help='Verbose mode (default=off)')
opts = parser.parse_args()

tm = models.TM(opts.tm, sys.maxint)
lm = models.LM(opts.lm)
sys.stderr.write('Reading %s...\n' % (opts.input,))
input_sents = [tuple(line.strip().split()) for line in open(opts.input).readlines()[:opts.num_sents]]
#TODO: Find the disagreements!!
hypothesis = namedtuple('hypothesis', 'logprob, lm_state, predecessor, phrase, spanish')
def findallsub(sent):
	eng_phrases=[]
	translatables=defaultdict(list)
	for length in range(len(sent)):
		for i in range(len(sent)-length):
			subsect = sent[i:i+length+1]
			if subsect in tm:
				translatables[length+1].append(subsect)
	return translatables

def extract_english_recursive(h):
	return '' if h.predecessor is None else '%s%s ' % (extract_english_recursive(h.predecessor), h.phrase)#.english)
def extract_spanish_recursive(h):
	return '' if h.predecessor is None else '%s%s ' % (extract_spanish_recursive(h.predecessor), h.spanish)
def fillchart(n,k,h,chart,transtables,tot,marker,local_tm,text):
	if (h.spanish== None):
		r =0
	else:
		r= indexfind(h.spanish,text)+len(h.spanish.split())
	for spw in translatables[k]:
		#for phrase in tm[spw]:
		#	logprob = h.logprob + phrase.logprob
		esp = " ".join(spw)
		dist = abs(indexfind(esp,text)+1-r)
		#if (len(esp.split())==1):
		#	d=idx+1
		#elif (len(esp.split())==2):
		#	d=idx+2
		#else:
		#	d= idx+3
		penalty=0.0
		#if not(dist > len(text)/4):
		#	penalty= 0.0
		#elif not(dist > len(text)/2):
		#	penalty = -2.0
		#else:
		#	penalty= -4.0
		for phrase in local_tm[spw]:
			logprob = penalty +h.logprob + local_tm[spw][phrase]
			lm_state= h.lm_state
			#for word in phrase.english.split():
			for word in phrase.split():
				(lm_state,word_lp)= lm.score(lm_state,word)
				logprob += word_lp
			if ((n+k) == tot):
				(lm_state,word_lp)= lm.score(lm_state,marker)
				logprob += word_lp
				logprob += lm.end(lm_state)
			else: 
				logprob += 0.0
			new_hypothesis = hypothesis(logprob, lm_state, h, phrase,esp)
			if lm_state not in chart[n+k] or chart[n+k][lm_state].logprob < logprob: # second case is recombination
				chart[n+k][lm_state] = new_hypothesis
	return chart
#for sent in input_sents:
def findmax(sent,local_tm,marker):
	#marker= sent[-1]
	#sent = sent[:-1]
	text = " ".join(sent)
	initial_hypothesis = hypothesis(0.0, lm.begin(), None, None,None)
	#chart represents states for each length of source. Goal= chart[len(sent)][(lm_state,len(sent))] != initial_hypothesis
	chart = [{} for _ in sent] + [{}]
	chart[0][lm.begin()] = initial_hypothesis
	tot=len(sent)
	for k in translatables:
		#sys.stderr.write("starting from 0....")
		chart = fillchart(0,k,initial_hypothesis,chart,translatables,tot,marker,local_tm,text)

	for i in range(1,len(sent)):
		sys.stderr.write(str(i)+"....")
		for lm_state in chart[i]:
			for k in translatables:
				if not((i+k) > len(sent)):
					chart1 = fillchart(i,k,chart[i][lm_state],chart,translatables,tot,marker,local_tm,text)
	sys.stderr.write("\n")
	winner = sorted(chart[tot].itervalues(), key=lambda h: h.logprob)
	#print winner[-1]
	sys.stderr.write(extract_english_recursive(winner[-1])+marker+"\n")
	#print extract_spanish_recursive(winner[-1])+marker
	return winner[-1]

def indexfind(esp,espa):
	sub = espa.find(esp+" ")
	if (sub== -1):
		sub = espa.find(esp)
	return len(espa[:sub].split())
storage=[]
for sent in input_sents:
	marker= sent[-1]
	sent= sent[:-1]
	text = " ".join(sent)
	translatables= findallsub(sent)
	# This is a way to modify the translation probabilities
	local_tm = defaultdict(lambda: defaultdict(float))
	indexdict={}
	for k in translatables:
		for spw in translatables[k]:
			for phr in tm[spw]:
				local_tm[spw][phr.english]= phr.logprob
	#lag_mults_prev = [0.0 for _ in sent]
	lag_mults = [0.0 for _ in sent]
	step= 1.0
	dualflip= 0
	dual_prev= 0
	iterations=1
	to_add=[]
	while (1):
		sys.stderr.write("-------------------Iteration "+str(iterations)+"-------------------\n")
		winner = findmax(sent,local_tm,marker)
		dual = winner.logprob
		if not((dual_prev- dual)>0):
			sys.stderr.write("FLIPPED! FLIPPED! FLIPPED!\n")
			dualflip += 1
		alpha = step*1.0/(dualflip+1)
		if ((not(abs(dual-dual_prev)>0.0001))or(iterations>60)):
			if (not(abs(dual-dual_prev)>0.0001)):	
				print extract_english_recursive(winner)+marker
				f= open(opts.input+"final","wb")
				#to_add = (dict(local_tm),winner,count)
				push = sorted(to_add,key= lambda x: x[3],reverse=True)
				cPickle.dump(push,f)
				f.close()
			break
		dual_prev = dual
		sys.stderr.write("The Dual is:"+str(dual)+"\n")
		esp=[]
		eng=[]
		pred = winner
		while not(pred.spanish == None):
			esp.append(pred.spanish)
			eng.append(pred.phrase)
			pred = pred.predecessor
		print esp
		print eng
		#print text
		y=[]
		for spa in esp:
			idx = indexfind(spa,text)
			if (len(spa.split())==1):
				y.append(idx)
			elif (len(spa.split())==2):
				y.extend([idx,idx+1])
			else:
				y.extend([idx,idx+1,idx+2])
		#print y
		y= Counter(y)
		#print y
		count = [0.0]*len(sent)
		for k in y:
			count[k]=y[k]
		sys.stderr.write(str(count)+"\n")
		if (iterations % 6 ==0):
			push = max(to_add,key= lambda x: x[3])
			#print push[2],push[3]
			to_put = push[4]
			#print push[4]
			f= open(opts.input+"iter"+str(to_put),"wb")
			#to_add = (dict(local_tm),winner,count)
			cPickle.dump(push,f)
			f.close()
		#if (count== [1]*len(sent)):
		#	break
		#else:
		ones = Counter(count)[1]
		to_add.append((dict(local_tm),winner,count,ones,iterations))
		tmp=[0.0 for _ in sent]
		for i,(prev,yval) in enumerate(zip(lag_mults,count)):
			tmp[i] = prev - alpha*(yval-1)
		#print tmp
		for es,en in zip(esp,eng):
			ind = indexfind(es,text)
			es = tuple(es.split())
			for i,e in enumerate(es):
				#print "es: "+str(es)+" en: "+ str(en)+" "+str(local_tm[es][en])
				#for k in local_tm[es]:
				local_tm[es][en] += tmp[ind+i] - lag_mults[ind+i]
		lag_mults = tmp
		iterations += 1
				#print "es: "+str(es)+" en: "+ str(en)+" "+str(local_tm[es][en])
