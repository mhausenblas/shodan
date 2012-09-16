#!/usr/bin/python

""" 
  An event-sourcing-based RDF datastore and processor.

@author: Michael Hausenblas, http://mhausenblas.info/#i
@since: 2012-09-16
@status: init
"""
import os, sys, logging, getopt, StringIO, datetime, git

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
	"""Creates a directory in user's home containing RDF NTriple & HDT doc, and inits git repo with it"""
	uhome = os.path.expanduser('~') # user home
	storedir = os.path.join(uhome, storename)
	storent = os.path.join(storedir, 'datastore.nt')
	# storehdt = os.path.join(storedir, 'datastore.hdt')
	
	if DEBUG: logging.debug("initialising datastore in: %s" %os.path.abspath(storedir))

	if not os.path.exists(storedir):
		os.makedirs(storedir)
		
	ds = open(storent, 'w')
	ds.write("");
	ds.close()
	
	g = git.Git(os.path.abspath(storedir)) 
	g.init()
	g.add(os.path.abspath(storent))
	commitmsg = 'init store %s' %storename
	g.commit(m=commitmsg)


def usage():
	print("Usage: python shodan.py --init | --add | --remove | --match")
	print("Example: python shodan.py --init example1")


if __name__ == '__main__':
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hi:v", ["help", "init", "verbose"])
		for opt, arg in opts:
			if opt in ("-h", "--help"):
				usage()
				sys.exit()
			elif opt in ("-i", "--init"):
				storename = arg
				logging.info("Using storename: %s" %storename)
				init_store(storename)
			elif opt in ("-v", "--verbose"): 
				DEBUG = True
	except getopt.GetoptError, err:
		print str(err)
		usage()
		sys.exit(2)