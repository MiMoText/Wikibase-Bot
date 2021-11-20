import sys
import pprint
from enum import Enum
from SPARQLWrapper import SPARQLWrapper, JSON

class SparQL_Mode(Enum):
  QID = '1'
  PID = '2'
  IDforStatement = '3'
  label = '?label'
  value = '?value'
  ID_WithTarget = 4
  ID_from_P30 = 5
  ID_without_Property_and_instance_of_Item = 6

class SparQL_Properties(Enum):
  instance_of = 'P2'
  BGRF_ID = 'P13'

def prettyPrint(variable):
  pp = pprint.PrettyPrinter(indent=4)
  pp.pprint(variable)


def GetEntryOverSPARQL(ENDPOINT, item, mode=SparQL_Mode.QID, prop="P13", lang='en', target=None, instanceOf = None):
  '''
  Get Entry with Label Name and Language
  '''
  
  item = item.replace("'", ".")
  item = item.replace("’", ".")
  item = item.replace("(", ".")
  item = item.replace(")", ".")
  item = item.replace("É", ".")
  item = item.replace("È", ".")
  item = item.replace("*", ".")  
  item = item.replace("]", ".") 
  item = item.replace("[", ".") 

  #SPARQL endpoint
  endpoint_url = "http://zora.uni-trier.de:" + ENDPOINT + "/proxy/wdqs/bigdata/namespace/wdq/sparql"
  
  #Dynamic Query
  if mode == SparQL_Mode.QID:
    query = """
    SELECT *
    {
      ?item rdfs:label ?label.
      Filter not exists {?item rdf:type wikibase:Property}
      Filter (regex(?label, '^""" + item + """$', 'i'))
      Filter (lang(?label) = '""" + lang + """') 
      BIND (str(Replace(str(?item), '\\\\D+\\\\d+\\\\D+\\\\/', '')) as ?Result)    
    }
    """

  elif mode == SparQL_Mode.PID:
    query = """
    SELECT *
    {
      ?item rdfs:label ?label.
      ?item rdf:type wikibase:Property.
      Filter (regex(?label, '^""" + item + """$', 'i'))
      Filter (lang(?label) = '""" + lang + """') 
      BIND (str(Replace(str(?item), '\\\\D+\\\\d+\\\\D+\\\\/', '')) as ?Result)    
    }
    """
    
  elif mode == SparQL_Mode.IDforStatement:
    query = """
    SELECT *
    {
      ?item wdt:"""+prop+""" '"""+item+"""'.    
      ?item rdfs:label ?label.
      Filter (lang(?label) = 'en')
      BIND (str(Replace(str(?item), "\\\\D+\\\\d+\\\\D+\\\\/", "")) as ?Result) 
    }
    """
  elif mode == SparQL_Mode.value:
    query ="""
    select *
    {
      wd:""" + item + """ wdt:""" + prop + """ ?Result.
    }
    """
  
  elif mode == SparQL_Mode.ID_WithTarget:
    query ="""
    select *
    {
      ?item rdfs:label ?label.
      ?item wdt:P2 wd:""" + target + """.
      Filter (regex(?label, '^"""+ item +"""$'))
      BIND (str(Replace(str(?item), "\\\\D+\\\\d+\\\\D+\\\\/", "")) as ?Result)
    }
    """
  
  elif mode == SparQL_Mode.ID_from_P30:
    query="""
    select *
    {
      ?item wdt:P30|wdt:P58 ?label.
      Filter (regex(str(?label), "^""" + item + """$", "i"))
      BIND (str(Replace(str(?item), "\\\\D+\\\\d+\\\\D+\\\\/", "")) as ?Result)
    }
    """
  elif mode == SparQL_Mode.ID_without_Property_and_instance_of_Item:
    query = """
    SELECT *
    {
      ?item rdfs:label ?label.
      ?item wdt:P2 wd:""" + instanceOf + """.
      Filter not exists {?item rdf:type wikibase:Property}
      Filter not exists {?item """ + prop + """ ?o}
      Filter (regex(?label, '^""" + item + """$', 'i'))
      Filter (lang(?label) = '""" + lang + """') 
      BIND (str(Replace(str(?item), '\\\\D+\\\\d+\\\\D+\\\\/', '')) as ?Result)    
    }
    """

  #print(item)
  results = get_results(endpoint_url, query)
  #prettyPrint(results)
  for result in results["results"]["bindings"]:
      #print('ITEM: ' + result['item']['value'].split('/')[-1])
      return result['Result']['value']

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