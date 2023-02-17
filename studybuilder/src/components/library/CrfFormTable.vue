<template>
<div>
  <n-n-table
    :headers="headers"
    :items="forms"
    item-key="uid"
    sort-by="name"
    sort-desc
    has-api
    :options.sync="options"
    :server-items-length="total"
    @filter="getForms"
    column-data-resource="concepts/odms/forms"
    export-data-url="concepts/odms/forms"
    export-object-label="CRFForms"
    >
    <template v-slot:actions="">
      <v-btn
        class="ml-2"
        fab
        dark
        small
        color="primary"
        @click.stop="openForm"
        :title="$t('CRFForms.add_form')"
        data-cy="add-crf-form"
        >
        <v-icon dark>
          mdi-plus
        </v-icon>
      </v-btn>
    </template>
    <template v-slot:item.name="{ item }">
      {{ item.name }}
    </template>
    <template v-slot:item.description="{ item }">
      <div v-html="getDescription(item)" />
    </template>
    <template v-slot:item.notes="{ item }">
      <div v-html="getNotes(item)" />
    </template>
    <template v-slot:item.repeating="{ item }">
      {{ item.repeating }}
    </template>
    <template v-slot:item.activity_groups="{ item }">
      {{ item.activity_groups | names }}
    </template>
    <template v-slot:item.status="{ item }">
      <status-chip :status="item.status" />
    </template>
    <template v-slot:item.actions="{ item }">
      <actions-menu :actions="actions" :item="item" />
    </template>
    <template v-slot:item.relations="{ item }">
      <v-btn
        fab
        dark
        small
        color="primary"
        icon
        @click="openRelationsTree(item)"
        >
        <v-icon dark>
          mdi-family-tree
        </v-icon>
      </v-btn>
    </template>
  </n-n-table>
  <v-dialog
    v-model="showForm"
    persistent
    content-class="fullscreen-dialog"
    >
    <crf-form-form
      @close="closeForm"
      @newVersion="newVersion"
      @approve="approve"
      :selectedForm="selectedForm"
      class="fullscreen-dialog"
      :readOnlyProp="selectedForm && selectedForm.status === statuses.FINAL"
      />
  </v-dialog>
  <v-dialog
    v-model="showFormHistory"
    @keydown.esc="closeFormHistory"
    persistent
    max-width="1200px"
    >
    <history-table
      :title="formHistoryTitle"
      @close="closeFormHistory"
      :headers="headers"
      :items="formHistoryItems"
      />
  </v-dialog>
  <crf-activities-models-link-form
    :open="linkForm"
    @close="closeLinkForm"
    :item-to-link="selectedForm"
    item-type="form" />
  <v-dialog v-model="showRelations"
            @keydown.esc="closeRelationsTree()"
            max-width="800px"
            persistent>
    <odm-references-tree
      :item="selectedForm"
      type="form"
      @close="closeRelationsTree()"/>
  </v-dialog>
  <confirm-dialog ref="confirm" :text-cols="6" :action-cols="5" />
</div>
</template>

<script>
import NNTable from '@/components/tools/NNTable'
import StatusChip from '@/components/tools/StatusChip'
import ActionsMenu from '@/components/tools/ActionsMenu'
import crfs from '@/api/crfs'
import CrfFormForm from '@/components/library/CrfFormForm'
import HistoryTable from '@/components/tools/HistoryTable'
import CrfActivitiesModelsLinkForm from '@/components/library/CrfActivitiesModelsLinkForm'
import statuses from '@/constants/statuses'
import filteringParameters from '@/utils/filteringParameters'
import OdmReferencesTree from '@/components/library/OdmReferencesTree.vue'
import ConfirmDialog from '@/components/tools/ConfirmDialog'
import crfTypes from '@/constants/crfTypes'
import parameters from '@/constants/parameters'
import dataFormating from '@/utils/dataFormating'
import { mapGetters } from 'vuex'
import _isEmpty from 'lodash/isEmpty'

export default {
  components: {
    NNTable,
    StatusChip,
    ActionsMenu,
    CrfFormForm,
    HistoryTable,
    CrfActivitiesModelsLinkForm,
    OdmReferencesTree,
    ConfirmDialog
  },
  props: {
    elementProp: Object
  },
  computed: {
    ...mapGetters({
      forms: 'crfs/forms',
      total: 'crfs/totalForms'
    }),
    formHistoryTitle () {
      if (this.selectedForm) {
        return this.$t(
          'CrfFormTable.form_history_title',
          { formUid: this.selectedForm.uid })
      }
      return ''
    }
  },
  data () {
    return {
      actions: [
        {
          label: this.$t('_global.approve'),
          icon: 'mdi-check-decagram',
          iconColor: 'success',
          condition: (item) => item.possible_actions.find(action => action === 'approve'),
          click: this.approve
        },
        {
          label: this.$t('_global.edit'),
          icon: 'mdi-pencil',
          iconColor: 'primary',
          condition: (item) => item.possible_actions.find(action => action === 'edit'),
          click: this.edit
        },
        {
          label: this.$t('_global.view'),
          icon: 'mdi-eye-outline',
          iconColor: 'primary',
          condition: (item) => item.status === statuses.FINAL,
          click: this.view
        },
        {
          label: this.$t('_global.new_version'),
          icon: 'mdi-plus-circle-outline',
          iconColor: 'primary',
          condition: (item) => item.possible_actions.find(action => action === 'new_version'),
          click: this.newVersion
        },
        {
          label: this.$t('_global.inactivate'),
          icon: 'mdi-close-octagon-outline',
          iconColor: 'primary',
          condition: (item) => item.possible_actions.find(action => action === 'inactivate'),
          click: this.inactivate
        },
        {
          label: this.$t('_global.reactivate'),
          icon: 'mdi-undo-variant',
          iconColor: 'primary',
          condition: (item) => item.possible_actions.find(action => action === 'reactivate'),
          click: this.reactivate
        },
        {
          label: this.$t('_global.delete'),
          icon: 'mdi-delete',
          iconColor: 'error',
          condition: (item) => item.possible_actions.find(action => action === 'delete'),
          click: this.delete
        },
        {
          label: this.$t('CrfLinikingForm.link_activity_groups'),
          icon: 'mdi-plus',
          iconColor: 'primary',
          condition: (item) => item.status === statuses.FINAL,
          click: this.openLinkForm
        },
        {
          label: this.$t('_global.history'),
          icon: 'mdi-history',
          click: this.openFormHistory
        }
      ],
      headers: [
        { text: '', value: 'actions', width: '5%' },
        { text: this.$t('CRFForms.oid'), value: 'oid' },
        { text: this.$t('_global.relations'), value: 'relations' },
        { text: this.$t('_global.name'), value: 'name' },
        { text: this.$t('_global.description'), value: 'description' },
        { text: this.$t('CRFItems.impl_notes'), value: 'notes' },
        { text: this.$t('CrfFormTable.repeating'), value: 'repeating' },
        { text: this.$t('_global.links'), value: 'activity_groups' },
        { text: this.$t('_global.version'), value: 'version' },
        { text: this.$t('_global.status'), value: 'status' }
      ],
      showForm: false,
      showHistory: false,
      selectedForm: null,
      options: {},
      filters: '',
      showFormHistory: false,
      linkForm: false,
      showRelations: false,
      formHistoryItems: []
    }
  },
  mounted () {
    this.getForms()
    if (this.elementProp.tab === 'forms' && this.elementProp.type === crfTypes.FORM && this.elementProp.uid) {
      this.edit({ uid: this.elementProp.uid })
    }
  },
  created () {
    this.statuses = statuses
  },
  methods: {
    getDescription (item) {
      const engDesc = item.descriptions.find(el => el.language === parameters.ENG)
      if (engDesc) {
        return engDesc.description
      }
      return ''
    },
    getNotes (item) {
      const engDesc = item.descriptions.find(el => el.language === parameters.ENG)
      if (engDesc) {
        return engDesc.sponsor_instruction
      }
      return ''
    },
    openRelationsTree (item) {
      this.showRelations = true
      this.selectedForm = item
    },
    closeRelationsTree () {
      this.selectedForm = null
      this.showRelations = false
    },
    async delete (item) {
      let relationships = 0
      await crfs.getFormRelationship(item.uid).then(resp => {
        if (resp.data.OdmTemplate && resp.data.OdmTemplate.length > 0) {
          relationships = resp.data.OdmTemplate.length
        }
      })
      const options = {
        type: 'warning',
        cancelLabel: this.$t('_global.cancel'),
        agreeLabel: this.$t('_global.continue')
      }
      if (relationships > 0 && await this.$refs.confirm.open(`${this.$t('CRFForms.delete_warning_1')} ${relationships} ${this.$t('CRFForms.delete_warning_2')}`, options)) {
        crfs.delete('forms', item.uid).then((resp) => {
          this.getForms()
        })
      } else if (relationships === 0) {
        crfs.delete('forms', item.uid).then((resp) => {
          this.getForms()
        })
      }
    },
    approve (item) {
      crfs.approve('forms', item.uid).then((resp) => {
        this.getForms()
        this.$emit('updateForm', { type: crfTypes.FORM, element: resp.data })
      })
    },
    inactivate (item) {
      crfs.inactivate('forms', item.uid).then((resp) => {
        this.$emit('updateForm', { type: crfTypes.FORM, element: resp.data })
        this.getForms()
      })
    },
    reactivate (item) {
      crfs.reactivate('forms', item.uid).then((resp) => {
        this.$emit('updateForm', { type: crfTypes.FORM, element: resp.data })
        this.getForms()
      })
    },
    newVersion (item) {
      crfs.newVersion('forms', item.uid).then((resp) => {
        this.$emit('updateForm', { type: crfTypes.FORM, element: resp.data })
        this.getForms()
      })
    },
    edit (item) {
      crfs.getForm(item.uid).then((resp) => {
        this.selectedForm = resp.data
        this.showForm = true
        this.$emit('clearUid')
      })
    },
    view (item) {
      crfs.getForm(item.uid).then((resp) => {
        this.selectedForm = resp.data
        this.showForm = true
      })
    },
    openForm () {
      this.selectedForm = null
      this.showForm = true
    },
    async closeForm () {
      if (!_isEmpty(this.selectedForm)) {
        await crfs.getForm(this.selectedForm.uid).then((resp) => {
          this.$emit('updateForm', { type: crfTypes.FORM, element: resp.data })
        })
      }
      this.showForm = false
      this.selectedForm = null
      this.getForms()
    },
    async openFormHistory (form) {
      this.selectedForm = form
      const resp = await crfs.getFormAuditTrail(form.uid)
      this.formHistoryItems = this.transformItems(resp.data)
      this.showFormHistory = true
    },
    closeFormHistory () {
      this.selectedForm = null
      this.showFormHistory = false
    },
    transformItems (items) {
      const result = []
      for (const item of items) {
        const newItem = { ...item }
        if (newItem.activity_groups) {
          newItem.activity_groups = dataFormating.names(newItem.activity_groups)
        } else {
          newItem.activity_groups = ''
        }
        result.push(newItem)
      }
      return result
    },
    openLinkForm (item) {
      this.selectedForm = item
      this.linkForm = true
    },
    closeLinkForm () {
      this.linkForm = false
      this.selectedForm = null
      this.getForms()
    },
    async getForms (filters, sort, filtersUpdated) {
      if (filters) {
        this.filters = filters
      }
      const params = filteringParameters.prepareParameters(
        this.options, this.filters, sort, filtersUpdated)
      await this.$store.dispatch('crfs/fetchForms', params)
    }
  },
  watch: {
    options: {
      handler () {
        this.getForms()
      },
      deep: true
    },
    elementProp (value) {
      if (value.tab === 'forms' && value.type === crfTypes.FORM && value.uid) {
        this.edit({ uid: value.uid })
      }
    }
  }
}
</script>
