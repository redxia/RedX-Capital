import json
import pandas as pd
from utilities import util

with open("utilities\spine_mapping.jsonc","r") as read_json:
    df = json.load(read_json)

mapping_str = """SELECT * FROM research.kdolgin.ATEC_MAPPING_BUILD_FILE_KEEP;"""
ATEC_MAP = util.MAPPING('ATEC', 'PRODUCT', mapping_str)

#region segment
# TODO later, fix the mapping there is a bad dictionary parts
for i in df:
    # Product, product_type, segment. i iterates categories
    for j in df[i]:
        search_column = j
        #print(len(df[i][j]))
        for k in df[i][j]:
            #print(j)
            #print(df[i][j][k])
            #print(len(df[i][j][k]))
            value=" ".join(k.split('_'))
            for l in df[i][j][k]:
                print('printing df[i][j][k]')
                print(df[i][j][k])
                print('printing l')
                print(l)
                #if len(df[i][j][k][l]) == 1: # length 1 array use one arguement
                #print(k)
                    #print(df[i][j][k][l])
                #print(i)
                #ATEC_MAP.mapping(str_filter=df[i][j][k][0], value=value, search_column=search_column)
                #pass
# check length and if else branch to
#endregion segment

ATEC_MAP.get_dataframe().isnull().sum()