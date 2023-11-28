<template>
<div>
  <n-n-table
    :headers="headers"
    :items="studyElements"
    :sort-desc="sortDesc"
    export-object-label="StudyElements"
    item-key="element_uid"
    :options.sync="options"
    :export-data-url="exportDataUrl"
    has-api
    :column-data-resource="`studies/${selectedStudy.uid}/study-elements`"
    @filter="getStudyElements"
    :history-data-fetcher="fetchElementsHistory"
    :history-title="$t('StudyElements.global_history_title')"
    >
    <template v-slot:afterSwitches>
      <div :title="$t('NNTableTooltips.reorder_content')">
        <v-switch
          v-model="sortMode"
          :label="$t('NNTable.reorder_content')"
          hide-details
          class="mr-6"
          />
      </div>
    </template>
    <template v-slot:body="props" v-if="sortMode">
      <draggable
        :list="props.items"
        tag="tbody"
        @change="onChange($event)"
        >
        <tr
          v-for="(item, index) in props.items"
          :key="index"
          >
          <td width="3%">
            <actions-menu :actions="actions" :item="item"/>
          </td>
          <td width="7%">
            <v-icon
              small
              class="page__grab-icon">
              mdi-sort
            </v-icon>
            {{ item.order }}
          </td>
          <td width="10%">{{ item.element_type.sponsor_preferred_name }}</td>
          <td width="10%">{{ item.element_subtype.sponsor_preferred_name }}</td>
          <td width="15%">{{ item.name }}</td>
          <td width="15%">{{ item.short_name }}</td>
          <td width="5%">{{ item.start_rule }}</td>
          <td width="10%">{{ item.end_rule }}</td>
          <td width="5%"><v-chip :data-cy="'color='+item.element_colour" :color="item.element_colour" small /></td>
          <td width="10%">{{ item.description }}</td>
          <td width="5%">{{ item.start_date | date }}</td>
          <td width="5%">{{ item.user_initials }}</td>
        </tr>
      </draggable>
    </template>
    <template v-slot:item.name="{ item }">
      <router-link :to="{ name: 'StudyElementOverview', params: { study_id: selectedStudy.uid, id: item.element_uid } }">
        {{ item.name }}
      </router-link>
    </template>
    <template v-slot:item.element_colour="{ item }">
      <v-chip :data-cy="'color='+item.element_colour" :color="item.element_colour" small />
    </template>
    <template v-slot:item.start_date="{ item }">
      {{ item.start_date | date }}
    </template>
    <template v-slot:item.actions="{ item }">
      <div class="pr-0 mr-0">
        <actions-menu :actions="actions" :item="item"/>
      </div>
    </template>
    <template v-slot:item.element_type="{ item }">
      {{ getElementType(item) }}
    </template>
    <template v-slot:actions="">
      <v-btn
        data-cy="add-study-compound"
        fab
        small
        color="primary"
        @click.stop="showForm = true"
        :title="$t('StudyElements.add_element')"
        :disabled="!checkPermission($roles.STUDY_WRITE) || selectedStudyVersion !== null"
      >
        <v-icon>
          mdi-plus
        </v-icon>
      </v-btn>
    </template>
  </n-n-table>
  <study-elements-form
    :open="showForm"
    @close="closeForm"
    :metadata="activeElement"
    />
  <v-dialog
    v-model="showElementHistory"
    @keydown.esc="closeElementHistory"
    persistent
    :max-width="globalHistoryDialogMaxWidth"
    :fullscreen="globalHistoryDialogFullscreen"
    >
    <history-table
      :title="studyElementHistoryTitle"
      @close="closeElementHistory"
      :headers="headers"
      :items="elementHistoryItems"
      />
  </v-dialog>
  <confirm-dialog ref="confirm" :text-cols="6" :action-cols="5" />
</div>
</template>

<script>
import { mapGetters } from 'vuex'
import { bus } from '@/main'
import ActionsMenu from '@/components/tools/ActionsMenu'
import ConfirmDialog from '@/components/tools/ConfirmDialog'
import NNTable from '@/components/tools/NNTable'
import StudyElementsForm from './StudyElementsForm'
import arms from '@/api/arms'
import terms from '@/api/controlledTerminology/terms'
import draggable from 'vuedraggable'
import filteringParameters from '@/utils/filteringParameters'
import { accessGuard } from '@/mixins/accessRoleVerifier'
import HistoryTable from '@/components/tools/HistoryTable'

export default {
  mixins: [accessGuard],
  components: {
    ConfirmDialog,
    NNTable,
    StudyElementsForm,
    ActionsMenu,
    HistoryTable,
    draggable
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy',
      selectedStudyVersion: 'studiesGeneral/selectedStudyVersion'
    }),
    exportDataUrl () {
      return `studies/${this.selectedStudy.uid}/study-elements`
    },
    studyElementHistoryTitle () {
      if (this.selectedElement) {
        return this.$t(
          'StudyElements.study_element_history_title',
          { elementUid: this.selectedElement.element_uid })
      }
      return ''
    }
  },
  data () {
    return {
      actions: [
        {
          label: this.$t('_global.edit'),
          icon: 'mdi-pencil-outline',
          iconColor: 'primary',
          condition: () => !this.selectedStudyVersion,
          click: this.editStudyElement,
          accessRole: this.$roles.STUDY_WRITE
        },
        {
          label: this.$t('_global.delete'),
          icon: 'mdi-delete-outline',
          iconColor: 'error',
          condition: () => !this.selectedStudyVersion,
          click: this.deleteStudyElement,
          accessRole: this.$roles.STUDY_WRITE
        },
        {
          label: this.$t('_global.history'),
          icon: 'mdi-history',
          click: this.openElementHistory
        }
      ],
      headers: [
        { text: '', value: 'actions', width: '5%' },
        { text: '#', value: 'order', width: '5%' },
        { text: this.$t('StudyElements.el_type'), value: 'element_type.sponsor_preferred_name' },
        { text: this.$t('StudyElements.el_sub_type'), value: 'element_subtype.sponsor_preferred_name' },
        { text: this.$t('StudyElements.el_name'), value: 'name' },
        { text: this.$t('StudyElements.el_short_name'), value: 'short_name' },
        { text: this.$t('StudyElements.el_start_rule'), value: 'start_rule' },
        { text: this.$t('StudyElements.el_end_rule'), value: 'end_rule' },
        { text: this.$t('StudyElements.colour'), value: 'element_colour' },
        { text: this.$t('_global.description'), value: 'description' },
        { text: this.$t('_global.modified'), value: 'start_date' },
        { text: this.$t('_global.modified_by'), value: 'user_initials' }
      ],
      showForm: false,
      sortBy: 'name',
      sortDesc: false,
      studyElements: [],
      activeElement: null,
      elementTypes: [],
      sortMode: false,
      options: {},
      total: 0,
      showElementHistory: false,
      elementHistoryItems: [],
      selectedElement: null,
      showStudyElementsHistory: false
    }
  },
  methods: {
    async fetchElementsHistory () {
      const resp = await arms.getStudyElementsVersions(this.selectedStudy.uid)
      return resp.data
    },
    getStudyElements (filters, sort, filtersUpdated) {
      const params = filteringParameters.prepareParameters(
        this.options, filters, sort, filtersUpdated)
      params.study_uid = this.selectedStudy.uid
      params.study_value_version = this.selectedStudyVersion
      arms.getStudyElements(this.selectedStudy.uid, params).then(resp => {
        this.studyElements = resp.data.items
        this.total = resp.data.total
      })
    },
    async deleteStudyElement (element) {
      const options = { type: 'warning' }
      let msg
      const context = { element: element.name }
      if (element.study_compound_dosing_count) {
        context.compoundDosings = element.study_compound_dosing_count
        msg = this.$t('StudyElements.confirm_delete_cascade', context)
      } else {
        msg = this.$t('StudyElements.confirm_delete', context)
      }
      if (!await this.$refs.confirm.open(msg, options)) {
        return
      }
      arms.deleteStudyElement(this.selectedStudy.uid, element.element_uid).then(resp => {
        bus.$emit('notification', { msg: this.$t('StudyElements.el_deleted') })
        this.getStudyElements()
      })
    },
    editStudyElement (item) {
      this.activeElement = item
      this.showForm = true
    },
    closeForm () {
      this.activeElement = null
      this.showForm = false
      this.getStudyElements()
    },
    async openElementHistory (element) {
      this.selectedElement = element
      const resp = await arms.getStudyElementVersions(this.selectedStudy.uid, element.element_uid)
      this.elementHistoryItems = resp.data
      this.showElementHistory = true
    },
    closeElementHistory () {
      this.showElementHistory = false
      this.selectedElement = null
    },
    getElementType (item) {
      const type = this.elementTypes.filter(el => el.term_uid === item.code)[0]
      if (item.code && type) {
        return type.sponsor_preferred_name
      }
    },
    onChange (event) {
      const element = event.moved.element
      const newOrder = {
        new_order: this.studyElements[event.moved.newIndex].order
      }
      arms.updateElementOrder(this.selectedStudy.uid, element.element_uid, newOrder).then(resp => {
        this.getStudyElements()
      })
    }
  },
  mounted () {
    this.getStudyElements()
    this.$store.dispatch('studiesGeneral/fetchUnits')
    terms.getByCodelist('elementTypes').then(resp => {
      this.elementTypes = resp.data.items
    })
  }
}
</script>
