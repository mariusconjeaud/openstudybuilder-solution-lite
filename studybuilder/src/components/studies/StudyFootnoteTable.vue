<template>
<div>
  <n-n-table
    :headers="headers"
    :items="studyFootnotes"
    item-key="uid"
    has-api
    :column-data-resource="`studies/${selectedStudy.uid}/study-soa-footnotes`"
    export-object-label="StudyFootnotes"
    :export-data-url="exportDataUrl"
    :options.sync="options"
    :server-items-length="total"
    @filter="fetchFootnotes"
    :history-data-fetcher="fetchFootnotesHistory"
    :history-title="$t('StudyFootnoteTable.global_history_title')"
    :history-html-fields="historyHtmlFields"
    >
    <template v-slot:actions>
      <v-btn
        data-cy="add-study-footnote"
        fab
        small
        color="primary"
        @click.stop="showForm = true"
        :title="$t('StudyFootnoteForm.add_title')"
        :disabled="!checkPermission($roles.STUDY_WRITE) || selectedStudyVersion !== null"
        >
        <v-icon>
          mdi-plus
        </v-icon>
      </v-btn>
    </template>
    <template v-slot:item.order="{ item }">
      {{ item.order | letteredOrder }}
    </template>
    <template v-slot:item.name="{ item }">
      <template v-if="item.footnote_template">
        <n-n-parameter-highlighter
          :name="item.footnote_template.name"
          default-color="orange"
          />
      </template>
      <template v-else>
        <n-n-parameter-highlighter
          :name="item.footnote.name"
          :show-prefix-and-postfix="false"
          />
      </template>
    </template>
    <template v-slot:item.referenced_items="{ item }">
      {{ removeDuplicates(item.referenced_items) | itemNames }}
    </template>
    <template v-slot:item.start_date="{ item }">
      {{ item.start_date | date }}
    </template>
    <template v-slot:item.actions="{ item }">
      <actions-menu
        :actions="actions"
        :item="item"
        :badge="actionsMenuBadge(item)"
        />
    </template>
  </n-n-table>
  <v-dialog v-model="showForm"
            persistent
            fullscreen
            content-class="fullscreen-dialog"
            >
    <study-footnote-form
      @close="closeForm"
      :current-study-footnotes="studyFootnotes"
      class="fullscreen-dialog"
      @added="fetchFootnotes"
      />
  </v-dialog>
  <study-footnote-edit-form
    :open="showEditForm"
    :study-footnote="selectedFootnote"
    @close="closeEditForm"
    @updated="fetchFootnotes"
    />
  <v-dialog v-model="showHistory"
            @keydown.esc="closeHistory"
            persistent
            :max-width="globalHistoryDialogMaxWidth"
            :fullscreen="globalHistoryDialogFullscreen">
    <history-table
      :title="studyFootnoteHistoryTitle"
      @close="closeHistory"
      :headers="headers"
      :items="footnoteHistoryItems"
      :html-fields="historyHtmlFields"
      />
  </v-dialog>
  <confirm-dialog ref="confirm" :text-cols="6" :action-cols="5" />
</div>
</template>

<script>
import { accessGuard } from '@/mixins/accessRoleVerifier'
import ActionsMenu from '@/components/tools/ActionsMenu'
import { bus } from '@/main'
import ConfirmDialog from '@/components/tools/ConfirmDialog'
import filteringParameters from '@/utils/filteringParameters'
import StudyFootnoteEditForm from '@/components/studies/StudyFootnoteEditForm'
import StudyFootnoteForm from '@/components/studies/StudyFootnoteForm'
import { mapGetters } from 'vuex'
import NNParameterHighlighter from '@/components/tools/NNParameterHighlighter'
import NNTable from '@/components/tools/NNTable'
import study from '@/api/study'
import HistoryTable from '@/components/tools/HistoryTable'
import dataFormating from '@/utils/dataFormating'

export default {
  mixins: [accessGuard],
  components: {
    ActionsMenu,
    ConfirmDialog,
    StudyFootnoteEditForm,
    StudyFootnoteForm,
    NNParameterHighlighter,
    NNTable,
    HistoryTable
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy',
      selectedStudyVersion: 'studiesGeneral/selectedStudyVersion',
      studyFootnotes: 'studyFootnotes/studyFootnotes',
      total: 'studyFootnotes/total'
    }),
    exportDataUrl () {
      return `studies/${this.selectedStudy.uid}/study-soa-footnotes`
    },
    studyFootnoteHistoryTitle () {
      if (this.selectedFootnote) {
        return this.$t(
          'StudyFootnoteTable.study_footnote_history_title',
          { studyFootnoteUid: this.selectedFootnote.uid })
      }
      return ''
    }
  },
  mounted () {
    this.fetchFootnotes()
    this.$store.dispatch('studyActivities/fetchStudyActivities', { studyUid: this.selectedStudy.uid })
  },
  data () {
    return {
      actions: [
        {
          label: this.$t('_global.edit'),
          icon: 'mdi-pencil-outline',
          iconColor: 'primary',
          click: this.editStudyFootnote,
          condition: () => !this.selectedStudyVersion,
          accessRole: this.$roles.STUDY_WRITE
        },
        {
          label: this.$t('_global.delete'),
          icon: 'mdi-delete-outline',
          iconColor: 'error',
          click: this.deleteStudyFootnote,
          condition: () => !this.selectedStudyVersion,
          accessRole: this.$roles.STUDY_WRITE
        },
        {
          label: this.$t('_global.history'),
          icon: 'mdi-history',
          click: this.openHistory
        }
      ],
      footnoteHistoryItems: [],
      headers: [
        { text: '', value: 'actions', width: '5%' },
        { text: this.$t('_global.order_short'), value: 'order', width: '3%' },
        { text: this.$t('StudyFootnoteTable.footnote'), value: 'name', filteringName: 'footnote.name_plain' },
        { text: this.$t('StudyFootnoteTable.covered_items'), value: 'referenced_items', filteringName: 'referenced_items.item_name' }
      ],
      historyHtmlFields: ['footnote.name'],
      options: {},
      selectedFootnote: null,
      showEditForm: false,
      showForm: false,
      showHistory: false
    }
  },
  methods: {
    removeDuplicates (arr) {
      const uniqueItems = {}
      const result = []

      for (const item of arr) {
        const key = `${item.item_name}_${item.item_type}`
        if (!uniqueItems[key]) {
          uniqueItems[key] = true
          result.push(item)
        }
      }

      return result
    },
    actionsMenuBadge (item) {
      if (!item.footnote && item.footnote_template.parameters.length > 0) {
        return {
          color: 'error',
          icon: 'mdi-exclamation'
        }
      }
      return null
    },
    closeEditForm () {
      this.showEditForm = false
      this.selectedFootnote = null
    },
    closeForm () {
      this.showForm = false
      this.selectedFootnote = null
    },
    closeHistory () {
      this.selectedFootnote = null
      this.showHistory = false
    },
    async openHistory (studyFootnote) {
      this.selectedStudyFootnote = studyFootnote
      const resp = await study.getStudyFootnoteAuditTrail(this.selectedStudy.uid, studyFootnote.uid)
      resp.data.forEach(element => {
        element.referenced_items = dataFormating.itemNames(element.referenced_items).replaceAll(' ,', '')
        element.name = element.footnote ? element.footnote.name_plain : element.footnote_template.name_plain
      })
      this.footnoteHistoryItems = resp.data
      this.showHistory = true
    },
    async fetchFootnotesHistory () {
      const resp = await study.getStudyFootnotesAuditTrail(this.selectedStudy.uid)
      resp.data.forEach(element => {
        element.referenced_items = dataFormating.itemNames(element.referenced_items).replaceAll(' ,', '')
        element.name = element.footnote ? element.footnote.name_plain : element.footnote_template.name_plain
      })
      return resp.data
    },
    fetchFootnotes (filters, sort, filtersUpdated) {
      const params = filteringParameters.prepareParameters(
        this.options, filters, sort, filtersUpdated)
      params.studyUid = this.selectedStudy.uid
      params.study_value_version = this.selectedStudyVersion
      this.$store.dispatch('studyFootnotes/fetchStudyFootnotes', params)
    },
    editStudyFootnote (studyFootnote) {
      this.selectedFootnote = studyFootnote
      this.showEditForm = true
    },
    async deleteStudyFootnote (studyFootnote) {
      const options = { type: 'warning' }
      const footnote = studyFootnote.footnote ? studyFootnote.footnote.name_plain : '(unnamed)'

      if (await this.$refs.confirm.open(this.$t('StudyFootnoteTable.confirm_delete', { footnote }), options)) {
        this.$store.dispatch('studyFootnotes/deleteStudyFootnote', {
          studyUid: this.selectedStudy.uid,
          studyFootnoteUid: studyFootnote.uid
        }).then(() => {
          this.fetchFootnotes()
          bus.$emit('notification', { msg: this.$t('StudyFootnoteTable.delete_footnote_success') })
        })
      }
    }
  },
  watch: {
    options () {
      this.fetchFootnotes()
    },
    '$route.params.editFootnote' (value) {
      this.editStudyFootnote(value)
      this.$route.params.editFootnote = null
    }
  }
}
</script>
