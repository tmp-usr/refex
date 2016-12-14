import sys

from storm.locals import ReferenceSet

from storm_objects import Ensembl, Ensembl2GO, Uniprot, GO, HpaClass, HpaSubLoc

from storm_objects import Uniprot2HpaClass, Uniprot2HpaSubLoc
from storm_objects import Ensembl2HpaClass, Ensembl2HpaSubLoc
from storm_objects import Uniprot2KEGG

from db_base import DBBase

import pdb


class Selector(DBBase):
    """
        TODO : uniprot2ensembl2go and uniprot2kegg will be done after
        filter the uniprots for the ones in our database through the
        gene symbols.


        DB-ID Mapping approaches:
            1. input list of ids returns a dictionary of reference_id: [target_list (objects)]
            2. input list of ids returns a dictionary of target_id: [reference_list (objects)]
            3. input list returns a generator of ids in the corresponding order
            4. input list of ids returns a generator of lists. equivalent to type 1, different data str.
            5. id vs. id mapping for one to one tables
            6. id vs. list for one to many tables.
            
        
        * ids are database accessions if they have widely used ones such as KO ids or ENSEMBL ids.
        In other cases where the biological database does not have widely used identifiers or have
        manually assigned identifiers by refex, entry names are used instead. 
            

    """
    
    def __init__(self):
        DBBase.__init__(self)

    @property
    def all_hpaclasses(self):
        return [hc for hc in self.store.find(HpaClass)]

    @property
    def all_hpasublocs(self):
        return [hsl for hsl in self.store.find(HpaSubLoc)]

    @property
    def all_ensembls(self):
        return [e for e in self.store.find(Ensembl)]

    @property
    def all_uniprots(self):
        return [u for u in self.store.find(Uniprot)]

    @property
    def all_gos(self):
        return [go for go in self.store.find(GO)]



##############################  Type 1 Mappers  ##################################
#1. input list of ids returns a dictionary of reference_id: [target_list (objects)]

    def get_ensembl2uniprot(self, ensembl_ids):
        """
            multiple genes can be coding for the same protein. the function is
            rewritten as ensembl2uniprots
        """
        ensembl2uniprot= {}
        for ensembl_id in ensembl_ids:
            ensembl= self.store.find(Ensembl, Ensembl.id == unicode(ensembl_id)).one()
            if not ensembl:
                continue
            
            ensembl2uniprot[ensembl_id] = [self.get_uniprot_by_id(ensembl.uniprot_id)]

        return ensembl2uniprot



    def get_ensembl2go(self, ensembl_ids):
        Ensembl.gos= ReferenceSet(Ensembl.id, Ensembl2GO.ensembl_id,
                         Ensembl2GO.go_id,
                         GO.id)
        
        ensembl2go= {}
        for ensembl_id in ensembl_ids:
            ensembl= self.store.find(Ensembl, Ensembl.id == unicode(ensembl_id)).one()       
            if not ensembl:    
                continue
            ensembl2go[ensembl_id]= [go for go in ensembl.gos]
        return ensembl2go


    def get_uniprot2ensembl(self, uniprot_ids):
       
        import urllib2
        import re

        uniprot2ensembl= {}
        
        for uniprot_id in uniprot_ids:
            
            ensembls= self.store.find(Ensembl, Ensembl.uniprot_id == unicode(uniprot_id))
        

            ensembls= [e for e in ensembls]
            if not ensembls:

                req = urllib2.Request('http://www.uniprot.org/uniprot/%s.fasta' % uniprot_id)
                fasta_entry = urllib2.urlopen(req).read()
                fasta_header= fasta_entry.split("\n")[0]
                
                exp= "GN=(\w+)"
                m= re.search(exp, fasta_header)
                
                
                if "GN=" not in fasta_header:
                    continue

                gene_symbol = m.group(1)
                
                ensembl= self.store.find(Ensembl, Ensembl.symbol == unicode(gene_symbol)).one()
                
                if not ensembl:
                    continue
                
                else:
                    ensembls=[ensembl]
                    

            uniprot2ensembl[uniprot_id] = ensembls
       
        return uniprot2ensembl


    def get_uniprot2go(self, uniprot_ids):

        Ensembl.gos= ReferenceSet(Ensembl.id, Ensembl2GO.ensembl_id,
                         Ensembl2GO.go_id,
                         GO.id)


        uniprot2go= {}
            
        uniprot2ensembl= self.get_uniprot2ensembl(uniprot_ids)
        
        for uniprot_id, ensembls in uniprot2ensembl.iteritems():
            
            for ensembl in ensembls:
                if uniprot_id not in uniprot2go:
                    uniprot2go[uniprot_id] =[]
                
                uniprot2go[uniprot_id]+= list(set(ensembl.gos))
                
        return uniprot2go



    def get_uniprot2hpasubloc(self, uniprot_ids):
        Uniprot.hpasublocs= ReferenceSet(Uniprot.id, 
                            Uniprot2HpaSubLoc.uniprot_id,
                            Uniprot2HpaSubLoc.hpasubloc_id,
                            HpaSubLoc.id)

        uniprot2hpasubloc= {}
        for uniprot_id in uniprot_ids:
            uniprot= self.get_uniprot_by_id(uniprot_id)
            uniprot2hpaclass[uniprot.id] = [hpaclass for hpaclass in uniprot.sublocs]
        
        return uniprot2hpasubloc


    def get_uniprot2kegg(self, uniprot_ids):
        """
            TODO
        """
        
        uniprot2kegg= {}
        for uniprot_id in uniprot_ids: 
            results= self.store.find(Uniprot2KEGG, Uniprot2KEGG.uniprot_id == unicode(uniprot_id))
            if uniprot_id not in uniprot2kegg:
                uniprot2kegg[uniprot_id] = []
                
                for result in results:
                    uniprot2kegg[uniprot_id].append(result.kegg_id)
        
        return uniprot2kegg

    def get_hpaclass2ensembls(self, hpa_class_names):
        """
            Fixed
        """
        HpaClass.ensembls= ReferenceSet(HpaClass.id,
                         Ensembl2HpaClass.hpaclass_id, Ensembl2HpaClass.ensembl_id,
                         Ensembl.id)
 
        hpaclass2ensembls= {}
        for hpa_class_name in hpa_class_names:
            hpa_class= self.get_hpaclass_by_name(hpa_class_name)
            
            hpaclass2ensembls[hpa_class_name] = [ensembl for ensembl in hpa_class.ensembls]
        
        return hpaclass2ensembls
          

    def get_ensembl2hpaclass(self, ensembl_ids):
        Ensembl.hpaclasses= ReferenceSet(Ensembl.uniprot_id,  
                                         Uniprot2HpaClass.uniprot_id,
                                         Uniprot2HpaClass.hpaclass_id,
                                         HpaClass.id)
        
        ensembl2hpaclass= {}
        for ensembl_id in ensembl_ids:
            ensembl= self.get_ensembl_by_id(unicode(ensembl_id))
            if not ensembl:    
                continue
            ensembl2hpaclass[ensembl.id] = [hpaclass for hpaclass in ensembl.hpaclasses]
        
        return ensembl2hpaclass


    def get_ensembl2hpasubloc(self, ensembl_ids):
        Ensembl.hpasublocs= ReferenceSet(Ensembl.uniprot_id,  
                                         Uniprot2HpaSubLoc.uniprot_id,
                                         Uniprot2HpaSubLoc.hpasubloc_id,
                                         HpaSubLoc.id)
        
        ensembl2hpasublocs= {}
        for ensembl_id in ensembl_ids:
            ensembl= self.get_ensembl_by_id(unicode(ensembl_id))
            if not ensembl:    
                continue
            ensembl2hpasublocs[ensembl.id] = [hpasubloc for hpasubloc in ensembl.hpasublocs]
        
        return ensembl2hpasublocs


    def get_go2ensembls(self, go_ids):
        GO.ensembles= ReferenceSet(GO.id,
                         Ensembl2GO.go_id, Ensembl2GO.ensembl_id,
                         Ensembl.id)

        go2ensembl= {}
        for go_id in go_ids:
            go= self.get_go_by_id(go_id)
            if not go:
                go = self.get_go_by_name(go_id)

            go2ensembl[go_id]= [ensembl for ensembl in go.ensembles]

        return go2ensembl
   

    def get_uniprot2hpaclass(self, uniprot_ids):
        Uniprot.hpaclasses= ReferenceSet(Uniprot.id, 
                            Uniprot2HpaClass.uniprot_id,
                            Uniprot2HpaClass.hpaclass_id,
                            HpaClass.id)

        uniprot2hpaclass= {}
        for uniprot_id in uniprot_ids:
            uniprot= self.get_uniprot_by_id(uniprot_id)
            uniprot2hpaclass[uniprot.id] = [hpaclass for hpaclass in uniprot.hpaclasses]
        
        return uniprot2hpaclass



    def get_hpasubloc2ensembls(self, hpa_subloc_names):
        """
            Fixed
        """
        
        HpaSubLoc.ensembls= ReferenceSet(HpaSubLoc.id,
                         Ensembl2HpaSubLoc.hpasubloc_id, Ensembl2HpaSubLoc.ensembl_id,
                         Ensembl.id)

        
        hpasubloc2ensembls= {}
        for hpa_subloc_name in hpa_subloc_names:
            hpa_subloc= self.get_hpasubloc_by_name(hpa_subloc_name)
            
            hpasubloc2ensembls[hpa_subloc_name] = [ensembl for ensembl in hpa_subloc.ensembls]
        
        return hpasubloc2ensembls



    def get_ensembl2kegg(self, ensembl_ids):
        ensembl2kegg= {}
        for ensembl_id in ensembl_ids:
            ensembl= self.get_ensembl_by_id(ensembl_id)
            if not ensembl:
                continue

            results= self.store.find(Uniprot2KEGG, Uniprot2KEGG.uniprot_id == ensembl.uniprot_id)
            for result in results:
                if ensembl.id not in ensembl2kegg:
                    ensembl2kegg[ensembl.id] = []
                ensembl2kegg[ensembl.id].append(result.kegg_id)

        return ensembl2kegg
        

########################################################################################

############################### TYPE 2 ###########################################
#2. input list of ids returns a dictionary of target_id: [reference_list (objects)]

    def get_go2ensembl_by_ensembl(self, ensembl_ids):
        
        go2ensembl= {}
        for ensembl_id in ensembl_ids:
            e2gos= self.store.find(Ensembl2GO, Ensembl2GO.ensembl_id == unicode(ensembl_id))
            for e2go in e2gos:
                if e2go.go_id not in go2ensembl:
                    go2ensembl[e2go.go_id] = []
                go2ensembl[e2go.go_id].append(e2go.ensembl)
        
        return go2ensembl

    def get_uniprot2ensembl_by_ensembl(self, ensembl_ids):
        uniprot2ensembl= {}
        for ensembl_id in ensembl_ids:
            ensembl= self.store.find(Ensembl, Ensembl.id == unicode(ensembl_id)).one()
            if not ensembl:
                continue

            if ensembl.uniprot_id not in uniprot2ensembl:
                uniprot2ensembl[ensembl.uniprot_id]= []
            
            uniprot2ensembl[ensembl.uniprot_id].append(ensembl)
        
        return uniprot2ensembl

    def get_hpasubloc2ensembl_by_ensembl(self, ensembl_ids):
        pass

    def get_hpaclass2ensembl_by_ensembl(self, esnembl_ids):
        pass

    def get_kegg2ensembl_by_ensembl(self, ensembl_ids):
        pass


    def get_go2uniprot_by_uniprot(self, uniprot_ids):
        pass

    def get_kegg2uniprot_by_uniprot(self, uniprot_ids):
        pass

    def get_hpasubloc2uniprot_by_uniprot(self, uniprot_ids):
        pass

    def get_hpaclass2uniprot_by_uniprot(self, uniprot_ids):
        pass



##################################################################################

############################ Type 3 #################################
#  3. input list returns a generator of ids in the corresponding order

    def yield_ensembl2uniprot(self, ensembl_ids):
        """
            multiple genes can be coding for the same protein. the function is
            rewritten as ensembl2uniprots
        """
        for ensembl_id in ensembl_ids:
            ensembl= self.store.find(Ensembl, Ensembl.id == unicode(ensembl_id)).one()
            if ensembl:
                yield ensembl.uniprot_id
            else:
                yield "EnsemblIDNotFound"

    
    def yield_ensembl2entrez(self, ensembl_ids):
        for ensembl_id in ensembl_ids:
            ensembl= self.store.find(Ensembl, Ensembl.id == unicode(ensembl_id)).one()
            if ensembl:
                yield ensembl.entrez_id
            else:
                yield "EnsemblIDNotFound"
   
#######################################################################




##################################  TYPE 4 ###################################
#4. input list of ids returns a generator of lists. equivalent to type 1, 
#different data str.

    def yield_uniprot2entrez(self, uniprot_ids):
        
        for uniprot_id in uniprot_ids:
            results= self.store.find(Ensembl, Ensembl.uniprot_id == unicode(uniprot_id))
            yield [ensembl.entrez_id for ensembl in results]

##############################################################################



###################  TYPE 5  ##########################
#5. id vs. id mapping for one to one tables


    def get_entrez2uniprot(self, entrez_ids):
        pass


    def get_entrez2go(self, entrez_ids):
        pass

#######################################################


############ TYPE 6 Mappers ###########################
#6. id vs. list for one to many tables.
    def get_ensembl_by_uniprot_id(self, uniprot_id):
        return [e for e in self.store.find(Ensembl, Ensembl.uniprot_id == unicode(uniprot_id))]


###########################################################



###################   DB selectors  #######################

    def get_hpaclass_by_name(self, hpa_class_name):
        return self.store.find(HpaClass, HpaClass.name.lower() == unicode(hpa_class_name).lower()).one()

    def get_hpaclass_by_id(self, hpaclass_id):
        return self.store.find(HpaClass, HpaClass.id == int(hpaclass_id)).one()

    def get_hpasubloc_by_name(self, hpa_subloc_name):
        return self.store.find(HpaSubLoc, HpaSubLoc.name.lower() == unicode(hpa_subloc_name).lower()).one()
    
    def get_hpasubloc_by_id(self, hpasubloc_id):
        return self.store.find(HpaSubLoc, HpaSubLoc.id == int(hpasubloc_id)).one()


    def get_ensembl_by_symbol(self, symbol):
        return self.store.find(Ensembl, Ensembl.symbol.lower() == unicode(symbol).lower()).one()


    def get_go_by_id(self, go_id):
        return self.store.find(GO, GO.id == unicode(go_id)).one()


    def get_go_by_name(self, go_name):
        return self.store.find(GO, GO.name.lower()  == unicode(go_name).lower()).one()


    def get_uniprot_by_id(self, uniprot_id):
        return self.store.find(Uniprot, Uniprot.id  == unicode(uniprot_id)).one()

                                                                                        
    def get_ensembl_by_id(self, ensembl_id):
        return self.store.find(Ensembl, Ensembl.id == unicode(ensembl_id)).one()


############################################################

usage="""
hpa_class_names = ["Disease related genes","Enzymes", "Predicted secreted proteins"]


ensembl_ids= ["ENSG00000169245", "ENSG00000163737", "ENSG00000280165" ]

go_ids= ["GO:0006739","GO:0006741","GO:0006742","GO:0009455","GO:0019342","GO:0042964","GO:0042965","GO:0045454","GO:0046206","GO:0046207","GO:0051341","GO:0051353","GO:0051354","GO:0051775","GO:0051776","GO:0055114","GO:0071461","GO:0071941","GO:0075137","GO:1904732","GO:1904733","GO:1904734"]

s= Selector()
#ensembl2go = s.get_ensembl2go(ensembl_ids)
#ensembl2hpaclasses= s.get_ensembl2hpaclass(ensembl_ids)
hpaclass2ensembles= s.get_hpaclass2ensembls(hpa_class_names)

for hpaclass, ensembls in hpaclass2ensembles.iteritems(): 
    for ensembl in ensembls:
        
        print "\t".join([hpaclass, ensembl.id])
        
"""
