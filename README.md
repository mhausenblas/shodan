# shodan

An [event-sourcing-based](http://martinfowler.com/eaaDev/EventSourcing.html) RDF datastore and processor.

## Usage

Let's create a new RDF datastore first:

	$ python shodan.py --init ex1
	2012-09-17T04:27:23 INFO Creating new store [ex1]
	2012-09-17T04:27:24 DEBUG Initialised datastore in [/Users/michael/ex1]
	
You can check if this has worked out: go to your home directory where you should find a new directory named with the store name, `ex1` in our case.

Now, lets add some triples. Shodan assumes you have the data in [RDF NTriples](http://www.w3.org/TR/rdf-testcases/#ntriples "RDF Test Cases") format in a file. I'm going to use the test data supplied with shodan and go like:

	$ python shodan.py --add ex1:data/input_data_0.nt
	2012-09-17T04:27:28 INFO Adding data to store [ex1] from input file [data/input_data_0.nt]
	2012-09-17T04:27:28 DEBUG Updated datastore [ex1] with:
	<http://example.org/#m> <http://xmlns.com/foaf/0.1/knows> <http://example.org/#r> .

## Dependencies

* [HDT](http://www.rdfhdt.org/), download and build [HDT Java](http://code.google.com/p/hdt-java/)
* [git](http://git-scm.com/), asssuming everyone has it installed anyways
* [GitPython](https://github.com/gitpython-developers/GitPython), easy install it

## License

This software is licensed under [Apache 2.0](http://www.apache.org/licenses/LICENSE-2.0.html) Software License.