f=open("ibm1.al","rb")
g=open("ibm1_c.al","wb")
for line in f:
	als=line.split()

	als=[s.split("-")[1]+"-"+s.split("-")[0] for s in als]
	g.write(" ".join(als)+"\n")
