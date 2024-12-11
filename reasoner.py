from py4j.java_gateway import JavaGateway
import sys 
        
class ELDestroyer:
    def __init__(self, ontology, gateway):
        # set ontology inside of class
        self.ontology = ontology
        print("Loaded the ontology!")
        print("Converting to binary conjunctions")
        # get formater for pretty printing 
        self.formatter = gateway.getSimpleDLFormatter()
        # convert ontology to BinaryConjuntions 
        gateway.convertToBinaryConjunctions(ontology)
        self.axioms = ontology.tbox().getAxioms()
        self.allConcepts = ontology.getSubConcepts()
        self.concepts = ontology.getConcepts()
        self.simple_concepts = ontology.getConceptNames()
        self.const = self.gateway.getELFactory()
        self.class_types = ["ConceptConjunction", "ExistentialRoleRestriction"]
        self.individuals = {0:{'concepts': [], 'roles': []}},
        self.axion_types = ["GeneralConceptInclusion", "EquivalenceAxiom"]

    def top_rule(self):
        self.top = self.elFactory.getTop()
        self.individuals[self.currentIndividual]['concepts'].append(top)
    
    def apply_conjunction_rule1(self, ind, rhs):
        # conjuncts from rhs 
        conjuncts = rhs.getConjuncts()
        
        # iterate over conjunctions 
        for conj in conjuncts:
            # if conjunct not present append 
            if conj not in self.individuals[ind]["concepts"]:
                self.individuals[ind]["concepts"].append(conj)

        

    def apply_conjunction_rule2(self, ind, lhs, rhs):
        # create conjunct concept
        lhs_str = self.formatter.format(lhs)
        rhs_str = self.formatter.format(rhs)
        conjunct = self.const.getConjunction(self.const.getConceptName(lhs_str),self. const.getConceptName(rhs_str))

        # loop over string axioms
        for ax in [self.formatter.format(axiom) for axiom in axioms]:
            # check if cnjunct exits
            if conjunct in ax:
                self.individuals[ind]["concepts"].append(conjunct)
                break


    def r_successor_rule_1(self, rhs, ind):
        # extract roles
        role = self.formatter.format(rhs)[1:].split()

        # concepts that role point to in ind
        cls = ".".join(role[1:])

        for i, v in self.individuals.items():
            if cls in v["concepts"]:
                self.individuals[ind]["roles"].append((role, i))
                return
        
        # create new individual when successor no individual has cls
        new_ind = max(key for key in self.individuals.keys()) + 1
        self.individuals[new_ind] = {'concepts': [cls], 'roles': []}

        # assign role (successor) to current individual
        self.individuals[ind]["roles"].append(role, new_ind)


        # # all the succesors of ind with role found
        # inds = [self.individuals[ind]["roles"][i][1] for i in range(len(self.individials[ind]["roles"])) if self.individuals[ind]["roles"][i][0] == role[0]]

    def r_successor_rule_2(self, rhs, ind):
        # extract roles
        role = self.formatter.format(rhs)[1:].split()

        # concepts that role point to in ind
        cls = ".".join(role[1:])
        
        # inidviduals, values 
        for i, v in self.individuals.items():
            if cls in v["concepts"]:
                self.individuals[ind]["concepts"].append(rhs)
                return
        
    def get_classt(self, ind):
        return self.individuals[self.ind]['concepts'].getClass().getSimpleName()
    
    def get_count(self):
        # calculate total amount of concepts and roles in individuals 
        count = sum([len(self.individuals[i]["concepts"]) for i in self.individuals.keys()])
        count += + sum([len(self.individuals[i]["roles"]) for i in self.individuals.keys()])
        return count
    
    def apply_rules(self, rhs, ind):
        if(rhs.getClass().getSimpleName() == self.class_types[0]):
            self.apply_conjunction_rule1(ind, rhs)
            self.apply_conjunction_rule2(ind, rhs)
        else:
            # applying the rules if the lhs is an existential role restriction
            self.r_successor_rule_1(ind, rhs)
            self.r_successor_rule_2(ind, rhs)

    def assign_concepts(self, axiom):
        # get constituents of axiom 
        # if(axiom.getClass().getSimpleName() 
        lhs = axiom.lhs()
        rhs = axiom.rhs()

        # applying equivalence axioms
        if axiom.getClass().getSimpleName() == self.axion_types[1]: 
            for ind, v in self.individuals.items():
                # check lhs in concepts
                if lhs in v["concepts"]:
                    self.individuals[ind]['concepts'].append(rhs)
                    self.apply_rules(rhs, ind)
                # check rhs in concepts 
                if rhs in v["concepts"]:
                    self.individuals[ind]['concepts'].append(lhs)
                    self.apply_rules(lhs, ind)
                    

        # applying general concept inclusion axioms
        else:
            # check if the lhs is a simple concept
            if lhs in self.simple_concepts:
            # apply rules based on the axiom type
                for ind, v in self.individuals.items():
                    # check if lhs occurs inside the individuals concepts
                    if lhs in v["concepts"]:
                        # applying the rules if the lhs is a concept conjunction
                        self.individuals[ind]["concepts"].append(rhs)
                        self.apply_rules(rhs, ind)

                        # if(rhs.getClass().getSimpleName() == self.class_types[0]):
                        #     self.apply_conjunction_rule1(ind, rhs)
                        #     self.apply_conjunction_rule2(ind, rhs)
                        # else:
                        #     # applying the rules if the lhs is an existential role restriction
                        #     self.r_successor_rule_1(ind, rhs)
                        #     self.r_successor_rule_2(ind, rhs)

            # if the lhs is not a simple concept, get the conj
            else:

                # get the conjuncts of the lhs
                lhs_c = lhs.getConjuncts() # [0] = conjunct1, [1] = conjunct2

                # loop over individual
                for ind, v in self.individuals.items():
                    # check if first lhs concepts is in the individuals concepts
                    if lhs_c[0] in v["concepts"]:
                        # check if the lhs is a concept conjunction


                        ## check for simple concepts 
                        if lhs_c[1].getClass().getSimpleName() == self.class_types[0]:
                            if lhs_c[1] in v["concepts"]:
                                self.apply_rules(lhs_c[1], rhs, ind)
                        # check if the lhs is an existential role restriction
                        else:
                            # get the role of the lhs
                            role = self.formatter.format(lhs)[1:].split(".") # [0] = role, [1] = concept

                            # indfind the individuals that have the role
                            inds = [v["roles"][i][1] for i in range(len(v["roles"])) if v["roles"][i][0] == role[0]]
                            
                            # check if concept is in the found individuals
                            for i in inds:
                                if role[1] in self.individuals[i]["concepts"]:
                                    # append lhs_c[1]
                                    self.individuals[ind]["concepts"].append(lhs_c[1])
                                    # append lhs
                                    self.individuals[ind]["concepts"].append(lhs)
                                    # => rhs is present 
                                    self.individuals[ind]["concepts"].append(rhs)
                                    # apply rules to rhs 
                                    self.apply_rules(lhs, rhs, ind)
                                    break
                    
            # if(axiom.getClass().getSimpleName() == self.axion_types[0]:
               
        
    #     if lhs in concepts:
    #     else:
    #         self.individuals[self.currentIndividual].append(lhs)

    def get_subsumers(self, class_name):

        self.individuals[self.currentIndividual].append(class_name)
        self.top_rule()
        if self.get_classt(self.currentIndividual) in self.class_types:
            self.apply_conjunction_rule1(self.currentIndividual, self.get_classt(self.currentIndividual))
            self.r_successor_rule(self.currentIndividual, self.get_classt(self.currentIndividual))

        # convergence criterian
        change = True

        current_count = self.get_count()

        while change:

            # previous count  
            for axiom in self.axioms:
                self.assign_concepts(axiom)
            
            # get new count 
            new_count = self.get_count()

            # check for convergence
            if new_count == current_count:
                change = False
            else:
                current_count = new_count 
        
        # return subsumer of given class
        return self.individuals[0]["concepts"]

def pretty_print(lst):
    for elem in lst:
        print(elem)


def main():
   
    # check if terminal arguments are given correctly
    if len(sys.argv) > 3: 
        print("Usage: python reasoner.py ontology_file class_name")
        return 1
    
     # connect to the java gateway of dl4python
    gateway = JavaGateway()

    # get a parser from OWL files to DL ontologies
    parser = gateway.getOWLParser()

    # loand ontology from given command line argument
    ontology = gateway.getOWLParser().parseFile(sys.argv[1])
    
    # init reasoner 
    reasoner = ELDestroyer(ontology, gateway)

    # get concept subsumers 
    subsumers = reasoner.get_subsumers(sys.argv[2])

    pretty_print(subsumers)
    return 0

if __name__ == "__main__":
    main()


