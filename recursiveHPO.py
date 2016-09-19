import sys
import re
import getopt

SEP = re.compile('\n\[Term\]')

def usage():
	usageLine = '''\
Usage:
	-h: Print this help message
	-i: [Required] HPO file in obo format
	-o: [Required] Output file
	-A: [Optional] [Y | N] include alternative HPO IDs, default 'N'
	'''
	print usageLine

def recursive_hpo(inputID, termDict, IDList, fwrite, allRecord):
  '''
  Print and return each parent-child relation of HPO
  '''
	try:
		nextInputID = termDict[inputID]
	except KeyError:
		IDs = '-'.join(IDList)
		outputLine = '%s-%s\n' % (IDs, inputID)
		fwrite(outputLine)
		outputLine = outputLine.strip()
		allRecord.append(outputLine)
		
	else:
		IDList.append(inputID)
		IDs = '-'.join(IDList)
		outputLine = '%s\n' % IDs
		fwrite(outputLine)
		outputLine = outputLine.strip()
		allRecord.append(outputLine)

		for i in nextInputID:
			inputID = i
			recursive_hpo(inputID, termDict, IDList, fwrite, allRecord)
			IDList = [IDs]
	return allRecord

def alt_id(altDict, allIDs, fwrite):
	for k, v in altDict.items(): # id -> alt_ids
		if v:
			for i in allIDs:
				items = i.split('-')
				if k in items:
					index_k = items.index(k)
					for j in v:
						items[index_k] = j
						line = '-'.join(items)
						outputLine = '%s\n' % line
						fwrite(outputLine)

if __name__ == '__main__':

	try:
		opts, args = getopt.getopt(sys.argv[1:], 'hi:o:A:', [])
	except getopt.GetoptError, err:
		print str(err)
		usage()
		sys.exit(1)

	hpo_obo, outputFile, includeAltID = ('', '', '')
	for opt, optVal in opts:
		if opt in ('-h', '--help'):
			usage()
			sys.exit(1)
		elif opt in ('-i'):
			hpo_obo = optVal
		elif opt in ('-o'):
			outputFile = optVal
		elif opt in ('-A'):
			includeAltID = optVal
		else:
			print 'Unknown options %s' % opt
			sys.exit(1)

	if hpo_obo == '':
		print 'Input file is required!'
		sys.exit(1)
	if outputFile == '':
		print 'Output file is required!'
		sys.exit(1)

	fileContent = ''
	with open(hpo_obo, 'r') as fp:
		fileContent = fp.read()
	
	termDict = {}
	altDict = {}
	if fileContent:
		termList = SEP.split(fileContent)
		for term in termList:
			lines = term.split('\n')
			termID = ''
			for line in lines:
				if line.startswith('id: HP:'):
					termID = line[4:]
					altDict[termID] = []
				if line.startswith('is_a: ') and termID:
					parentID = line[6:16]
					termDict[parentID] = termDict.get(parentID, [])
					termDict[parentID].append(termID)
				if line.startswith('alt_id: ') and termID:
					altID = line[8:]
					altDict[termID].append(altID)

	IDList = []
	allRecord = []
	f = open(outputFile, 'w')
	fwrite = f.write
	allIDs = recursive_hpo('HP:0000001', termDict, IDList, fwrite, allRecord)

	if includeAltID.upper() == 'Y' or includeAltID.upper() == 'YES': pass
	else: includeAltID = False
	if includeAltID:
		alt_id(altDict, allIDs, fwrite)

	f.close()
