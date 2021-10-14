'''
Create a list of all to be imported BGRF Data
BGRF-ID, title, author, authorX..
'''

import os
import csv

dirname = os.path.dirname(__file__)
TSV_BGRF100 = os.path.join(dirname, 'data/BGRF_100.tsv')
TSV_BGRF2000_m100 = os.path.join(dirname, 'data/BGRF_2000-100.tsv')
header = ['BGRF_ID', 'Title', 'Author']

def getDict(filename):
  BGRF = {}
  rowCounter = 0
  with open(filename, 'r', newline='') as tsv_data:
    reader = csv.DictReader(tsv_data, delimiter='\t')
    for row in reader:
      if rowCounter > 1 and 'P13' in row and row['P13'] != '' and 'check' in row and row['check'] == '' \
      or rowCounter > 1 and 'P13' in row and row['P13'] != '' and 'check' not in row:
        authorCount = 0
        tmpDict = {}
        tmpDict.update({'Title':row['P4']})
        if 'P5' in row and row['P5'] != '':
          tmpDict.update({'Author':row['P5']})
        whileAuthor = True
        while(whileAuthor):
          authorCount = authorCount + 1
          if str(authorCount) + 'P5' in row and row[str(authorCount) + 'P5'] != '':
            tmpDict.update({'Author' + str(authorCount):row[str(authorCount) + 'P5']})
            if 'Author' + str(authorCount) not in header:
              header.append('Author' + str(authorCount))
          else:
            whileAuthor = False
        BGRF.update({row['P13']:tmpDict})
      rowCounter = rowCounter + 1
  return BGRF

Dict_BGRF100 = getDict(TSV_BGRF100)
Dict_BGRF2000_m100 = getDict(TSV_BGRF2000_m100)

DICT_BGRF = {**Dict_BGRF100, **Dict_BGRF2000_m100}

TSV_BGRF = os.path.join(dirname, 'data/importedBGRFList.tsv')
with open(TSV_BGRF, 'w') as out_file:
  tsv_writer = csv.writer(out_file, delimiter='\t')
  tsv_writer.writerow(header)
  for key in sorted(DICT_BGRF):
    tmpList = []
    tmpList.append(key)
    tmpList.append(DICT_BGRF[key]['Title'])
    if 'Author' in DICT_BGRF[key]:
      tmpList.append(DICT_BGRF[key]['Author'])
    whileAuthor = True
    authorCount = 0
    while(whileAuthor):
      authorCount = authorCount + 1
      if 'Author' + str(authorCount) in DICT_BGRF[key]:
        tmpList.append(DICT_BGRF[key]['Author' + str(authorCount)])
      else:
        whileAuthor = False
    tsv_writer.writerow(tmpList) 


    #print(key + '' + str(DICT_BGRF[key]))