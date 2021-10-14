import sys
import os
import csv
from pywikibot.data import api
import pywikibot
import datetime
import pprint
import sys
from SPARQLWrapper import SPARQLWrapper, JSON
from enum import Enum
from pywikibot.page import ItemPage


if len(sys.argv) == 2:
  file = sys.argv[1]
else:
  print('Datei angeben!')
  exit()

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, file)

#tsv = open(filename)
#read_tsv = csv.reader(tsv, delimiter="\t")

site = pywikibot.Site('en', 'most100')
repo = site.data_repository()

def CheckForEntry(item):
  '''
  check if item is in wikibase
  '''
  wikiEntries = getItems(site, item, 'en')
  prettyPrint(wikiEntries)
  if not wikiEntries['search']:
    return True
  else:
    itemFound = False
    for elem in wikiEntries['search']:
      if elem['label'] == item:
        itemFound = True
    return not itemFound

def CheckForProperty(elem):
  '''
  check if property is in wikibse
  '''
  wikiEntries = getProperties(site, elem)
  prettyPrint(wikiEntries)
  if not wikiEntries['search']:
    return True
  else:
    itemFound = False
    for e in wikiEntries['search']:
      if e['label'] == elem:
        itemFound = True
    return not itemFound

def GetEntry(item, lang):
  '''
  return QID for item

  lang -- en, de, fr

  TODO: change to SparQL?
  '''
  print(item)
  wikiEntries = getItems(site, item, lang)
  prettyPrint(wikiEntries)
  if wikiEntries['search']:
    QID = 0
    for elem in wikiEntries['search']:
      if elem['match']['text'] == item:
        QID = elem['id']
        print('GetEntry ' + QID)
        return QID
  return

class Verbs(Enum):
  label = '?label'
  #wdt:
  instance_of = 'P2'
  BGRF_ID = 'P13'

def GetEntryOverSPARQL(item, lang='en',prop=Verbs.label):
  '''
  Get Entry with Label Name and Language
  '''
  #SPARQL endpoint
  endpoint_url = "http://zora.uni-trier.de:44100/proxy/wdqs/bigdata/namespace/wdq/sparql"
  
  #Dynamic Query
  if prop == Verbs.label:
    query = """
    SELECT
      ?item ?itemLabel ?value
    WHERE 
    {
      ?item ?label '"""+item+"""'@"""+lang+"""       
      SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE]". }
    }
    """
  else:
    query = """
    SELECT
      ?item ?itemLabel ?value
    WHERE 
    {
      ?item wdt:"""+prop.value+""" '"""+item+"""'       
      SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE]". }
    }
    """
  #print(item)
  results = get_results(endpoint_url, query)
  #prettyPrint(results)
  for result in results["results"]["bindings"]:
      #print('ITEM: ' + result['item']['value'].split('/')[-1])
      return result['item']['value'].split('/')[-1]

def GetEntryWithID(id):
  '''
  return item to specific id
  '''
  print(id)
  wikiEntries = getItems(site, id, 'en')
  prettyPrint(wikiEntries)
  if wikiEntries['search']:
    QID = 0
    for elem in wikiEntries['search']:
      if elem['id'] == item:
        QID = elem['id']
        print('GetEntry ' + QID)
    return QID
  return

def GetProperty(item):
  '''
  return PID of Property
  '''
  print(item)
  wikiEntries = getProperties(site, item)
  prettyPrint(wikiEntries)
  if wikiEntries['search']:
    QID = 0
    for elem in wikiEntries['search']:
      if elem['label'] == item:
        QID = elem['id']
        print('GetProperty ' + QID)
    return QID
  return

def CreateProperty(title, datatypeProp):
  '''
  creates a new property

  title (string) - property name

  datatypeProp (string) - type of property, need to be wikibase compliant
  '''
  # TODO: Exchange CheckForProperty with SparQL search?
  if CheckForProperty(title):
    new_item = pywikibot.PropertyPage(repo,datatype=datatypeProp)
    label_dict = {'fr': title, 'de': title, 'en':title}
    new_item.editLabels(labels=label_dict, summary='Setting labels') 
    return new_item.getID()
  return

def CreateItem(row):
  '''
  creates a new item

  row (list) - list with title, description, 

  '''
  if CheckForEntry(row['title-fr']) and CheckForEntry(row['title-de']) and CheckForEntry(row['title-en']):
    new_item = pywikibot.ItemPage(repo)
    label_dict = {'fr': row['title-fr'], 'de': row['title-de'], 'en': row['title-en']}
    new_item.editLabels(labels=label_dict, summary="Setting labels")

    if 'description-fr' in row or 'description-de' in row or 'description-en' in row:
      desc_dict = {'fr': row['description-fr'], 'de': row['description-de'], 'en': row['description-en']}
      new_item.editDescriptions(descriptions=desc_dict, summary="Setting descriptions")

    return new_item

def CreateAuthor(name):
  '''
  Create author with name as Label for en,de,fr

  name (string) -- author name
  '''
  #Setting Labels
  new_item = pywikibot.ItemPage(repo)
  label_dict = {'fr': name, 'de': name, 'en':name}
  new_item.editLabels(labels=label_dict, summary="Setting labels")

  #Add name as monolingual Statement
  new_claim = pywikibot.Claim(repo, 'p9')
  target = pywikibot.WbMonolingualText(name, "fr")
  new_claim.setTarget(target)
  new_item.addClaim(new_claim, summary="Adding claim P9")

  #Set (P2) instance of (Q10)) human
  new_claim = pywikibot.Claim(repo, 'P2')
  target = pywikibot.ItemPage(repo, 'Q10')
  new_claim.setTarget(target)
  new_item.addClaim(new_claim, summary="Adding claim P2")

  #Set (P30) occupation (Q15) author
  new_claim = pywikibot.Claim(repo, 'P30')
  target = pywikibot.ItemPage(repo, 'Q15')
  new_claim.setTarget(target)
  new_item.addClaim(new_claim, summary="Adding claim P9")

  return new_item.getID()

def CreateWerk(title):
  '''
  Create novel with title as Label for en,de,fr

  title (string) -- title of novel
  '''
  #Setting Labels
  new_item = pywikibot.ItemPage(repo)
  label_dict = {'fr': title, 'de': title, 'en':title}
  new_item.editLabels(labels=label_dict, summary="Setting labels")

  #Set (P2) instance of (Q2) literary work (P14) stated in (Q1)
  new_ref = pywikibot.Claim(repo, 'P14', True)
  ref_target = pywikibot.ItemPage(repo, 'Q1')
  new_ref.setTarget(ref_target)
  sources = []
  sources.append(new_ref)

  new_claim = pywikibot.Claim(repo, 'P2')
  target = pywikibot.ItemPage(repo, 'Q2')
  new_claim.setTarget(target)
  new_claim.addSources(sources, summary="Adding reference Q1")
  new_item.addClaim(new_claim, summary="Adding claim P2")

  #Set (P39) genre (Q12) fictional prose (P14) stated in (Q1)
  new_ref = pywikibot.Claim(repo, 'P14', True)
  ref_target = pywikibot.ItemPage(repo, 'Q1')
  new_ref.setTarget(ref_target)
  sources = []
  sources.append(new_ref)

  new_claim = pywikibot.Claim(repo, 'P39')
  target = pywikibot.ItemPage(repo, 'Q12')
  new_claim.setTarget(target)
  new_claim.addSources(sources, summary="Adding reference Q1")
  new_item.addClaim(new_claim, summary="Adding claim P39")

  return new_item

def getItems(site, itemtitle, language):
  '''
  Query Params for Items

  site --

  itemtitle -- 

  language -- en, de, fr
  '''
  params = { 'action' :'wbsearchentities' , 'format' : 'json' , 'language' : language, 'type' : 'item', 'search': itemtitle}
  request = api.Request(site=site,**params)
  return request.submit()

def getProperties(site, itemtitle):
  '''
  Query Params for Property
  '''
  params = { 'action' :'wbsearchentities' , 'format' : 'json' , 'language' : 'en', 'type' : 'property', 'search': itemtitle}
  request = api.Request(site=site,**params)
  return request.submit()

def getItem(site, wdItem, token):
  request = api.Request(site=site,
                        action='wbgetentities',
                        format='json',
                        ids=wdItem)    
  return request.submit()

def prettyPrint(variable):
  pp = pprint.PrettyPrinter(indent=4)
  pp.pprint(variable)

def CreateReferenz(claim, ref_prop, ref_target):
  '''
  add referenz to given claim

  claim (claim) -- claim to add the reference

  ref_prop (string) -- PID

  ref_Target (string) -- QID or PID
  '''
  targetFound = False
  for claimSources in claim.getSources():
    for referenceProperty, referenceClaims in claimSources.items():
      if referenceProperty == ref_prop:
        for referenceClaim in referenceClaims:
          if ref_target == referenceClaim.getTarget().id:
            targetFound = True

  if not targetFound:
    target = pywikibot.ItemPage(repo, ref_target)
    ref = pywikibot.Claim(repo, ref_prop, True)
    ref.setTarget(target)
    sources = []
    sources.append(ref)
    claim.addSources(sources, summary="Adding reference " + ref_target)

def CreateClaim(item, prop, target, references = None):
  #TODO change description after

  '''
  Add a new Claim to given Item

  Keyword arguments:

  item (ItemPage) -- given item

  prop (str) -- PID of statement property

  target (str) -- QID of linked target

  references (list of tuples) -- (reference_property, reference_target) default None

  '''
  targetFound = False
  itemClaims = item.get()['claims']
  for claimProperty, claims in itemClaims.items():
    if claimProperty == prop:
      for claim in claims:
        claimTargetId = claim.getTarget().id
        if claimTargetId == target:
          targetFound = True
          for ref in references:
            CreateReferenz(claim, ref[0], ref[1])
      
  if not targetFound:
    claim = pywikibot.Claim(repo, prop)
    claim.setTarget(setTarget(prop, target))
    for ref in references:
      if target and ref[0] and ref[1]:
        CreateReferenz(claim, ref[0], ref[1])
    item.addClaim(claim, summary='Adding claim ' + prop)



  '''if claim.getTarget() != None and references != None:
    for ref in references:
      CreateReferenz(claim, ref[0], ref[1])
  else:
    claim.setTarget(setTarget(prop, target))
    if references != None:
      for ref in references:
        if target and ref[0] and ref[1]:
          CreateReferenz(claim, ref[0], ref[1])
    item.addClaim(claim, summary='Adding claim ' + prop)'''

def setTarget(prop, target):
  '''
  Set Target based on property Type
  
  prop (string) -- property to be linked

  target (string) -- target of the link
  '''
  propertyPage = pywikibot.PropertyPage(repo, prop)
  propertyPage.get()
  if propertyPage._type == 'wikibase-item':
    return pywikibot.ItemPage(repo, target)
  elif propertyPage._type == 'wikibase-property':
    return pywikibot.PropertyPage(repo, target)
  elif propertyPage._type == 'monolingualtext':
    return pywikibot.WbMonolingualText(target, "fr")
  elif propertyPage._type == 'time':
    return pywikibot.WbTime(int(target), calendarmodel = 'http://www.wikidata.org/entity/Q1985727')
  elif propertyPage._type == 'external_id':
    return target
  elif propertyPage._type == 'url':
    return target
  elif propertyPage._type == 'commonsMedia':
    return target
  elif propertyPage._type == 'quantity':
    return pywikibot.WbQuantity(target)
  else:
    return target 

def get_results(endpoint_url, query):
    '''
    get SPARQL resdults
    '''
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


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
  QID_thematicVocab = GetEntry('thematic vocabulary', 'en')
  QID_thematicConcept = GetEntry('thematic concept', 'en')
  QID_spatialVocab = GetEntry('spatial vocabulary', 'en')
  QID_spatialConcept = GetEntry('spatial concept', 'en')
  PID_closeMatch = GetProperty('close match')
  for row in reader:
    if rowcount == 1:
      print(row)    
      print('-----')
    if infos[0] == 'create' and infos[1] == 'properties' and rowcount > 1:
      print(row)
      print(CreateProperty(row['title'], row['datatype']))
    elif infos[0] == 'create' and infos[1] == 'items' and rowcount > 1:
      CreateItem(row)
    elif infos[0] == 'update' and rowcount > 1:
      itemQID = GetEntry(row['pointer'], 'en')
      item = pywikibot.ItemPage(repo, itemQID)
      CreateClaim()
    elif infos[0] == 'create' and infos[1] == 'vocab' and rowcount > 1:

      if CheckForEntry(row['title-fr']) and CheckForEntry(row['title-de']) and CheckForEntry(row['title-en']):
        new_item = pywikibot.ItemPage(repo)
        label_dict = {'fr': row['title-fr'], 'de': row['title-de'], 'en': row['title-en']}
        new_item.editLabels(labels=label_dict, summary="Setting labels")

        if 'description-fr' in row or 'description-de' in row or 'description-en' in row:
          desc_dict = {'fr': row['description-fr'], 'de': row['description-de'], 'en': row['description-en']}
          new_item.editDescriptions(descriptions=desc_dict, summary="Setting descriptions")

        if infos[2] == 'thematic':
          if(row['check'] == "exact match"):
            CreateClaim(new_item, 'P31', row['P31'], [('P14', QID_thematicVocab)])
          elif(row['check'] == "close match"):
            CreateClaim(new_item, PID_closeMatch, row['P31'], [('P14', QID_thematicVocab)])
      
          CreateClaim(new_item, 'P2', QID_thematicConcept, [('P14', QID_thematicVocab)])
          CreateClaim(new_item, 'P25', QID_thematicVocab)
        elif infos[2] == "spatial":
          if(row['check'] == "exact match"):
            CreateClaim(new_item, 'P31', row['P31'], [('P14', QID_spatialVocab)])
          elif(row['check'] == "close match"):
            CreateClaim(new_item, PID_closeMatch, row['P31'], [('P14', QID_spatialVocab)])
      
          CreateClaim(new_item, 'P2', QID_spatialConcept, [('P14', QID_spatialVocab)])
          CreateClaim(new_item, 'P25', QID_spatialVocab)          


        print(new_item.getID())
    elif infos[0] == 'add' and infos[1] == 'statements' and rowcount > 1:

      QID_BGRF_ID = GetEntryOverSPARQL(row['pointer'],'en', Verbs.BGRF_ID)
      QID_themeConcept = GetEntryOverSPARQL(row['value'], 'fr')
      PID_about = GetEntryOverSPARQL('about')
      PID_stated_in = GetEntryOverSPARQL('stated in')
      QID_matching_table = GetEntryOverSPARQL('BGRF_Matching-Table')

      print(QID_BGRF_ID)
      print(QID_themeConcept)
      print(QID_matching_table)
      
      #TODO: use new createClaim function

      try:
        #BGRF_ID about ThemKonzept stated in Q1 and stated in Matching Table
        item = pywikibot.ItemPage(repo, QID_BGRF_ID)

        claim = pywikibot.Claim(repo, PID_about)
        claim.setTarget(setTarget(PID_about, QID_themeConcept))


        if QID_themeConcept and PID_stated_in and QID_matching_table:
          CreateReferenz(claim, PID_stated_in, QID_matching_table)
        if QID_themeConcept and PID_stated_in:
          CreateReferenz(claim, PID_stated_in, 'Q1')
        item.addClaim(claim, summary='Adding claim ' + PID_about)
      except:
        print('POINTER: ' + row['pointer']) 
      
      # TODO change for multiple referenzes
      #CreateClaim(item, PID_about, QID_themeConcept, PID_stated_in, QID_matching_table)
    elif infos[0] == 'add' and infos[1] == 'statementsModel' and rowcount > 1:
      QID_BGRF_ID = GetEntryOverSPARQL(row['pointer'],'en', Verbs.BGRF_ID)
      QID_themeConcept = GetEntryOverSPARQL(row['value'], 'fr')
      PID_about = GetEntryOverSPARQL('about')
      PID_stated_in = GetEntryOverSPARQL('stated in')
      QID_Topic_Modell = GetEntryOverSPARQL('Topic Model MMT 11-2020')
      QID_topic_labels = GetEntryOverSPARQL('Topic Labels and Concepts')

      #print(QID_BGRF_ID)
      #print(QID_themeConcept)
            
      #BGRF_ID about ThemKonzept stated in Q1 and stated in Matching Table
      item = pywikibot.ItemPage(repo, QID_BGRF_ID)

      references = []
      references.append((PID_stated_in, QID_Topic_Modell))
      references.append((PID_stated_in, QID_topic_labels))
      if(QID_themeConcept != None and QID_BGRF_ID != None):
        CreateClaim(item, PID_about, QID_themeConcept, references)
      
      #claim = pywikibot.Claim(repo, PID_about)
      #claim.setTarget(SetTarget(PID_about, QID_themeConcept))

      #if QID_themeConcept and PID_stated_in and QID_Topic_Modell:
      #  CreateReferenz(claim, PID_stated_in, QID_Topic_Modell)
      #if QID_themeConcept and PID_stated_in and QID_topic_labels:
      #  CreateReferenz(claim, PID_stated_in, QID_topic_labels)
      #item.addClaim(claim, summary='Adding claim ' + PID_about)

    elif infos[0] == 'create' and infos[1] == 'topics' and rowcount > 1:
      if not GetEntryOverSPARQL(row['title-fr'],'fr') or not GetEntryOverSPARQL(row['title-de'],'de') or not GetEntryOverSPARQL(row['title-en'],'en'):
        new_item = pywikibot.ItemPage(repo)
        label_dict = {'fr': row['title-fr'], 'de': row['title-de'], 'en': row['title-en']}
        new_item.editLabels(labels=label_dict, summary="Setting labels")

        if 'description-fr' in row or 'description-de' in row or 'description-en' in row:
          desc_dict = {'fr': row['description-fr'], 'de': row['description-de'], 'en': row['description-en']}
          new_item.editDescriptions(descriptions=desc_dict, summary="Setting descriptions")

        topic_QID = GetEntryOverSPARQL('topic', 'en')
        #topic_QID = GetEntry('topic')
        topic_model = GetEntryOverSPARQL('Topic Model MMT 11-2020', 'en')
        PID_representedBy = GetEntryOverSPARQL('represented by', 'en')
        CreateClaim(new_item, 'P2', topic_QID, [('P14', topic_model)])
        CreateClaim(new_item, 'P25', topic_model)
        #CreateClaim(new_item, 'P58', row['p58'])
        #CreateClaim(new_item, 'P58', row['1p58'])
        if row['p58'] and GetEntryOverSPARQL(row['p58'], 'en'):
          CreateClaim(new_item, PID_representedBy, GetEntryOverSPARQL(row['p58'], 'en'))
        if row['1p58'] and GetEntryOverSPARQL(row['1p58'], 'en'):
          CreateClaim(new_item, PID_representedBy, GetEntryOverSPARQL(row['1p58'],'en'))
    elif infos[0] == 'new' and infos[1] == 'items' and rowcount > 1:
      #TODO 2000 Check sigle
      if CheckForEntry(row['P4']): #and not row['check']:
        new_item = CreateWerk(row['P4'])
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
                  wikiEntries = getItems(site, value, 'en')
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
                    for elem in wikiEntries['search']:
                      if elem['label'] == value:
                        authorQID = elem['id']
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