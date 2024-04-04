# Reports and Dashboards

Beside the table listing and download option generally available in the StudyBuilder application the system also support NeoDash reports and dashboards.

> Note: In the current release NeoDash must be opened manually, described in next section. From next release, links to the NeoDash reports will be embedded into the StudyBuilder app.

> Note: In the current release only one NeoDash report is supported (Activity Dashboard). From next release multiple reports will be supported.

## Open NeoDash

The URL to access the NeoDash report will follow this pattern, where text in '[ ]' is optional and *italic* text is replaced by environment specific values:

> [open]studybuilder[.*environment*].*domain*/neodash/

A simple way to get the URL for the NeoDash reports is:
1. Click on the StudyBuilder application logo in the top left corner.
2. Copy the URL from the address line
3. Open a new tab in the browser, paste the URL, and add: /neodash/
4. The NeoDash login page should be displayed <br>
![Study Builder](~@source/images/user_guides/neodash_sso_screen.png) <br>
5. Select to use 'SSO' and then click the 'Sign in' button.<br>

> Note: Select the database in which the neodash report is stored. Typically the mdr and not neo4j.

6. If requested to select a browser account, select your Microsoft identity account you use for the application.
7. The NeoDash report should open


## Activity Library Dashboard

Additionally to the Application, a Neo4j Dashboard is available to browse and understand biomedical concepts which are the activities in the StudyBuilder. 

Within the StudyBuilder application, you can define and see the activities in the "Library" -> "Concepts" -> "Activities" part.

![StudyBuilder view of activities](~@source/images/user_guides/guide_bc_dash_06.png)

The activities are managed in groups and subgroups. Whereas the "Activity" can be viewed as an "umbrella" that defines all general attributes, the "ActivityInstance" is the detailed specification of the logical observation. This includes reference to context and qualifier values. For example, the ActivityInstance includes references to ADaM BDS PARAM/PARAMCD or column name in ADSL, it also includes internal unique identification as well as internal topic code. This detailed specification will enable unique identification of source data, representation in SDTM by several qualifiers, and representation in ADaM BDS by PARAMCD value.


### Activity Dashboard

The activity dashboard is an option to view the activities from a different perspective. Especially when working with biomedical concepts from the StudyBuilder and others like the CDISC CoSMOS, it might be valuable to have a database closer access as the dashboard provides. When you have access to the StudyBuilder environment, see guide on how to open NeoDash in previous section.

The dashboard is organized in different tabs supporting different purposes. 

![Screenshot of Tabs from dashboard](~@source/images/user_guides/guide_bc_dash_15.png)

* <b>ReadMe</b>
This tab provides a quick overview of the numbers of Activities and ActivityInstances. 
<br>
* <b>Search top-down/bottom-up</b>
These two tabs are designed to navigate the "Activity Lib" either via a top-down or bottom-up search. 
<br>
* <b>Activity to SDTM</b>
Then there is the option to get Activities to SDTM using a specific implementation guide. 
<br>
* <b>Activity in COSMOS format</b>
As the CDISC collaboration with the CoSMOS initiative is very important, there is also a mapping of activities in the StudyBuilder to the CDISC CoSMOS format.
<br>
* <b>Activites used in studies</b>
An overview of the activity usage in studies. This view is preliminary and will be expanded with more study details.
<br>
* <b>Search Activity Instance</b>
This is a page for searching directly from ActivityInstance level.
<br>
* <b>Basic dashboard features</b>
In the panels there are options to expand/maximise and to refresh

![Icons for Maximize and Refresh](~@source/images/user_guides/guide_bc_dash_16.png)


#### Introduction / ReadMe

The first dashboard page gives an overview of activities, their grouping and the types including counting statistics.

![Screenshot of "ReadMe" tab from dashboard](~@source/images/user_guides/guide_bc_dash_05.png)

The first graphic (A) shows the "Groupings of Activities" as a circle-packing, which shows the available types and sub-types. To drill-down click on one of the circles. To get back click on the refresh icon in the top-right corner of the panel.

Next to this, there are the numbers of activities and instances (B). An instance is the specific definition of an observation which is used in studies. The table for "Number of Activities and Instances by group and subgroup" (C) can be used to get an overview of the groups and subgroups whereas the table "Number of Activities and Instances by type and subtype" shows the overview with type and sub type (D).

#### Activity Lib (search top-down)

The second tab allows you to look at activities from the top-down perspective. You can browse the class and sub-class followed by the group and subgroup. 

![Screenshot of second tab from dashboard](~@source/images/user_guides/guide_bc_dash_08.png)

The description section in the top of the page provides a short guide to the selection panel below. Start typing from the left-most panel and move toward the right side.

In the selection area (A) a class is provided (fx Findings, Events, Interventions) to narrow down the list of Activities. Then the sub-class is provided (fx Numeric Finding, Categoric Finding etc), group and finally sub-group. 

> Note: specifying a sub-group will display all the individual activities in the histogram as individual bars. The hight of the bar indicates the number of instances for the activity.

The "Number of activities" histogram (B) updates with the concrete numbers when you filter the activities. 

Depending on your selection in filter (A), the "List of activities" (C) lists the activities matching your filter. When clicking one concrete activity, the details of this activity are displayed (D).

![Screenshot for selecting an activity](~@source/images/user_guides/guide_bc_dash_09.png)

We can see that the `PULSE RATE` has an associated domain, a test_name_code which consists of a code and a name, a unit_dimension and a standard_unit.

Below we can see the representation of that activity as in the graph database in the logical view or physical view (E). The complex model enables us to link all information. The following screenshot shows the logical view for `PULSE RATE`. 

![Screenshot for logical view for pulse rate](~@source/images/user_guides/guide_bc_dash_10.png)

The last part displays information about concrete activities instances. There is the selection part (F) and the display as logical view part (G). 

When we select for example `ALBUMIN` as activity, it could have three different instances depending on the purpose of activity collection. 

![Screenshot for ALBUMIN instances](~@source/images/user_guides/guide_bc_dash_11.png)

There is an instance for "Albumin Urine", where the specimen is "Urine", the second instance is for the specimen "Serum" and the third one is collected differently with the purpose for "AE Requiring Additional Data".

#### Activity Lib (search bottom-up)

The search bottom-up tab enables you to search for one or more activities in the search field (A) and get an overview of the groups (B) and sub-groups (C) the selected activities belong to. In (D) you can select the activity belonging to the group and sub-group of interest and have its details displayed in (E).

![Screenshot for bottom-up content](~@source/images/user_guides/guide_bc_dash_12.png)

#### Activity to SDTM

The "Activity to SDTM" tab provides a detailed view of how activities are linked to specific SDTM items within a particular implementation guide. This feature allows you to visualize the relationship between activities and SDTM items, enhancing your understanding of the data structure.

![Screenshot for Activity to SDTM](~@source/images/user_guides/guide_bc_dash_13.png)

The dashboard has a 1000 row limitation to display, so to limit the number of activity instances, you can select the activity sub-group and the corresponding activity instance belonging to the selected sub-group are listed in (A). Given that SDTM standards evolve over time, item definitions and structures may change. Therefore, you have the option to select a specific implementation version (B). Once selected, the mapping as defined in the implementation guide is displayed (C). Please note that for some activities, the mapping may not yet be available in the database. In such cases, the mapping will not be displayed until it is added.

#### Activity in COSMoS format

In an effort to standardize and streamline the representation of Biomedical Concepts, CDISC initiated the Conceptual and Operational Standards Metadata Services (COSMoS) project in 2022. More details about this project can be found on their <a href="https://www.cdisc.org/cdisc-biomedical-concepts" target="_blank">homepage</a>. As part of this initiative, CDISC has adopted the YAML format for displaying biomedical concepts.

Our dashboard has been designed to align with this standard. It can map the activities defined in StudyBuilder into a valid COSMoS format, ensuring compatibility and interoperability with other systems that adhere to the same standard.

The following section presents an example of how the activity instance "TEMPERATURE" is represented in the COSMoS format.

```yaml
category:
  - Vital Signs
dataElementConcepts:
  - dataType: string
    conceptId: C44276
    exampleSet:
      - TEMPERATURE
    shortName: unit_dimension
    href: https://ncithesaurus.nci.nih.gov/ncitbrowser/ConceptReport.jsp?dictionary=NCI_Thesaurus&ns=ncit&code=C44276
  - dataType: string
    conceptId: C82587
    exampleSet:
      - C
    shortName: standard_unit
    href: https://ncithesaurus.nci.nih.gov/ncitbrowser/ConceptReport.jsp?dictionary=NCI_Thesaurus&ns=ncit&code=C82587
  - dataType: string
    conceptId: C25341
    exampleSet:
      - SKIN
    shortName: location
    href: https://ncithesaurus.nci.nih.gov/ncitbrowser/ConceptReport.jsp?dictionary=NCI_Thesaurus&ns=ncit&code=C25341
packageType: bc
definition: A measurement of the temperature of the body.
synonym:
  - TEMP
  - Temperature
resultScale:
  - Quantitative
conceptId: C174446
domain: VS
parentConceptId: C25206
shortName: Body Temperature
href: https://ncithesaurus.nci.nih.gov/ncitbrowser/ConceptReport.jsp?dictionary=NCI_Thesaurus&ns=ncit&code=C174446
packageDate: 2023-04-30
```

#### Activities used in Studies

This provides a view of where specific activities are utilized across different studies. This feature allows you to track the usage of activities.

In the selection box (A), you can choose one or more activities. Upon selection, the dashboard dynamically displays the studies in which these activities are used (B). 

![Screenshot for Activities used in Studies](~@source/images/user_guides/guide_bc_dash_14.png)

#### Search Activity Instance
This view provides a quick way to display details of one or more activity instances without having to specify the activity. 