import time, subprocess, shlex, os
from multiprocessing import Process, Queue
import matplotlib.pyplot as plt
import seaborn as sb
import numpy as np

imageCount = 0

def readFromFile(width = 8, pixelPerHex = 2):
	def normalization(strList):
		strList = [int(i,16) for i in strList]
		return strList
	mid = []
	result = []
	f = open("/home/smile/Desktop/readData.txt",'r')
	ctx = f.readline()
	f.close()
	while( len(ctx) < 5 ): #some value, fail to read correctly
		print("\n", "RETRY","\n")
		f = open("/home/smile/Desktop/readData.txt",'r')
		ctx = f.readline()
		f.close()

	if(len(ctx)%pixelPerHex):
		raise Exception("data / pixelPerHex is not 0")
	for i in range(int(len(ctx)/pixelPerHex)):
		mid.append(ctx[i*pixelPerHex: (i+1)*pixelPerHex])
	mid = normalization(mid)
	if(len(mid)%width):
		raise Exception("data / width is not 0")
	for i in range(int(len(mid)/width)):
		result.append(mid[i*width:(i+1)*width])
	return result

def drawGrid(q):
	global imageCount
	imageCount+=1
	def refreshGrid(ax, q):
		global imageCount
		imageCount+=1
		if(not q.empty() and q.get()=="END"):
			exit()
		data = np.array(readFromFile())
		ax.cla()
		ax = sb.heatmap(data, vmin=0, vmax=255,cbar=False, linewidths=0.3, annot=True, fmt="d", cmap = "jet")
		print("refresh")
		plt.pause(0.01)

	data = np.array(readFromFile())
	fig, ax = plt.subplots(figsize=(12,12))
	ax = sb.heatmap(data, vmin=0, vmax=255, linewidths=0.3, annot=True, fmt="d", cmap = "jet")

	# draw gridlines
	plt.show(block = False)
	plt.pause(0.01)
	while(True):
		refreshGrid(ax, q)

def callSllurp(turnOnTime=5, mask=None):
	cmd = 'sllurp access -P 3 -r 32 -mb 3 -wp 48 '
	if mask:
		cmd += "--tag-filter-mask "
		cmd += str(mask)
	cmd += ' 192.168.0.2'
	FNULL = open(os.devnull, 'w')
	subprocess.call(shlex.split(cmd),stdout=FNULL, stderr=subprocess.STDOUT, timeout=turnOnTime)
	FNULL.close()


if __name__ == "__main__":
	turnOnTime = 5
	q = Queue()
	th1 = Process(target=callSllurp, args=(turnOnTime,)) #"e200001974080066"
	th1.start()
	th2 = Process(target=drawGrid, args=(q,))
	th2.start()
	th1.join()
	q.put("END")
	th2.join()
	cmd = 'sllurp reset 192.168.0.2'
	subprocess.call(shlex.split(cmd))
	print(f'\n{imageCount}\n')