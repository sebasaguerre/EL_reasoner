from py4j.java_gateway import JavaGateway
import sys 
        
class ELDestroyer:
    def __init__(self, ontology, gateway): 
        # set ontology inside of class
        self.ontology = ontology
        # get formater for pretty printing 
        self.formatter = gateway.getSimpleDLFormatter()
        # convert ontology to BinaryConjuntions 
        gateway.convertToBinaryConjunctions(self.ontology)
        self.axioms = self.ontology.tbox().getAxioms()
        self.allConcepts = self.ontology.getSubConcepts()
        self.simple_concepts = self.ontology.getConceptNames()
        self.axiom_conjuncts = [concept for concept in self.allConcepts if concept.getClass().getSimpleName() == "ConceptConjunction"]
        self.const = gateway.getELFactory()
        self.class_types = ["ConceptConjunction", "ExistentialRoleRestriction", "ConceptName", "TopConcept$"]
        self.individuals = {}
        self.axion_types = ["GeneralConceptInclusion", "EquivalenceAxiom"]

    def top_rule(self, ind):
        self.top = self.const.getTop()
        self.individuals[ind]['concepts'].add(self.top)

    def banned_classes(self, lhs, rhs):

        # get lhs and rhs class types 
        ctype_lhs = lhs.getClass().getSimpleName()
        ctype_rhs = rhs.getClass().getSimpleName()

        # prevent working with concepts outside of EL 
        if ctype_lhs not in self.class_types or ctype_rhs not in self.class_types: 
            return True 
        else:
            return False 
            


    def get_conjuncts(self, conjunct):
        # get conjunct data 
        f_conjunct = self.formatter.format(conjunct)
        c_conjunct = conjunct.getClass().getSimpleName()
        
        # extract conjuncts 
        conjuncts = self.formatter.format(conjunct).strip("()").split(" ⊓ ")
        
        # flag = None

        # if "∃" in conjuncts[0]:
        #     flag = "L"
        #     sub_parts = conjuncts[0][1:].split(".")
        #     role = self.const.getRole(sub_parts[0])
        #     concept = self.const.getConceptName(sub_parts[0])
        #     c_lhs = self.const.getExistentialRoleRestriction(role, concept)
        # # create rhs concept object        
        # else:
        #     c_lhs = self.const.getConceptName(conjuncts[0])

        # create lhs concept object
        c_lhs = self.const.getConceptName(conjuncts[0])
    
        # construct rhs as a esixtential_role_restriction
        if "∃" in conjuncts[1]:
            flag = "R"
            sub_parts = conjuncts[1][1:].split(".")
            role = self.const.getRole(sub_parts[0])
            concept = self.const.getConceptName(sub_parts[1])
            c_rhs = self.const.getExistentialRoleRestriction(role, concept)
        # create rhs concept object        
        else:
            c_rhs = self.const.getConceptName(conjuncts[1])

        # if flag == "L":
        #     return c_rhs, c_lhs
        # else:
        return c_lhs, c_rhs
    
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

        f_ax_conjuncts = [self.formatter.format(conj) for conj in self.axiom_conjuncts]

        for conjunct in self.axiom_conjuncts:
            # get conjunct lhs, rhs
            f_conjunct = self.formatter.format(conjunct)

            # conjunct lhs and rhs 
            c_lhs, c_rhs = self.get_conjuncts(conjunct)

            for ind, v in self.individuals.items():

                if c_lhs in v["concepts"] and c_rhs in v["concepts"]:

                    self.individuals[ind]["concepts"].add(conjunct)
            

        # rhs_str = self.formatter.format(rhs)
        # conjunct = self.const.getConjunction(self.const.getConceptName(lhs_str),self. const.getConceptName(rhs_str))

 
    def r_successor_rule_1(self, rhs, ind):
        # extract roles
        role = self.formatter.format(rhs)[1:].split(".")

        # concepts that role point to in ind
        cls = ".".join(role[1:])
        cls_obj = self.const.getConceptName(cls)

        
        for i, v in self.individuals.items():
            if cls_obj in v["concepts"]:
                self.individuals[ind]["roles"].update(tuple([role[0], i]))
                return
        
        # create new individual when successor no individual has cls
        new_ind = max(key for key in self.individuals.keys()) + 1
        self.individuals[new_ind] = {'concepts': set([cls_obj]), 'roles': set([])}
        self.top_rule(new_ind)


        # assign role (successor) to current individual
        self.individuals[ind]["roles"].update(tuple([role[0], new_ind]))


    def r_successor_rule_2(self, rhs, ind):
        # extract roles
        role = self.formatter.format(rhs)[1:].split(".")

        # concepts that role point to in ind
        cls = "".join(role[1:])
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
        # if(rhs.getClass().getSimpleName()  self.class_types[1]):
        self.r_successor_rule_1(rhs, ind)
        self.r_successor_rule_2(rhs, ind)

        self.apply_conjunction_rule1()
        self.apply_conjunction_rule2()
      
            
    def assign_concepts(self, axiom):
        # get constituents of axiom 
        f_axiom = self.formatter.format(axiom)

        if axiom.getClass().getSimpleName() == "EquivalenceAxiom":
            # constituents of equivalence
            const = self.formatter.format(axiom).split("≡")
            # get 
            lhs = self.const.getConceptName(const[0])
            rhs = self.const.getConceptName(const[1]) 
        
        else:
            lhs = axiom.lhs()
            rhs = axiom.rhs()

        # prevent working with concepts outside of EL 
        if self.banned_classes(lhs, rhs): return 

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

            # lhs is not simple 
            else:
                 
                # lhs is existential  
                if lhs.getClass().getSimpleName() == self.class_types[1]:
                    # extract roles
                    role = self.formatter.format(lhs)[1:].split(".")
                    # concepts that role point to in ind
                    cls = "".join(role[1:])
                    cls_obj = self.const.getConceptName(cls)

                    # loop over indiividuals 
                    for ind, v in self.individuals.items():
                        

                        roles = list(v["roles"])
                        # roles that the individual has 
                        ind_roles = [roles[i][0] for i in range(len(v["roles"]))]

                        if role in ind_roles:
                            # role successors 
                            succs = [list(v["roles"])[i][1] for i in range(len(v["roles"])) if list(v["roles"])[i][0] == role[0]]
                            
                            # loop over successors 
                            for i in succs:
                                    # check if successor with concepts exist
                                    if cls_obj in self.individuals[i]["concepts"]:
                                        # assign lhs and rhs 
                                        self.individuals[ind]["concepts"].add(lhs)
                                        self.individuals[ind]["concepts"].add(rhs )
                        
                # lhs is conjunction
                else:
                    
                    # break down conjunction
                    l_lhs, l_rhs = self.get_conjuncts(lhs)

                    if self.banned_classes(l_lhs, l_rhs): return

                    ctype_llhs = l_lhs.getClass().getSimpleName()
                    ctype_lrhs = l_rhs.getClass().getSimpleName()


                    # loop over individual
                    for ind in range(len(self.individuals.keys())):

                        # check if first lhs concepts is in the individuals concepts
                        if l_lhs in self.individuals[ind]["concepts"]:
                            ## check for simple concepts 
                            if l_rhs.getClass().getSimpleName() == self.class_types[0]:
                                if l_rhs in self.individuals[ind]["concepts"]:
                                    self.individuals[ind]["concepts"].add(rhs)
                                    self.individuals[ind]["concepts"].add(lhs)
                                    self.apply_rules(rhs, ind)

                            # check if the lhs is an existential role restriction
                            else:
                                # get the role of the lhs
                                role = self.formatter.format(lhs)[1:].split(".") # [0] = role, [1] = concept

                                #  class that role point to 
                                cls = "".join(role[1:])
                                cls_obj = self.const.getConceptName(cls)

                                # values current individual 
                                v = self.individual[ind]

                                # indfind the individuals that have the role
                                roles = list(v["roles"])
                                inds = [roles[i][1] for i in range(len(v["roles"])) if roles[i][0] == role[0]]
                                
                                # check if concept is in the found individuals
                                for i in inds:
                                    if cls_obj in self.individuals[i]["concepts"]:
                                        # append lhs_c[1]
                                        self.individuals[ind]["concepts"].add(l_rhs)
                                        # append lhs
                                        self.individuals[ind]["concepts"].add(lhs)
                                        # => rhs is present 
                                        self.individuals[ind]["concepts"].add(rhs)
                                        # apply rules to rhs 
                                        self.apply_rules(rhs, ind)

                                        break
               
        
    #     if lhs in concepts:
    #     else:
    #         self.individuals[self.currentIndividual].append(lhs)

    def get_subsumers(self, class_name):

        #  convert class_name into jav.obj
        class_name_obj = self.const.getConceptName(class_name)

        # initilaize first individual 
        self.individuals[0] = {"concepts" : set([class_name_obj]), "roles" : set([])}
        self.top_rule(0)
        
        format_concepts = set()

        
        # convergence criterian
        change = True

        current_count = self.get_count()

        count = 0
        
        while change:

            # previous count  
            for axiom in self.axioms:
                if axiom.getClass().getSimpleName() not in self.axion_types: continue 
                self.assign_concepts(axiom)
            
            # get new count 
            new_count = self.get_count()
            # print(f"Current while loop iteration {count}")
            # print(f"Previous count {current_count}, new count {new_count}")

            for concept in self.individuals[0]["concepts"]:
                format_concepts.add(self.formatter.format(concept))


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
    inp = True
    # check if terminal arguments are given correctly
    if inp == False:
        if len(sys.argv) < 3: 
            print("Usage: python reasoner.py ontology_file class_name")
            return 1
        
     # connect to the java gateway of dl4python
    gateway = JavaGateway()

    # get a parser from OWL files to DL ontologies
    parser = gateway.getOWLParser()

    # formatter 
    formatter = gateway.getSimpleDLFormatter()

    # loand ontology from given command line argument
    file  = input("Give input file: ") if inp else sys.argv[1]
    ontology = gateway.getOWLParser().parseFile(file)
    
    # init reasoner 
    reasoner = ELDestroyer(ontology, gateway)

    concept  = input("Give concept: ") if inp else sys.argv[2]

    # get concept subsumers 
    subsumers = reasoner.get_subsumers(concept)

    pretty_print(subsumers, formatter)
    return 0

if __name__ == "__main__":
    main()


