import pickle
import pdb

### main_objects
from storm_objects import Uniprot, Ensembl, GO, HpaClass, HpaSubLoc

### intermediary_objects
from storm_objects import Ensembl2GO, Uniprot2HpaClass, Uniprot2HpaSubLoc
from storm_objects import Ensembl2HpaClass, Ensembl2HpaSubLoc
from storm_objects import Uniprot2KEGG

from db_base import DBBase


class Inserter(DBBase):
    def __init__(self):

        DBBase.__init__(self)
        
        #self.db_base.drop_tables()
        #self.db_base.create_tables()
        #self.drop_table(unicode("ensembl"))
        #self.generate_table_strings()
        #self.create_table("ensembl2hpaclass")
        #self.create_table("ensembl2hpasubloc")
        #self.insert_main_tables()
        self.insert_intermediary_tables()


    def insert_ensembl(self, ensemble_id, entrez_id, uniprot_id, symbol, synonyms):
        result= self.store.find(Ensembl, Ensembl.id == unicode(ensemble_id)).one()
        if not result:
            e= Ensembl()
            e.id= unicode(ensemble_id)
            e.entrez_id= int(entrez_id)
            e.uniprot_id= unicode(uniprot_id)
            e.symbol= unicode(symbol)
            e.synonyms= unicode(synonyms)

            self.store.add(e)
            self.store.commit()
   
    def insert_uniprot(self, uniprot_id, name):
        result= self.store.find(Uniprot, Uniprot.id == unicode(uniprot_id)).one()
        if not result:
            u= Uniprot()
            u.id= unicode(uniprot_id)
            u.name= unicode(name)

            self.store.add(u)
            self.store.commit()

    def insert_go(self, go_id, name, domain_id):
        result= self.store.find(GO, GO.id == unicode(go_id)).one()
        if not result:
        
            go = GO() 
            go.id= unicode(go_id)
            go.name= unicode(name)
            go.domain= int(domain_id) 

            self.store.add(go)
            self.store.commit()



    def insert_hpa_class(self, name):
        result= self.store.find(HpaClass, HpaClass.name == unicode(name)).one()
        if not result:
            hc= HpaClass()
            hc.name= unicode(name)
            self.store.add(hc)
            self.store.commit()

    def insert_hpa_sub_loc(self, name):
        result=  self.store.find(HpaSubLoc, HpaSubLoc.name == unicode(name)).one()
        if not result:
            hsl= HpaSubLoc()
            hsl.name= unicode(name)
            self.store.add(hsl)
            self.store.commit()


    def insert_kegg(self, kegg_id, name):
        result= self.store.find(KEGG, KEGG.id == unicode(kegg_id)).one()
        if not result:
            kegg= KEGG()
            kegg.id= unicode(kegg_id)
            kegg.name= unicode(name)

            self.store.add(kegg)
            self.store.commit()
    


    def insert_uniprots(self):
        f_ensemble_mapping = open("../mapping/hgnc.mapping.table.2016-07-15.xls")
        header= f_ensemble_mapping.next()

        for line in f_ensemble_mapping:
            cols= line.rstrip('\n').split('\t')
            
            prot_name= cols[2]
            prot_id= cols[11]
            
            if prot_id != "":
                self.insert_uniprot(prot_id, prot_name)
   

    def insert_ensembls(self):
        f_ensemble_mapping = open("../mapping/hgnc.mapping.table.2016-07-15.xls")
        header= f_ensemble_mapping.next()

        for line in f_ensemble_mapping:
            cols= line.rstrip('\n').split('\t')
           

            symbol= cols[1]
            synonyms= cols[4]
            entrez_id= cols[8]
            ensembl_id= cols[12]

            
            if entrez_id == "" or ensembl_id == "":
                continue
            self.insert_ensembl(ensembl_id, entrez_id, uniprot_id, symbol, synonyms)    

            

    def insert_hpa_protclasses_sublocs(self):
        protclasses= {}
        sublocs= {}
        with open("../mapping/proteinatlas.xls") as f_proteinatlas:
            for line in f_proteinatlas:
                cols= line.rstrip("\n").split("\t")
                protclass= cols[6]
                subloc= cols[15]
                
                for pclass in protclass.split(", "):


                    if pclass not in protclasses:
                        protclasses[pclass] = 1
                        self.insert_hpa_class(pclass)
                
                for sloc in subloc.split(", "):

                    if sloc not in sublocs:
                        sublocs[sloc] = 1
                        self.insert_hpa_sub_loc(sloc)


                self.store.commit()


    def insert_gos(self):
        """
            domains: 
                1: molecular_function
                2: biological_process
                3: cellular_components

        """
        domains= { "molecular_function":1, "biological_process":2, "cellular_component":3}
        f_go_mapping= open("../mapping/term.txt")
        
        for line in f_go_mapping:
            cols= line.rstrip("\n").split("\t")
            
            go_id = cols[3]
            name= cols[1]
            domain= cols[2]
            try:
                domain_id= domains[domain]
            except:
                continue


            self.insert_go(go_id, name, domain_id)


    def insert_main_tables(self):
        #self.insert_uniprots()
        self.insert_ensembls()
        #self.insert_gos()
        #self.insert_hpa_protclasses_sublocs()


    def insert_ensembl2gos(self):
        with open("../mapping/ensemble2go.txt") as f_e2go:
            for line in f_e2go:
                cols= line.rstrip("\n").split("\t")
                ensembl_id= cols[1]
                go_name= cols[4]
                ensembl= self.store.find(Ensembl, Ensembl.id == unicode(ensembl_id)).one()
                go= self.store.find(GO, GO.name == unicode(go_name)).one()
                if ensembl and go:
                    e2go= Ensembl2GO()
                    e2go.ensembl_id = ensembl.id
                    e2go.go_id= go.id
                    
                    self.store.add(e2go)
            
                self.store.commit()



    def insert_uniprot2hpaclass_and_subloc(self):
       
        uniprot2hpasubloc= {}
        uniprot2hpaclass= {}

        with open("../mapping/proteinatlas.xls") as f_ensembl2hpa:
            f_ensembl2hpa.next()
            for line in f_ensembl2hpa:
                cols= line.rstrip("\n").split("\t")
                
                ensembl_id= cols[2]
                uniprot_name= cols[3]
                prot_class_names= cols[6].split(', ')
                sub_loc_names= cols[15].split(', ')

                ensembl= self.store.find(Ensembl, Ensembl.id == unicode(ensembl_id)).one()
                if ensembl:
                    uniprot_id= ensembl.uniprot_id
               
                for sub_loc_name in sub_loc_names:
                
                    sub_loc= self.store.find(HpaSubLoc, HpaSubLoc.name == unicode(sub_loc_name)).one()
                    if sub_loc:
                        subloc_id= sub_loc.id
                
                        if (uniprot_id, subloc_id) not in uniprot2hpasubloc:
                            uniprot2hpasubloc[(uniprot_id, subloc_id)]= 1

                            print uniprot_id, subloc_id

                            u2hsl= Uniprot2HpaSubLoc()
                            u2hsl.uniprot_id = uniprot_id
                            u2hsl.hpasubloc_id= subloc_id 
                        
                            self.store.add(u2hsl)


                for prot_class_name in prot_class_names:
                    prot_class= self.store.find(HpaClass, HpaClass.name == unicode(prot_class_name)).one()
                    if prot_class:
                        prot_class_id= prot_class.id
                       
                        if (uniprot_id, prot_class_id) not in uniprot2hpaclass:
                            uniprot2hpaclass[(uniprot_id, prot_class_id)]= 1

                            print uniprot_id, prot_class_id

                            u2hc= Uniprot2HpaClass() 
                            u2hc.uniprot_id= uniprot_id
                            u2hc.hpaclass_id= prot_class_id
                    
                            self.store.add(u2hc)


                self.store.commit()

    def insert_ensembl2hpaclass_and_subloc(self):
        ensembl2hpasubloc= {}
        ensembl2hpaclass= {}

        with open("../mapping/proteinatlas.xls") as f_ensembl2hpa:
            f_ensembl2hpa.next()
            for line in f_ensembl2hpa:
                cols= line.rstrip("\n").split("\t")
                
                ensembl_id= cols[2]
                prot_class_names= cols[6].split(', ')
                sub_loc_names= cols[15].split(', ')

                ensembl= self.store.find(Ensembl, Ensembl.id == unicode(ensembl_id)).one()
                if ensembl:

                    for sub_loc_name in sub_loc_names:
                    
                        sub_loc= self.store.find(HpaSubLoc, HpaSubLoc.name == unicode(sub_loc_name)).one()
                        if sub_loc:
                            subloc_id= sub_loc.id
                    
                            if (ensembl.id, subloc_id) not in ensembl2hpasubloc:
                                ensembl2hpasubloc[(ensembl.id, subloc_id)]= 1
                            
                                e2hsl= Ensembl2HpaSubLoc()
                                e2hsl.ensembl_id = ensembl.id
                                e2hsl.hpasubloc_id= subloc_id 
                        
                                print ensembl.id, prot_class_id
                                self.store.add(e2hsl)


                    for prot_class_name in prot_class_names:
                        prot_class= self.store.find(HpaClass, HpaClass.name == unicode(prot_class_name)).one()
                        if prot_class:
                            prot_class_id= prot_class.id
                            
                            if (ensembl.id, prot_class_id) not in ensembl2hpaclass:
                                ensembl2hpaclass[(ensembl.id, prot_class_id)] = 1

                                e2hc= Ensembl2HpaClass() 
                                e2hc.ensembl_id= ensembl.id
                                e2hc.hpaclass_id= prot_class_id
                                
                                print ensembl.id, prot_class_id
                                self.store.add(e2hc)


                self.store.commit()


    def insert_uniprot2kegg(self):
        uniprot2kegg= {}

        with open("../mapping/uniprot2ko_hgnc.txt") as f_uniprot2ko:
            for line in f_uniprot2ko:
                cols= line.rstrip("\n").split("\t")
                
                uniprot_id= cols[0]
                kegg_id= cols[2]

                if (uniprot_id, kegg_id) not in uniprot2kegg:
                    uniprot2kegg[(uniprot_id, kegg_id)] = 1

                    u2kegg= Uniprot2KEGG()
                    u2kegg.uniprot_id= unicode(uniprot_id)
                    u2kegg.kegg_id= unicode(kegg_id)
                    
                    print uniprot_id, kegg_id
                    self.store.add(u2kegg)
        
            self.store.commit()

    def insert_intermediary_tables(self):
        #self.insert_uniprot2hpaclass_and_subloc()
        #self.insert_ensembl2gos()
        #self.insert_ensembl2hpaclass_and_subloc()
        self.insert_uniprot2kegg() 

ins= Inserter()


trash= """
    def update_uniprot2hpa(self, uniprot_id, name="", hpa_class_name="", hpa_sub_loc_name="", go_id=""):
        result= self.store.find(Uniprot2Hpa, Uniprot2Hpa.id == uniprot_id).one() 
        assert result is not None, "Insert the uniprot2hpa first!"
        
        u2h= result
        
        if uniprot_id != "":
            u2h.id= unicode(uniprot_id)
        
        if name != "":
            u2h.name= unicode(name)
        
        if hpa_class_name != "":
            u2h.hpa_class_id= self.get_hpa_class_by_name(hpa_class_name).id
        
        if hpa_sub_loc_name != "":
            u2h.hpa_sub_loc_id= self.get_hpa_sub_loc_by_name(hpa_cub_loc_name).id
        
        if go_id != "":
            u2h.go_id= unicode(go_id)

        self.store.commit()

    def update_ensemble2biodb(self, ensemble_id, entrez_id= 0, prot_id= ""):
        result= self.store.find(Ensemble2Biodb, Ensemble2Biodb.id == ensemble_id).one()
        assert result is not None, "Insert the ensemble2biodb first!"
        
        e2b= result
        
        if entrez_id != 0:
            e2b.entrez_id= int(entrez_id)
        
        if prot_id != "":
            e2b.prot_id= unicode(prot_id)

        
        self.store.commit()



        create_ensemble_string='CREATE TABLE ensemble2biodb (id VARCHAR PRIMARY KEY, entrez_id INTEGER, prot_id VARCHAR, go_id VARCHAR, kegg_id VARCHAR, FOREIGN KEY (prot_id) REFERENCES uniprot2hpa (id))'
        
        create_uniprot_string= 'CREATE TABLE uniprot2hpa (id VARCHAR PRIMARY KEY, name VARCHAR, hpa_class_id INTEGER, hpa_sub_loc_id INTEGER, FOREIGN KEY (hpa_class_id) REFERENCES hpaclass (id), FOREIGN KEY (hpa_sub_loc_id) REFERENCES hpasubloc (id), FOREIGN KEY (go_id) REFERENCES go (id))'

        create_hpaclass_string= 'CREATE TABLE hpaclass (id INTEGER PRIMARY KEY, name VARCHAR)'
        create_hpasubloc_string= 'CREATE TABLE hpasubloc (id INTEGER PRIMARY KEY, name VARCHAR)'
        create_go_string= 'CREATE TABLE go (id INTEGER PRIMARY KEY, name VARCHAR)'



    def insert_ensembls_uniprots(self):
        ensemble2subloc= pickle.load(open("../mapping/ensemble2subloc.dmp"))
        ensemble2proclass= pickle.load(open("../mapping/ensemble2proclass.dmp"))
        
        f_ensemble_mapping = open("../mapping/hgnc.mapping.table.2016-07-15.xls")
        #f_go_mapping= open("../mapping/ensemble2go.txt")
        header= f_ensemble_mapping.next()

        for line in f_ensemble_mapping:
            cols= line.rstrip('\n').split('\t')
            
            prot_name= cols[2]
            entrez_id= cols[8]
            prot_id= cols[11]
            ensemble_id= cols[12]

        
            subloc= ensemble2subloc[ensemble_id]
            protclass= ensemble2proclass[ensemble_id] 


            s_subloc= self.store.find(HpaSubLoc, HpaSubLoc.name == unicode(subloc)).one()
            s_protclass= self.store.find(HpaClass, HpaClass.name == unicode(protclass)).one()

            pdb.set_trace()

            self.insert_ensemble2biodb(ensemble_id, entrez_id, prot_id)
            
            try:

                self.insert_uniprot2hpa(prot_id, name=prot_name, hpa_class_name=s_protclass.id, hpa_sub_loc_name=s_subloc.id)
            except:
                pdb.set_trace()




    def insert_ensembl2uniprot(self):
        f_ensemble_mapping = open("../mapping/hgnc.mapping.table.2016-07-15.xls")
        header= f_ensemble_mapping.next()

        for line in f_ensemble_mapping:
            cols= line.rstrip('\n').split('\t')         
            
            uniprot_id= cols[11]
            ensembl_id= cols[12]


            if ensemble_id == "" or uniprot_id == "":
                continue


            e2u = Ensembl2Uniprot()
            e2u.ensembl_id= ensemble_id
            e2u.uniprot_id= uniprot_id


"""
