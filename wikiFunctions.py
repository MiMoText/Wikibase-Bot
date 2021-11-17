import pywikibot
from pywikibot.data import api
import wikiSQL as SQL
import re


'''
Items
'''
def getItem(site, wdItem, token):
  request = api.Request(site=site,
                        action='wbgetentities',
                        format='json',
                        ids=wdItem)    
  return request.submit()

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

def CreateItem(repo, ENDPOINT, row):
  '''
  creates a new item

  row (list) - list with title, description, 

  '''
  #TODO: quatsch? anders
  
  new_item = pywikibot.ItemPage(repo)
  if 'FR MiMoText' in row and row['FR MiMoText'] != '':
    fr = row['FR MiMoText']
  elif 'FR' in row and row['FR'] != '':
    fr = row['FR']
  else:
    fr = ''
  if 'EN MiMoText' in row and row['EN MiMoText'] != '':
    en = row['EN MiMoText']
  elif 'EN' in row and row['EN'] != '':
    en = row['EN']
  else:
    en = ''
  if 'DE MiMoText' in row and row['DE MiMoText'] != '':
    de = row['DE MiMoText']
  elif 'DE' in row and row['DE'] != '':
    de = row['DE']
  else:
    de = ''
  label_dict = {'fr': fr, 'de': de, 'en': en}
  new_item.editLabels(labels=label_dict, summary="Setting labels")

  if 'description-fr' in row or 'description-de' in row or 'description-en' in row:
    desc_dict = {'fr': row['description-fr'], 'de': row['description-de'], 'en': row['description-en']}
    new_item.editDescriptions(descriptions=desc_dict, summary="Setting descriptions")

  return new_item

def CreateAuthor(name, repo):
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

def CreateWerk(title, repo):
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

'''
Properties
'''
def getProperties(site, itemtitle):
  '''
  Query Params for Property
  '''
  params = { 'action' :'wbsearchentities' , 'format' : 'json' , 'language' : 'en', 'type' : 'property', 'search': itemtitle}
  request = api.Request(site=site,**params)
  return request.submit()

def GetProperty(site, item):
  '''
  return PID of Property
  '''
  wikiEntries = getProperties(site, item)
  if wikiEntries['search']:
    QID = 0
    for elem in wikiEntries['search']:
      if elem['label'] == item:
        QID = elem['id']
    return QID
  return

def CreateProperty(repo, title, datatypeProp):
  '''
  creates a new property

  title (string) - property name

  datatypeProp (string) - type of property, need to be wikibase compliant
  '''
  # TODO: Exchange CheckForProperty with SparQL search?
  if CheckForProperty(repo, title):
    new_item = pywikibot.PropertyPage(repo,datatype=datatypeProp)
    label_dict = {'fr': title, 'de': title, 'en':title}
    new_item.editLabels(labels=label_dict, summary='Setting labels') 
    return new_item.getID()
  return

def CreateReferenz(repo, ENDPOINT, claim, ref_prop, ref_target):
  '''
  add referenz to given claim

  claim (claim) -- claim to add the reference

  ref_prop (string) -- PID

  ref_Target (string) -- QID or PID
  '''

  if ref_target[:1] != 'Q':
    ref_target = SQL.GetEntryOverSPARQL(ENDPOINT,ref_target, SQL.SparQL_Mode.QID)
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

def CreateClaim(repo, ENDPOINT, item, prop, target, references = None):
  #TODO change description after
  #TODO check if claim is already set


  '''
  Add a new Claim to given Item

  Keyword arguments:

  item (ItemPage) -- given item

  prop (str) -- PID of statement property

  target (str) -- QID of linked target

  references (list of tuples) -- (reference_property, reference_target) default None
  '''

  #print(item, prop, target, references)
  targetFound = False
  itemClaims = item.get()['claims']
  for claimProperty, claims in itemClaims.items():
    if claimProperty == prop:
      for claim in claims:
        if target == "99.11": #TODO: different werk
          claimTargetId = None
        else:
          claimTargetId = claim.getTarget().id
        if claimTargetId == target:
          targetFound = True
          if references:
            for ref in references:
              CreateReferenz(repo, ENDPOINT, claim, ref[0], ref[1])
      
  if not targetFound:
    print(repo)
    print(prop)
    propPage= pywikibot.PropertyPage(repo, prop)
    propPage.get()
    print(propPage._type)
    claim = ''
    claim = pywikibot.Claim(repo, prop)
    print(prop)
    sTarget = SetTarget(repo,ENDPOINT, prop, target)
    if sTarget:
      claim.setTarget(sTarget)
      if references:
        for ref in references:
          if target and ref[0] and ref[1]:
            CreateReferenz(repo,ENDPOINT,claim, ref[0], ref[1])
      item.addClaim(claim, summary='Adding claim ' + prop)

def getClaim(item, pid, ENDPOINT=None, REPO=None, target=None):
  #print(item)
  #TODO: items with more then one matching property
  itemClaims = item.get()['claims']
  for claimProperty, claims in itemClaims.items():
      if claimProperty == pid:
          for claim in claims:
            if not REPO or not ENDPOINT:
              return claim
            if not target:
              return None
            if re.match(r"^Q\d+$", target):
              qid = target
            else:
              propertyPage = pywikibot.PropertyPage(REPO, pid)
              propertyPage.get(True)
              if propertyPage._type == "wikibase-item":
                qid = SQL.GetEntryOverSPARQL(ENDPOINT, target)
                if not qid:
                  qid = SQL.GetEntryOverSPARQL(ENDPOINT, target, lang="fr")
                if not qid:
                  qid = SQL.GetEntryOverSPARQL(ENDPOINT, target, lang="de")
            if claim.target_equals(qid):
              return claim
            
          return None
            

def SetTarget(repo,ENDPOINT, prop, target):
  '''
  Set Target based on property Type
  
  prop (string) -- property to be linked

  target (string) -- target of the link
  '''

  propertyPage = pywikibot.PropertyPage(repo, prop)
  propertyPage.get()
  if propertyPage._type == 'wikibase-item':
    print(target, "TARGET")
    if not re.match(r"Q\d+$", target):
      t1 = SQL.GetEntryOverSPARQL(ENDPOINT, target, lang='fr')
      target = SQL.GetEntryOverSPARQL(ENDPOINT,target)
      if not target:
        target = t1
      if not target:
        return
      print(target)
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
  elif propertyPage._type == 'globe-coordinate':
    print("Coordinates")
    coordinates = target.split(',')
    lat = coordinates[0]
    lon = coordinates[1]
    precision = "0.000001"
    print(lat, lon, precision)
    coord = pywikibot.Coordinate(lat, lon, precision=precision)
    print(str(coord))
    return coord
  else:
    return target 

def CheckForEntry(site, item):
  '''
  check if item is in wikibase
  '''
  wikiEntries = getItems(site, item, 'en')
  if not wikiEntries['search']:
    return True
  else:
    itemFound = False
    for elem in wikiEntries['search']:
      if elem['label'] == item:
        itemFound = True
    return not itemFound

def CheckForProperty(site, elem):
  '''
  check if property is in wikibse
  '''
  wikiEntries = getProperties(site, elem)
  if not wikiEntries['search']:
    return True
  else:
    itemFound = False
    for e in wikiEntries['search']:
      if e['label'] == elem:
        itemFound = True
    return not itemFound

def GetEntry(site, item, lang):
  '''
  return QID for item

  lang -- en, de, fr

  TODO: change to SparQL?
  '''
  wikiEntries = getItems(site, item, lang)
  if wikiEntries['search']:
    QID = 0
    for elem in wikiEntries['search']:
      if elem['match']['text'] == item:
        QID = elem['id']
        return QID
  return

