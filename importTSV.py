from pickle import TRUE
import sys
import os
import csv
import wikiFunctions as wf
import wikiSQL as SQL
import pywikibot
import pprint
import re

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

site = pywikibot.Site('en', server)
repo = site.data_repository()

def prettyPrint(variable):
  pp = pprint.PrettyPrinter(indent=4)
  pp.pprint(variable)

def GetEntryWithID(id):
  '''
  return item to specific id
  '''
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
  return

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
  QID_thematicVocab = SQL.GetEntryOverSPARQL(ENDPOINT,'thematic vocabulary')
  QID_thematicConcept = SQL.GetEntryOverSPARQL(ENDPOINT,'thematic concept')
  QID_spatialVocab = SQL.GetEntryOverSPARQL(ENDPOINT,'spatial vocabulary')
  QID_spatialConcept = SQL.GetEntryOverSPARQL(ENDPOINT,'spatial concept')
  PID_closeMatch = SQL.GetEntryOverSPARQL(ENDPOINT,'close match')
  row0 = ''
  for row in reader:
    if rowcount == 1:
      print(row)    
      print('-----')
    elif rowcount == 0:
      row0 = row
    elif infos[0] == 'create' and infos[1] == 'properties' and rowcount > 1:
      print(row)
      print(wf.CreateProperty(row['title'], row['datatype']))
    elif infos[0] == 'create' and infos[1] == 'items' and rowcount > 1:
      if 'EN' in row and row['EN'] != '':
        id = SQL.GetEntryOverSPARQL(ENDPOINT, row['EN'])
      elif 'FR' in row and row['FR'] != '':
        id = SQL.GetEntryOverSPARQL(ENDPOINT, row['FR'], SQL.SparQL_Mode.ID, '', 'fr')
      elif 'DE' in row and row['DE'] != '':
        id = SQL.GetEntryOverSPARQL(ENDPOINT, row['DE'], SQL.SparQL_Mode.ID, '', 'de')
      print("ID----------------",id)
      if id :
        item = pywikibot.ItemPage(repo,id)
      else:
        item = wf.CreateItem(repo, ENDPOINT, row)
      print(item)
      for property in row:
        if property != 'FR' and property != 'DE' and property != 'EN' and item:
          if row0[property] != None and row0[property] != '' and re.match(r"P\d+$", property):
            if row[property] != '' and row[property] != None:
              if row[property].strip() != '#':
                print("CREATE CLAIM 1")
                wf.CreateClaim(repo,ENDPOINT, item, property, row[property])
            else:
              claim = wf.getClaim(item, property)
              if not claim:
                print("CREATE CLAIM 2")
                wf.CreateClaim(repo, ENDPOINT,item, property, row0[property])
          elif re.match(r"P\d+$", property) and row[property] != '' and row[property] != None:
            claim = wf.getClaim(item, property)
            print("CLAIM",claim)
            if not claim or claim.getTarget() != row[property]:
              print("Create CLaim 3")
              print(item, property, row[property])
              wf.CreateClaim(repo,ENDPOINT,item, property, row[property])
          elif row0[property] != None and row0[property] != '' and re.match(r"P\d+RP\d+$", property):
            if row[property] != None and row[property] != '':
              if row[property] != '#':
                print("single Entry") #TODO Entry in Cell
            else:
              pos = property.find("R")
              prop = property[:pos]
              propRef = property[pos+1:]
              propRefTarget = row0[property]
              
              print(pos, prop, propRef, propRefTarget)
              print(row[prop])

              if 'EN' in row and row['EN'] != '':
                id = SQL.GetEntryOverSPARQL(ENDPOINT, row['EN'])
              elif 'FR' in row and row['FR'] != '':
                id = SQL.GetEntryOverSPARQL(ENDPOINT, row['FR'], SQL.SparQL_Mode.ID, '', 'fr')
              elif 'DE' in row and row['DE'] != '':
                id = SQL.GetEntryOverSPARQL(ENDPOINT, row['DE'], SQL.SparQL_Mode.ID, '', 'de')
              if id:
                item = pywikibot.ItemPage(repo,id)
              claim = wf.getClaim(item, prop)
              print(claim)
              if claim:
                print(True)
                print("Create ref 4")
                wf.CreateReferenz(repo,ENDPOINT, claim, propRef, propRefTarget)
              else:
                print(False)
                references = [(propRef, propRefTarget)]
                if row[prop] == '' and row0[prop]:
                  print("Create CLaim with Ref 5")
                  wf.CreateClaim(repo, ENDPOINT,item, prop, row0[prop], references)
    elif infos[0] == 'update' and rowcount > 1:

      if 'P13' in row:
        print(row['P13'])
        QID_item = SQL.GetEntryOverSPARQL(ENDPOINT,row['P13'], SQL.SparQL_Mode.IDforStatement)
      elif 'ID' in row:
        QID_item = SQL.GetEntryOverSPARQL(ENDPOINT,row['ID'])
      
      item = pywikibot.ItemPage(repo, QID_item)
      
      print("QID", QID_item)
      #check headers and choose operation based on it
      #TODO: how to signal if update or new and what to do with multiple items in statement
      for property in head:       
        #All Properties in format Px
        if(re.match(r"P\d+$", property)):
          if property != 'P13' and property != 'P26' and not row0[property] and QID_item:
            value = SQL.GetEntryOverSPARQL(ENDPOINT,QID_item, SQL.SparQL_Mode.value, property)
            if not value and row[property]:
              print("CREATE CLAIM 1")
              wf.CreateClaim(repo, ENDPOINT,item, property, row[property])
              print("NO VLAUE-----------------------")
            elif row[property] and value != row[property]:
              print("ITEM", item)
              claim = wf.getClaim(item, property)
              print("VALUE", value, row[property])
              print("CLAIM", claim)
              print("SET TARGET 1")
              target = wf.setTarget(repo, ENDPOINT, property, row[property])
              print("CLAIMBEFORE", claim)
              claim.changeTarget(target)
              print("CLAIMAFTER", claim)
            print("Value", value)
            #TODO: hier bin ich dran
            #CreateClaim(item, elem, row['elem'])
          elif property != 'P13' and property != 'P26' and row0[property]:
            if row[property]:
              print("CreateClaim", property, row[property])
            else:
              print("createClaim", property, row0[property])
        #All Properties with Reference in format PxR
        if(re.match(r"P\d+RP\d+$", property)):
          pos = property.find("R")
          prop = property[:pos]
          propRef = property[pos+1:]
          propRefTarget = row0[property]
          if propRef != 'P13' and propRef != 'P26' and row0[property] and QID_item:
            if 'P13' in row:
              print(row['P13'])
              QID_item = SQL.GetEntryOverSPARQL(ENDPOINT,row['P13'], SQL.SparQL_Mode.IDforStatement)
            elif 'ID' in row:
              QID_item = SQL.GetEntryOverSPARQL(ENDPOINT,row['ID'])
            item = pywikibot.ItemPage(repo, QID_item)
            claim = wf.getClaim(item, prop)
            if claim:
              print("CreateRef 1")
              wf.CreateReferenz(repo, ENDPOINT, claim, propRef, propRefTarget)
            else: 
              print("Create Claim 2")
              references = [(propRef, propRefTarget)]
              wf.CreateClaim(repo,ENDPOINT, item, prop, row[prop], references)      
    elif infos[0] == 'create' and infos[1] == 'vocab' and rowcount > 1:

      if not SQL.GetEntryOverSPARQL(ENDPOINT,row['title-fr'],'fr') and not SQL.GetEntryOverSPARQL(ENDPOINT,row['title-de'],'de') and not SQL.GetEntryOverSPARQL(ENDPOINT,row['title-en']):
        new_item = pywikibot.ItemPage(repo)
        label_dict = {'fr': row['title-fr'], 'de': row['title-de'], 'en': row['title-en']}
        new_item.editLabels(labels=label_dict, summary="Setting labels")

        if 'description-fr' in row or 'description-de' in row or 'description-en' in row:
          desc_dict = {'fr': row['description-fr'], 'de': row['description-de'], 'en': row['description-en']}
          new_item.editDescriptions(descriptions=desc_dict, summary="Setting descriptions")

        if infos[2] == 'thematic':
          if(row['check'] == "exact match"):
            wf.CreateClaim(repo, ENDPOINT,new_item,'P31', row['P31'], [('P14', QID_thematicVocab)])
          elif(row['check'] == "close match"):
            wf.CreateClaim(repo,ENDPOINT,new_item, PID_closeMatch, row['P31'], [('P14', QID_thematicVocab)])
      
          wf.CreateClaim(repo,ENDPOINT,new_item,'P2', QID_thematicConcept, [('P14', QID_thematicVocab)])
          wf.CreateClaim(repo,ENDPOINT,new_item,'P25', QID_thematicVocab)
        elif infos[2] == "spatial":
          if(row['check'] == "exact match"):
            wf.CreateClaim(repo,ENDPOINT,new_item,'P31', row['P31'], [('P14', QID_spatialVocab)])
          elif(row['check'] == "close match"):
            wf.CreateClaim(repo,ENDPOINT,new_item, PID_closeMatch, row['P31'], [('P14', QID_spatialVocab)])
      
          wf.CreateClaim(repo,ENDPOINT,new_item,'P2', QID_spatialConcept, [('P14', QID_spatialVocab)])
          wf.CreateClaim(repo,ENDPOINT,new_item,'P25', QID_spatialVocab)          


        print(new_item.getID())
    elif infos[0] == 'add' and infos[1] == 'statements' and rowcount > 1:

      QID_BGRF_ID = SQL.GetEntryOverSPARQL(ENDPOINT,row['pointer'],'en', SQL.SparQL_Mode.BGRF_ID)
      QID_concept = SQL.GetEntryOverSPARQL(ENDPOINT,row['value'], 'fr')
      PID_about = SQL.GetEntryOverSPARQL(ENDPOINT,'about')
      PID_stated_in = SQL.GetEntryOverSPARQL(ENDPOINT,'stated in')
      QID_matching_table = SQL.GetEntryOverSPARQL(ENDPOINT,'BGRF_Matching-Table')

      print(QID_BGRF_ID)
      print(QID_concept)
      print(QID_matching_table)

      #BGRF_ID about concept stated in Q1 and stated in Matching Table
      item = pywikibot.ItemPage(repo, QID_BGRF_ID)

      references = []
      references.append((PID_stated_in, QID_matching_table))
      references.append((PID_stated_in, 'Q1'))
      if QID_concept != None and QID_BGRF_ID != None:
        wf.CreateClaim(repo,ENDPOINT,item, PID_about, QID_concept, references)
    elif infos[0] == 'add' and infos[1] == 'statementsModel' and rowcount > 1:
      QID_BGRF_ID = SQL.GetEntryOverSPARQL(ENDPOINT,row['pointer'],'en', SQL.SparQL_Mode.BGRF_ID)
      QID_concept = SQL.GetEntryOverSPARQL(ENDPOINT,row['value'], 'fr')
      PID_about = SQL.GetEntryOverSPARQL(ENDPOINT,'about')
      PID_stated_in = SQL.GetEntryOverSPARQL(ENDPOINT,'stated in')
      QID_Topic_Modell = SQL.GetEntryOverSPARQL(ENDPOINT,'Topic Model MMT 11-2020')
      QID_topic_labels = SQL.GetEntryOverSPARQL(ENDPOINT,'Topic Labels and Concepts')

      #BGRF_ID about themeConcept stated in topic models and stated in labels and concepts
      item = pywikibot.ItemPage(repo, QID_BGRF_ID)

      references = []
      references.append((PID_stated_in, QID_Topic_Modell))
      references.append((PID_stated_in, QID_topic_labels))
      if(QID_concept != None and QID_BGRF_ID != None):
        wf.CreateClaim(item, ENDPOINT,PID_about, QID_concept, references)
    elif infos[0] == 'create' and infos[1] == 'topics' and rowcount > 1:
      if not SQL.GetEntryOverSPARQL(ENDPOINT,row['title-fr'],'fr') or not SQL.GetEntryOverSPARQL(ENDPOINT,row['title-de'],'de') or not SQL.GetEntryOverSPARQL(ENDPOINT,row['title-en'],'en'):
        new_item = pywikibot.ItemPage(repo)
        label_dict = {'fr': row['title-fr'], 'de': row['title-de'], 'en': row['title-en']}
        new_item.editLabels(labels=label_dict, summary="Setting labels")

        if 'description-fr' in row or 'description-de' in row or 'description-en' in row:
          desc_dict = {'fr': row['description-fr'], 'de': row['description-de'], 'en': row['description-en']}
          new_item.editDescriptions(descriptions=desc_dict, summary="Setting descriptions")

        topic_QID = SQL.GetEntryOverSPARQL(ENDPOINT,'topic', 'en')
        #topic_QID = GetEntry('topic')
        topic_model = SQL.GetEntryOverSPARQL(ENDPOINT,'Topic Model MMT 11-2020', 'en')
        PID_representedBy = SQL.GetEntryOverSPARQL(ENDPOINT,'represented by', 'en')
        wf.CreateClaim(repo,ENDPOINT,new_item, 'P2', topic_QID, [('P14', topic_model)])
        wf.CreateClaim(repo,ENDPOINT,new_item, 'P25', topic_model)
        #CreateClaim(new_item, 'P58', row['p58'])
        #CreateClaim(new_item, 'P58', row['1p58'])
        if row['p58'] and SQL.GetEntryOverSPARQL(ENDPOINT,row['p58'], 'en'):
          wf.CreateClaim(repo,ENDPOINT,new_item, PID_representedBy, SQL.GetEntryOverSPARQL(ENDPOINT,row['p58'], 'en'))
        if row['1p58'] and SQL.GetEntryOverSPARQL(ENDPOINT,row['1p58'], 'en'):
          wf.CreateClaim(repo,ENDPOINT,new_item, PID_representedBy, SQL.GetEntryOverSPARQL(ENDPOINT,row['1p58'],'en'))
    elif infos[0] == 'new' and infos[1] == 'items' and rowcount > 1:
      #TODO 2000 Check sigle
      if wf.CheckForEntry(row['P4']): #and not row['check']:
        new_item = wf.CreateWerk(row['P4'])
        for key, value in row.items():
          if(key == 'check'):
            continue
          if key:
            addAnonym = True
            if key[:1].isdigit() and int(key[:1]) < 6:
              key = key[1:]
              addAnonym = False
            prop = pywikibot.PropertyPage(repo, key)
            prop.get()
            print('{0}, {1}, {2}'.format(prop._type, key, value))
            try:
              new_claim = pywikibot.Claim(repo, key)
              if prop._type == 'string':
                print("String")
                target = value
              elif prop._type == 'wikibase-item':
                print("Item")
                if value:
                  wikiEntries = wf.getItems(site, value, 'en')
                  prettyPrint(wikiEntries)
                  # TODO Dupletten eventuell nicht durch list da sparql?
                  
                  if not wikiEntries['search'] and key == 'P5' and value not in authors_Already_Imported:
                    print('empty')
                    authorQID = wf.CreateAuthor(value)
                    authors_Already_Imported[value] = authorQID
                  elif value in authors_Already_Imported:
                    authorQID = authors_Already_Imported[value] 
                  else:
                    print('not Empty')
                    for property in wikiEntries['search']:
                      if property['label'] == value:
                        authorQID = property['id']
                  print(authorQID)
                  target = pywikibot.ItemPage(repo, authorQID) 
                elif key == 'P5' and addAnonym:
                  new_claim = pywikibot.Claim(repo, 'P15')
                  target = 'anonieme'
                else:
                  continue                 
              elif prop._type == 'wikibase-property':
                print("Prop")
                target = pywikibot.PropertyPage(repo, value)
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
              new_ref = pywikibot.Claim(repo, 'P14', True)
              ref_target = pywikibot.ItemPage(repo, 'Q1')
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