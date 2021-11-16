# Name: Redmond Xia
# Date: 2/16/2021
# Description: This scripts maps out alphatec

import pandas as pd
from utilities import util
%load_ext autoreload
%autoreload 2
#import re
#import numpy as np

ATEC_MAPPING_STR = """SELECT * 
                      FROM research.kdolgin.ATEC_MAPPING_BUILD_FILE_KEEP;"""

#ATEC_MAP = util.connect_snwflk(ATEC_MAPPING_STR)

#region testing checking mapping function 
#plt as plate also
df = ATEC_MAP
category ="SEGMENT"
str_filter = ".*BLADE.*"
search_column="PRODUCT"

#region extra str args
second_str=False
str_filter2=".*anterior.*"
negation_2nd=False
third_str=False
str_filter3="\\bTI\\b"
negation_3rd=False
#endregion extra str

DSCRPT_NULLS = df.loc[df[category].isnull(), search_column]
MASK = DSCRPT_NULLS.str.contains(str_filter, case=False, regex=True)
MASK.sum()

MASK = MASK[MASK == True]

#region second str
if second_str: # does not contain second string
    if third_str:
        if negation_2nd:
            if negation_3rd:
                MASK = MASK & ~df.loc[MASK.index, search_column].str.contains(str_filter2, 
                                                                            case=False, regex=True) & \
                                ~df.loc[MASK.index, search_column].str.contains(str_filter3, 
                                                                                case=False, regex=True)
            else:
                MASK = MASK & ~df.loc[MASK.index, search_column].str.contains(str_filter2, 
                                                                            case=False, regex=True) & \
                                df.loc[MASK.index, search_column].str.contains(str_filter3, 
                                                                            case=False, regex=True)
        else:
            if negation_3rd:
                MASK = MASK & df.loc[MASK.index, search_column].str.contains(str_filter2, 
                                                                            case=False, regex=True) & \
                            ~df.loc[MASK.index, search_column].str.contains(str_filter3, 
                                                                            case=False, regex=True)
            else:
                MASK = MASK & df.loc[MASK.index, search_column].str.contains(str_filter2, 
                                                                                case=False, regex=True) & \
                            df.loc[MASK.index, search_column].str.contains(str_filter3, 
                                                                                case=False, regex=True)
    else:
        if negation_2nd:
            MASK = MASK & ~df.loc[MASK.index, search_column].str.contains(str_filter2, 
                                                                            case=False, regex=True)
        else:
            MASK = MASK & df.loc[MASK.index, search_column].str.contains(str_filter2, 
                                                                            case=False, regex=True)
#endregion second str

MASK.sum()
MASK = MASK[MASK == True]
df.loc[MASK.index, search_column]#.to_csv("plate_lvl_1.csv", index=False)
df.loc[MASK.index, category]
df.loc[MASK.index, "MAX_DESCRIPTION"]
#df.loc[MASK.index, category] = value
#endregion checking mapping function

ATEC_MAP = util.MAPPING(ticker="ATEC",category="PRODUCT", mapping_str=ATEC_MAPPING_STR)

#region PRODUCT MAPPING # uses a negation argument
# util.mapping(df=ATEC_MAP, category="PRODUCT", str_filter="guide ?wire", value="GUIDEWIRE")

# util.mapping(df=ATEC_MAP, category="PRODUCT", str_filter=".*\\bscre?ws?\\b.*", value="SET SCREW", 
#                                               second_str=True, str_filter2=".*\\bsets?\\b.*")

# util.mapping(df=ATEC_MAP, category="PRODUCT", str_filter=".*\\bscre?ws?\\b.*", value="FIXED-ANGLE", 
#                                               second_str=True, str_filter2=".*\\bfixed\\b.*")
# util.mapping(df=ATEC_MAP, category="PRODUCT", str_filter=".*\\bscre?ws?\\b.*", value="FIXED-ANGLE", 
#                                               second_str=True, str_filter2=".*uni.*")
# util.mapping(df=ATEC_MAP, category="PRODUCT", str_filter=".*\\bscre?ws?\\b.*", value="FIXED-ANGLE", 
#                                               second_str=True, str_filter2=".*\\bmonoaxial\\b.*")

# util.mapping(df=ATEC_MAP, category="PRODUCT", str_filter=".*\\bscre?ws?\\b.*", value="VARIABLE-ANGLE", 
#                                               second_str=True, str_filter2=".*variable.*")
# util.mapping(df=ATEC_MAP, category="PRODUCT", str_filter=".*\\bscre?ws?\\b.*", value="VARIABLE-ANGLE", 
#                                               second_str=True, str_filter2=".*poly.*")

# util.mapping(df=ATEC_MAP, category="PRODUCT", str_filter=".*\\brod?\\b.*", value="SPINAL ROD")
# util.mapping(df=ATEC_MAP, category="PRODUCT", str_filter=".*\\bdrills?\\b.*", value="ACCESSORIES")
# util.mapping(df=ATEC_MAP, category="PRODUCT", str_filter=".*\\bconnectors?\\b.*", value="SPINAL CONNECTOR", 
#                                               second_str=True, str_filter2=".*\\bcrosslinks?\\b.*", negation_2nd=True)
# util.mapping(df=ATEC_MAP, category="PRODUCT", str_filter=".*\\bcrosslinks?\\b.*", value="SPINAL CROSSLINK", 
#                                               second_str=True, str_filter2=".*\\bconnectors?\\b.*", negation_2nd=True)

# util.mapping(df=ATEC_MAP, category="PRODUCT", str_filter=".*\\bspacers?\\b.*", value="STANDARD SPACER", 
#                                               second_str=True, str_filter2=".*grafts?.*", negation_2nd=True)
# util.mapping(df=ATEC_MAP, category="PRODUCT", str_filter=".*\\bspacers?\\b.*", value="GRAFT SPACER", 
#                                               second_str=True, str_filter2=".*grafts?.*", negation_2nd=True)

# util.mapping(df=ATEC_MAP, category="PRODUCT", str_filter=".*\\bplates?\\b.*", value="ONE-LEVEL PLATE", 
#                                               second_str=True, str_filter2="\\b1\\b", negation_2nd=True, 
#                                               third_str=True, str_filter3="\\blevels?\\b")

# util.mapping(df=ATEC_MAP, category="PRODUCT", str_filter=".*\\bplates?\\b.*", value="ONE-LEVEL PLATE", 
#                                               second_str=True, str_filter2="\\b1\\b", negation_2nd=True, 
#                                               third_str=True, str_filter3="\\blvls?\\b")

# util.mapping(df=ATEC_MAP, category="PRODUCT", str_filter=".*\\bplates?\\b.*", value="TWO-LEVEL PLATE", 
#                                               second_str=True, str_filter2="\\b2\\b", negation_2nd=True, 
#                                               third_str=True, str_filter3="\\blevels?\\b")
# util.mapping(df=ATEC_MAP, category="PRODUCT", str_filter=".*\\bplates?\\b.*", value="TWO-LEVEL PLATE", 
#                                               second_str=True, str_filter2="\\b2\\b", negation_2nd=True, 
#                                               third_str=True, str_filter3="\\blvls?\\b")
# util.mapping(df=ATEC_MAP, category="PRODUCT", str_filter=".*\\bplates?\\b.*", value="MULTI-LEVEL PLATE", 
#                                               second_str=True, str_filter2="\\b3\\b", negation_2nd=True, 
#                                               third_str=True, str_filter3="\\blevels?\\b")
# util.mapping(df=ATEC_MAP, category="PRODUCT", str_filter=".*\\bplates?\\b.*", value="MULTI-LEVEL PLATE", 
#                                               second_str=True, str_filter2="\\b3\\b", negation_2nd=True, 
#                                               third_str=True, str_filter3="\\blvls?\\b")

# util.mapping(df=ATEC_MAP, category="PRODUCT", str_filter=".*\\bplates?\\b.*", value="MULTI-LEVEL PLATE", 
#                                               second_str=True, str_filter2="\\b4\\b", negation_2nd=True, 
#                                               third_str=True, str_filter3="\\blevels?\\b")
# util.mapping(df=ATEC_MAP, category="PRODUCT", str_filter=".*\\bplates?\\b.*", value="MULTI-LEVEL PLATE", 
#                                               second_str=True, str_filter2="\\b4\\b", negation_2nd=True, 
#                                               third_str=True, str_filter3="\\blvls?\\b")

# util.mapping(df=ATEC_MAP, category="PRODUCT", str_filter=".*plate.*", value="ANTERIOR PLATE", 
#                           second_str=True, str_filter2=".*anterior.*")
# util.mapping(df=ATEC_MAP, category="PRODUCT", str_filter=".*\\bcages?\\b.*", value="STANDARD SPACER", 
#                                               second_str=True, str_filter2=".*grafts?.*", negation_2nd=True) # cages are grafts, ask kenny

# util.mapping(df=ATEC_MAP, category="PRODUCT", str_filter="^rods?.*", value="SPINAL ROD", 
#                                               second_str=True, str_filter2=".*\\brod?\\b.*", negation_2nd=True) # Missed beginning rods words
# util.mapping(df=ATEC_MAP, category="PRODUCT", str_filter=".*\\bhooks?\\b.*", value="ACCESSORIES", 
#                                               second_str=False) # Missed beginning rods words
#endregion product mapping
# ask about cage and the additional
# do see some errors in plate, graft plates
# very few spacers are graft

#region PRODUCT TYPE MAPPING
# SEt screws are rod fixations
# SPACERS are INTERBODY DEVICES
util.mapping(df=ATEC_MAP, category="PRODUCT_TYPE", str_filter=".*\\bscre?ws?\\b.*", value="PEDICLE SCREW", 
                                                   second_str=True, str_filter2=".*ped.*")
util.mapping(df=ATEC_MAP, category="PRODUCT_TYPE", str_filter="\\bspacer\\b", value="INTERBODY DEVICE", search_column="PRODUCT")
util.mapping(df=ATEC_MAP, category="PRODUCT_TYPE", str_filter="\\brod\\b", value="ROD FIXATION", search_column="PRODUCT")

util.mapping(df=ATEC_MAP, category="PRODUCT_TYPE", str_filter="\\baccessories\\b", value="ACCESSORIES", search_column="PRODUCT")
util.mapping(df=ATEC_MAP, category="PRODUCT_TYPE", str_filter="SET SCREW", value="ROD FIXATION", search_column="PRODUCT")
util.mapping(df=ATEC_MAP, category="PRODUCT_TYPE", str_filter="ANTERIOR PLATE", value="STABILIZATION PLATE", search_column="PRODUCT")
# Screw and plates are harder, what makes a pedicle screw and plate etc...
#endregion PRODUCT TYPE MAPPING

#region SEGMENT
#SPINES are SCREWS, INTERBODY DEVICE, ROD, PLATE, 
# fiber, profuse, neocore, shields, putty are biologics
util.mapping(df=ATEC_MAP, category="SEGMENT", str_filter="INTERBODY", value="SPINAL IMPLANTS", search_column="PRODUCT_TYPE")
util.mapping(df=ATEC_MAP, category="SEGMENT", str_filter="ROD", value="SPINAL IMPLANTS", search_column="PRODUCT_TYPE")
#biologics
util.mapping(df=ATEC_MAP, category="SEGMENT", str_filter="\\bfibers?\\b", value="BIOLOGICS", search_column="MAX_DESCRIPTION")
util.mapping(df=ATEC_MAP, category="SEGMENT", str_filter="\\bprofuses?\\b", value="BIOLOGICS", search_column="MAX_DESCRIPTION")
util.mapping(df=ATEC_MAP, category="SEGMENT", str_filter="\\bneocores?\\b", value="BIOLOGICS", search_column="MAX_DESCRIPTION")
util.mapping(df=ATEC_MAP, category="SEGMENT", str_filter="shields?", value="BIOLOGICS", search_column="MAX_DESCRIPTION")
util.mapping(df=ATEC_MAP, category="SEGMENT", str_filter="puttys?", value="BIOLOGICS", search_column="MAX_DESCRIPTION")
#endregion SEGMENT

#region BRAND
util.mapping(df=ATEC_MAP, category="BRAND", str_filter="ZODIACS?", value="ZODIAC", search_column="MAX_DESCRIPTION")
util.mapping(df=ATEC_MAP, category="BRAND", str_filter="ILLICOS?", value="ILLICO", search_column="MAX_DESCRIPTION")
util.mapping(df=ATEC_MAP, category="BRAND", str_filter="ARSENALS?", value="ARSENAL", search_column="MAX_DESCRIPTION")
util.mapping(df=ATEC_MAP, category="BRAND", str_filter="SOLANAS?", value="SOLANAS", search_column="MAX_DESCRIPTION")
util.mapping(df=ATEC_MAP, category="BRAND", str_filter="ASPIDAS?", value="ASPIDA", search_column="MAX_DESCRIPTION")
util.mapping(df=ATEC_MAP, category="BRAND", str_filter="SOLUS?", value="SOLUS", search_column="MAX_DESCRIPTION")
util.mapping(df=ATEC_MAP, category="BRAND", str_filter="XENON", value="XENON", search_column="MAX_DESCRIPTION")
util.mapping(df=ATEC_MAP, category="BRAND", str_filter="AMP", value="AMP", search_column="MAX_DESCRIPTION")
util.mapping(df=ATEC_MAP, category="BRAND", str_filter=".*\\bOSSEOSCREWS?\\b.*", value="OSSEOSCREW", search_column="MAX_DESCRIPTION")
util.mapping(df=ATEC_MAP, category="BRAND", str_filter=".*\\bTRESTLES?\\b.*", value="TRESTLE LUXE", 
                                                                             search_column="MAX_DESCRIPTION")
util.mapping(df=ATEC_MAP, category="BRAND", str_filter=".*\\bINVICTUS?\\b.*", value="INVICTUS", 
                                                                             search_column="MAX_DESCRIPTION")
                                                                             
# BATTALION
util.mapping(df=ATEC_MAP, category="BRAND", str_filter=".*\\bBATTALIONS?\\b.*", value="BATTALION PS", 
                          search_column="MAX_DESCRIPTION", second_str=True, str_filter2=".*\\bPS\\b.*")
util.mapping(df=ATEC_MAP, category="BRAND", str_filter=".*\\bBATTALIONS?\\b.*", value="BATTALION LATERAL", 
                          search_column="MAX_DESCRIPTION", second_str=True, str_filter2=".*\\bLATERAL\\b.*")
util.mapping(df=ATEC_MAP, category="BRAND", str_filter=".*\\bBATTALION\\b.*", value="BATTALION PC", 
                          search_column="MAX_DESCRIPTION", second_str=True, str_filter2=".*\\bPC\\b.*")
util.mapping(df=ATEC_MAP, category="BRAND", str_filter=".*\\bBATTALION\\b.*", value="BATTALION", search_column="MAX_DESCRIPTION")

# IDENTITI
util.mapping(df=ATEC_MAP, category="BRAND", str_filter=".*\\bIDENTITI\\b.*", value="IDENTITI PS", 
                          search_column="MAX_DESCRIPTION", second_str=True, str_filter2=".*\\bPS\\b.*")
util.mapping(df=ATEC_MAP, category="BRAND", str_filter=".*\\bIDENTITI\\b.*", value="IDENTITI CERVICAL", 
                          search_column="MAX_DESCRIPTION", second_str=True, str_filter2=".*\\bCERVICAL\\b.*")
util.mapping(df=ATEC_MAP, category="BRAND", str_filter=".*\\bIDENTITI\\b.*", value="IDENTITI PC", 
                          search_column="MAX_DESCRIPTION", second_str=True, str_filter2=".*\\bPC\\b.*")
util.mapping(df=ATEC_MAP, category="BRAND", str_filter=".*\\bIDENTITI\\b.*", value="IDENTITI PO", 
                          search_column="MAX_DESCRIPTION", second_str=True, str_filter2=".*\\bPO\\b.*")
util.mapping(df=ATEC_MAP, category="BRAND", str_filter=".*\\bIDENTITI\\b.*", value="IDENTITI ALIF", 
                          search_column="MAX_DESCRIPTION", second_str=True, str_filter2=".*\\bALIF\\b.*",
                          third_str=True, str_filter3=".*\\bPS\\b.*",negation_3rd=True)

# NOVEL                          
util.mapping(df=ATEC_MAP, category="BRAND", str_filter=".*\\bNOVEL\\b.*", value="NOVEL XS", 
                          search_column="MAX_DESCRIPTION", second_str=True, str_filter2=".*\\bXS\\b.*")
util.mapping(df=ATEC_MAP, category="BRAND", str_filter=".*\\bNOVEL\\b.*", value="NOVEL CP", 
                          search_column="MAX_DESCRIPTION", second_str=True, str_filter2=".*\\bCP\\b.*")
util.mapping(df=ATEC_MAP, category="BRAND", str_filter="NOVEL", value="NOVEL", search_column="MAX_DESCRIPTION")

util.mapping(df=ATEC_MAP, category="BRAND", str_filter=".*\\bATEC\\b.*", value="ATEC ALIF", 
                          search_column="MAX_DESCRIPTION", second_str=True, str_filter2=".*\\bALIF\\b.*")
util.mapping(df=ATEC_MAP, category="BRAND", str_filter=".*\\bATEC\\b.*", value="ATEC LLIF", 
                          search_column="MAX_DESCRIPTION", second_str=True, str_filter2=".*\\bLLIF\\b.*")

util.mapping(df=ATEC_MAP, category="BRAND", str_filter=".*\\bTRANSCEND\\b.*", value="TRANSCEND LIF", 
                          search_column="MAX_DESCRIPTION", second_str=True, str_filter2=".*\\bLLIF\\b.*")
#endregion BRAND

#region afterlogic
# PRODUCT START
util.mapping(df=ATEC_MAP, category="PRODUCT_TYPE", str_filter="SPINAL CONNECTO", value="CONNECTORS/PLATES", 
                          search_column="PRODUCT")
util.mapping(df=ATEC_MAP, category="SEGMENT", str_filter="SPINAL CONNECTO", value="SPINAL IMPLANTS", 
                          search_column="PRODUCT")

util.mapping(df=ATEC_MAP, category="PRODUCT_TYPE", str_filter="SPINAL CROSSLINK", value="CONNECTORS/PLATES", 
                          search_column="PRODUCT")
util.mapping(df=ATEC_MAP, category="SEGMENT", str_filter="SPINAL CROSSLINK", value="SPINAL IMPLANTS", 
                          search_column="PRODUCT")

util.mapping(df=ATEC_MAP, category="PRODUCT_TYPE", str_filter="GUIDEWIRE", value="ACCESSORIES", 
                          search_column="PRODUCT")
util.mapping(df=ATEC_MAP, category="SEGMENT", str_filter="GUIDEWIRE", value="SPINAL IMPLANTS", 
                          search_column="PRODUCT")

util.mapping(df=ATEC_MAP, category="PRODUCT_TYPE", str_filter="GUIDEWIRE", value="ACCESSORIES", 
                          search_column="PRODUCT")
util.mapping(df=ATEC_MAP, category="SEGMENT", str_filter="GUIDEWIRE", value="SPINAL IMPLANTS", 
                          search_column="PRODUCT")

# PRODUCT TYPE START
util.mapping(df=ATEC_MAP, category="SEGMENT", str_filter="ACCESSORIES", value="SPINAL IMPLANTS", 
                          search_column="PRODUCT_TYPE")
util.mapping(df=ATEC_MAP, category="SEGMENT", str_filter="PEDICLE SCREW", value="SPINAL IMPLANTS", 
                          search_column="PRODUCT_TYPE")

util.mapping(df=ATEC_MAP, category="SEGMENT", str_filter="ANTERIOR PLATE", value="SPINAL IMPLANTS", 
                          search_column="PRODUCT")

util.mapping(df=ATEC_MAP, category="SEGMENT", str_filter="VARIABLE-ANGLE", value="SPINAL IMPLANTS", 
                          search_column="PRODUCT")
util.mapping(df=ATEC_MAP, category="SEGMENT", str_filter="FIXED-ANGLE", value="SPINAL IMPLANTS", 
                          search_column="PRODUCT")
util.mapping(df=ATEC_MAP, category="SEGMENT", str_filter="TWO-LEVEL PLATE", value="SPINAL IMPLANTS", 
                          search_column="PRODUCT")
util.mapping(df=ATEC_MAP, category="SEGMENT", str_filter="ONE-LEVEL PLATE", value="SPINAL IMPLANTS", 
                          search_column="PRODUCT")
util.mapping(df=ATEC_MAP, category="PRODUCT_TYPE", str_filter="ONE-LEVEL PLATE", value="PLATE FIXATION", 
                          search_column="PRODUCT")
util.mapping(df=ATEC_MAP, category="PRODUCT_TYPE", str_filter="TWO-LEVEL PLATE", value="PLATE FIXATION", 
                          search_column="PRODUCT")
#endregion afterlogic

ATEC_MAP.to_excel("ATEC_NEW_SPINE_MAP.xlsx", index=False)

ATEC_MAP["BRAND"].isnull().sum()
ATEC_MAP["SEGMENT"].isnull().sum()
ATEC_MAP["PRODUCT"].isnull().sum()
ATEC_MAP["PRODUCT_TYPE"].isnull().sum()

