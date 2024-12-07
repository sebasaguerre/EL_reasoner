from py4j.java_gateway import JavaGateway
import sys 



def main():
    # connect to the java gateway of dl4python
    gateway = JavaGateway()

    # get a parser from OWL files to DL ontologies
    parser = gateway.getOWLParser()

    # get a formatter to print in nice DL format
    formatter = gateway.getSimpleDLFormatter()

    if len(sys.argv) > 3: 
        print("Usage: python reasoner.py ontology_file class_name")
        return 1

    # loand ontology from given command line argument
    ontology = parser.parseFile(sys.argv[1])
    
    # convert ontology to binaryconfunction
    gateway.convertToBinaryConjunctions(ontology)

    reasoner(ontology)


def t_rule(ind):
    pass

def conj1_rule(ind):
    pass

def conj2_rule(ind):
    pass

def ex1_rule(ind):
    pass

def ex2_rule(ind):
    pass

def subs_rule(ind):
    pass

def reasoner(ontology, gateway):
    axioms = ontology.tbox().getAxioms()
    classes = ontology.getSubConcepts()
    construct = gateway.ELfactory()
    inds = { 0 : []}
    
    for axiom in axioms:
        pass