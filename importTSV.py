import sys
import os
import csv

from rdflib.term import Statement
from wikiFunctions import CreateClaim, getClaim, CreateProperty, CreateItem, CreateReferenz, SetTarget, CheckForEntry, CreateWerk, CreateAuthor, getItems
from wikiSQL import GetEntryOverSPARQL, SparQL_Mode, SparQL_Properties, get_results
import pywikibot
import pprint
import re
import time

#Server argument 1 and file argument 2
#Server family: most100, wikitestmost, preLive, Live
#SPARQL Endpoint
if len(sys.argv) == 4:
  server = sys.argv[1]
  file = sys.argv[2]
  ENDPOINT = sys.argv[3]
else:
  print('Datei angeben!')
  exit()


dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, file)

SITE = pywikibot.Site('en', server)
REPO = SITE.data_repository()

def prettyPrint(variable):
  pp = pprint.PrettyPrinter(indent=4)
  pp.pprint(variable)

'''def GetEntryWithID(id):
  
  return item to specific id
  
  
  print(id)
  wikiEntries = wf.getItems(site, id, 'en')
  prettyPrint(wikiEntries)
  if wikiEntries['search']:
    QID = 0
    for elem in wikiEntries['search']:
      if elem['id'] == item:
        QID = elem['id']
        print('GetEntry ' + QID)
    return QID
  return'''

def propDPD(item, pid, value):

  pid = re.findall("P\d+", pid)[0]
  qid = GetEntryOverSPARQL(ENDPOINT, value)
  claim = getClaim(item, pid)
  if claim:
    currValue = GetEntryOverSPARQL(ENDPOINT, qid, SparQL_Mode.value, pid)
    if currValue != value:
      CreateClaim(REPO, ENDPOINT, item, pid, qid)
  else:
    CreateClaim(REPO, ENDPOINT, item, pid, qid)

def test(item):
  print("TEST")
  GetEntryOverSPARQL(ENDPOINT, item, "CHARRIÈRE, Isabelle-Agnès-Elisabeth van Tuyll van Serooskerken van Zuylen, dame de")

def nar_locTarget(pid, check, row):
  QID_Loc = None
  if check in row and row[check] != "":
    QID_Loc = GetEntryOverSPARQL(ENDPOINT, row[check], SparQL_Mode.ID_from_P30)
  
  if not QID_Loc: 
    QID_Loc = GetEntryOverSPARQL(ENDPOINT, row[pid])
    if not QID_Loc:
        QID_Loc = GetEntryOverSPARQL(ENDPOINT, row[pid], lang="fr")
    if not QID_Loc:
        QID_Loc = GetEntryOverSPARQL(ENDPOINT, row[pid], lang="de")
  return QID_Loc
'''
Import Logic here
# TODO: Main Class?
'''
with open(filename, 'r', newline='') as tsv_data:
  headReader = csv.reader(tsv_data, delimiter='\t')
  head = next(headReader)
  infos = next(headReader)
  p_= next(headReader)
print(head)

with open(filename, 'r', newline='') as tsv_data:
  reader = csv.DictReader(tsv_data, delimiter='\t')
  rowcount = 0
  #List of Authors who are already imported in this Import
  authors_Already_Imported = {}
  QID_thematicVocab = GetEntryOverSPARQL(ENDPOINT,'thematic vocabulary')
  QID_thematicConcept = GetEntryOverSPARQL(ENDPOINT,'thematic concept')
  QID_spatialVocab = GetEntryOverSPARQL(ENDPOINT,'spatial vocabulary')
  QID_spatialConcept = GetEntryOverSPARQL(ENDPOINT,'spatial concept')
  PID_closeMatch = GetEntryOverSPARQL(ENDPOINT,'close match')
  row0 = ''
  for row in reader:
    if rowcount == 1:
      print(row)    
      print('-----')
    elif rowcount == 0:
      row0 = row
    elif infos[0] == 'create' and infos[1] == 'properties' and rowcount > 1:
      print(CreateProperty(REPO, row['title'], row['datatype']))
    elif infos[0] == 'test' and rowcount > 1:
      if 'EN' in row and row['EN'] != '':
        id = GetEntryOverSPARQL(ENDPOINT, row['EN'])
      elif 'FR' in row and row['FR'] != '':
        id = GetEntryOverSPARQL(ENDPOINT, row['FR'], SparQL_Mode.QID, '', 'fr')
      elif 'DE' in row and row['DE'] != '':
        id = GetEntryOverSPARQL(ENDPOINT, row['DE'], SparQL_Mode.QID, '', 'de')
      #Get item if exist
      if id:
        item = pywikibot.ItemPage(REPO,id)
      else:
        item = CreateItem(REPO, ENDPOINT, row)
      test(item)
    #-------------------------------------------------------------------------------------------------------------------------------
    # create item -----------------------------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------------------------------------
    elif infos[0] == 'create' and infos[1] == 'items' and rowcount > 1:
      #TODO: AUTHOR P5 Unknown

      # Skip if entry in check column, e.g. sigle in BGRF_2000
      if 'check' in row and row['check'] != '':
        rowcount = rowcount + 1
        continue

      id = None
      # Get qid for entry
      if 'FR MiMoText' in row and row["FR MiMoText"] != '':
        id = GetEntryOverSPARQL(ENDPOINT, row['FR MiMoText'], lang='fr')
      elif not id and 'EN MiMoText' in row and row["EN MiMoText"] != '':
        id = GetEntryOverSPARQL(ENDPOINT, row['EN MiMoText'])
      elif not id and 'DE MiMoText' in row and row["DE MiMoText"] != '':
        id = GetEntryOverSPARQL(ENDPOINT, row['DE MiMoText'], lang='de')
      elif not id and 'EN' in row and row['EN'] != '':
        id = GetEntryOverSPARQL(ENDPOINT, row['EN'])
      elif not id and 'FR' in row and row['FR'] != '':
        id = GetEntryOverSPARQL(ENDPOINT, row['FR'], SparQL_Mode.QID, '', 'fr')
      elif not id and 'DE' in row and row['DE'] != '':
        id = GetEntryOverSPARQL(ENDPOINT, row['DE'], SparQL_Mode.QID, '', 'de')
      #Get item if exist, else create new item 
      print(id)
      if id:
        print("in id")
        if "new" in row and row['new'] != "":
          item = CreateItem(REPO, ENDPOINT, row)
        else:
          item = pywikibot.ItemPage(REPO,id)
      else:
        print("not in id")
        item = CreateItem(REPO, ENDPOINT, row)

      if item:
        claimP30 = None
        claimP58 = None
        if "P30" in row:
          claimP30 = getClaim(item, "P30")
        if "P58" in row:
          claimP58 = getClaim(item, "P58")
        if (claimP30 and not claimP30.target_equals(row["P30"]) or (claimP58 and not claimP58.target_equals(row["P58"]))):
          item = CreateItem(REPO, ENDPOINT, row)

      #for every PID in row
      for pid in row:
        if pid != 'FR' and pid != 'DE' and pid != 'EN' and item:
          if re.match(r"\d+P\d+$", pid) and row[pid] != '' and row[pid] != None: # xPx and entry in row
            propDPD(item, pid, row[pid])
          if row0[pid] != None and row0[pid] != '' and re.match(r"P\d+$", pid): # Px and entry in head (row0)
            if row[pid] != '' and row[pid] != None: # check entry in row
              if row[pid].strip() != '#': # check if entry is #
                CreateClaim(REPO,ENDPOINT, item, pid, row[pid])
            else: # no entry in row
              item.get(True)
              claim = getClaim(item, pid)
              if not claim:
                CreateClaim(REPO, ENDPOINT,item, pid, row0[pid])
          elif re.match(r"P\d+$", pid) and row[pid] != '' and row[pid] != None: # Px and entry in row
            claim = getClaim(item, pid)
            propertyPage = pywikibot.PropertyPage(REPO, pid)
            propertyPage.get()
            qid = None
            print("PX entry in row", item.getID(), pid, row[pid])
            if propertyPage._type == "wikibase-item":
              qid = GetEntryOverSPARQL(ENDPOINT,row[pid])
              print("QID", qid)
              if row[pid] == "[temps paraître encore]" or row[pid] == "[femme fille servir]" or row[pid] == "[chevalier voir mot]" or row[pid] == "[voir croire là]" or row[pid] == "[point voir jour]" or row[pid] == "[point voir moins]": #TODO: handle topics
                continue
            if not claim or (qid and not claim.target_equals(qid)) or (not qid and claim.getTarget() != row[pid]):
              print("CreateClaim", pid, row[pid])
              CreateClaim(REPO,ENDPOINT,item, pid, row[pid])
          elif row0[pid] != None and row0[pid] != '' and re.match(r"P\d+RP\d+$", pid): # PxRPx and entry in head (row0)
            if row[pid] != None and row[pid] != '': # check entry in row
              if row[pid] != '#':
                print("single Entry") #TODO Entry in Cell
            else:
              pos = pid.find("R")
              prop = pid[:pos]
              propRef = pid[pos+1:]
              propRefTarget = row0[pid]
              print("PXRPX entry in head", item.getID(), pid, row0[pid])
              print(pos, prop, propRef, propRefTarget)

              #if 'EN' in row and row['EN'] != '':
              #  id = GetEntryOverSPARQL(ENDPOINT, row['EN'])
              #elif 'FR' in row and row['FR'] != '':
              #  id = GetEntryOverSPARQL(ENDPOINT, row['FR'], SparQL_Mode.QID, '', 'fr')
              #elif 'DE' in row and row['DE'] != '':
              #  id = GetEntryOverSPARQL(ENDPOINT, row['DE'], SparQL_Mode.QID, '', 'de')
              #if id:
              item.get(True)
              #print("Sleep for 3 sek to check Ref")
              #time.sleep(3)
              claim = getClaim(item, prop)
              #print("Claim REF", claim)
              if claim:
                CreateReferenz(REPO,ENDPOINT, claim, propRef, propRefTarget)
              else:
                references = [(propRef, propRefTarget)]
                if row[prop] == '' and row0[prop]:
                  CreateClaim(REPO, ENDPOINT,item, prop, row0[prop], references)
          
          elif re.match(r"P\d+RP\d+$", pid) and row[pid] and row[pid] != '':
            pos = pid.find("R")
            prop = pid[:pos]
            propRef = pid[pos+1:]
            propRefTarget = row[pid]
            item.get(True)
            claim = getClaim(item, prop)
            if claim:
              CreateReferenz(REPO,ENDPOINT, claim, propRef, propRefTarget)
            else:
              references = [(propRef, propRefTarget)]
              CreateClaim(REPO, ENDPOINT,item, prop, row0[prop], references)
    #-------------------------------------------------------------------------------------------------------------------------------
    # Update -----------------------------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------------------------------------
    elif infos[0] == 'update' and rowcount > 1:

      if 'IDcheck' in row and row["IDcheck"] != '':
        QID_item = GetEntryOverSPARQL(ENDPOINT, row["IDcheck"], SparQL_Mode.ID_from_P30)
      elif 'P13' in row and row["P13"] != '':
        QID_item = GetEntryOverSPARQL(ENDPOINT,row['P13'], SparQL_Mode.IDforStatement)
      elif 'ID' in row and row["ID"] != '':
        QID_item = GetEntryOverSPARQL(ENDPOINT,row['ID'])
      elif ('EN MiMoText' in row and row["EN MiMoText"] != '' and row["IDcheck"] == ''):
        QID_item = GetEntryOverSPARQL(ENDPOINT, row["EN MiMoText"], SparQL_Mode.ID_without_Property_and_instance_of_Item, "wdt:P30|wdt:P58", instanceOf="Q26")  
        if ('FR MiMoText' in row and row["FR MiMoText"] != '' and row["IDcheck"] == '') and not QID_item:
          QID_item = GetEntryOverSPARQL(ENDPOINT, row["FR MiMoText"], SparQL_Mode.ID_without_Property_and_instance_of_Item, "wdt:P30|wdt:P58",'fr', instanceOf="Q26") 
        if ('DE MiMoText' in row and row["DE MiMoText"] != '' and row["IDcheck"] == '') and not QID_item:
          QID_item = GetEntryOverSPARQL(ENDPOINT, row["DE MiMoText"], SparQL_Mode.ID_without_Property_and_instance_of_Item, "wdt:P30|wdt:P58",'de', instanceOf="Q26") 
      elif 'EN MiMoText' in row and row["EN MiMoText"] != '':
        QID_item = GetEntryOverSPARQL(ENDPOINT, row['EN MiMoText'])
      elif 'FR MiMoText' in row and row["FR MiMoText"] != '':
        QID_item = GetEntryOverSPARQL(ENDPOINT, row['FR MiMoText'], lang='fr')
      elif 'DE MiMoText' in row and row["DE MiMoText"] != '':
        QID_item = GetEntryOverSPARQL(ENDPOINT, row['DE MiMoText'], lang='de')
      elif 'EN' in row and row['EN'] != '':
        QID_item = GetEntryOverSPARQL(ENDPOINT, row['EN'])
      elif 'FR' in row and row['FR'] != '':
        QID_item = GetEntryOverSPARQL(ENDPOINT, row['FR'], SparQL_Mode.QID, '', 'fr')
      elif 'DE' in row and row['DE'] != '':
        QID_item = GetEntryOverSPARQL(ENDPOINT, row['DE'], SparQL_Mode.QID, '', 'de')

       

      statement = None
      if "statements" in row0 and row0["statements"] != '':
        statement = GetEntryOverSPARQL(ENDPOINT, row0["statements"])       

      if not QID_item:
        continue

      item = pywikibot.ItemPage(REPO, QID_item)
      
      #check headers and choose operation based on it
      #TODO: how to signal if update or new and what to do with multiple items in statement
      for pid in head:       
        if re.match(r"^P\d+$", pid) and row[pid] != '': # Px
          if pid != 'P13' and pid != 'P26' and not row0[pid] and item:
            item.get(True)
            if infos[1] == "edit":
              propertyPage = pywikibot.PropertyPage(REPO, pid)
              propertyPage.get()

              claim = getClaim(item, pid)
              if claim:
                if statement and propertyPage._type == "wikibase-item":
                  QID_Target = GetEntryOverSPARQL(ENDPOINT, row[pid], SparQL_Mode.ID_WithTarget, target=statement)
                  claim.changeTarget(SetTarget(REPO, ENDPOINT, pid, QID_Target))
                else:
                  claim.changeTarget(SetTarget(REPO, ENDPOINT, pid, row[pid]))
              else:

                if statement and propertyPage._type == "wikibase-item":
                  QID_Target = GetEntryOverSPARQL(ENDPOINT, row[pid], SparQL_Mode.ID_WithTarget, target=statement)
                  CreateClaim(REPO, ENDPOINT, item, pid, QID_Target)
                else:
                  if row[pid] != '': 
                    CreateClaim(REPO, ENDPOINT, item, pid, row[pid])
            elif pid == "P52":
              QID_Loc = nar_locTarget(pid, "check", row)
              if not QID_Loc:
                continue
              item.get(True)
              claim = getClaim(item, pid, ENDPOINT, REPO, QID_Loc)
              if claim:
                print("d smth")
              else:
                CreateClaim(REPO, ENDPOINT, item, pid, QID_Loc)
            else:
              claim = getClaim(item, pid, ENDPOINT, REPO, row[pid])               
              if not claim:
                CreateClaim(REPO,ENDPOINT, item, pid, row[pid])
          elif pid != 'P13' and pid != 'P26' and row0[pid] and item:
            item.get(True)
            print("PID and row0 update")


            '''value = ''
            #value = GetEntryOverSPARQL(ENDPOINT,QID_item, SparQL_Mode.value, pid)
            if not value and row[pid]:
              print("CREATE CLAIM 1", pid, row[pid])
              CreateClaim(REPO, ENDPOINT,item, pid, row[pid])
              print("NO VLAUE-----------------------")
            elif row[pid] and value != row[pid]:
              item.get(True)
              claim = getClaim(item, pid)
              target = SetTarget(REPO, ENDPOINT, pid, row[pid])
              claim.changeTarget(target)
            print("Value", value)
            #TODO: hier bin ich dran
            #CreateClaim(item, elem, row['elem'])
          elif pid != 'P13' and pid != 'P26' and row0[pid]:
            if row[pid]:
              CreateClaim(REPO, ENDPOINT, pid, row[pid])
              print("CreateClaim", pid, row[pid])
            else:
              print("createClaim", pid, row0[pid])'''
        if re.match(r"P\d+$", pid) and row0[pid] != None and row0[pid] != '': # Px and entry in head (row0)
          if row0[pid] == "delete":
            item.get(True)
            claim = getClaim(item, pid)
            if claim:
              item.removeClaims(claim)
          elif row[pid] != '' and row[pid] != None: # check entry in row
            if row[pid].strip() != '#': # check if entry is #
              CreateClaim(REPO,ENDPOINT, item, pid, row[pid])
          else: # no entry in row
            item.get(True)
            claim = getClaim(item, pid, ENDPOINT, REPO, row0[pid])
            if not claim:
              CreateClaim(REPO, ENDPOINT,item, pid, row0[pid])
        if re.match(r"^P\d+RP\d+$", pid) and row0[pid] != '': # PxRPx

          pos = pid.find("R")
          prop = pid[:pos]
          propRef = pid[pos+1:]
          propRefTarget = row0[pid]
          
          if not re.match(r"(P|Q)\d+", propRefTarget):
            qid = None
            qid = GetEntryOverSPARQL(ENDPOINT, propRefTarget)
            if not qid:
              qid = GetEntryOverSPARQL(ENDPOINT, propRefTarget, lang="fr")
            if not qid:
              qid = GetEntryOverSPARQL(ENDPOINT, propRefTarget, lang="de")
            propRefTarget = qid

          if propRef != 'P13' and propRef != 'P26' and row0[pid] and item and row[prop]:
            '''if 'P13' in row:
              print(row['P13'])
              QID_item = GetEntryOverSPARQL(ENDPOINT,row['P13'], SparQL_Mode.IDforStatement)
            elif 'ID' in row:
              QID_item = GetEntryOverSPARQL(ENDPOINT,row['ID'])
            item = pywikibot.ItemPage(REPO, QID_item)'''
            item.get(True)

            propertyPage = pywikibot.PropertyPage(REPO, prop)
            propertyPage.get()

            if statement and propertyPage._type == "wikibase-item":
              QID_Target = GetEntryOverSPARQL(ENDPOINT, row[pid], SparQL_Mode.ID_WithTarget, target=statement)
              claim = getClaim(item, prop, ENDPOINT, REPO, QID_Target)
            elif prop == "P52":
              QID_Loc = nar_locTarget(prop, "check", row)
              if not QID_Loc:
                continue
              item.get(True)
              claim = getClaim(item, prop, ENDPOINT, REPO, QID_Loc)
            else:
              claim = getClaim(item, prop, ENDPOINT, REPO, row[prop])
            if claim:
              print("CreateRef 1")
              CreateReferenz(REPO, ENDPOINT, claim, propRef, propRefTarget)
            else: 
              print("Create Claim 2")
              references = [(propRef, propRefTarget)]
              if prop == "P52":
                CreateClaim(REPO, ENDPOINT, item, prop, QID_Loc, references)
              else:
                CreateClaim(REPO,ENDPOINT, item, prop, row[prop], references)    
        if re.match(r"^P\d+R\d+P\d+$", pid): # PxRxPx
          pos = pid.find("R")
          prop = pid[:pos]
          propRef = pid[pos+2:]
          propRefTarget = row0[pid]

          if propRef != 'P13' and propRef != 'P26' and row0[pid] and item:
            '''if 'P13' in row:
              print(row['P13'])
              QID_item = GetEntryOverSPARQL(ENDPOINT,row['P13'], SparQL_Mode.IDforStatement)
            elif 'ID' in row:
              QID_item = GetEntryOverSPARQL(ENDPOINT,row['ID'])
            item = pywikibot.ItemPage(REPO, QID_item)'''
            item.get(True)
            claim = getClaim(item, prop, ENDPOINT, REPO, row[prop])
            if claim:
              print("CreateRef 1")
              CreateReferenz(REPO, ENDPOINT, claim, propRef, propRefTarget)
            else: 
              print("Create Claim 2")
              references = [(propRef, propRefTarget)]
              CreateClaim(REPO,ENDPOINT, item, prop, row[prop], references) 
        if re.match(r"^\d+P\d+$", pid) and row[pid] != '': # xPx
          pos = pid.find("P")
          num = pid[:pos]
          prop = pid[pos:]

          if prop == "P52":
            QID_Loc = nar_locTarget(pid, num + "check", row)
            if not QID_Loc:
              continue
            item.get(True)
            claim = getClaim(item, prop, ENDPOINT, REPO, QID_Loc)
            if claim:
              print("d smth")
            else:
              CreateClaim(REPO, ENDPOINT, item, prop, QID_Loc)
        if re.match(r"^\d+P\d+RP\d+$", pid) and row0[pid] != '': # xPxRPx
          pos = pid.find("R")
          numProp = pid[:pos]
          propRef = pid[pos+1:]
          propRefTarget = row0[pid]
          posNumProp = numProp.find("P")
          num = numProp[:posNumProp]
          prop = numProp[posNumProp:]

          if not re.match(r"(P|Q)\d+", propRefTarget):
            qid = None
            qid = GetEntryOverSPARQL(ENDPOINT, propRefTarget)
            if not qid:
              qid = GetEntryOverSPARQL(ENDPOINT, propRefTarget, lang="fr")
            if not qid:
              qid = GetEntryOverSPARQL(ENDPOINT, propRefTarget, lang="de")
            propRefTarget = qid

          if prop == "P52" and row[numProp] != '':
            QID_Loc = nar_locTarget(numProp, num+"check", row)
            if not QID_Loc:
              continue
            item.get(True)
            claim = getClaim(item, prop, ENDPOINT, REPO, QID_Loc)
            if claim:
              print("CreateRef 1")
              CreateReferenz(REPO, ENDPOINT, claim, propRef, propRefTarget)
            else: 
              print("Create Claim 2")
              references = [(propRef, propRefTarget)]
              CreateClaim(REPO,ENDPOINT, item, prop, QID_Loc, references) 
        if pid == "FR MiMoText":
          if row["FR MiMoText"] != '':
            fr = row["FR MiMoText"]
          elif row["FR"] != '':
            fr = row["FR"]
          else:
            fr = ''

          if row["EN MiMoText"] != '':
            en = row["EN MiMoText"]
          elif row["EN"] != '':
            en = row["EN"]
          else:
            en = ''

          if row["DE MiMoText"] != '':
            de = row["DE MiMoText"]
          elif row["DE"] != '':
            de = row["DE"]
          else:
            de = ''

          label_dict = {'fr': fr, 'de': de, 'en': en}
          item.editLabels(labels=label_dict, summary="edit labels")
            
    elif infos[0] == 'create' and infos[1] == 'vocab' and rowcount > 1:

      if not GetEntryOverSPARQL(ENDPOINT,row['title-fr'],'fr') and not GetEntryOverSPARQL(ENDPOINT,row['title-de'],'de') and not GetEntryOverSPARQL(ENDPOINT,row['title-en']):
        new_item = pywikibot.ItemPage(REPO)
        label_dict = {'fr': row['title-fr'], 'de': row['title-de'], 'en': row['title-en']}
        new_item.editLabels(labels=label_dict, summary="Setting labels")

        if 'description-fr' in row or 'description-de' in row or 'description-en' in row:
          desc_dict = {'fr': row['description-fr'], 'de': row['description-de'], 'en': row['description-en']}
          new_item.editDescriptions(descriptions=desc_dict, summary="Setting descriptions")

        if infos[2] == 'thematic':
          if(row['check'] == "exact match"):
            CreateClaim(REPO, ENDPOINT,new_item,'P31', row['P31'], [('P14', QID_thematicVocab)])
          elif(row['check'] == "close match"):
            CreateClaim(REPO,ENDPOINT,new_item, PID_closeMatch, row['P31'], [('P14', QID_thematicVocab)])
      
          CreateClaim(REPO,ENDPOINT,new_item,'P2', QID_thematicConcept, [('P14', QID_thematicVocab)])
          CreateClaim(REPO,ENDPOINT,new_item,'P25', QID_thematicVocab)
        elif infos[2] == "spatial":
          if(row['check'] == "exact match"):
            CreateClaim(REPO,ENDPOINT,new_item,'P31', row['P31'], [('P14', QID_spatialVocab)])
          elif(row['check'] == "close match"):
            CreateClaim(REPO,ENDPOINT,new_item, PID_closeMatch, row['P31'], [('P14', QID_spatialVocab)])
      
          CreateClaim(REPO,ENDPOINT,new_item,'P2', QID_spatialConcept, [('P14', QID_spatialVocab)])
          CreateClaim(REPO,ENDPOINT,new_item,'P25', QID_spatialVocab)          


        print(new_item.getID())
    elif infos[0] == 'add' and infos[1] == 'statements' and rowcount > 1:

      QID_BGRF_ID = GetEntryOverSPARQL(ENDPOINT,row['pointer'], SparQL_Mode.IDforStatement)
      QID_concept = GetEntryOverSPARQL(ENDPOINT,row['value'], SparQL_Mode.QID, '', 'fr')
      PID_about = GetEntryOverSPARQL(ENDPOINT,'about')
      PID_stated_in = GetEntryOverSPARQL(ENDPOINT,'stated in')
      QID_matching_table = GetEntryOverSPARQL(ENDPOINT,'BGRF_Matching-Table')

      print(QID_BGRF_ID)
      print(QID_concept)
      print(QID_matching_table)

      #BGRF_ID about concept stated in Q1 and stated in Matching Table
      item = pywikibot.ItemPage(REPO, QID_BGRF_ID)

      references = []
      references.append((PID_stated_in, QID_matching_table))
      references.append((PID_stated_in, 'Q1'))
      if QID_concept != None and QID_BGRF_ID != None:
        CreateClaim(REPO,ENDPOINT,item, PID_about, QID_concept, references)
    elif infos[0] == 'add' and infos[1] == 'statementsModel' and rowcount > 1:
      QID_BGRF_ID = GetEntryOverSPARQL(ENDPOINT,row['pointer'], SparQL_Mode.IDforStatement)
      QID_concept = GetEntryOverSPARQL(ENDPOINT,row['value'], SparQL_Mode.QID, '', 'fr')
      PID_about = GetEntryOverSPARQL(ENDPOINT,'about')
      PID_stated_in = GetEntryOverSPARQL(ENDPOINT,'stated in')
      QID_Topic_Modell = GetEntryOverSPARQL(ENDPOINT,'Topic Model MMT 11-2020')
      QID_topic_labels = GetEntryOverSPARQL(ENDPOINT,'Topic Labels and Concepts')

      #BGRF_ID about themeConcept stated in topic models and stated in labels and concepts
      item = pywikibot.ItemPage(REPO, QID_BGRF_ID)

      references = []
      references.append((PID_stated_in, QID_Topic_Modell))
      references.append((PID_stated_in, QID_topic_labels))
      if(QID_concept != None and QID_BGRF_ID != None):
        CreateClaim(REPO, ENDPOINT,item ,PID_about, QID_concept, references)
    elif infos[0] == 'create' and infos[1] == 'topics' and rowcount > 1:
      if not GetEntryOverSPARQL(ENDPOINT,row['title-fr'],SparQL_Mode.QID,'','fr') or not GetEntryOverSPARQL(ENDPOINT,row['title-de'],SparQL_Mode.QID,'','de') or not GetEntryOverSPARQL(ENDPOINT,row['title-en'],'en'):
        new_item = pywikibot.ItemPage(REPO)
        label_dict = {'fr': row['title-fr'], 'de': row['title-de'], 'en': row['title-en']}
        new_item.editLabels(labels=label_dict, summary="Setting labels")

        if 'description-fr' in row or 'description-de' in row or 'description-en' in row:
          desc_dict = {'fr': row['description-fr'], 'de': row['description-de'], 'en': row['description-en']}
          new_item.editDescriptions(descriptions=desc_dict, summary="Setting descriptions")

        topic_QID = GetEntryOverSPARQL(ENDPOINT,'topic')
        #topic_QID = GetEntry('topic')
        topic_model = GetEntryOverSPARQL(ENDPOINT,'Topic Model MMT 11-2020')
        PID_representedBy = GetEntryOverSPARQL(ENDPOINT,'represented by')
        CreateClaim(REPO,ENDPOINT,new_item, 'P2', topic_QID, [('P14', topic_model)])
        CreateClaim(REPO,ENDPOINT,new_item, 'P25', topic_model)
        #CreateClaim(new_item, 'P58', row['p58'])
        #CreateClaim(new_item, 'P58', row['1p58'])
        if row['p58'] and GetEntryOverSPARQL(ENDPOINT,row['p58']):
          CreateClaim(REPO,ENDPOINT,new_item, PID_representedBy, GetEntryOverSPARQL(ENDPOINT,row['p58']))
        if row['1p58'] and GetEntryOverSPARQL(ENDPOINT,row['1p58']):
          CreateClaim(REPO,ENDPOINT,new_item, PID_representedBy, GetEntryOverSPARQL(ENDPOINT,row['1p58']))
    elif infos[0] == 'new' and infos[1] == 'items' and rowcount > 1:
      #TODO 2000 Check sigle
      if CheckForEntry(REPO, row['P4']): #and not row['check']:
        new_item = CreateWerk(row['P4'], REPO)
        for key, value in row.items():
          if(key == 'check'):
            continue
          if key:
            addAnonym = True
            if key[:1].isdigit() and int(key[:1]) < 6:
              key = key[1:]
              addAnonym = False
            prop = pywikibot.PropertyPage(REPO, key)
            prop.get()
            print('{0}, {1}, {2}'.format(prop._type, key, value))
            try:
              new_claim = pywikibot.Claim(REPO, key)
              if prop._type == 'string':
                print("String")
                target = value
              elif prop._type == 'wikibase-item':
                print("Item")
                if value:
                  wikiEntries = getItems(SITE, value, 'en')
                  prettyPrint(wikiEntries)
                  # TODO Dupletten eventuell nicht durch list da sparql?
                  
                  if not wikiEntries['search'] and key == 'P5' and value not in authors_Already_Imported:
                    print('empty')
                    authorQID = CreateAuthor(value)
                    authors_Already_Imported[value] = authorQID
                  elif value in authors_Already_Imported:
                    authorQID = authors_Already_Imported[value] 
                  else:
                    print('not Empty')
                    for pid in wikiEntries['search']:
                      if pid['label'] == value:
                        authorQID = pid['id']
                  print(authorQID)
                  target = pywikibot.ItemPage(REPO, authorQID) 
                elif key == 'P5' and addAnonym:
                  new_claim = pywikibot.Claim(REPO, 'P15')
                  target = 'anonieme'
                else:
                  continue                 
              elif prop._type == 'wikibase-property':
                print("Prop")
                target = pywikibot.PropertyPage(REPO, value)
              elif prop._type == 'monolingualtext':
                print("Mono")
                target = pywikibot.WbMonolingualText(value, "fr")
              elif prop._type == 'time':
                print("Time")
                target = pywikibot.WbTime(int(value), calendarmodel = 'http://www.wikidata.org/entity/Q1985727')
              elif prop._type == 'external_id':
                print("External")
                target = value
              elif prop._type == 'url':
                print("URL")
                target = value
              elif prop._type == 'commonsMedia':
                print("CM")
                target = value
              elif prop._type == 'quantity':
                print("Quantity")
                target = pywikibot.WbQuantity(value)
              new_ref = pywikibot.Claim(REPO, 'P14', True)
              ref_target = pywikibot.ItemPage(REPO, 'Q1')
              new_ref.setTarget(ref_target)
              sources = []
              sources.append(new_ref)
              new_claim.setTarget(target)
              if key != 'P13':
                new_claim.addSources(sources, summary="Adding reference Q1")
              new_item.addClaim(new_claim, summary="Adding claim " + key)
            except: 
                e = sys.exc_info()[0]
                print( "<p>Error: %s</p>" % e )
          else:
            print('No Key {0}, {1}'.format(key, value))
  #      CreateAuthor(row)
    rowcount = rowcount + 1

