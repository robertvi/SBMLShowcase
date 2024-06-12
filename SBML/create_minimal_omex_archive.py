#!/usr/bin/env python

'''
use pymetadata module to create a minimal valid combine archive
using LEMS_NML2_Ex9_FN.sbml and LEMS_NML2_Ex9_FN.sedml
'''

import sys
sys.path.append("..")
import utils
import os
import re
import shutil


sbml_file = 'LEMS_NML2_Ex9_FN.sbml'
sedml_file = 'LEMS_NML2_Ex9_FN.sedml'
# _old version
sedml_file = 'LEMS_NML2_Ex9_FN_old.sedml'

# create temporary sedml file with xmlns:sbml attribute if missing
sedml_file_temp = utils.add_xmlns_sbml_attribute_if_missing(sedml_file, sbml_file)

# save sedml file in temp folder 
if not os.path.exists('temp_sedml_files'):
    os.makedirs('temp_sedml_files')
temp_file_name = (re.sub(r'(\.sedml)', r'_temp\1', sedml_file))
with open('temp_sedml_files/' + temp_file_name, 'w') as f:
    f.write(sedml_file_temp) 

sedml_filepath = os.path.join('temp_sedml_files', temp_file_name)
print(sedml_file)

print(utils.get_entry_format(sedml_filepath, 'SEDML'))

utils.create_omex(sedml_filepath,sbml_file)

message = utils.run_biosimulators_docker('tellurium',sedml_file,sbml_file)[1][3:-3]

print(message)

## remove 'temp_sedml_files' folder
#shutil.rmtree('temp_sedml_files')
print('Finished')
