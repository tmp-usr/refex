from selector import Selector


class GSBuilder(object):
    def __init__(self, db_name, is_entrez = True):
        self.db_name = db_name
        self.is_entrez= is_entrez
        self.selector= Selector()
        
    def build(self, gmt_file_path):
        
        
        if self.db_name == "hpa_class":
            gene_set_names= [hc.name for hc in self.selector.get_all_hpaclasses()]
            geneset2e= self.selector.get_hpaclass2ensembls(gene_set_names)
        
        elif self.db_name == "hpa_subloc":
            gene_set_names= [hsl.name for hsl in self.selector.get_all_hpasublocs()]
            gene_set_names.remove(u"Miscellaneous")
            geneset2e= self.selector.get_hpasubloc2ensembls(gene_set_names)
        
        with open(gmt_file_path, "w") as f_gmt:
            for gene_set_name, es in geneset2e.iteritems():
                gene_set_name= gene_set_name.upper().replace(" ","_")
                fields= [gene_set_name, "ref/%s"%gene_set_name, "\t".join([str(e.entrez_id) for e in es])]
                line= "\t".join(fields)+"\n"
                f_gmt.write(line)
    
#gs= GSBuilder("hpa_class")

#gs.build("../gsea/gene_sets/hpaclass.121016.entrez.gmt")

