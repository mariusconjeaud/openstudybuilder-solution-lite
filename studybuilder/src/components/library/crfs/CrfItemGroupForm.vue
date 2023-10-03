<template>
<div>
  <horizontal-stepper-form
    ref="stepper"
    :title="title"
    :help-items="helpItems"
    :steps="steps"
    @close="close"
    @save="submit"
    :form-observer-getter="getObserver"
    :form-url="formUrl"
    :editable="isEdit()"
    :save-from-any-step="isEdit()"
    >
    <template v-slot:step.form="{ step }">
      <validation-observer :ref="`observer_${step}`">
        <v-card
          elevation="4"
          class="mx-auto pa-4">
          <div class="text-h5 mb-4">{{ $t('CRFForms.definition') }}</div>
          <v-row>
            <v-col cols="7">
              <validation-provider
                v-slot="{ errors }"
                rules="required">
                <v-text-field
                  :label="$t('CRFItemGroups.name') + '*'"
                  data-cy="item-group-name"
                  v-model="form.name"
                  :error-messages="errors"
                  dense
                  clearable
                  :readonly="readOnly"
                />
              </validation-provider>
            </v-col>
            <v-col cols="5">
              <v-text-field
                :label="$t('CRFItemGroups.oid')"
                data-cy="item-group-oid"
                v-model="form.oid"
                dense
                clearable
                :readonly="readOnly"
              />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="2">
              <validation-provider
                rules="required">
                <v-radio-group
                  class="mt-2"
                  v-model="form.repeating"
                  :label="$t('CRFItemGroups.repeating')"
                  :readonly="readOnly"
                >
                  <v-radio :label="$t('_global.yes')" value="Yes" />
                  <v-radio :label="$t('_global.no')" value="No" />
                </v-radio-group>
              </validation-provider>
            </v-col>
            <v-col cols="5">
              <div class="subtitle-2 text--disabled">{{ $t('_global.description') }}</div>
              <vue-editor
                v-model="engDescription.description"
                :editor-toolbar="customToolbar"
                v-show="readOnly"
                :disabled="readOnly"/>
              <vue-editor
                v-model="engDescription.description"
                :editor-toolbar="customToolbar"
                :placeholder="$t('_global.description')"
                v-show="!readOnly"
                :disabled="readOnly"/>
            </v-col>
            <v-col cols="5">
              <div class="subtitle-2 text--disabled">{{ $t('CRFItemGroups.impl_notes') }}</div>
              <vue-editor
                v-model="engDescription.sponsor_instruction"
                :editor-toolbar="customToolbar"
                data-cy="crf-item-group-help-for-sponsor"
                v-show="readOnly"
                :disabled="readOnly"/>
              <vue-editor
                v-model="engDescription.sponsor_instruction"
                :editor-toolbar="customToolbar"
                :placeholder="$t('CRFItemGroups.impl_notes')"
                data-cy="crf-item-group-help-for-sponsor"
                v-show="!readOnly"
                :disabled="readOnly"/>
            </v-col>
          </v-row>
        </v-card>
        <v-card
          elevation="4"
          class="mx-auto mt-3 pa-4">
          <div class="text-h5 mb-4">{{ $t('CRFForms.display') }}</div>
          <v-row>
            <v-col cols="3">
              <v-text-field
                :label="$t('CRFForms.displayed_text')"
                data-cy="crf-item-group-displayed-text"
                v-model="engDescription.name"
                dense
                clearable
                :readonly="readOnly"
              />
            </v-col>
            <v-col cols="9">
              <div class="subtitle-2 text--disabled">{{ $t('CRFItemGroups.compl_instructions') }}</div>
              <vue-editor
                v-model="engDescription.instruction"
                :editor-toolbar="customToolbar"
                data-cy="crf-item-group-help-for-site"
                v-show="readOnly"
                :disabled="readOnly"/>
              <vue-editor
                v-model="engDescription.instruction"
                :editor-toolbar="customToolbar"
                :placeholder="$t('CRFItemGroups.compl_instructions')"
                data-cy="crf-item-group-help-for-site"
                v-show="!readOnly"
                :disabled="readOnly"/>
            </v-col>
          </v-row>
        </v-card>
        <v-card
          elevation="4"
          class="mx-auto mt-3 pa-4">
          <div class="text-h5 mb-4">{{ $t('CRFForms.annotations') }}</div>
          <v-row>
            <v-col cols="6">
              <v-select
                v-model="form.sdtm_domain_uids"
                :label="$t('CRFItemGroups.domain')"
                data-cy="item-group-domain"
                :items="domains"
                :item-text="getDomainDisplay"
                item-value="term_uid"
                dense
                clearable
                multiple
                :readonly="readOnly">
                <template v-slot:selection="{index}">
                  <div v-if="index === 0">
                    <span>{{ getFirstDomainDisplay() }}</span>
                  </div>
                  <span
                    v-if="index === 1"
                    class="grey--text text-caption mr-1"
                  >
                    (+{{ form.sdtm_domain_uids.length - 1 }})
                  </span>
                </template>
              </v-select>
            </v-col>
            <v-col cols="6">
              <v-text-field
                :label="$t('CRFItemGroups.sas_dataset')"
                data-cy="item-group-sas-dataset-name"
                v-model="form.sasDatasetName"
                dense
                clearable
                :readonly="readOnly"
              />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="2">
              <v-radio-group
                class="mt-2"
                v-model="form.isReferenceData"
                :label="$t('CRFItemGroups.is_referential')"
                :readonly="readOnly"
              >
                <v-radio :label="$t('_global.yes')" value="Yes" />
                <v-radio :label="$t('_global.no')" value="No" />
              </v-radio-group>
            </v-col>
            <v-col cols="4">
              <v-select
                v-model="form.origin"
                :label="$t('CRFItemGroups.origin')"
                data-cy="item-group-origin"
                :items="origins"
                item-text="nci_preferred_name"
                item-value="nci_preferred_name"
                dense
                clearable
                :readonly="readOnly"/>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="6">
              <v-text-field
                :label="$t('CRFItemGroups.purpose')"
                data-cy="item-group-purpose"
                v-model="form.purpose"
                dense
                clearable
                :readonly="readOnly"
              />
            </v-col>
            <v-col cols="6">
              <v-text-field
                :label="$t('CRFItemGroups.comment')"
                data-cy="item-group-comment"
                v-model="form.comment"
                dense
                clearable
                :readonly="readOnly"
              />
            </v-col>
          </v-row>
        </v-card>
      </validation-observer>
    </template>
    <template v-slot:step.extensions>
      <crf-extensions-management-table
        type="ItemGroupDef"
        :read-only="readOnly"
        :edit-extensions="selectedExtensions"
        @setExtensions="setExtensions"/>
    </template>
    <template v-slot:step.alias="{ step }">
      <validation-observer :ref="`observer_${step}`">
          <div class="mb-5">
            {{ $t('CRFItemGroups.create') }}
          </div>
          <v-row>
            <v-col>
              <v-text-field
                :label="$t('CRFItemGroups.context')"
                data-cy="item-group-alias-context"
                v-model="alias.context"
                dense
                clearable
                :readonly="readOnly"
              />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="10">
              <v-text-field
                :label="$t('CRFItemGroups.name')"
                data-cy="item-group-alias-name"
                v-model="alias.name"
                dense
                clearable
                :readonly="readOnly"
              />
            </v-col>
            <v-col>
              <v-btn
                data-cy="save-button"
                color="secondary"
                @click="createAlias"
                class="mr-2"
                :disabled="readOnly"
                >
                {{ $t('_global.save') }}
              </v-btn>
            </v-col>
          </v-row>
          <div class="mb-5">
            {{ $t('CRFItemGroups.select') }}
          </div>
          <validation-provider
            v-slot="{ errors }"
            rules=""
            >
            <v-select
              v-model="form.alias_uids"
              :items="aliases"
              multiple
              :label="$t('CRFItemGroups.aliases')"
              dense
              clearable
              :item-text="getAliasDisplay"
              item-value="uid"
              :error-messages="errors"
              :readonly="readOnly">
              <template v-slot:selection="{item, index}">
                <div v-if="index === 0" data-cy="item-group-selected-alias">
                  <span>{{ item.name }}</span>
                </div>
                <span
                  v-if="index === 1"
                  class="grey--text text-caption"
                >
                  (+{{ form.alias_uids.length -1 }})
                </span>
              </template>
            </v-select>
          </validation-provider>
      </validation-observer>
    </template>
    <template v-slot:step.description="{ step }">
      <validation-observer :ref="`observer_${step}`">
        <crf-description-table
          @setDesc="setDesc"
          :editDescriptions="desc"
          :readOnly="readOnly"/>
      </validation-observer>
    </template>
    <template v-slot:step.change_description="{ step }">
      <validation-observer :ref="`observer_${step}`">
        <v-row>
          <v-col>
            <validation-provider
              v-slot="{ errors }"
              rules="required"
              >
                <v-text-field
                  :label="$t('CRFForms.change_desc')"
                  data-cy="item-group-change-description"
                  v-model="form.change_description"
                  :error-messages="errors"
                  clearable
                  :readonly="readOnly"
                />
            </validation-provider>
          </v-col>
        </v-row>
      </validation-observer>
    </template>
    <template v-slot:actions>
      <actions-menu :actions="actions" :item="form" v-if="selectedGroup"/>
    </template>
  </horizontal-stepper-form>
  <crf-activities-models-link-form
    :open="linkForm"
    @close="closeLinkForm"
    :item-to-link="selectedGroup"
    item-type="itemGroup" />
  <confirm-dialog ref="confirm" :text-cols="6" :action-cols="5" />
</div>
</template>

<script>
import crfs from '@/api/crfs'
import terms from '@/api/controlledTerminology/terms'
import HorizontalStepperForm from '@/components/tools/HorizontalStepperForm'
import { bus } from '@/main'
import libraries from '@/constants/libraries'
import CrfDescriptionTable from '@/components/library/crfs/CrfDescriptionTable'
import { VueEditor } from 'vue2-editor'
import { mapGetters } from 'vuex'
import ActionsMenu from '@/components/tools/ActionsMenu'
import CrfActivitiesModelsLinkForm from '@/components/library/crfs/CrfActivitiesModelsLinkForm'
import actions from '@/constants/actions'
import parameters from '@/constants/parameters'
import CrfExtensionsManagementTable from '@/components/library/crfs/CrfExtensionsManagementTable'
import ConfirmDialog from '@/components/tools/ConfirmDialog'
import crfTypes from '@/constants/crfTypes'

export default {
  components: {
    HorizontalStepperForm,
    CrfDescriptionTable,
    VueEditor,
    ActionsMenu,
    CrfActivitiesModelsLinkForm,
    CrfExtensionsManagementTable,
    ConfirmDialog
  },
  props: {
    selectedGroup: Object,
    readOnlyProp: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    ...mapGetters({
      userData: 'app/userData'
    }),
    title () {
      return (this.isEdit())
        ? (this.readOnly ? this.$t('CRFItemGroups.item_group') + ' - ' + this.form.name : this.$t('CRFItemGroups.edit_group') + ' - ' + this.form.name)
        : this.$t('CRFItemGroups.add_group')
    },
    formUrl () {
      if (this.isEdit()) {
        return `${window.location.href.replace('crf-tree', 'item-groups')}/item-group/${this.selectedGroup.uid}`
      }
      return null
    }
  },
  data () {
    return {
      helpItems: [
        'CRFItemGroups.name',
        'CRFItemGroups.oid',
        'CRFItemGroups.repeating',
        'CRFItemGroups.description',
        'CRFItemGroups.impl_notes',
        'CRFItemGroups.displayed_text',
        'CRFItemGroups.compl_instructions',
        'CRFItemGroups.aliases',
        'CRFItemGroups.context'
      ],
      form: {
        oid: 'G.',
        repeating: 'No',
        isReferenceData: 'no',
        alias_uids: [],
        sdtm_domain_uids: []
      },
      desc: [],
      aliases: [],
      alias: {},
      steps: [],
      selectedExtensions: [],
      createSteps: [
        { name: 'form', title: this.$t('CRFItemGroups.group_details') },
        { name: 'extensions', title: this.$t('CRFForms.vendor_extensions'), belowDisplay: true },
        { name: 'description', title: this.$t('CRFItemGroups.description_details'), belowDisplay: true },
        { name: 'alias', title: this.$t('CRFItemGroups.alias_details') }
      ],
      editSteps: [
        { name: 'form', title: this.$t('CRFItemGroups.group_details') },
        { name: 'extensions', title: this.$t('CRFForms.vendor_extensions'), belowDisplay: true },
        { name: 'description', title: this.$t('CRFItemGroups.description_details'), belowDisplay: true },
        { name: 'alias', title: this.$t('CRFItemGroups.alias_details') },
        { name: 'change_description', title: this.$t('CRFForms.change_desc') }
      ],
      origins: [],
      domains: [],
      engDescription: { library_name: 'Sponsor', language: parameters.ENG },
      customToolbar: [
        ['bold', 'italic', 'underline'],
        [{ script: 'sub' }, { script: 'super' }],
        [{ list: 'ordered' }, { list: 'bullet' }]
      ],
      readOnly: this.readOnlyProp,
      linkForm: false,
      actions: [
        {
          label: this.$t('_global.approve'),
          icon: 'mdi-check-decagram',
          iconColor: 'success',
          condition: (item) => !this.readOnly,
          click: this.approve
        },
        {
          label: this.$t('_global.new_version'),
          icon: 'mdi-plus-circle-outline',
          iconColor: 'primary',
          condition: (item) => this.readOnly,
          click: this.newVersion
        },
        {
          label: this.$t('_global.delete'),
          icon: 'mdi-delete-outline',
          iconColor: 'error',
          condition: (item) => item.possible_actions ? item.possible_actions.find(action => action === actions.DELETE) : false,
          click: this.delete
        },
        {
          label: this.$t('CrfLinikingForm.link_activity_sub_groups'),
          icon: 'mdi-plus',
          iconColor: 'primary',
          condition: (item) => this.readOnly,
          click: this.openLinkForm
        }
      ]
    }
  },
  methods: {
    getGroup () {
      crfs.getItemGroup(this.selectedGroup.uid).then((resp) => {
        this.initForm(resp.data)
      })
    },
    openLinkForm () {
      this.linkForm = true
    },
    closeLinkForm () {
      this.linkForm = false
      this.getGroup()
    },
    async newVersion () {
      let relationships = 0
      await crfs.getRelationships(this.selectedGroup.uid, 'item-groups').then(resp => {
        if (resp.data.OdmForm && resp.data.OdmForm.length > 0) {
          relationships = resp.data.OdmForm.length
        }
      })
      const options = {
        type: 'warning',
        cancelLabel: this.$t('_global.cancel'),
        agreeLabel: this.$t('_global.continue')
      }
      if (relationships > 1 && await this.$refs.confirm.open(`${this.$t('CRFForms.new_version_warning')}`, options)) {
        crfs.newVersion('item-groups', this.selectedGroup.uid).then((resp) => {
          this.$emit('updateItemGroup', { type: crfTypes.GROUP, element: resp.data })
          this.$emit('newVersion', this.selectedGroup)
          this.readOnly = false
          this.getGroup()
        })
      } else if (relationships <= 1) {
        crfs.newVersion('item-groups', this.selectedGroup.uid).then((resp) => {
          this.$emit('updateItemGroup', { type: crfTypes.GROUP, element: resp.data })
          this.$emit('newVersion', this.selectedGroup)
          this.readOnly = false
          this.getGroup()
        })
      }
    },
    approve () {
      this.$emit('approve', this.selectedGroup)
      this.readOnly = true
      this.getGroup()
    },
    async delete () {
      let relationships = 0
      await crfs.getRelationships(this.selectedGroup.uid, 'item-groups').then(resp => {
        if (resp.data.OdmForm && resp.data.OdmForm.length > 0) {
          relationships = resp.data.OdmForm.length
        }
      })
      const options = {
        type: 'warning',
        cancelLabel: this.$t('_global.cancel'),
        agreeLabel: this.$t('_global.continue')
      }
      if (relationships > 0 && await this.$refs.confirm.open(`${this.$t('CRFItemGroups.delete_warning_1')} ${relationships} ${this.$t('CRFItemGroups.delete_warning_2')}`, options)) {
        crfs.delete('item-groups', this.selectedGroup.uid).then((resp) => {
          this.$emit('close')
        })
      } else if (relationships === 0) {
        crfs.delete('item-groups', this.selectedGroup.uid).then((resp) => {
          this.$emit('close')
        })
      }
    },
    setDesc (desc) {
      this.desc = desc
    },
    getDomainDisplay (item) {
      return `${item.nci_preferred_name} (${item.code_submission_value})`
    },
    getFirstDomainDisplay () {
      return this.domains.find(el => el.term_uid === this.form.sdtm_domain_uids[0]).nci_preferred_name
    },
    getObserver (step) {
      return this.$refs[`observer_${step}`]
    },
    close () {
      this.form = {
        oid: 'G.',
        repeating: 'No',
        isReferenceData: 'no',
        alias_uids: [],
        sdtm_domain_uids: []
      }
      this.desc = []
      this.selectedExtensions = []
      this.engDescription = { library_name: 'Sponsor', language: parameters.ENG }
      this.$refs.stepper.reset()
      this.$emit('close')
    },
    async submit () {
      await this.createOrUpdateDescription()
      this.form.library_name = libraries.LIBRARY_SPONSOR
      if (this.form.oid === 'G.') {
        this.$set(this.form, 'oid', '')
      }
      try {
        if (this.isEdit()) {
          this.form.alias_uids = this.form.alias_uids.map(alias => alias.uid ? alias.uid : alias)
          await crfs.updateItemGroup(this.form, this.selectedGroup.uid).then(async resp => {
            await this.linkExtensions(this.selectedGroup.uid)
            bus.$emit('notification', { msg: this.$t('CRFItemGroups.group_updated') })
            this.close()
          })
        } else {
          await crfs.createItemGroup(this.form).then(async resp => {
            await this.linkExtensions(resp.data.uid)
            bus.$emit('notification', { msg: this.$t('CRFItemGroups.group_created') })
            this.$emit('linkGroup', resp)
            this.close()
          })
        }
      } finally {
        this.$refs.stepper.loading = false
      }
    },
    setExtensions (extensions) {
      this.selectedExtensions = extensions
    },
    async linkExtensions (uid) {
      const elements = this.selectedExtensions.filter(el => el.type === 'Element')
      const elementAttributes = this.selectedExtensions.filter(el => el.vendor_element)
      const namespaceAttributes = this.selectedExtensions.filter(el => el.type === 'Attribute' && el.vendor_namespace && !el.vendor_element)
      const data = {
        elements: elements,
        element_attributes: elementAttributes,
        attributes: namespaceAttributes
      }
      await crfs.setExtensions('item-groups', uid, data)
    },
    async createAlias () {
      this.alias.library_name = libraries.LIBRARY_SPONSOR
      await crfs.createAlias(this.alias).then(resp => {
        this.form.alias_uids.push(resp.data.uid)
        crfs.getAliases().then(resp => {
          this.aliases = resp.data.items
          this.alias = {}
          bus.$emit('notification', { msg: this.$t('CRFItemGroups.alias_created') })
        })
      })
    },
    async createOrUpdateDescription () {
      const descArray = []
      this.desc.forEach(e => {
        if (e.uid) {
          descArray.push(e)
        } else {
          e.library_name = libraries.LIBRARY_SPONSOR
          descArray.push(e)
        }
      })
      if (!this.engDescription.name) {
        this.engDescription.name = this.form.name
      }
      descArray.push(this.engDescription)
      this.form.descriptions = descArray
    },
    async initForm (item) {
      this.form = item
      this.form.alias_uids = item.aliases
      this.form.sdtm_domain_uids = item.sdtm_domains.map(el => el.uid)
      this.form.change_description = this.$t('_global.draft_change')
      if (item.descriptions.find(el => el.language === parameters.ENG)) {
        this.engDescription = item.descriptions.find(el => el.language === parameters.ENG)
      }
      this.desc = item.descriptions.filter((el) => el.language !== parameters.ENG)
      const params = {}
      if (item.vendor_attributes.length > 0 || item.vendor_element_attributes.length > 0) {
        params.filters = { uid: { v: [...item.vendor_attributes.map(attr => attr.uid), ...item.vendor_element_attributes.map(attr => attr.uid)], op: 'co' } }
        await crfs.getAllAttributes(params).then(resp => {
          resp.data.items.forEach(el => {
            el.type = 'Attribute'
            el.value = [...item.vendor_attributes, ...item.vendor_element_attributes].find(attr => attr.uid === el.uid).value
          })
          this.selectedExtensions = resp.data.items
        })
      }
      if (item.vendor_elements.length > 0) {
        params.filters = { uid: { v: item.vendor_elements.map(attr => attr.uid), op: 'co' } }
        await crfs.getAllElements(params).then(resp => {
          resp.data.items.forEach(el => {
            el.type = 'Element'
            el.value = item.vendor_elements.find(attr => attr.uid === el.uid).value
          })
          this.selectedExtensions = [...resp.data.items, ...this.selectedExtensions]
        })
      }
    },
    getAliasDisplay (item) {
      return `${item.context} - ${item.name}`
    },
    isEdit () {
      if (this.selectedGroup) {
        return Object.keys(this.selectedGroup).length !== 0
      }
      return false
    }
  },
  mounted () {
    terms.getAttributesByCodelist('originType').then(resp => {
      this.origins = resp.data.items
    })
    terms.getAttributesByCodelist('sdtmDomainAbbreviation').then(resp => {
      this.domains = resp.data.items.sort(function (a, b) {
        return a.nci_preferred_name.localeCompare(b.nci_preferred_name)
      })
    })
    crfs.getAliases().then(resp => {
      this.aliases = resp.data.items
    })
    if (this.isEdit()) {
      this.steps = this.readOnly ? this.createSteps : this.editSteps
    } else {
      this.steps = this.createSteps
    }
    if (!this.userData.multilingual) {
      this.steps = this.steps.filter(function (obj) {
        return obj.name !== 'description'
      })
    }
  },
  watch: {
    readOnlyProp (value) {
      this.readOnly = value
    },
    userData: {
      handler () {
        if (!this.userData.multilingual) {
          this.steps = this.steps.filter(function (obj) {
            return obj.name !== 'description'
          })
        } else {
          this.steps = this.createSteps
        }
      }
    },
    selectedGroup: {
      handler (value) {
        if (this.isEdit()) {
          this.steps = this.readOnly ? this.createSteps : this.editSteps
          this.initForm(value)
        } else {
          this.steps = this.createSteps
        }
        if (!this.userData.multilingual) {
          this.steps = this.steps.filter(function (obj) {
            return obj.name !== 'description'
          })
        }
      },
      immediate: true
    }
  }
}
</script>
