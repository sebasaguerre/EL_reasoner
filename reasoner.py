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
        gateway.convertToBinaryConjunctions(self.ontology)
        self.axioms = self.ontology.tbox().getAxioms()
        self.allConcepts = self.ontology.getSubConcepts()
        self.simple_concepts = self.ontology.getConceptNames()
        self.axiom_conjuncts = [concept for concept in self.allConcepts if concept.getClass().getSimpleName() == "ConceptConjunction"]
        self.const = gateway.getELFactory()
        self.class_types = ["ConceptConjunction", "ExistentialRoleRestriction"]
        self.individuals = {}
        self.axion_types = ["GeneralConceptInclusion", "EquivalenceAxiom"]

    def top_rule(self, ind):
        self.top = self.const.getTop()
        self.individuals[ind]['concepts'].add(self.top)
    
    def apply_conjunction_rule1(self):
       
       # if conjunct in individual add conjuncts 
       for ind, v in self.individuals.items():
            # loop over all concepts in a ind
            for concept in v["concepts"]:
                if concept.getClass().getSimpleName() == "ConceptConjunction":
                    lhs = concept.lhs()
                    self.individuals[ind]["concepts"].add(lhs)
                    rhs = concept.rhs()
                    self.individuals[ind]["concepts"].add(rhs)
        

    def apply_conjunction_rule2(self):
        # create conjunct concept
        for conjunct in self.axiom_conjuncts:
            # get conjunct lhs, rhs
            c_lhs = conjunct.lhs()
            c_rhs = conjunct.rhs()

            for ind, v in self.individuals.items():
                if c_lhs in v["concepts"] and c_rhs in v["concepts"]:
                    self.individuals[ind]["concepts"].add(conjunct)
            

        # rhs_str = self.formatter.format(rhs)
        # conjunct = self.const.getConjunction(self.const.getConceptName(lhs_str),self. const.getConceptName(rhs_str))

 
    def r_successor_rule_1(self, rhs, ind):
        # extract roles
        role = self.formatter.format(rhs)[1:].split()

        # concepts that role point to in ind
        cls = ".".join(role[1:])
        cls_obj = self.const.getConceptName(cls)


        for i, v in self.individuals.items():
            if cls_obj in v["concepts"]:
                self.individuals[ind]["roles"].update((role, i))
                return
        
        # create new individual when successor no individual has cls
        new_ind = max(key for key in self.individuals.keys()) + 1
        self.individuals[new_ind] = {'concepts': set([cls]), 'roles': set([])}
        self.top_rule(new_ind)

        # assign role (successor) to current individual
        self.individuals[ind]["roles"].update((role, new_ind))


        # # all the succesors of ind with role found
        # inds = [self.individuals[ind]["roles"][i][1] for i in range(len(self.individials[ind]["roles"])) if self.individuals[ind]["roles"][i][0] == role[0]]

    def r_successor_rule_2(self, rhs, ind):
        # extract roles
        role = self.formatter.format(rhs)[1:].split()

        # concepts that role point to in ind
        cls = ".".join(role[1:])
        cls_obj = self.const.getConceptName(cls)

        # inidviduals, values 
        for i, v in self.individuals.items():
            if cls_obj in v["concepts"]:
                self.individuals[ind]["concepts"].add(rhs)
                return
        
    def get_classt(self, ind):
        return self.individuals[ind]['concepts'].getClass().getSimpleName()
    
    def get_count(self):
        # calculate total amount of concepts and roles in individuals 
        count = sum([len(self.individuals[i]["concepts"]) for i in self.individuals.keys()])
        count += sum([len(self.individuals[i]["roles"]) for i in self.individuals.keys()])
        return count
    
    def apply_rules(self, rhs, ind):
        if(rhs.getClass().getSimpleName() != self.class_types[1]):
            self.apply_conjunction_rule1()
            self.apply_conjunction_rule2()
        else:
            # applying the rules if the lhs is an existential role restriction
            self.r_successor_rule_1(rhs, ind)
            self.r_successor_rule_2(rhs, ind)

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
                    self.individuals[ind]['concepts'].add(rhs)
                    self.apply_rules(rhs, ind)
                # check rhs in concepts 
                if rhs in v["concepts"]:
                    self.individuals[ind]['concepts'].add(lhs)
                    self.apply_rules(lhs, ind)
                    

        # applying general concept inclusion axioms
        else:
            # check if the lhs is a simple concept
            if lhs in self.simple_concepts:
            # apply rules based on the axiom type
                for ind in range(len(self.individuals.keys())):
                    # check if lhs occurs inside the individuals concepts
                    if lhs in self.individuals[ind]["concepts"]:
                        # applying the rules if the lhs is a concept conjunction
                        self.individuals[ind]["concepts"].add(rhs)
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
                for ind in range(len(self.individuals.keys())):
                    # check if first lhs concepts is in the individuals concepts
                    if lhs_c[0] in self.individuals[ind]["concepts"]:
                        # check if the lhs_c[1] is simple class
                        # if lhs_c[1].getClass().getSimpleName() not in self.class_types:
                        #     if lhs_c[1] in v["concepts"]:
                        #         self.individuals[ind]["concepts"].append(rhs)
                        #         self.apply_rules(rhs, ind)
                        ## check for simple concepts 
                        if lhs_c[1].getClass().getSimpleName() == self.class_types[0]:
                            if lhs_c[1] in self.individuals[ind]["concepts"]:
                                self.individuals[ind]["concepts"].add(rhs)
                                self.apply_rules(rhs, ind)
                        # check if the lhs is an existential role restriction
                        else:
                            # get the role of the lhs
                            role = self.formatter.format(lhs)[1:].split(".") # [0] = role, [1] = concept

                            # values current individual 
                            v = self.individual[ind]

                            # indfind the individuals that have the role
                            inds = [v["roles"][i][1] for i in range(len(v["roles"])) if v["roles"][i][0] == role[0]]
                            
                            # check if concept is in the found individuals
                            for i in inds:
                                if role[1] in self.individuals[i]["concepts"]:
                                    # append lhs_c[1]
                                    self.individuals[ind]["concepts"].add(lhs_c[1])
                                    # append lhs
                                    self.individuals[ind]["concepts"].add(lhs)
                                    # => rhs is present 
                                    self.individuals[ind]["concepts"].add(rhs)
                                    # apply rules to rhs 
                                    self.apply_rules(rhs, ind)
                                    break
                    
            # if(axiom.getClass().getSimpleName() == self.axion_types[0]:
               
        
    #     if lhs in concepts:
    #     else:
    #         self.individuals[self.currentIndividual].append(lhs)

    def get_subsumers(self, class_name):

        #  convert class_name into jav.obj
        class_name_obj = self.const.getConceptName(class_name)

        # initilaize first individual 
        self.individuals[0] = {"concepts" : set([class_name_obj]), "roles" : set([])}
        self.top_rule(0)

        # if self.get_classt(0) in self.class_types:
        #     self.apply_conjunction_rule1(self.individuals[0], self.get_classt(class_name))
        #     self.r_successor_rule(self.individuals[0], self.get_classt(class_name))

        # convergence criterian
        change = True

        current_count = self.get_count()

        count = 0
        
        while change:

            # previous count  
            for axiom in self.axioms:
                self.assign_concepts(axiom)
            
            # get new count 
            new_count = self.get_count()
            print(f"Current while loop iteration {count}")
            print(f"Previous count {current_count}, new count {new_count}")

            # check for convergence
            if new_count == current_count:
                change = False
            else:
                current_count = new_count 
            
            count += 1
            
        
        # return subsumer of given class
        return self.individuals[0]["concepts"]

def pretty_print(lst, formatter):
    for elem in lst:
        print(formatter.format(elem))


def main():
   
    # check if terminal arguments are given correctly
    # if len(sys.argv) < 3: 
    #     print("Usage: python reasoner.py ontology_file class_name")
    #     return 1
    
     # connect to the java gateway of dl4python
    gateway = JavaGateway()

    # get a parser from OWL files to DL ontologies
    parser = gateway.getOWLParser()

    # formatter 
    formatter = gateway.getSimpleDLFormatter()

    # loand ontology from given command line argument
    ontology = gateway.getOWLParser().parseFile("cto.clinical-trials-ontology.1.owl.xml")
    
    # init reasoner 
    reasoner = ELDestroyer(ontology, gateway)

    # get concept subsumers 
    subsumers = reasoner.get_subsumers("Delusion")

    pretty_print(subsumers, formatter)
    return 0

if __name__ == "__main__":
    main()


