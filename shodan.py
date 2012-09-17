#!/usr/bin/python

""" 
  An event-sourcing-based RDF datastore and processor.

@author: Michael Hausenblas, http://mhausenblas.info/#i
@since: 2012-09-16
@status: init
"""
import os, sys, logging, getopt, StringIO, datetime, git
from subprocess import call

# config

DEBUG = True

# here you need to specify the path where you've build http://code.google.com/p/hdt-java/ 
# try ./rdf2hdt.sh data/test.nt data/test.hdt in this directory if things don't work
HDT_PATH = '/Users/michael/Documents/dev/hdt/hdt-java/'

if DEBUG:
	FORMAT = '%(asctime)-0s %(levelname)s %(message)s [at line %(lineno)d]'
	logging.basicConfig(level=logging.DEBUG, format=FORMAT, datefmt='%Y-%m-%dT%I:%M:%S')
else:
	FORMAT = '%(asctime)-0s %(message)s'
	logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt='%Y-%m-%dT%I:%M:%S')


def init_store(storename):
	"""Creates a directory in user's home containing RDF NTriple & HDT doc, and inits git repo with it."""
	uhome = os.path.expanduser('~') # user home
	storedir = os.path.join(uhome, storename)
	storent = os.path.join(storedir, 'datastore.nt')
	storehdt = os.path.join(storedir, 'datastore.hdt')
	now = datetime.datetime.now()
	
	if DEBUG: logging.debug('initialising datastore in: %s' %os.path.abspath(storedir))

	if not os.path.exists(storedir):
		os.makedirs(storedir)
	
	# create the original store in NTriple format
	ds = open(storent, 'w')
	ds.write(''.join(['<file://', os.path.abspath(storedir), '> <http://purl.org/dc/terms/title> "', storename, '" .\n']))
	ds.write(''.join(['<file://', os.path.abspath(storedir), '> <http://purl.org/dc/terms/creator> <https://github.com/mhausenblas/shodan> .\n']))
	ds.write(''.join(['<file://', os.path.abspath(storedir), '> <http://purl.org/dc/terms/created> "', now.strftime('%Y-%m-%d'), '" .\n']))
	ds.close()
	
	# convert the original store in NTriple to HDT
	convert2HDT(os.path.abspath(storent), os.path.abspath(storehdt))
	
	# commit both store files into git repo
	g = git.Git(os.path.abspath(storedir)) 
	g.init()
	g.add(os.path.abspath(storent))
	g.add(os.path.abspath(storehdt))
	commitmsg = 'init store %s' %storename
	g.commit(m=commitmsg)

def convert2HDT(ntdoc, htdoc):
	"""Converts an RDF NTriple document into an HDT document and returns result code from call."""
	params = '%s %s' %(ntdoc, htdoc)
	cmd = ''.join(['java -server -Xms1024M -Xmx1024M -classpath "', HDT_PATH, 'bin:',  HDT_PATH, 'lib/*" org.rdfhdt.hdt.tools.RDF2HDT ', params])
	if DEBUG: logging.debug('Calling HDT converter with:\n%s' %cmd)
	return call(cmd, shell=True)

def usage():
	print('Usage: python shodan.py --init {storename} | --add | --remove | --match')
	print('Example: python shodan.py --init ex1')


if __name__ == '__main__':
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'hi:a:', ['help', 'init', 'add'])
		for opt, arg in opts:
			if opt in ('-h', '--help'):
				usage()
				sys.exit()
			elif opt in ('-i', '--init'):
				storename = arg
				logging.info('Creating new store [%s]' %storename)
				init_store(storename)
			elif opt in ('-a', '--add'):
				params = arg.split(',')
				logging.info('Adding data to store [%s] %s' %(params[0], params[1]))
				convert2HDT(params[0], params[1])
	except getopt.GetoptError, err:
		print str(err)
		usage()
		sys.exit(2)