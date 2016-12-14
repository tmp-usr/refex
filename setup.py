from setuptools import setup

setup(
      name             = 'refex',
      version          = '0.0.1',
      description      = 'Biological database cross-referencing tool.',
      long_description = open('README.md').read(),
      license          = 'MIT',
      url              = 'http://github.com/tmp-usr/refex/',
      author           = 'Kemal Sanli',
      author_email     = 'kemalsanli1@gmail.com',
      classifiers      = ['Topic :: Scientific/Engineering :: Bio-Informatics'],
      packages         = ['refex', 
                          'refex/gsea',
                          'refex/sqling',
                          ],
     
      include_package_data = True,
      package_dir= {"refex":'refex'},
      package_data = {'refex': [
                          'mapping/refex.db',
                          'gsea/gene_sets/*.gmt'
          ] } ,      
      install_requires = ['storm'],
)
