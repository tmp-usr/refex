import os
from collections import OrderedDict
from storm.locals import Store, create_database


tables= ["ensembl", "uniprot", "go", "hpaclass", "hpasubloc", "kegg",
         "ensembl2go","uniprot2hpaclass", "uniprot2hpasubloc", "ensembl2kegg" ]


sql_db_path= os.path.join(os.path.dirname(__file__), "../mapping/refex.db")

class DBBase(object):
    def __init__(self):
        self.sql_db_path= sql_db_path
        self.__init_database()
        self.create_table_strings= {}

    def __init_database(self):    
        """
        creates the sqlite database instance and checks if the database exists in biodb.
        """
        database= create_database("sqlite:%s" % self.sql_db_path)
        print "Created storm database from %s." % self.sql_db_path
        self.store= Store(database)
     
    def drop_table(self, table_name):
        drop_table_string= "drop table %s" %table_name 
        self.store.execute(drop_table_string)


    def drop_tables(self):
        
        drop_table_string= "drop table " 
        
        for table in tables:
            drop_table_str= drop_table_string + table
            try:
                self.store.execute(drop_table_str)
            except:
                continue

        self.store.commit()


    @property
    def generate_table_strings(self):

        self.create_table_strings["ensembl"]=  self.generate_create_table_string("ensembl", 
                                    OrderedDict([("id", "VARCHAR PRIMARY KEY"),
                                            ("entrez_id", "INTEGER"), ("uniprot_id", "VARCHAR"),
                                            ("symbol","VARCHAR"),("synonyms","VARCHAR")]),
                                            {"uniprot_id":("uniprot", "id")}) 
        
        self.create_table_strings["uniprot"]= self.generate_create_table_string("uniprot",
                                    OrderedDict([("id", "VARCHAR PRIMARY KEY"),
                                              ("name", "VARCHAR") ]) )
        
        self.create_table_strings["go"]= self.generate_create_table_string("go",
                                    OrderedDict([("id", "VARCHAR PRIMARY KEY"),
                                              ("name", "VARCHAR"), ("domain","INTEGER")]))
        

        self.create_table_strings["kegg"]= self.generate_create_table_string("kegg",
                                    OrderedDict([("id", "VARCHAR PRIMARY KEY"),
                                     ("name", "VARCHAR")]))

        self.create_table_strings["hpaclass"]= self.generate_create_table_string("hpaclass",
                                    OrderedDict([("id", "INTEGER PRIMARY KEY"),
                                                ("name", "VARCHAR")]))

        self.create_table_strings["hpasubloc"]= self.generate_create_table_string("hpasubloc",
                                   OrderedDict([("id", "INTEGER PRIMARY KEY"),
                                                ("name", "VARCHAR")]))
        
        self.create_table_strings["ensembl2go"]= self.generate_create_table_string("ensembl2go",
                                   OrderedDict([("id", "INTEGER PRIMARY KEY"),
                                                ("ensembl_id", "VARCHAR"), ("go_id", "VARCHAR")]),
                                                
                                                {"ensembl_id":("ensembl", "id"),
                                                 "go_id": ("go","id")})

        self.create_table_strings["uniprot2hpaclass"]= self.generate_create_table_string("uniprot2hpaclass",
                                    OrderedDict([("id","INTEGER PRIMARY KEY"),
                                                 ("uniprot_id","VARCHAR"), ("hpaclass_id", "INTEGER") ]),
                                                 
                                                 {"uniprot_id":("uniprot","id"), "hpaclass_id":("hpaclass","id")})

        self.create_table_strings["uniprot2hpasubloc"]= self.generate_create_table_string("uniprot2hpasubloc",
                                    OrderedDict([("id","INTEGER PRIMARY KEY"),
                                                 ("uniprot_id","VARCHAR"), ("hpasubloc_id", "INTEGER") ]),
                                                 {"uniprot_id":("uniprot","id"), "hpasubloc_id":("hpasubloc","id")})

        self.create_table_strings["ensembl2kegg"]=  self.generate_create_table_string("ensembl2kegg",
                                    OrderedDict([("id","INTEGER PRIMARY KEY"),
                                                 ("ensembl_id","VARCHAR"), ("kegg_id", "VARCHAR") ]),
                                                 {"ensembl_id":("ensembl","id"), "kegg_id":("kegg","id")})
        
        self.create_table_strings["ensembl2hpasubloc"]= self.generate_create_table_string("ensembl2hpasubloc",
                                    OrderedDict([("id","INTEGER PRIMARY KEY"),
                                                 ("ensembl_id","VARCHAR"), ("hpasubloc_id", "INTEGER") ]),
                                                 {"ensembl_id":("ensembl","id"), "hpasubloc_id":("hpasubloc","id")})

        self.create_table_strings["ensembl2hpaclass"]= self.generate_create_table_string("ensembl2hpaclass",
                                    OrderedDict([("id","INTEGER PRIMARY KEY"),
                                                 ("ensembl_id","VARCHAR"), ("hpaclass_id", "INTEGER") ]),
                                                 
                                                 {"ensembl_id":("ensembl","id"), "hpaclass_id":("hpaclass","id")})

        self.create_table_strings["uniprot2kegg"]= self.generate_create_table_string("uniprot2kegg",
                                    OrderedDict([("id","INTEGER PRIMARY KEY"),
                                                 ("uniprot_id","VARCHAR"), ("kegg_id", "INTEGER") ]),
                                                 
                                                 {"uniprot_id":("uniprot","id"), "kegg_id":("kegg","id")})

        return self.create_table_strings

    def create_table(self, table_name):
        self.store.execute(self.generate_table_strings[table_name])
        self.store.commit()

    
    def create_tables(self):
        for table_name, create_table_string in self.create_table_strings.iteritems():
            self.store.execute(create_table_string)
            self.store.commit() 


    def generate_create_table_string(self, table_name, tables, foreign_keys= {}):
        """
            table_name: str
            tables: OrderedDict with fieldname as keys and type as value
            foreign keys: with source_id as keys, and  (target_table, target_id)
            as values
        """
        
        starter= "CREATE TABLE %s " %table_name

        table_str= ""
        for table, table_type in tables.iteritems():
            table_str+= "%s %s, " %(table, table_type)

            
        table_str = "(%s" %table_str.rstrip(', ')
        
        foreign_key_str=""
        for source_id, (target_name, target_id) in foreign_keys.iteritems():
            foreign_key_str+=", FOREIGN KEY (%s) REFERENCES %s (%s)" %(source_id, target_name, target_id)
        
        foreign_key_str+= ");"

        return "".join([starter, table_str, foreign_key_str]) 


