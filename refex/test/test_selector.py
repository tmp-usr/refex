from refex.sqling.selector import Selector

sl= Selector()
#test_list= [e.id for e in sl.all_ensembls[:5]]

def test_uniprot2ensemb_by_ensembl():
    return sl.get_uniprot2ensembl_by_ensembl(test_list)

def test_ensembl2uniprot():
    return sl.get_ensembl2uniprot(test_list)


def test_ensembl2go():
    return sl.get_ensembl2go(test_list)


def test_uniprot2go():
    test_ids= open("test_proteins.txt").read().split("\n")
    return sl.get_uniprot2go(test_ids[:10])


def test_uniprot2ensembl():
    test_ids= open("test_proteins.txt").read().split("\n")
    return sl.get_uniprot2ensembl(test_ids[:10])

results= test_uniprot2ensembl()

for uniprot, ensembls in results.iteritems():
    print "######"
    print uniprot, [e.id for e in ensembls][0], [e.uniprot_id for e in ensembls][0]
    #for ensembl, gos in ensembl2gos.iteritems():
    #    print ensembl, [go.id for go in gos]

        
#type1_result= test_ensembl2go()

#for db, es in  type1_result.iteritems():
#    print db, ":", [e.id for e in es]




