//Activity with data type and role
MATCH (p_agrp:ActivityGroupValue)<-[R1:IN_GROUP]-(p_asgrp:ActivitySubGroupValue)<-[R2:IN_SUB_GROUP]-(p_act:ActivityValue)
MATCH(p_act)<-[R3:IN_HIERARCHY]-(p_ai:ActivityInstanceValue)<-[R42:LATEST]-(p_ai_r:ActivityInstanceRoot),(p_ai)-[R4:ACTIVITY_INSTANCE_CLASS]->(p_aicr:ActivityInstanceClassRoot)-[R5:LATEST]->(p_aic:ActivityInstanceClassValue) where p_ai.adam_param_code='SYSBP'
MATCH (p_ai:ActivityInstanceValue)-[R6:CONTAINS_ACTIVITY_ITEM]->(p_aitm1:ActivityItemValue)
OPTIONAL MATCH(p_aitm1)<-[R7:LATEST]-(p_aitm1r:ActivityItemRoot)<-[R8:HAS_ACTIVITY_ITEM]-(p_aitmc1r:ActivityItemClassRoot)-[R9:LATEST]->(p_aitmc1:ActivityItemClassValue)
OPTIONAL MATCH (p_aicr)-[R10:PARENT_CLASS]->(p_aicrp:ActivityInstanceClassRoot)-[R11:LATEST]->(p_aicp:ActivityInstanceClassValue)
OPTIONAL MATCH (p_aicrp)-[R12:PARENT_CLASS]->(p_aicrpp:ActivityInstanceClassRoot)-[R13:LATEST]->(p_aicpp:ActivityInstanceClassValue)
OPTIONAL MATCH(p_aitmc1r)<-[R14:HAS_ITEM_CLASS]-(p_aicr)
OPTIONAL MATCH(p_aitmc1r)<-[R15:HAS_ITEM_CLASS]-(p_aicrp)
OPTIONAL MATCH(p_aitmc1r)<-[R16:HAS_ITEM_CLASS]-(p_aicrpp) 
OPTIONAL MATCH (p_aitm1)-[R17]->(p_ct2cd:CTTermRoot)-[R18:HAS_NAME_ROOT]->(ct2cdr:CTTermNameRoot)-[R19:LATEST]->(p_ct2_sponsor), (p_ct2cd)-[R20:HAS_ATTRIBUTES_ROOT]->(ct2att:CTTermAttributesRoot)-[R21:LATEST]->(p_ct2_cdisc)
OPTIONAL MATCH (p_aitm1)-[:HAS_UNIT_DEFINITION]->(p_unitdefr:UnitDefinitionRoot)-[R22:LATEST]->(p_unitdef:UnitDefinitionValue)
OPTIONAL MATCH(p_ct2cd)<-[R23:HAS_TERM]-(clr:CTCodelistRoot)-[R24:HAS_ATTRIBUTES_ROOT]->(clatt:CTCodelistAttributesRoot),(clr)-[R25:HAS_NAME_ROOT]->(clattr:CTCodelistNameRoot)-[R26:LATEST]-(p_cl_sponsor),(clatt)-[R27:LATEST]->(p_cl_cdisc:CTCodelistAttributesValue),(pc:CTPackageCodelist) where ((p_cl_cdisc)<-[:CONTAINS_ATTRIBUTES]-(pc) and pc.uid CONTAINS "SDTM") or NOT ((p_cl_cdisc)<-[:CONTAINS_ATTRIBUTES]-())
OPTIONAL MATCH (p_unitdef:UnitDefinitionValue)-[R28:HAS_CT_DIMENSION]-(unit_term:CTTermRoot)<-[R29:HAS_TERM]-(cl_root)-[R30:HAS_ATTRIBUTES_ROOT]->(clattr2)-[R31:LATEST]->(unit_cld)
OPTIONAL MATCH(p_aitmc1)-[R32:HAS_ROLE]->(p_role_r:CTTermRoot), (p_role_r)-[R33:HAS_NAME_ROOT]->(ctnr_role)-[R34:LATEST]->(p_role_val), (p_role_r)-[R35:HAS_ATTRIBUTES_ROOT]->(ctattr)-[R36:LATEST]->(p_role_attr_val)
OPTIONAL MATCH(p_aitmc1)-[R37:HAS_DATA_TYPE]->(p_dtype_r),  (p_dtype_r)-[R38:HAS_NAME_ROOT]->(ctnr_dtype)-[R39:LATEST]->(p_dtype_val), (p_dtype_r)-[R40:HAS_ATTRIBUTES_ROOT]->(ctattr_dtype)-[R41:LATEST]->(p_dtype_attr_val)
return distinct p_agrp,p_asgrp,p_act,p_ai,p_aicr,p_aic,p_aitm1,p_aitm1r,p_aitmc1r,p_aitmc1,p_aicrp,p_aicp,p_aicrpp,p_aicpp,p_ct2cd,ct2cdr,p_ct2_sponsor,ct2att,p_ct2_cdisc,p_unitdefr,p_unitdef,clr,clatt,clattr,p_cl_sponsor,p_cl_cdisc,unit_term,cl_root,clattr2,unit_cld,p_role_r,ctattr,ctnr_role, p_role_val, p_role_attr_val,p_dtype_r,p_dtype_val, ctnr_dtype,p_dtype_attr_val,ctattr_dtype,R1,R2, R3, R4, R5, R6, R7, R8, R9, R10, R11, R12, R13, R14, R15, R16, R17, R18, R19, R20, R21, R22, R23, R24, R25, R26, R27, R28, R29, R30, R31, R32, R33, R34, R35, R36, R37, R38, R39, R40, R41, R42

//Activity as logical view - used in the procedures
MATCH (p_agrp:ActivityGroupValue)<-[R1:IN_GROUP]-(p_asgrp:ActivitySubGroupValue)<-[R2:IN_SUB_GROUP]-(p_act:ActivityValue)
WITH p_agrp, p_asgrp,p_act,
apoc.create.vNode(["ActivityGroup"], properties(p_agrp)) as agrp,
apoc.create.vNode(["ActivitySubGroup"],properties(p_asgrp)) as asgrp,
apoc.create.vNode(["Activity"],properties(p_act)) as act
WITH p_act,agrp,asgrp,act,
apoc.create.vRelationship(agrp,"HAS",{type:"logical"},asgrp) as r1,
apoc.create.vRelationship(asgrp,"HAS",{type:"logical"},act) as r2
with p_act,agrp,asgrp,act,r1,r2
MATCH(p_act)<-[R3:IN_HIERARCHY]-(p_ai:ActivityInstanceValue)<-[R42:LATEST]-(p_ai_r:ActivityInstanceRoot),(p_ai)-[R4:ACTIVITY_INSTANCE_CLASS]->(p_aicr:ActivityInstanceClassRoot)-[R5:LATEST]->(p_aic:ActivityInstanceClassValue) where p_ai.adam_param_code='ALB'
WITH p_act,p_ai,p_aicr,p_aic,agrp,asgrp,act,r1,r2,
apoc.create.vNode(["ActivityInstance"],properties(p_ai)) as ai,
apoc.create.vNode(["ActivityInstanceClass"],properties(p_aic)) as aic
WITH p_act,p_ai,p_aicr,p_aic,agrp,asgrp,act,ai,aic,r1,r2,
apoc.create.vRelationship(act,"HAS",{type:"logical"},ai) as r3,
apoc.create.vRelationship(ai,"OF_CLASS",{type:"logical"},aic) as r6
WITH p_act,p_ai,p_aicr,p_aic,agrp,asgrp,act,ai,aic,r1,r2,r3,r6
MATCH (p_ai:ActivityInstanceValue)-[R4:CONTAINS_ACTIVITY_ITEM]->(p_aitm1:ActivityItemValue)
OPTIONAL MATCH(p_aitm1)<-[R5:LATEST]-(p_aitm1r:ActivityItemRoot)<-[R6:HAS_ACTIVITY_ITEM]-(p_aitmc1r:ActivityItemClassRoot)-[R7:LATEST]->(p_aitmc1:ActivityItemClassValue)
OPTIONAL MATCH (p_aicr)-[R10:PARENT_CLASS]->(p_aicrp:ActivityInstanceClassRoot)-[R11:LATEST]->(p_aicp:ActivityInstanceClassValue)
OPTIONAL MATCH (p_aicrp)-[R12:PARENT_CLASS]->(p_aicrpp:ActivityInstanceClassRoot)-[R13:LATEST]->(p_aicpp:ActivityInstanceClassValue)
OPTIONAL MATCH(p_aitmc1r)<-[R14:HAS_ITEM_CLASS]-(p_aicr)
OPTIONAL MATCH(p_aitmc1r)<-[R15:HAS_ITEM_CLASS]-(p_aicrp)
OPTIONAL MATCH(p_aitmc1r)<-[R16:HAS_ITEM_CLASS]-(p_aicrpp) 
WITH p_act,p_ai,p_aicr,p_aic,p_aitm1,p_aitm1r,p_aitmc1r,p_aitmc1,p_aicp,p_aicpp,R14,R15,R16,agrp,asgrp,act,ai,aic,r1,r2,r3,r6,
apoc.create.vNode(["ActivityItem"],properties(p_aitm1)) as aitm1,
apoc.create.vNode(["ActivityItemClass"],properties(p_aitmc1)) as aitmc1,
CASE WHEN R15 is not null THEN apoc.create.vNode(["ActivityInstanceClass"],properties(p_aicp)) END as aicp,
CASE WHEN R16 is not null THEN apoc.create.vNode(["ActivityInstanceClass"],properties(p_aicpp)) END as aicpp
WITH p_act,p_ai,p_aicr,p_aic,p_aitm1,p_aitm1r,p_aitmc1r,p_aitmc1,R14,R15,R16,agrp,asgrp,act,ai,aic,aicp,aicpp,aitm1,aitmc1,r1,r2,r3,r6,
apoc.create.vRelationship(ai,"HAS",{type:"logical"},aitm1) as r4,
apoc.create.vRelationship(aitm1,"OF_CLASS",{type:"logical"},aitmc1) as r5,
CASE WHEN (R14 is not null) THEN 
apoc.create.vRelationship(aitmc1,"OF_CLASS",{type:"logical"},aic) END as r7,
CASE WHEN (R15 is not null) 
THEN apoc.create.vRelationship(aitmc1,"OF_CLASS",{type:"logical"},aicp) END as r8,
CASE WHEN (R16 is not null) 
THEN apoc.create.vRelationship(aitmc1,"OF_CLASS",{type:"logical"},aicpp) END as r9
with p_act,p_ai,p_aicr,p_aic,p_aitm1,p_aitm1r,p_aitmc1r,p_aitmc1,agrp,asgrp,act,ai,aic,aitm1,aitmc1,aicp,aicpp,r1,r2,r3,r4,r5,r6,r7,r8,r9
OPTIONAL MATCH (p_aitm1)-[R17]->(p_ct2cd:CTTermRoot)-[R18:HAS_NAME_ROOT]->(ct2cdr:CTTermNameRoot)-[R19:LATEST]->(p_ct2_sponsor), (p_ct2cd)-[R20:HAS_ATTRIBUTES_ROOT]->(ct2att:CTTermAttributesRoot)-[R21:LATEST]->(p_ct2_cdisc)
OPTIONAL MATCH (p_aitm1)-[:HAS_UNIT_DEFINITION]->(p_unitdefr:UnitDefinitionRoot)-[:LATEST]->(p_unitdef:UnitDefinitionValue)
OPTIONAL MATCH(p_aitmc1)-[:HAS_ROLE]->(p_role_r:CTTermRoot)-[:HAS_NAME_ROOT]->(ctnr_role)-[:LATEST]->(p_role_val), (p_role_r)-[:HAS_ATTRIBUTES_ROOT]->(ctattr)-[:LATEST]->(p_role_attr_val)
OPTIONAL MATCH(p_aitmc1)-[:HAS_DATA_TYPE]->(p_dtype_r)-[:HAS_NAME_ROOT]->(ctnr_dtype)-[:LATEST]->(p_dtype_val), (p_dtype_r)-[:HAS_ATTRIBUTES_ROOT]->(ctattr_dtype)-[:LATEST]->(p_dtype_attr_val)
with distinct p_act as p_act,p_ai as p_ai,p_aicr as p_aicr,p_aitm1 as p_aitm1,p_aitm1r as p_aitm1r,p_aitmc1r as p_aitmc1r,p_aitmc1 as p_aitmc1,p_ct2cd as p_ct2cd,p_ct2_sponsor as p_ct2_sponsor,p_ct2_cdisc as p_ct2_cdisc,p_unitdefr as p_unitdefr,p_unitdef as p_unitdef,p_role_r as p_role_r, p_role_val as p_role_val, p_role_attr_val as p_role_attr_val,p_dtype_r as p_dtype_r, p_dtype_val as p_dtype_val, p_dtype_attr_val as p_dtype_attr_val,
agrp as agrp,asgrp as asgrp,act as act,ai as ai,aic as aic,aitm1 as aitm1,aitmc1 as aitmc1,aicp as aicp,aicpp as aicpp,r1 as r1,r2 as r2,
r3 as r3,r4 as r4,r5 as r5,r6 as r6, r7 as r7, r8 as r8, r9 as r9
WITH distinct p_act,p_ai,p_aicr,p_aitm1,p_aitm1r,p_aitmc1r,p_aitmc1,p_ct2cd,p_unitdefr,p_unitdef,p_ct2_sponsor,p_ct2_cdisc,p_role_r,p_role_val,p_role_attr_val,p_dtype_r,p_dtype_val,p_dtype_attr_val,agrp,
asgrp,act,ai,aic,aicp,aicpp,aitm1,aitmc1,r1,r2,r3,r4,r5,r6,r7,r8,r9,
CASE WHEN p_ct2cd is not null THEN
apoc.create.vNode(["CTTerm"],apoc.map.merge(properties(p_ct2_cdisc),properties(p_ct2_sponsor))) END as ct2,
CASE WHEN p_unitdefr is not null THEN
apoc.create.vNode(["CTTerm"],properties(p_unitdef)) END as unit_ct,
CASE WHEN p_role_r is not null THEN apoc.create.vNode(["CTTerm"],apoc.map.merge(properties(p_role_val),properties(p_role_attr_val))) END as role,
CASE WHEN p_dtype_r is not null THEN apoc.create.vNode(["CTTerm"],apoc.map.merge(properties(p_dtype_val),properties(p_dtype_attr_val))) END as dtype
WITH distinct p_act,p_ai,p_aicr,p_aitm1,p_aitm1r,p_aitmc1r,p_aitmc1,p_ct2cd,p_unitdefr,p_unitdef,p_ct2_sponsor,p_ct2_cdisc,p_role_r,p_dtype_r,agrp,asgrp,act,
ai,aic,aicp,aicpp,aitm1,aitmc1,ct2,unit_ct,role,dtype,r1,r2,r3,r4,r5,r6,r7,r8,r9,
CASE WHEN p_ct2cd is not null THEN
apoc.create.vRelationship(aitm1,"FOR",{type:"logical"},ct2) END as r16, 
CASE WHEN p_unitdefr is not null THEN
apoc.create.vRelationship(aitm1,"FOR",{type:"logical"},unit_ct) END as r18,
CASE WHEN p_role_r is not null THEN apoc.create.vRelationship(aitmc1,"HAS_ROLE",{type:"logical"},role)END as r20,
CASE WHEN p_dtype_r is not null THEN apoc.create.vRelationship(aitmc1,"HAS_TYPE",{type:"logical"},dtype) END as r21
with distinct  p_act,p_ai,p_aicr,p_aitm1,p_aitm1r,p_aitmc1r,p_aitmc1,p_ct2cd,p_unitdef,p_unitdefr,p_ct2_sponsor,p_ct2_cdisc,agrp,asgrp,act,ai,aic,aicp,aicpp,aitm1,aitmc1,ct2,unit_ct,role,dtype,r1,r2,r3,r4,r5,r6,r7,r8,r9,r16,r18,r20,r21
OPTIONAL MATCH(p_ct2cd)<-[R22:HAS_TERM]-(clr:CTCodelistRoot)-[R23:HAS_ATTRIBUTES_ROOT]->(clatt:CTCodelistAttributesRoot),(clr)-[R24:HAS_NAME_ROOT]->(clattr:CTCodelistNameRoot)-[:LATEST]-(p_cl_sponsor),(clatt)-[:LATEST]->(p_cl_cdisc:CTCodelistAttributesValue),(pc:CTPackageCodelist) where ((p_cl_cdisc)<-[:CONTAINS_ATTRIBUTES]-(pc) and pc.uid CONTAINS "SDTM") or NOT ((p_cl_cdisc)<-[:CONTAINS_ATTRIBUTES]-())
OPTIONAL MATCH (p_unitdef:UnitDefinitionValue)-[:HAS_CT_DIMENSION]-(unit_term:CTTermRoot)<-[:HAS_TERM]-(cl_root)-[:HAS_ATTRIBUTES_ROOT]->(clattr2)-[:LATEST]->(unit_cld)
with distinct p_act as p_act,p_ai as p_ai,p_aicr as p_aicr,p_aitm1 as p_aitm1,p_aitm1r as p_aitm1r,p_aitmc1r as p_aitmc1r,p_aitmc1 as p_aitmc1,p_ct2cd as p_ct2cd,p_unitdefr as p_unitdefr,clr as clr,p_cl_sponsor as p_cl_sponsor,p_cl_cdisc as p_cl_cdisc, unit_cld as unit_cld,agrp as agrp,asgrp as asgrp,act as act,ai as ai,aic as aic,aitm1 as aitm1,aitmc1 as aitmc1,aicp as aicp,aicpp as aicpp,ct2 as ct2,unit_ct as unit_ct, role as role, dtype as dtype, r1 as r1,r2 as r2,r3 as r3,r4 as r4,r5 as r5,r6 as r6,r7 as r7,r8 as r8,r9 as r9,r16 as r16,r18 as r18,r20 as r20,r21 as r21
WITH p_act,p_ai,p_aicr,p_aitm1,p_aitm1r,p_aitmc1r,p_aitmc1,p_ct2cd,p_unitdefr,clr,p_cl_sponsor,p_cl_cdisc, unit_cld,agrp,asgrp,act,ai,aic,aicp,aicpp,aitm1,aitmc1,ct2,unit_ct,role,dtype,r1,r2,r3,r4,r5,r6,r7,r8,r9,r16,r18,r20,r21,
CASE WHEN p_ct2cd is not null THEN apoc.create.vNode(["CTCodeList"],apoc.map.merge(properties(p_cl_cdisc),properties(p_cl_sponsor))) END as cl,
CASE WHEN p_unitdefr is not null THEN
apoc.create.vNode(["CTCodeList"],properties(unit_cld)) END as unit_cl
WITH distinct p_act as p_act,p_ai as p_ai,p_aicr  as p_aicr,p_aitm1  as p_aitm1,p_aitm1r as p_aitm1r,p_aitmc1r as p_aitmc1r,p_aitmc1 as p_aitmc1,p_ct2cd  as p_ct2cd,p_unitdefr as p_unitdefr,agrp as agrp,asgrp as asgrp,act as act,ai as ai,aic as aic,aicp as aicp,aicpp as aicpp,aitm1 as aitm1,aitmc1 as aitmc1,ct2 as ct2,cl as cl,unit_ct as unit_ct,unit_cl as unit_cl, role as role, dtype as dtype,r1 as r1,r2 as r2,r3 as r3,r4 as r4,r5 as r5,r6 as r6,r7 as r7,r8 as r8,r9 as r9,r16 as r16,r18 as r18, r20 as r20, r21 as r21
WITH p_act,p_ai,p_aicr,p_aitm1,p_aitm1r,p_aitmc1r,p_aitmc1,p_ct2cd,p_unitdefr,agrp,asgrp,act,ai,aic,aicp,aicpp,aitm1,aitmc1,ct2,cl,unit_ct,unit_cl,role,dtype,r1,r2,r3,r4,r5,r6,r7,r8,r9,r16,r18,r20,r21,
CASE WHEN p_ct2cd is not null THEN
apoc.create.vRelationship(cl,"HAS",{type:"logical"},ct2) END as r17,
CASE WHEN p_unitdefr is not null THEN
apoc.create.vRelationship(unit_ct,"HAS",{type:"logical"},unit_cl) END as r19
return distinct agrp,asgrp,act,ai,aic,aicp,aicpp,aitm1,aitmc1,ct2,cl,unit_ct,unit_cl,role, dtype, r1,r2,r3,r4,r5,r6,r7,r8,r9,r16,r17,r18,r19,r20,r21

//activityInstance as cosmos concept
call custom.activityInstanceAsLogical($neodash_cosmos_activity_instance) YIELD row WITH 
row["aic"] as aic,
row["agrp"] as agrp,
row["aitmc1"] as aitmc1,
row["ai"] as ai,
row["dtype"] as dtype
with aic, asgrp, aitmc1,ai,dtype,
collect(distinct(coalesce(apoc.any.property(ct2,'code_submission_value'),apoc.any.property(unit_ct,'name')))) as val_list
WITH aic, asgrp, dtype, aitmc1,ai,val_list,toInteger(apoc.any.property(aitmc1,'order')) as var_order
call custom.nci_get_concept_code_from_term(apoc.any.property(aitmc1,'name')) YIELD code as item_concept_id
with aic, asgrp, dtype, aitmc1,ai, var_order, item_concept_id,
apoc.map.fromPairs( [
                    ['conceptId', item_concept_id],
                    ['href', 'https://ncithesaurus.nci.nih.gov/ncitbrowser/ConceptReport.jsp?dictionary=NCI_Thesaurus&ns=ncit&code='+item_concept_id],
                    ['shortName', apoc.any.property(aitmc1,'name')],
                    ['dataType',apoc.any.property(dtype,'name')],
                    ['exampleSet',val_list]
                    ]) as varlist order by var_order
with asgrp, aic, ai, collect(varlist) as vars,
CASE when (apoc.any.property(aic,'name')='NumericFinding') THEN 'Quantitative' ELSE 
CASE WHEN (apoc.any.property(aic,'name')='CategoricFinding') THEN 'Ordinal' ELSE 
 null END END as aiclass
 with asgrp,ai,vars,aiclass
 call custom.nci_get_concept_code_from_term(apoc.any.property(ai,'name')) YIELD code as conceptId
 with asgrp, ai,vars, aiclass,conceptId
 call custom.get_parent_concept_code(conceptId) YIELD code as parentConceptId
 with asgrp, ai,vars, aiclass,conceptId, parentConceptId
 call custom.get_nci_concept_definition(conceptId) YIELD conceptDefinition as conceptDefinition
 with asgrp, ai,vars, aiclass,conceptId, parentConceptId, conceptDefinition
 call custom.get_nci_concept_synonyms(bc_id) YIELD conceptSynonyms as bc_synonyms
  with asgrp, ai,vars, aiclass,conceptId, parentConceptId, conceptDefinition,bc_synonyms,
 apoc.map.fromPairs([ 
                    ['packageDate','2023-04-30'],
                    ['packageType','bc'],
                    ['conceptId',conceptID],
                    ['href', 'https://ncithesaurus.nci.nih.gov/ncitbrowser/ConceptReport.jsp?dictionary=NCI_Thesaurus&ns=ncit&code='+conceptId],
                    ['parentConceptId',parentConceptId],
                    ['category',collect(apoc.any.property(asgrp,'name'))],
                    ['shortName',apoc.any.property(ai,'name')],
                    ['synonym',collect(bc_synonyms)],
                    ['resultScale',aiclass],
                    ['definition',conceptDefinition],
                    ['dataElementConcepts', vars]
                    ]) as activity
return distinct activity