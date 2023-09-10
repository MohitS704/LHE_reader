import functools
import graphlib

class lhe_particle(object):
    def __init__(self, line) -> None:
        self.row_values = list(map(float,line.split()))
        
        self.parents = set()
        self.children = set()
        
        if len(self.row_values) != 13:
            raise ValueError("LHE Event Formatted Incorrectly!\nLength of {:.0f} instead of desired 13!".format(len(self.row_values)))
    
    @functools.cached_property
    def quantities(self):
        tags = ["ID", "STATUS", "MOTHER_1", "MOTHER_2", "COLOR_1", "COLOR_2", "VECTOR", "MASS", "LIFETIME", "SPIN"]
        values = self.row_values[:6] + [self.row_values[6:10]] + self.row_values[10:]
        returnable = dict(zip(tags, values))
        returnable["MOTHER_1"], returnable["MOTHER_2"] = int(returnable["MOTHER_1"]), int(returnable["MOTHER_2"])
        return returnable
    
    @functools.cached_property
    def id(self):
        return int(self.quantities['ID'])
    
    def add_parents(self, *parents):
        [self.parents.add(parent) for parent in parents]
    
    def add_children(self, *children):
        [self.children.add(child) for child in children]
    
    def __str__(self) -> str:
        return "ID={:.0f} STATUS={:.0f}".format(self.quantities["ID"], self.quantities["STATUS"])
    
    def __repr__(self) -> str:
        return str(self)

    def print(self):
        print("\n".join([key+":"+str(self.quantities[key]) for key in self.quantities]) + "\n")
    
    def __iter__(self):
        for key in self.quantities.keys():
            yield key
    
    @functools.cached_property
    def is_production_particle(self):
        return len(self.parents) == 0
    
    @functools.cached_property
    def is_final_state_particle(self):
        return len(self.children) == 0

class lhe_event(object):
    def __init__(self, event) -> None:
        # self.original_string = event
        
        self.n = 0
        self.proc = 0
        self.weight = 0
        self.fac_scale = 0
        self.alpha_em = 0
        self.alpha_s = 0
        
        event_quantities = []
        
        lines = event.split('\n')
        
        self.root = None
        self.final_state_particles = set()
        
        self.graph = graphlib.TopologicalSorter()
        
        particle_index = 0
        root_index = 0
        for line in lines:
            if "event" in line:
                continue
            try:
                row = lhe_particle(line)
                row_values = row.quantities
                
                event_quantities[particle_index] = row
                
                if row_values["MOTHER_1"] != 0 and row_values["MOTHER_2"] != 0:
                    parent1 = row_values["MOTHER_1"] - 1
                    parent2 = row_values["MOTHER_2"] - 1
                    row.add_parents(event_quantities[parent1], event_quantities[parent2])
                    event_quantities[parent1].add_children(row)
                    event_quantities[parent2].add_children(row)
                    
                    self.graph.add(row, event_quantities[parent1], event_quantities[parent2])
                else:
                    root_index += 1
                
                if row_values["STATUS"] == 1:
                    self.final_state_particles.add(row)
                    
                particle_index += 1
            except ValueError:
                self.n, self.proc, self.weight, self.fac_scale, self.alpha_em, self.alpha_s = list(map(float,line.split()))
                self.n, self.proc = int(self.n), int(self.weight)
                
                event_quantities = [None]*self.n #Initialize the array
        
        self.root = event_quantities[root_index]
    
    def __str__(self):
        return "Event with {:.0f} particles using Process {:.0f}".format(self.n, self.proc)
    
    def __repr__(self) -> str:
        return "n={:.0f} proc={:.0f}".format(self.n, self.proc)
    
    def print(self):
        # print(self.root.parents)
        printed = "(" + ",".join(str(s.id) for s in self.root.parents) + ")"
        printed += "->" + str(self.root.id)
        printed += "->(" + ",".join([str(i.id) for i in self if i.is_final_state_particle]) + ")"
        print("Event of the form:", printed)
    
    def __iter__(self):
        for row in self.graph.static_order():
            yield row