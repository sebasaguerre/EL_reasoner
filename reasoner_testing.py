#! /usr/bin/python

from py4j.java_gateway import JavaGateway

# connect to the java gateway of dl4python
gateway = JavaGateway()

# get a parser from OWL files to DL ontologies
parser = gateway.getOWLParser()

# get a formatter to print in nice DL format
formatter = gateway.getSimpleDLFormatter()

print("Loading the ontology...")

# load an ontology from a file
ontology = parser.parseFile("cto.clinical-trials-ontology.1.owl.xml")

print("Loaded the ontology!")

# IMPORTANT: the algorithm from the lecture assumes conjunctions to always be over two concepts
# Ontologies in OWL can however have conjunctions over an arbitrary number of concpets.
# The following command changes all conjunctions so that they have at most two conjuncts
print("Converting to binary conjunctions")
gateway.convertToBinaryConjunctions(ontology)

print("Converting to binary conjunctions")
gateway.convertToBinaryConjunctions(ontology)

# get the TBox axioms
tbox = ontology.tbox()
axioms = tbox.getAxioms()

print("These are the axioms in the TBox:")
for axiom in axioms:
    print(formatter.format(axiom))

# access the type of axioms:
foundGCI = False
foundEquivalenceAxiom = False
print()
print("Looking for axiom types in EL")
all_concepts = ontology.getSubConcepts()
simple_names = ontology.getConceptNames()
for concept in all_concepts:
    print(f"concept: {formatter.format(concept)}")
for name in simple_names:
    print(f"name: {formatter.format(name)}")