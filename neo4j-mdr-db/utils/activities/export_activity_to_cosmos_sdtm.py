import http
import yaml
import requests
from service_environment import ServiceEnvironment
from neo4j_database import Neo4jDatabase
from datetime import date

def nci_service_get_code_from_term(term):
 url = 'https://api-evsrest.nci.nih.gov/api/v1/concept/search?fromRecord=0&include=synonyms&pageSize=10&synonymSource=CDISC&term='+term+'&terminology=ncit&type=match'
 r = requests.get(url)
 concept_info = r.json()
 return concept_info['concepts'][0]['code']

#Specify the date of this package to be delivered to CDISC
#package_date = '2023-09-01'
today = date.today()
package_date = today.strftime("%Y-%b-%d")
#where ai.name in ['Pulse','Systolic Blood Pressure','Diastolic Blood Pressure']
db = Neo4jDatabase()
sdtm_query = """
MATCH (agrp)-[r1:HAS]->(asgrp)-[r2:HAS]->(act)-[r3:HAS]->(ai:ActivityInstance)-[r4:HAS]->(aitm1:ActivityItem),
(aitm1)-[r5:OF_CLASS]->(aitmc1:ActivityItemClass),
(ai)-[r6:OF_CLASS]->(aic:ActivityInstanceClass)-[r7:PARENT_CLASS]->(aicp:ActivityInstanceClass)
where ai.name in ['Pulse','Systolic Blood Pressure','Diastolic Blood Pressure']
OPTIONAL MATCH(aitmc1)-[r8:HAS]->(varclass:VariableClass)-[r9:HAS]->(var:Variable)<-[r10:HAS]-(ds:Dataset)<-[r11:HAS]-(dmig:DataModelIG),
(ai)-[r12:HAS]->(aitm2:ActivityItem)-[r13:FOR]->(ct:CTTerm)-[r15:IMPLEMENTED_IN]->(ds:Dataset)
OPTIONAL MATCH (aitm1)-[r16:FOR]->(ct2:CTTerm)<-[r17:HAS]-(cl:CTCodeList),
(aitmc1)-[r18:HAS_ROLE]->(role:CTTerm)<-[r19:HAS]-(cd_role:CTCodeList),
(aitmc1)-[r20:HAS_TYPE]->(type:CTTerm)<-[r21:HAS]-(cd_type:CTCodeList)
with aitmc1,dmig, ai, ds, ct2, ct, var,role,type,cd_role, cd_type,
apoc.map.fromPairs([
                   ['conceptId',cl.uid],
                   ['submissionValue',cl.submission_value]
                   ]) as cdlist,
CASE WHEN var.uid contains 'TEST' or var.uid contains 'TESTCD' or var.uid contains 'TERM' THEN
apoc.map.fromPairs([
                   ['conceptId',ct2.uid],
                   ['value',ct2.code_submission_value]
                   ]) 
END as assignedTerms,
CASE when aitmc1.data_collection='Yes' THEN 'Collected' ELSE 'Not Collected' END as collected
WITH aitmc1,dmig,ai,ds,var,cdlist,role,type,cd_type,assignedTerms,collected,
collect(distinct(ct2.code_submission_value)) as val_list
WITH aitmc1,dmig,ai,ds,var,cdlist,role,type,cd_type,assignedTerms,collected,val_list,
apoc.map.fromPairs( [
                    ['name', var.uid],
                    ['codelist',cdlist],
                    ['valueList', val_list],
                    ['subsetCodelist',cd_type.name],
                    ['AssignedTerm',assignedTerms],
                    ['role',role.code_submission_value],
                    ['dataType', type.code_submission_value],
                    ['originType', collected],
                    ['mandatoryVariable', aitmc1.mandatory],
                    ['var_order',toInteger(aitmc1.order)]
                    ]) as varlist order by varlist['var_order']
WITH dmig, ai,ds,collect(varlist) as vars
WITH dmig, ai,ds, vars, 
apoc.map.fromPairs([ 
                    ['packageType',dmig.name],
                    ['datasetSpecializationId',ai.topic_code],
                    ['domain',ds.code],
                    ['shortName',ai.name],
                    ['source',ds.code+'.'+ds.code+'TESTCD'],
                    ['sdtmigStartVersion',dmig.version],
                    ['Variables',vars]
                    ]) as activity
return  activity
"""
def process_instances_nn_sdtm():
  activity_list = db.graph().run(sdtm_query).data()
  for ai in activity_list :
    print(ai['activity']['domain'])
    dom = ai['activity']['domain'].lower()
    bc_file_name = 'nn_sdtm_bc_specialization_'+dom+'_'+ai['activity']['datasetSpecializationId'].lower()
    print(bc_file_name)
    bc = {}
    bc = {
        'packageDate': package_date,
        'packageType': ai['activity']['packageType'],
        'datasetSpecializationId': ai['activity']['datasetSpecializationId'],
        'domain': ai['activity']['domain'],
        'shortName': ai['activity']['shortName'],
        'source': ai['activity']['source'],
        'sdtmigStartVersion': ai['activity']['sdtmigStartVersion'],
        'sdtmigEndVersion': "",
        'biomedicalConceptId': nci_service_get_code_from_term(ai['activity']['shortName']),
        'variables': []
      }
    bc['variables'] = []
    if ai['activity']['Variables'] is not None:
      for var in ai['activity']['Variables']:
        nci_var_code = nci_service_get_code_from_term(var['name'])
        if var['name'].upper() not in ['DOMAIN']:
          print('VARNAME added: '+var['name'])
          if var['codelist']['conceptId'] is not None:
              itemref = 'https://ncithesaurus.nci.nih.gov/ncitbrowser/ConceptReport.jsp?dictionary=NCI_Thesaurus&ns=ncit&code='+var['codelist']['conceptId']
          else: None
          if var['name'].__contains__('TEST') | var['name'].__contains__('TERM'):
            v = {'name': var['name'],
                'isNonStandard': False,
                'codelist': 
                  {
                    'conceptId': var['codelist']['conceptId'],
                    'href':itemref,
                    'submissionValue':var['codelist']['submissionValue']
                   },  
                'assignedTerm': 
                  {
                    'conceptId': nci_var_code,
                    'value': "".join(var['valueList'])
                  },
                'role':var['role'],
                'relationship': [],
                'mandatoryVariable': True,
                'mandatoryValue': False,
                'comparator':'EQ'
                }
          else:
            if var['dataType'] in ['FLOAT','INTEGER']:
              v = {'name': var['name'],
                  'dataElementConceptId': nci_var_code,
                  'isNonStandard': False,
                  'role': var['role'],
                  'dataType': var['dataType'],
                  'length': None,
                  'format': None,
                  'significantDigits': None,
                  'relationship': [],
                  'mandatoryVariable': None, 
                  'mandatoryValue': None ,
                  'originType': None,
                  'originSource': None,
                  'vlmTarget': True
                  }
            else:
              v = {'name': var['name'],
                  'dataElementConceptId': nci_var_code,
                  'isNonStandard': False,
                  'codelist': 
                    {
                      'conceptId': var['codelist']['conceptId'],
                      'href': itemref,
                      'submissionValue': var['codelist']['submissionValue']
                     },
                  'subsetCodelist': None,
                  'valueList':  var['valueList'],
                  'role': var['role'],
                  'dataType': var['dataType'],
                  'length': None,
                  'relationship': [],
                  'mandatoryVariable': None, 
                  'mandatoryValue': None ,
                  'originType': None,
                  'originSource': None,
                  'vlmTarget': True
                  }
              
          bc['variables'].append(v)

    path = 'nn_converted_data/sdtm'
    if bc_file_name is not None:
     filename = path+bc_file_name+'.yaml'
     with open(filename, 'w') as file:
      yaml.dump([bc], file,sort_keys=False)


process_instances_nn_sdtm()





    
