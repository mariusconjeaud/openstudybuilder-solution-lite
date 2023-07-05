<template>
<div class="pt-4">
  <n-n-table
    :headers="headers"
    :items="criteria"
    item-key="study_criteria_uid"
    hide-fixed-headers-switch
    :export-data-url="exportDataUrl"
    :export-data-url-params="exportDataUrlParams"
    export-object-label="StudyCriteria"
    :history-data-fetcher="fetchAllCriteriaHistory"
    :history-title="$t('EligibilityCriteriaTable.global_history_title')"
    :history-html-fields="historyHtmlFields"
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
    <template v-slot:actions>
      <v-btn
        data-cy="add-study-criteria"
        fab
        small
        color="primary"
        @click.stop="addCriteria"
        :title="$t('EligibilityCriteriaTable.add_criteria')"
        >
        <v-icon dark>
          mdi-plus
        </v-icon>
      </v-btn>
    </template>
    <template v-slot:item.name="{ item }">
      <template v-if="item.criteria_template">
        <n-n-parameter-highlighter
          :name="item.criteria_template.name"
          default-color="orange"
          />
      </template>
      <template v-else>
        <n-n-parameter-highlighter
          :name="item.criteria.name"
          :show-prefix-and-postfix="false"
          />
      </template>
    </template>
    <template v-slot:item.key_criteria="{ item }">
      <v-checkbox
        v-model="item.key_criteria"
        @change="updateKeyCriteria($event, item.study_criteria_uid)"
        />
    </template>
    <template v-slot:item.start_date="{ item }">
      {{ item.start_date|date }}
    </template>
    <template v-slot:item.actions="{ item }">
      <actions-menu
        :key="item.study_criteria_uid"
        :actions="filterEditAction(item)"
        :item="item"
        :badge="actionsMenuBadge(item)"
        />
    </template>
    <template v-slot:body="props" v-if="criteria.length > 0 && sortMode">
      <draggable
        :list="props.items"
        tag="tbody"
        @change="onOrderChange($event)"
        >
        <tr
          v-for="(item, index) in props.items"
          :key="index"
          >
          <td v-if="props.showSelectBoxes">
            <v-checkbox
              :value="item.criteria.name"
              hide-details
              @change="props.select(!props.isSelected(item))"
              />
          </td>
          <td>
            <actions-menu
              :key="item.studyCriteriaUid"
              :actions="filterEditAction(item)"
              :item="item"
              :badge="actionsMenuBadge(item)"
              />
          </td>
          <td>
            <v-icon
              small
              v-if="sortMode"
              >
              mdi-sort
            </v-icon>
            {{ item.order }}
          </td>
          <td>
            <template v-if="item.criteria_template">
              <n-n-parameter-highlighter
                :name="item.criteria_template.name"
                default-color="orange"
                />
            </template>
            <template v-else>
              <n-n-parameter-highlighter
                :name="item.criteria.name"
                :show-prefix-and-postfix="false"
                />
            </template>
          </td>
          <td>
            <template v-if="item.criteria_template">
              <span v-html="item.criteria_template.guidance_text" />
            </template>
            <template v-else>
              <span v-html="item.criteria.criteria_template.guidance_text" />
            </template>
          </td>
          <td>
            <v-checkbox
              v-model="item.key_criteria"
              @change="updateKeyCriteria($event, item.study_criteria_uid)"
              />
          </td>
          <td>
            {{ item.start_date|date }}
          </td>
          <td>
            {{ item.user_initials }}
          </td>
        </tr>
      </draggable>
    </template>
  </n-n-table>
  <v-dialog v-model="showForm"
            persistent
            fullscreen
            content-class="fullscreen-dialog"
            >
    <eligibility-criteria-form
      @close="closeForm"
      :criteriaType="criteriaType"
      class="fullscreen-dialog"
      @added="getStudyCriteria"
      />
  </v-dialog>
  <v-dialog
    v-model="showEditForm"
    persistent
    fullscreen
    content-class="fullscreen-dialog"
    >
    <eligibility-criteria-edit-form
      :study-criteria="selectedStudyCriteria"
      @close="closeEditForm"
      @updated="getStudyCriteria"
      class="fullscreen-dialog"
      />
  </v-dialog>
  <confirm-dialog ref="confirm" :text-cols="6" :action-cols="5" />
</div>
</template>

<script>
import ActionsMenu from '@/components/tools/ActionsMenu'
import { bus } from '@/main'
import ConfirmDialog from '@/components/tools/ConfirmDialog'
import draggable from 'vuedraggable'
import EligibilityCriteriaEditForm from './EligibilityCriteriaEditForm'
import EligibilityCriteriaForm from './EligibilityCriteriaForm'
import { mapGetters } from 'vuex'
import NNParameterHighlighter from '@/components/tools/NNParameterHighlighter'
import NNTable from '@/components/tools/NNTable'
import study from '@/api/study'

export default {
  props: {
    criteriaType: Object
  },
  components: {
    ActionsMenu,
    ConfirmDialog,
    draggable,
    EligibilityCriteriaEditForm,
    EligibilityCriteriaForm,
    NNParameterHighlighter,
    NNTable
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy'
    }),
    exportDataUrl () {
      return `studies/${this.selectedStudy.uid}/study-criteria`
    },
    exportDataUrlParams () {
      return {
        filters: JSON.stringify({ 'criteria_type.sponsor_preferred_name_sentence_case': { v: [this.criteriaType.sponsor_preferred_name_sentence_case] } })
      }
    },
    studyCriteriaHistoryTitle () {
      if (this.selectedStudyCriteria) {
        return this.$t(
          'EligibilityCriteriaTable.study_criteria_history_title',
          { studyCriteriaUid: this.selectedStudyCriteria.study_criteria_uid })
      }
      return ''
    }
  },
  data () {
    return {
      actions: [
        {
          label: this.$t('_global.edit'),
          icon: 'mdi-pencil',
          iconColor: 'primary',
          click: this.editStudyCriteria
        },
        {
          label: this.$t('_global.delete'),
          icon: 'mdi-delete',
          iconColor: 'error',
          click: this.deleteStudyCriteria
        },
        {
          label: this.$t('_global.history'),
          icon: 'mdi-history',
          click: this.openHistory
        }
      ],
      criteria: [],
      criteriaHistoryItems: [],
      headers: [
        { text: '', value: 'actions', width: '5%' },
        { text: '#', value: 'order', width: '5%' },
        { text: this.criteriaType.sponsor_preferred_name, value: 'name', width: '30%' },
        { text: this.$t('EligibilityCriteriaTable.guidance_text'), value: 'guidance_text', width: '20%' },
        { text: this.$t('EligibilityCriteriaTable.key_criteria'), value: 'key_criteria' },
        { text: this.$t('_global.modified'), value: 'start_date' },
        { text: this.$t('_global.modified_by'), value: 'user_initials' }
      ],
      historyHtmlFields: ['name', 'guidance_text'],
      selectedStudyCriteria: null,
      showEditForm: false,
      showForm: false,
      showHistory: false,
      sortMode: false
    }
  },
  methods: {
    async fetchAllCriteriaHistory () {
      const resp = await study.getStudyCriteriaAllAuditTrail(this.selectedStudy.uid, this.criteriaType.term_uid)
      return this.transformItems(resp.data)
    },
    actionsMenuBadge (item) {
      if (!item.criteria && item.criteria_template.parameters.length > 0) {
        return {
          color: 'error',
          icon: 'mdi-exclamation'
        }
      }
      return undefined
    },
    filterEditAction (item) {
      if ((item.criteria && item.criteria.parameter_terms.length > 0) || (item.criteria_template && item.criteria_template.parameters.length > 0)) {
        return this.actions
      } else {
        return this.actions.slice(1)
      }
    },
    addCriteria () {
      this.showForm = true
    },
    closeEditForm () {
      this.showEditForm = false
    },
    closeForm () {
      this.showForm = false
    },
    closeHistory () {
      this.selectedStudyCriteria = null
      this.showHistory = false
    },
    async openHistory (studyCriteria) {
      this.selectedStudyCriteria = studyCriteria
      const resp = await study.getStudyCriteriaAuditTrail(this.selectedStudy.uid, studyCriteria.study_criteria_uid)
      this.criteriaHistoryItems = this.transformItems(resp.data)
      this.showHistory = true
    },
    editStudyCriteria (studyCriteria) {
      this.showEditForm = true
      this.selectedStudyCriteria = studyCriteria
    },
    async deleteStudyCriteria (studyCriteria) {
      const options = { type: 'warning' }
      let criterion = (studyCriteria.criteria_template) ? studyCriteria.criteria_template.name : studyCriteria.criteria.name

      criterion = criterion.replaceAll(/\[|\]/g, '')
      if (await this.$refs.confirm.open(this.$t('EligibilityCriteriaTable.confirm_delete', { criterion }), options)) {
        await study.deleteStudyCriteria(this.selectedStudy.uid, studyCriteria.study_criteria_uid)
        this.getStudyCriteria()
        bus.$emit('notification', { msg: this.$t('EligibilityCriteriaTable.delete_success') })
      }
    },
    getStudyCriteria (sortByOrder) {
      study.getStudyCriteriaWithType(this.selectedStudy.uid, this.criteriaType).then(resp => {
        this.criteria = this.transformItems(resp.data.items)
        if (sortByOrder) {
          this.sortStudyCriteria()
        }
      })
    },
    onOrderChange (event) {
      const studyCriteria = event.moved.element
      const replacedStudyCriteria = this.criteria[event.moved.newIndex]
      study.updateStudyCriteriaOrder(this.selectedStudy.uid, studyCriteria.study_criteria_uid, replacedStudyCriteria.order).then(resp => {
        this.getStudyCriteria()
      })
    },
    sortStudyCriteria () {
      this.criteria.sort((a, b) => {
        return a.order - b.order
      })
    },
    updateKeyCriteria (value, studyCriteriaUid) {
      study.updateStudyCriteriaKeyCriteria(this.selectedStudy.uid, studyCriteriaUid, value).then(resp => {
        this.getStudyCriteria()
      })
    },
    transformItems (items) {
      const result = []
      for (const item of items) {
        const newItem = { ...item }
        if (newItem.criteria_template) {
          newItem.name = item.criteria_template.name
          newItem.guidance_text = item.criteria_template.guidance_text
        } else {
          newItem.name = item.criteria.name
          newItem.guidance_text = item.criteria.guidance_text
        }
        result.push(newItem)
      }
      return result
    }
  },
  mounted () {
    this.$store.dispatch('studiesGeneral/fetchTrialPhases')
    this.getStudyCriteria()
  },
  watch: {
    sortMode (value) {
      this.headers.forEach(header => {
        this.$set(header, 'sortable', !value)
      })
      this.sortStudyCriteria()
    }
  }
}
</script>
