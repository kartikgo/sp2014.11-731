import sys
import optparse
from collections import defaultdict
import nltk
optparser = optparse.OptionParser()
optparser.add_option("-r","--reference", dest="ref", default= "data/dev.ref",help="reference set")
optparser.add_option("-k", "--kbest-list", dest="input", default="data/dev.100best", help="100-best translation lists")
optparser.add_option("-s","--source",dest="source",default="data/dev.src",help="Russian source file")
(opts, _) = optparser.parse_args()
all_hyps = [pair.split(' ||| ') for pair in open(opts.input)]
for k in all_hyps:
	num=''
	sent=''
	feats=''
	if (len(k)==3):
		num,sent,feats = k
	else:
		sent=k[0]
	text = nltk.word_tokenize(sent.strip())
	print " ".join(k[1] for k in nltk.pos_tag(text))
