import sys

def intersect(f2e, e2f):
	#return f2e.intersection(set([(v, k) for (k, v) in e2f]))
	return f2e.intersection(e2f)

def union(f2e, e2f):
	#return f2e.union(set([(v, k) for (k, v) in e2f]))
	return f2e.union(e2f)

def growDiag(f2e,e2f):
	common= list(intersect(f2e,e2f))
	combined= list(union(f2e,e2f))
	done=[]
	while set(done) != set(common):
		done=common
		cand=[]
		for (i,j) in done:
			neighbors=list(set([(i-1,j),(i-1,j-1),(i-1,j+1),(i+1,j),(i+1,j+1),(i+1,j-1),(i,j-1),(i,j+1)]).difference(set(common)))
		#cand1=[]
			for (i,j) in neighbors:
				if (i,j) in combined:
					if ((len(filter(lambda x:x[0]==i,done))==0) or (len(filter(lambda x: x[1]==j,done))==0)):
						common.append((i,j))
		#print len(cand),len(cand1)
		#cand=list(intersect(set(cand),set(combined)))
		#common.extend(cand)
	return set(common)

def makeset(fileh):
	alignments = {}
	for ind, line in enumerate(fileh):
		aligns = line.strip().split(" ")
		sentaligns = set()
		for algn in aligns:
			if algn == "":
				continue
			s, t = algn.split("-")
			sentaligns.add((int(s), int(t)))
		alignments[ind] = sentaligns
	return alignments


f2efile = open(sys.argv[1])
e2ffile = open(sys.argv[2])
outfile = open(sys.argv[3], "w")
f2esets = makeset(f2efile)
e2fsets = makeset(e2ffile)

for ctr in range(len(f2esets)):
	symm = growDiag(f2esets[ctr], e2fsets[ctr])
	towrite = []
	for (i, j) in symm:
		towrite.append("%d-%d"%(i, j))
	print >>outfile, " ".join(towrite)


