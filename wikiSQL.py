import sys
import pprint
from enum import Enum
from SPARQLWrapper import SPARQLWrapper, JSON

class SparQL_Mode(Enum):
  ID = '1'
  IDforStatement = '2'
  label = '?label'
  value = '?value'

class SparQL_Properties(Enum):
  instance_of = 'P2'
  BGRF_ID = 'P13'

def prettyPrint(variable):
  pp = pprint.PrettyPrinter(indent=4)
  pp.pprint(variable)


def GetEntryOverSPARQL(ENDPOINT, item, mode=SparQL_Mode.ID, prop="P13", lang='en'):
  '''
  Get Entry with Label Name and Language
  '''

  #SPARQL endpoint
  endpoint_url = "http://zora.uni-trier.de:" + ENDPOINT + "/proxy/wdqs/bigdata/namespace/wdq/sparql"
  
  #Dynamic Query
  if mode == SparQL_Mode.ID:
    query = """
    SELECT *
    {
      ?item rdfs:label ?label.
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