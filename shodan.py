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
HDT_PATH = '/Users/michael/Documents/dev/hdt/hdt-java'

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
	now = datetime.datetime.now()
	# storehdt = os.path.join(storedir, 'datastore.hdt')
	
	if DEBUG: logging.debug('initialising datastore in: %s' %os.path.abspath(storedir))

	if not os.path.exists(storedir):
		os.makedirs(storedir)
		
	ds = open(storent, 'w')
	ds.write(''.join(['<file://', os.path.abspath(storedir), '> <http://purl.org/dc/terms/title> "', storename, '" .\n']))
	ds.write(''.join(['<file://', os.path.abspath(storedir), '> <http://purl.org/dc/terms/creator> <https://github.com/mhausenblas/shodan> .\n']))
	ds.write(''.join(['<file://', os.path.abspath(storedir), '> <http://purl.org/dc/terms/created> "', now.strftime('%Y-%m-%d'), '" .\n']))
	ds.close()
	
	g = git.Git(os.path.abspath(storedir)) 
	g.init()
	g.add(os.path.abspath(storent))
	commitmsg = 'init store %s' %storename
	g.commit(m=commitmsg)

# NOTE: can't build HDT due to some funny compiler error, need to check back with Mario
# for now assume RDF2HDT is done manually (via UI)
def convert2HDT(ntdoc, htdoc):
	"""Converts an RDF NTriple document into an HDT document and returns result code from call."""
	params = '%s %s' %(ntdoc, htdoc)
	cmd = ''.join(['cd ', HDT_PATH, ' '])
	cmd += ''.join(['java -server -Xms1024M -Xmx1024M -classpath "', HDT_PATH, '/bin:',  HDT_PATH, '/lib/*" org.rdfhdt.hdt.tools.RDF2HDT ', params])
	if DEBUG: logging.debug('EXECUTE: %s' %cmd)
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