<template>
<div>
  <v-row>
    <v-switch class="ml-6 mt-6" v-if="!loading" v-model="sortMode" :label="$t('CrfTree.reorder')"/>
  </v-row>
  <v-data-table
    ref="templatesTable"
    :headers="headers"
    item-key="uid"
    :options.sync="options"
    :server-items-length="total"
    :items="templates"
    export-data-url="concepts/odms/templates"
    show-expand
    light
    class="mt-5 tableMinWidth"
    :loading="loading"
    hide-default-header
    width="100%"
    :expanded="templatesExpand"
    sort-by="name"
    >
    <template v-slot:header="{ props: { headers } }">
      <thead>
        <tr>
          <th v-for="header in headers" v-bind:key="header.value">
            <span>{{ header.text }}</span>
          </th>
        </tr>
      </thead>
    </template>
    <template v-slot:item="{ item, expand, isExpanded }">
      <tr style="background-color: var(--v-dfltBackgroundLight1-base)">
        <td width="1%">
          <v-btn @click="expand(!isExpanded)" v-if="isExpanded" icon>
            <v-icon dark>
              mdi-chevron-up
            </v-icon>
          </v-btn>
          <v-btn @click="expand(!isExpanded), getForms(item)" v-else-if="!loading && item.forms.length > 0" icon>
            <v-icon dark>
              mdi-chevron-down
            </v-icon>
          </v-btn>
        </td>
        <td width="30%">
          <v-row>
            <div class="mt-3"><actions-menu :actions="actions" :item="item"/></div>
            <v-icon color="primary">mdi-alpha-t-circle</v-icon>
            <div class="mt-3 ml-1 mr-1">{{ item.name }}</div>
          </v-row>
        </td>
        <td width="20%">{{ item.version }}</td>
        <td width="15%"><status-chip :status="item.status" /></td>
        <td width="10%"></td>
        <td width="10%"></td>
        <td width="10%">
          <v-menu
            offset-y
            >
            <template v-slot:activator="{ on, attrs }">
              <div>
                <v-btn
                  fab
                  dark
                  small
                  v-bind="attrs"
                  v-on="on"
                  color="success"
                  :title="$t('CrfTree.link_forms')"
                  v-show="item.status !== statuses.FINAL"
                  >
                  <v-icon dark>
                    mdi-plus
                  </v-icon>
                </v-btn>
              </div>
            </template>
            <v-list>
              <v-list-item @click="openForm(item, 'forms')">
                <v-list-item-icon>
                  <v-icon>mdi-plus</v-icon>
                </v-list-item-icon>
                <v-list-item-content>
                  {{ $t('CrfTree.link_existing')}}
                </v-list-item-content>
              </v-list-item>
              <v-list-item @click="openFormsForm(item)">
                <v-list-item-icon>
                  <v-icon>mdi-pencil</v-icon>
                </v-list-item-icon>
                <v-list-item-content>
                  {{ $t('CrfTree.create_and_link')}}
                </v-list-item-content>
              </v-list-item>
            </v-list>
          </v-menu>
        </td>
      </tr>
    </template>
    <template v-slot:expanded-item="{ headers, item }">
      <td :colspan="headers.length" class="pa-0">
        <v-data-table
          ref="formsTable"
          :headers="headers"
          :items="item.forms"
          item-key="uid"
          light
          hide-default-footer
          hide-default-header
          show-expand
          :expanded="formsExpand"
          sort-by="order_number"
          :key="formsTableKey"
          >
          <template v-slot:item="{ item, expand, isExpanded }">
            <tr style="background-color: var(--v-dfltBackgroundLight2-base)">
              <td width="1%">
                <v-btn @click="expand(!isExpanded)" v-if="isExpanded" icon>
                  <v-icon dark>
                    mdi-chevron-up
                  </v-icon>
                </v-btn>
                <v-btn @click="expand(!isExpanded), getItemGroups(item)" v-else-if="item.item_groups && item.item_groups.length > 0" icon>
                  <v-icon dark>
                    mdi-chevron-down
                  </v-icon>
                </v-btn>
              </td>
              <td width="30%">
                <v-row>
                  <v-btn
                    class="mt-4 ml-3"
                    icon x-small
                    v-if="sortMode"
                    @click="reorderContent(item, -1)">
                    <v-icon>
                      mdi-arrow-up
                    </v-icon>
                  </v-btn>
                  <v-btn
                    class="mt-4"
                    icon
                    x-small
                    v-if="sortMode"
                    @click="reorderContent(item, 1)">
                    <v-icon>
                      mdi-arrow-down
                    </v-icon>
                  </v-btn>
                  <div class="ml-2 mt-3"><actions-menu :actions="actions" :item="item"/></div>
                  <v-icon color="success">mdi-alpha-f-circle</v-icon>
                  <div class="mt-3 ml-1 mr-1">{{ item.name }}</div>
                </v-row>
              </td>
              <td width="20%">{{ item.version }}</td>
              <td width="15%"><status-chip :status="item.status" /></td>
              <td width="10%">
                <v-tooltip bottom>
                  <template v-slot:activator="{ on, attrs }">
                    <v-icon
                      color="success"
                      v-bind="attrs"
                      v-on="on"
                      v-if="item.locked === 'Yes'">
                        mdi-lock
                    </v-icon>
                  </template>
                  <span>{{ $t('CrfTree.locked') }}</span>
                </v-tooltip>
                <v-tooltip bottom>
                  <template v-slot:activator="{ on, attrs }">
                    <v-icon
                      color="success"
                      v-bind="attrs"
                      v-on="on"
                      v-if="item.mandatory === 'Yes'">
                        mdi-database-lock
                    </v-icon>
                  </template>
                  <span>{{ $t('CrfTree.mandatory') }}</span>
                </v-tooltip>
              </td>
              <td width="10%">
                <v-tooltip bottom>
                  <template v-slot:activator="{ on, attrs }">
                    <v-icon
                      color="success"
                      v-bind="attrs"
                      v-on="on"
                      v-if="item.repeating === 'Yes'">
                        mdi-repeat
                    </v-icon>
                  </template>
                  <span>{{ $t('CrfTree.repeating') }}</span>
                </v-tooltip>
              </td>
              <td width="10%">
                <v-menu
                  offset-y
                  >
                  <template v-slot:activator="{ on, attrs }">
                    <div>
                      <v-btn
                        fab
                        dark
                        small
                        v-bind="attrs"
                        v-on="on"
                        color="secondary"
                        :title="$t('CrfTree.link_item_groups')"
                        v-show="item.status !== statuses.FINAL"
                        >
                        <v-icon dark>
                          mdi-plus
                        </v-icon>
                      </v-btn>
                    </div>
                  </template>
                  <v-list>
                    <v-list-item @click="openForm(item, 'item-groups')">
                      <v-list-item-icon>
                        <v-icon>mdi-plus</v-icon>
                      </v-list-item-icon>
                      <v-list-item-content>
                        {{ $t('CrfTree.link_existing')}}
                      </v-list-item-content>
                    </v-list-item>
                    <v-list-item @click="openItemGroupForm(item)">
                      <v-list-item-icon>
                        <v-icon>mdi-pencil</v-icon>
                      </v-list-item-icon>
                      <v-list-item-content>
                        {{ $t('CrfTree.create_and_link')}}
                      </v-list-item-content>
                    </v-list-item>
                  </v-list>
                </v-menu>
              </td>
            </tr>
          </template>
          <template v-slot:expanded-item="{ headers, item }">
            <td :colspan="headers.length" class="pa-0">
              <v-data-table
                class="elevation-0"
                :headers="headers"
                :items="item.item_groups"
                item-key="uid"
                light
                hide-default-footer
                hide-default-header
                show-expand
                :expanded="groupsExpand"
                sort-by="order_number"
                :key="groupsTableKey"
                >
                <template v-slot:item="{ item, expand, isExpanded }">
                  <tr style="background-color: var(--v-dfltBackground-base)">
                    <td width="1%">
                      <v-btn @click="expand(!isExpanded)" v-if="isExpanded" icon>
                        <v-icon dark>
                          mdi-chevron-up
                        </v-icon>
                      </v-btn>
                      <v-btn @click="expand(!isExpanded), getItems(item)" v-else-if="item.items && item.items.length > 0" icon>
                        <v-icon dark>
                          mdi-chevron-down
                        </v-icon>
                      </v-btn>
                    </td>
                    <td width="30%" class="pl-0">
                      <v-row>
                        <v-btn
                          class="mt-4 ml-7"
                          icon x-small
                          v-if="sortMode"
                          @click="reorderContent(item, -1)">
                          <v-icon>
                            mdi-arrow-up
                          </v-icon>
                        </v-btn>
                        <v-btn
                          class="mt-4"
                          icon
                          x-small
                          v-if="sortMode"
                          @click="reorderContent(item, 1)">
                          <v-icon>
                            mdi-arrow-down
                          </v-icon>
                        </v-btn>
                        <div class="mt-3 ml-8"><actions-menu :actions="actions" :item="item"/></div>
                        <v-icon color="secondary">mdi-alpha-g-circle</v-icon>
                        <div class="mt-3 ml-1 mr-1">{{ item.name }}</div>
                      </v-row>
                    </td>
                    <td width="20%">{{ item.version }}</td>
                    <td width="15%"><status-chip :status="item.status" /></td>
                    <td width="10%">
                      <v-tooltip bottom v-if="checkIfConditionExist(item)">
                        <template v-slot:activator="{ on, attrs }">
                          <v-icon
                            color="success"
                            v-bind="attrs"
                            v-on="on">
                            mdi-alert-circle-check-outline
                          </v-icon>
                        </template>
                        <span>{{ $t('CrfTree.condition_applied') }}</span>
                      </v-tooltip>
                      <v-tooltip bottom>
                        <template v-slot:activator="{ on, attrs }">
                          <v-icon
                            color="success"
                            v-bind="attrs"
                            v-on="on"
                            v-if="item.locked === 'Yes'">
                              mdi-lock
                          </v-icon>
                        </template>
                        <span>{{ $t('CrfTree.locked') }}</span>
                      </v-tooltip>
                      <v-tooltip bottom>
                        <template v-slot:activator="{ on, attrs }">
                          <v-icon
                            color="success"
                            v-bind="attrs"
                            v-on="on"
                            v-if="item.mandatory === 'Yes'">
                              mdi-database-lock
                          </v-icon>
                        </template>
                        <span>{{ $t('CrfTree.mandatory') }}</span>
                      </v-tooltip>
                    </td>
                    <td width="10%">
                      <v-tooltip bottom>
                        <template v-slot:activator="{ on, attrs }">
                          <v-icon
                            color="success"
                            v-bind="attrs"
                            v-on="on"
                            v-if="item.repeating === 'Yes'">
                              mdi-repeat
                          </v-icon>
                        </template>
                        <span>{{ $t('CrfTree.repeating') }}</span>
                      </v-tooltip>
                      <v-tooltip bottom>
                        <template v-slot:activator="{ on, attrs }">
                          <v-icon
                            color="success"
                            v-bind="attrs"
                            v-on="on"
                            v-if="item.isReferenceData === 'Yes'">
                              mdi-arrow-decision-outline
                          </v-icon>
                        </template>
                        <span>{{ $t('CrfTree.ref_data') }}</span>
                      </v-tooltip>
                    </td>
                    <td width="10%">
                      <v-menu
                        offset-y
                        >
                        <template v-slot:activator="{ on, attrs }">
                          <div>
                            <v-btn
                              fab
                              dark
                              small
                              v-bind="attrs"
                              v-on="on"
                              color="red"
                              :title="$t('CrfTree.link_items')"
                              v-show="item.status !== statuses.FINAL"
                              >
                              <v-icon dark>
                                mdi-plus
                              </v-icon>
                            </v-btn>
                          </div>
                        </template>
                        <v-list>
                          <v-list-item @click="openForm(item, 'items')">
                            <v-list-item-icon>
                              <v-icon>mdi-plus</v-icon>
                            </v-list-item-icon>
                            <v-list-item-content>
                              {{ $t('CrfTree.link_existing')}}
                            </v-list-item-content>
                          </v-list-item>
                          <v-list-item @click="openItemForm(item)">
                            <v-list-item-icon>
                              <v-icon>mdi-pencil</v-icon>
                            </v-list-item-icon>
                            <v-list-item-content>
                              {{ $t('CrfTree.create_and_link')}}
                            </v-list-item-content>
                          </v-list-item>
                        </v-list>
                      </v-menu>
                    </td>
                  </tr>
                </template>
                <template v-slot:expanded-item="{ headers, item }">
                  <td :colspan="headers.length" class="pa-0">
                    <v-data-table
                      class="elevation-0"
                      :headers="headers"
                      :items="item.items"
                      item-key="uid"
                      sort-by="order_number"
                      light
                      hide-default-footer
                      hide-default-header
                      :key="itemsTableKey"
                      >
                      <template v-slot:item="{ item }">
                        <tr>
                          <td width="1%">
                            <v-btn icon>
                            </v-btn>
                          </td>
                          <td width="30%" class="pl-0">
                            <v-row>
                              <v-btn
                                class="mt-4 ml-7"
                                icon x-small
                                v-if="sortMode"
                                @click="reorderContent(item, -1)">
                                <v-icon>
                                  mdi-arrow-up
                                </v-icon>
                              </v-btn>
                              <v-btn
                                class="mt-4"
                                icon
                                x-small
                                v-if="sortMode"
                                @click="reorderContent(item, 1)">
                                <v-icon>
                                  mdi-arrow-down
                                </v-icon>
                              </v-btn>
                              <div class="mt-3 ml-10"><actions-menu :actions="actions" :item="item"/></div>
                              <v-icon color="error">mdi-alpha-i-circle</v-icon>
                              <div class="mt-3 ml-1 mr-1">{{ item.name }}</div>
                            </v-row>
                          </td>
                          <td width="20%">{{ item.version }}</td>
                          <td width="15%"><status-chip :status="item.status" /></td>
                          <td width="10%">
                            <v-tooltip bottom v-if="checkIfConditionExist(item)">
                              <template v-slot:activator="{ on, attrs }">
                                <v-icon
                                  color="success"
                                  v-bind="attrs"
                                  v-on="on">
                                  mdi-alert-circle-check-outline
                                </v-icon>
                              </template>
                              <span>{{ $t('CrfTree.condition_applied') }}</span>
                            </v-tooltip>
                            <v-tooltip bottom>
                              <template v-slot:activator="{ on, attrs }">
                                <v-icon
                                  color="success"
                                  v-bind="attrs"
                                  v-on="on"
                                  v-if="item.locked === 'Yes'">
                                    mdi-lock
                                </v-icon>
                              </template>
                              <span>{{ $t('CrfTree.locked') }}</span>
                            </v-tooltip>
                            <v-tooltip bottom>
                              <template v-slot:activator="{ on, attrs }">
                                <v-icon
                                  color="success"
                                  v-bind="attrs"
                                  v-on="on"
                                  v-if="item.mandatory === 'Yes'">
                                    mdi-database-lock
                                </v-icon>
                              </template>
                              <span>{{ $t('CrfTree.mandatory') }}</span>
                            </v-tooltip>
                            <v-tooltip bottom>
                              <template v-slot:activator="{ on, attrs }">
                                <v-icon
                                  color="success"
                                  v-bind="attrs"
                                  v-on="on"
                                  v-if="item.sdv === 'Yes'">
                                    mdi-source-branch-check
                                </v-icon>
                              </template>
                              <span>{{ $t('CrfTree.sdv') }}</span>
                            </v-tooltip>
                            <v-tooltip bottom>
                              <template v-slot:activator="{ on, attrs }">
                                <v-icon
                                  color="success"
                                  v-bind="attrs"
                                  v-on="on"
                                  v-if="item.data_entry_required === 'Yes'">
                                    mdi-location-enter
                                </v-icon>
                              </template>
                              <span>{{ $t('CrfTree.entry_required') }}</span>
                            </v-tooltip>
                          </td>
                          <td width="10%">
                            <v-tooltip bottom>
                              <template v-slot:activator="{ on, attrs }">
                                <v-icon
                                  color="success"
                                  v-bind="attrs"
                                  v-on="on">
                                    mdi-chart-donut
                                </v-icon>
                              </template>
                              <span>{{ item.datatype + $t('CrfTree.data_type') }}</span>
                            </v-tooltip>
                          </td>
                          <td width="10%"></td>
                        </tr>
                      </template>
                    </v-data-table>
                  </td>
                </template>
              </v-data-table>
            </td>
          </template>
        </v-data-table>
      </td>
    </template>
  </v-data-table>
  <crf-link-form
    :open="showForm"
    @close="closeForm"
    @cancel="cancelForm"
    :itemToLink="itemToLink"
    :itemsType="linkedItemsType"
    />
  <v-dialog
    v-model="conditionForm"
    persistent
    content-class="fullscreen-dialog"
    >
    <crf-condition-form
      :itemToLink="itemToLink"
      @close="closeConditionForm"
      @cancel="cancelConditionForm"
      :crfForms="forms"
      :crfGroup="currentItemGroup"
      :crfGroups="itemGroups"
      :crfItems="items"/>
  </v-dialog>
  <v-dialog
    v-model="showFormsForm"
    persistent
    content-class="fullscreen-dialog"
    >
    <crf-form-form
      @close="closeFormsForm"
      @linkForm="linkForm"
      :editItem="elementToEdit"
      :readOnlyProp="readOnlyForm"
      class="fullscreen-dialog"
      />
  </v-dialog>
  <v-dialog
    v-model="showItemGroupForm"
    persistent
    content-class="fullscreen-dialog"
    >
    <crf-item-group-form
      @close="closeItemGroupForm"
      @linkGroup="linkGroup"
      :editItem="elementToEdit"
      :readOnlyProp="readOnlyForm"
      class="fullscreen-dialog"
      />
  </v-dialog>
  <v-dialog
    v-model="showItemForm"
    persistent
    content-class="fullscreen-dialog"
    >
    <crf-item-form
      @close="closeItemForm"
      @linkItem="linkItem"
      :editItem="elementToEdit"
      :readOnlyProp="readOnlyForm"
      class="fullscreen-dialog"
      />
  </v-dialog>
  <crf-references-form
    :open="attributesForm"
    :element="attributesElement"
    @close="closeAttributesForm"
    />
  <v-dialog v-model="showDuplicationForm"
            max-width="800px"
            persistent>
    <crf-duplication-form
      @close="closeDuplicateForm"
      :item="duplicateElement"
      :type="type"
      />
  </v-dialog>
</div>
</template>

<script>
import crfs from '@/api/crfs'
import StatusChip from '@/components/tools/StatusChip'
import CrfLinkForm from '@/components/library/CrfLinkForm'
import CrfConditionForm from '@/components/library/CrfConditionForm'
import ActionsMenu from '@/components/tools/ActionsMenu'
import CrfItemGroupForm from '@/components/library/CrfItemGroupForm'
import CrfFormForm from '@/components/library/CrfFormForm'
import CrfItemForm from '@/components/library/CrfItemForm'
import CrfReferencesForm from '@/components/library/CrfReferencesForm'
import constants from '@/constants/parameters'
import crfTypes from '@/constants/crfTypes'
import statuses from '@/constants/statuses'
import CrfDuplicationForm from '@/components/library/CrfDuplicationForm'

export default {
  components: {
    ActionsMenu,
    StatusChip,
    CrfLinkForm,
    CrfConditionForm,
    CrfItemGroupForm,
    CrfFormForm,
    CrfItemForm,
    CrfReferencesForm,
    CrfDuplicationForm
  },
  props: {
    source: String,
    refresh: String
  },
  created () {
    this.statuses = statuses
  },
  data () {
    return {
      headers: [
        { text: this.$t('CrfTree.items_for_linking'), value: 'name' },
        { text: this.$t('_global.version'), value: 'version' },
        { text: this.$t('_global.status'), value: 'status' },
        { text: this.$t('CrfTree.ref_attr'), value: 'refAttr' },
        { text: this.$t('CrfTree.def_attr'), value: 'defAttr' },
        { text: this.$t('CrfTree.link'), value: 'link' }
      ],
      options: {},
      total: 0,
      templates: [],
      forms: [],
      itemGroups: [],
      items: [],
      loading: false,
      showForm: false,
      itemToLink: {},
      linkedItemsType: '',
      currentItemGroup: {},
      conditionForm: false,
      actions: [
        {
          label: this.$t('CrfTree.edit_condition'),
          icon: 'mdi-pencil',
          click: this.openConditionForm,
          condition: (item) => (this.checkIfConditionExist(item) && !item.forms && !item.item_groups)
        },
        {
          label: this.$t('CrfTree.set_condition'),
          icon: 'mdi-pencil',
          click: this.openConditionForm,
          condition: (item) => (!this.checkIfConditionExist(item) && !item.forms && !item.item_groups)
        },
        {
          label: this.$t('CrfTree.delete_condition'),
          icon: 'mdi-delete',
          iconColor: 'error',
          click: this.deleteCondition,
          condition: (item) => (this.checkIfConditionExist(item) && !item.forms && !item.item_groups)
        },
        {
          label: this.$t('CrfTree.go_to_def'),
          icon: 'mdi-arrow-left',
          click: this.goToDefinition
        },
        {
          label: 'Edit reference attributes',
          icon: 'mdi-pencil',
          click: this.editAttributes,
          condition: (item) => (item.status === statuses.DRAFT)
        },
        {
          label: 'Approve All',
          icon: 'mdi-check-decagram',
          click: this.approveAll,
          condition: (item) => (item.status === statuses.DRAFT)
        },
        {
          label: this.$t('_global.duplicate'),
          icon: 'mdi-content-copy',
          iconColor: 'primary',
          click: this.openDuplicateForm
        },
        {
          label: this.$t('CrfTree.preview_odm'),
          icon: 'mdi-file-xml-box',
          click: this.previewODM
        },
        {
          label: this.$t('CrfTree.expand'),
          icon: 'mdi-arrow-expand-down',
          condition: (item) => item.forms,
          click: this.expandWholeTemplate
        }
      ],
      templatesExpand: [],
      formsExpand: [],
      groupsExpand: [],
      showFormsForm: false,
      showTemplateForm: false,
      showItemGroupForm: false,
      showItemForm: false,
      sortMode: false,
      elementToEdit: {},
      readOnlyForm: false,
      type: '',
      formsTableKey: 0,
      groupsTableKey: 0,
      itemsTableKey: 0,
      attributesForm: false,
      attributesElement: {},
      showDuplicationForm: false,
      duplicateElement: {}
    }
  },
  methods: {
    openDuplicateForm (item) {
      this.duplicateElement = item
      this.type = item.forms ? crfTypes.TEMPLATE : item.item_groups ? crfTypes.FORM : item.items ? crfTypes.GROUP : crfTypes.ITEM
      this.showDuplicationForm = true
    },
    closeDuplicateForm () {
      this.type = ''
      this.showDuplicationForm = false
    },
    approveAll (item) {
      if (item.forms) {
        this.approveFormsAndTemplate(item)
      } else if (item.item_groups) {
        this.approveGroupsAndForm(item)
      } else {
        this.approveItemsAndGroup(item)
      }
    },
    async approveFormsAndTemplate (template) {
      for (const form of template.forms) {
        this.approveGroupsAndForm(form)
      }
      if (template.status === statuses.DRAFT) {
        await crfs.approve('templates', template.uid).then((resp) => {
          template.status = statuses.FINAL
        })
      }
    },
    async approveGroupsAndForm (form) {
      for (const group of form.item_groups) {
        this.approveItemsAndGroup(group)
      }
      if (form.status === statuses.DRAFT) {
        await crfs.approve('forms', form.uid).then((resp) => {
          form.status = statuses.FINAL
        })
      }
    },
    async approveItemsAndGroup (group) {
      for (const item of group.items) {
        if (item.status === statuses.DRAFT) {
          await crfs.approve('items', item.uid).then((resp) => {
            item.status = statuses.FINAL
          })
        }
      }
      if (group.status === statuses.DRAFT) {
        await crfs.approve('item-groups', group.uid).then((resp) => {
          group.status = statuses.FINAL
        })
      }
    },
    editAttributes (item) {
      this.attributesElement = item
      this.attributesForm = true
    },
    closeAttributesForm () {
      this.attributesElement = {}
      this.attributesForm = false
      this.groupsTableKey += 1
    },
    async expandWholeTemplate (item) {
      this.templatesExpand = this.templatesExpand.concat([item])
      await this.getForms(item)
      this.formsExpand = this.formsExpand.concat(item.forms)
      let groups = []
      for (const form of item.forms) {
        await this.getItemGroups(form)
        groups = groups.concat(form.item_groups)
      }
      this.groupsExpand = this.groupsExpand.concat(groups)
      for (const group of this.groupsExpand) {
        await this.getItems(group)
      }
    },
    previewODM (item) {
      const data = {
        tab: 'odm-viewer',
        uid: item.uid
      }
      if (item.forms) {
        data.type = crfTypes.TEMPLATE
      } else if (item.item_groups) {
        data.type = crfTypes.FORM
      } else if (item.items) {
        data.type = crfTypes.ITEM_GROUP
      } else {
        data.type = crfTypes.ITEM
      }
      this.$emit('redirectToPage', data)
    },
    goToDefinition (item) {
      const data = {
        uid: item.uid
      }
      if (item.forms) {
        data.type = crfTypes.TEMPLATE
        data.tab = 'templates'
      } else if (item.item_groups) {
        data.type = crfTypes.FORM
        data.tab = 'forms'
      } else if (item.items) {
        data.type = crfTypes.ITEM_GROUP
        data.tab = 'item-groups'
      } else {
        data.type = crfTypes.ITEM
        data.tab = 'items'
      }
      this.$emit('redirectToPage', data)
    },
    reorderContent (item, direction) {
      if (item.order_number === 0 && direction === -1) {
        return
      }
      const movedItemNewOrder = item.order_number + direction
      if (item.parentGroupUid) {
        const group = this.itemGroups.find(group => group.uid === item.parentGroupUid)
        if (direction === 1) {
          this.$set(group.items.find(el => el.order_number === movedItemNewOrder), 'order_number', (group.items.find(el => el.order_number === movedItemNewOrder).order_number - 1))
          item.order_number = movedItemNewOrder
        } else {
          this.$set(group.items.find(el => el.order_number === movedItemNewOrder), 'order_number', (group.items.find(el => el.order_number === movedItemNewOrder).order_number + 1))
          item.order_number = movedItemNewOrder
        }
        crfs.addItemsToItemGroup(group.items, group.uid, true).then(resp => {
        })
      } else if (item.parentFormUid) {
        const form = this.forms.find(form => form.uid === item.parentFormUid)
        if (direction === 1) {
          this.$set(form.item_groups.find(el => el.order_number === movedItemNewOrder), 'order_number', (form.item_groups.find(el => el.order_number === movedItemNewOrder).order_number - 1))
          item.order_number = movedItemNewOrder
        } else {
          this.$set(form.item_groups.find(el => el.order_number === movedItemNewOrder), 'order_number', (form.item_groups.find(el => el.order_number === movedItemNewOrder).order_number + 1))
          item.order_number = movedItemNewOrder
        }
        crfs.addItemGroupsToForm(form.item_groups, form.uid, true).then(resp => {
        })
      } else if (item.parentTemplateUid) {
        const template = this.templates.find(template => template.uid === item.parentTemplateUid)
        if (direction === 1) {
          this.$set(template.forms.find(el => el.order_number === movedItemNewOrder), 'order_number', (template.forms.find(el => el.order_number === movedItemNewOrder).order_number - 1))
          item.order_number = movedItemNewOrder
        } else {
          this.$set(template.forms.find(el => el.order_number === movedItemNewOrder), 'order_number', (template.forms.find(el => el.order_number === movedItemNewOrder).order_number + 1))
          item.order_number = movedItemNewOrder
        }
        crfs.addFormsToTemplate(template.forms, template.uid, true).then(resp => {
        })
      }
    },
    checkIfConditionExist (item) {
      return (item.collection_exception_condition_oid && item.collection_exception_condition_oid !== 'null' && item.collection_exception_condition_oid !== 'none')
    },
    openConditionForm (item) {
      this.itemToLink = item
      this.conditionForm = true
    },
    closeConditionForm () {
      this.itemToLink = {}
      this.conditionForm = false
      this.getTemplates()
    },
    cancelConditionForm () {
      this.itemToLink = {}
      this.conditionForm = false
    },
    openFormsForm (item) {
      this.itemToLink = item
      this.showFormsForm = true
    },
    closeFormsForm () {
      this.showFormsForm = false
      this.itemToLink = {}
      this.readOnlyForm = false
      this.getTemplates()
    },
    openItemGroupForm (item) {
      this.itemToLink = item
      this.showItemGroupForm = true
    },
    closeItemGroupForm () {
      this.showItemGroupForm = false
      this.itemToLink = {}
      this.readOnlyForm = false
      this.getTemplates()
    },
    openItemForm (item) {
      this.itemToLink = item
      this.showItemForm = true
    },
    closeItemForm () {
      this.showItemForm = false
      this.itemToLink = {}
      this.readOnlyForm = false
      this.getTemplates()
    },
    closeTemplateForm () {
      this.showTemplateForm = false
      this.itemToLink = {}
      this.readOnlyForm = false
      this.getTemplates()
    },
    linkForm (form) {
      const payload = [{
        uid: form.data.uid,
        order_number: this.itemToLink.forms.length,
        mandatory: false,
        collection_exception_condition_oid: null
      }]
      crfs.addFormsToTemplate(payload, this.itemToLink.uid, false).then(resp => {
        this.getTemplates()
      })
    },
    linkGroup (group) {
      const payload = [{
        uid: group.data.uid,
        order_number: this.itemToLink.item_groups.length,
        mandatory: false,
        collection_exception_condition_oid: null
      }]
      crfs.addItemGroupsToForm(payload, this.itemToLink.uid, false).then(resp => {
        this.getTemplates()
      })
    },
    linkItem (item) {
      const payload = [{
        uid: item.data.uid,
        order_number: this.itemToLink.items.length,
        mandatory: false,
        collection_exception_condition_oid: null,
        key_sequence: constants.NULL,
        methodOid: constants.NULL,
        imputation_method_oid: constants.NULL,
        role: constants.NULL,
        role_codelist_oid: constants.NULL,
        data_entry_required: 'No',
        sdv: 'No'
      }]
      crfs.addItemsToItemGroup(payload, this.itemToLink.uid, false).then(resp => {
        this.getTemplates()
      })
    },
    deleteCondition (item) {
      const data = {}
      data.filters = `{"oid":{ "v": ["${item.collection_exception_condition_oid}"], "op": "co" }}`
      crfs.getConditionByOid(data).then(resp => {
        crfs.deleteCondition(resp.data.items[0].uid).then(resp => {
          this.getTemplates()
        })
      })
    },
    async getForms (item) {
      // Checking if Template has any Forms
      if (item.forms && item.forms.length > 0) {
        const formsToGet = []
        item.forms.forEach(form => {
          // Checking if Form was already fetched from API, if not then it's added to an Object that holds Forms that we need to fetch
          if (!this.forms.find(el => el.uid === form.uid)) {
            formsToGet.push(form.uid)
          }
        })
        if (formsToGet.length > 0) {
          // Calling for Forms that were not yet fetched and saving them in forms Object so that we don't have to get them again for other Templates
          const params = {
            total_count: true,
            filters: { uid: { v: formsToGet } }
          }
          await crfs.get('forms', { params }).then((resp) => {
            resp.data.items.forEach(form => {
              resp.data.items[resp.data.items.indexOf(form)].parentTemplateUid = item.uid
            })
            formsToGet.forEach(form => {
              this.forms.push({ ...item.forms.find(el => el.uid === form), ...resp.data.items.find(el => el.uid === form) })
            })
          })
        }
        const forms = []
        // Overwriting Forms for those from forms Object
        this.templates.find(el => el.uid === item.uid).forms.forEach((form, index) => {
          forms.push(this.forms.find(el => el.uid === form.uid))
        })
        this.templates.find(el => el.uid === item.uid).forms = forms
        this.formsTableKey += 1
      }
      // Same logic was applied for Item Groups and Items
    },
    async getItemGroups (item) {
      if (item.item_groups && item.item_groups.length > 0) {
        const groupsToGet = []
        item.item_groups.forEach(group => {
          if (!this.itemGroups.find(el => el.uid === group.uid)) {
            groupsToGet.push(group.uid)
          }
        })
        if (groupsToGet.length > 0) {
          const params = {
            total_count: true,
            filters: { uid: { v: groupsToGet } }
          }
          await crfs.get('item-groups', { params }).then((resp) => {
            resp.data.items.forEach(group => {
              resp.data.items[resp.data.items.indexOf(group)].parentFormUid = item.uid
            })
            groupsToGet.forEach(group => {
              this.itemGroups.push({ ...item.item_groups.find(el => el.uid === group), ...resp.data.items.find(el => el.uid === group) })
            })
          })
        }
        const groups = []
        this.forms.find(el => el.uid === item.uid).item_groups.forEach((group, index) => {
          groups.push(this.itemGroups.find(el => el.uid === group.uid))
        })
        this.forms.find(el => el.uid === item.uid).item_groups = groups
        this.groupsTableKey += 1
      }
    },
    async getItems (item) {
      if (item.items.length > 0) {
        const itemsToGet = []
        item.items.forEach(item => {
          if (!this.items.find(el => el.uid === item.uid)) {
            itemsToGet.push(item.uid)
          }
        })
        if (itemsToGet.length > 0) {
          const params = {
            total_count: true,
            filters: { uid: { v: itemsToGet } }
          }
          await crfs.get('items', { params }).then((resp) => {
            resp.data.items.forEach(group => {
              resp.data.items[resp.data.items.indexOf(group)].parentGroupUid = item.uid
            })
            itemsToGet.forEach(it => {
              this.items.push({ ...item.items.find(el => el.uid === it), ...resp.data.items.find(el => el.uid === it) })
            })
          })
        }
        const items = []
        this.itemGroups.find(el => el.uid === item.uid).items.forEach((item, index) => {
          items.push(this.items.find(el => el.uid === item.uid))
        })
        this.itemGroups.find(el => el.uid === item.uid).items = items
        this.itemsTableKey += 1
      }
    },
    async getTemplates (sort) {
      this.loading = true
      const params = {
        page_number: (this.options.page),
        page_size: this.options.itemsPerPage,
        total_count: true
      }
      await crfs.get('templates', { params }).then((resp) => {
        this.templates = resp.data.items
        this.total = resp.data.total
      })
      this.loading = false
    },
    openForm (item, type) {
      this.linkedItemsType = type
      this.itemToLink = item
      this.showForm = true
    },
    closeForm () {
      this.showForm = false
      this.itemToLink = {}
      this.templatesExpand = []
      this.getTemplates()
    },
    cancelForm () {
      this.showForm = false
      this.itemToLink = {}
    }
  },
  watch: {
    options () {
      this.getTemplates()
    }
  }
}
</script>
<style scoped>
.tableMinWidth {
  min-width: 1440px !important;
}
.templates {
  background-color: var(--v-dfltBackgroundLight1-base);

}
.group {
  background-color: var(--v-dfltBackgroundLight2-base);
}
</style>
