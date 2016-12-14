from storm.locals import *

class Uniprot(object):
    __storm_table__= "uniprot"
    id= Unicode(primary = True)
    name= Unicode()

class Ensembl(object):
    __storm_table__= "ensembl"
    id= Unicode(primary = True)
    entrez_id= Int()
    uniprot_id= Unicode()
    symbol= Unicode()
    synonyms= Unicode()
    protein= Reference(uniprot_id, Uniprot.id)

class GO(object):
    __storm_table__=  "go"
    id= Unicode(primary=True)
    name= Unicode()
    domain= Int() 


class HpaClass(object):
    __storm_table__= "hpaclass"
    id= Int(primary=True)
    name= Unicode()


class HpaSubLoc(object):
    __storm_table__= "hpasubloc"
    id= Int(primary= True)
    name= Unicode()


class KEGG(object):
    __storm_table__= "kegg"
    id= Unicode(primary= True)
    name= Unicode()


class Ensembl2GO(object):
    __storm_table__= "ensembl2go"
    id=Int(primary = True)
    ensembl_id= Unicode()
    go_id= Unicode()
    ensembl= Reference(ensembl_id, Ensembl.id)
    go= Reference(go_id, GO.id)

class Ensembl2HpaClass(object):
    __storm_table__= "ensembl2hpaclass"
    id = Int(primary = True)
    ensembl_id = Unicode()
    hpaclass_id= Int()
    ensembl= Reference(ensembl_id, Ensembl.id)
    hpaclass= Reference(hpaclass_id, HpaClass.id)

class Ensembl2HpaSubLoc(object):
    __storm_table__ = "ensembl2hpasubloc"
    id= Int(primary= True)
    ensembl_id= Unicode()
    hpasubloc_id= Int()
    ensembl= Reference(ensembl_id, Ensembl.id)
    hpasubloc= Reference(hpasubloc_id, HpaSubLoc.id)


class Uniprot2HpaClass(object):
    __storm_table__= "uniprot2hpaclass"
    id= Int(primary = True)
    uniprot_id= Unicode()
    hpaclass_id= Int()
    uniprot= Reference(uniprot_id, Uniprot.id)
    hpaclass= Reference(hpaclass_id, HpaClass.id)
    

class Uniprot2HpaSubLoc(object):
    __storm_table__= "uniprot2hpasubloc"
    id= Int(primary = True)
    uniprot_id= Unicode()
    hpasubloc_id= Int()
    uniprot= Reference(uniprot_id, Uniprot.id)
    hpasubloc= Reference(hpasubloc_id, HpaSubLoc.id)


class Ensembl2KEGG(object):
    __storm_table__= "ensembl2kegg"
    id=Int(primary = True)
    ensembl_id= Unicode()
    kegg_id= Int()
    ensembl= Reference(ensembl_id, Ensembl.id)
    kegg= Reference(kegg_id, KEGG.id)


class Uniprot2KEGG(object):
    __storm_table__= "uniprot2kegg"
    id=Int(primary = True)
    uniprot_id= Unicode()
    kegg_id= Unicode()
    ensembl= Reference(uniprot_id, Uniprot.id)
    kegg= Reference(kegg_id, KEGG.id)




trash= """
class Ensembl2Uniprot(object):
    __storm_table__= "ensembl2uniprot"
    id= Int(primary= True)
    ensembl_id= Unicode()
    uniprot_id= Unicode()
    ensembl= Reference(ensembl_id, Ensembl.id)
    uniprot= Reference(uniprot_id, Uniprot.id)
"""

