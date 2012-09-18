#!/usr/bin/python

""" 
  An event-sourcing-based RDF datastore and processor.

@author: Michael Hausenblas, http://mhausenblas.info/#i
@since: 2012-09-16
@status: first API done
"""
import os, sys, logging, getopt, StringIO, datetime, git
from subprocess import call

# config

DEBUG = True

# here you need to specify the path where you've build http://code.google.com/p/hdt-java/ 
# try ./rdf2hdt.sh data/test.nt data/test.hdt in this directory if things don't work
HDT_PATH = '/Users/michael/Documents/dev/hdt/hdt-java/'
HDT_JENA_PATH = '/Users/michael/Documents/dev/hdt/hdt-jena/'

if DEBUG:
	FORMAT = '%(asctime)-0s %(levelname)s %(message)s [at line %(lineno)d]'
	logging.basicConfig(level=logging.DEBUG, format=FORMAT, datefmt='%Y-%m-%dT%I:%M:%S')
else:
	FORMAT = '%(asctime)-0s %(message)s'
	logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt='%Y-%m-%dT%I:%M:%S')


###############################################################################
# Shodan API

def init_store(storename):
	"""Creates a directory in user's home containing RDF NTriple & HDT doc, and inits/commits to git repo."""
	uhome = os.path.expanduser('~') # user home
	storedir = os.path.join(uhome, storename)
	storent = os.path.join(storedir, 'datastore.nt')
	storehdt = os.path.join(storedir, 'datastore.hdt')
	now = datetime.datetime.now()
	
	if not os.path.exists(storedir):
		os.makedirs(storedir)
	
	# create the original store in NTriple format
	ds = open(storent, 'w')
	ds.write(''.join(['<file://', os.path.abspath(storedir), '> <http://purl.org/dc/terms/title> "', storename, '" .\n']))
	ds.write(''.join(['<file://', os.path.abspath(storedir), '> <http://purl.org/dc/terms/creator> <https://github.com/mhausenblas/shodan> .\n']))
	ds.write(''.join(['<file://', os.path.abspath(storedir), '> <http://purl.org/dc/terms/created> "', now.strftime('%Y-%m-%d'), '" .\n']))
	ds.close()
	
	# init git repo and commit both store files
	g = git.Git(os.path.abspath(storedir)) 
	g.init()
	convertNCommit(storedir, storent, storehdt, 'init store %s' %storename)
	
	if DEBUG: logging.debug('Initialised datastore in [%s]' %os.path.abspath(storedir))

def add_store(storename, data):
	"""Adds NTriples data to an existing store, converts to HDT and commits to git repo."""
	uhome = os.path.expanduser('~') # user home
	storedir = os.path.join(uhome, storename)
	storent = os.path.join(storedir, 'datastore.nt')
	storehdt = os.path.join(storedir, 'datastore.hdt')
	
	# append NTriples data to existing file
	try:
		with open(storent, "a") as ntfile:
			ntfile.write(data)
	except IOError as err:
		# print str(err)
		logging.error('The datastore [%s] does not exist - generate it first, please!' %storename)
		usage()
		sys.exit(2)
	
	convertNCommit(storedir, storent, storehdt, 'updated store %s' %storename)
	if DEBUG: logging.debug('Updated datastore [%s] with:\n%s' %(storename, data))

def query_store(storename, data):
	"""Queries existing store using SPARQL."""
	uhome = os.path.expanduser('~') # user home
	storedir = os.path.join(uhome, storename)
	storehdt = os.path.join(storedir, 'datastore.hdt')

	query2HDT(storehdt, data)

###############################################################################
# Shodan utility functions

def convertNCommit(storedir, storent, storehdt, commitmsg):
	"""Converts an RDF NTriple document into an HDT document and commits it to the git repo."""
	# convert the original store in NTriple to HDT
	convert2HDT(os.path.abspath(storent), os.path.abspath(storehdt))
	
	# commit both store files into git repo
	g = git.Git(os.path.abspath(storedir)) 
	g.add(os.path.abspath(storent))
	g.add(os.path.abspath(storehdt))
	g.commit(m=commitmsg)

def convert2HDT(ntdoc, htdoc):
	"""Converts an RDF NTriple document into an HDT document and returns result code from call."""
	params = '%s %s' %(ntdoc, htdoc)
	cmd = ''.join(['java -server -Xms1024M -Xmx1024M -classpath "', HDT_PATH, 'bin:',  HDT_PATH, 'lib/*" org.rdfhdt.hdt.tools.RDF2HDT ', params])
	if DEBUG: logging.debug('Calling HDT converter with:\n%s' %cmd)
	return call(cmd, shell=True)

def query2HDT(htdoc, sparql):
	"""Queries an RDF HDT document using hdt-jena."""
	params = '%s "%s"' %(htdoc, sparql)
	cmd = ''.join(['java -d64 -server -Xmx1024M -classpath "', HDT_JENA_PATH, 'bin:',  HDT_JENA_PATH, 'lib/*:', HDT_PATH, 'bin:',  HDT_PATH, 'lib/*" HDTSparqlAPI ', params])
	if DEBUG: logging.debug('Executing HDT Jena SPARQL query with:\n%s' %cmd)
	return call(cmd, shell=True)

def parseNTFile(ntdoc):
	"""Reads in an RDF NTriple file from file system, returns a string of the content"""
	file = open(ntdoc, 'r')
	ret = file.read() # for now, simply read content - should validate the content(!)
	file.close()
	return ret

def parseSPARQLFile(sparqldoc):
	"""Reads in SPARQL file from file system, returns a string of the content"""
	file = open(sparqldoc, 'r')
	ret = file.read() # for now, simply read content - should validate the content(!)
	file.close()
	return ret

def usage():
	print('Usage: python shodan.py --init {storename} | --add | --remove | --match')
	print('Example 1 - init a datastore:\n  python shodan.py --init ex1')
	print('Example 2 - add triples to an existing datastore:\n  python shodan.py --add ex1:data/input_data_0.nt')
	print('Example 3 - issue a SPARQL query against existing datastore:\n  python shodan.py --query ex1:data/query_0.sparql')


if __name__ == '__main__':
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'hi:a:q:', ['help', 'init=', 'add=', 'query='])
		for opt, arg in opts:
			if opt in ('-h', '--help'):
				usage()
				sys.exit()
			elif opt in ('-i', '--init'):
				storename = arg
				logging.info('Creating new store [%s]' %storename)
				init_store(storename)
			elif opt in ('-a', '--add'):
				params = arg.split(':')
				logging.info('Adding data to store [%s] from input file [%s]' %(params[0], params[1]))
				add_store(params[0], parseNTFile(params[1]))
			elif opt in ('-q', '--query'):
				params = arg.split(':')
				logging.info('Querying store [%s] with SPARQL query from input file [%s]' %(params[0], params[1]))
				query_store(params[0], parseSPARQLFile(params[1]))
	except getopt.GetoptError, err:
		print str(err)
		usage()
		sys.exit(2)