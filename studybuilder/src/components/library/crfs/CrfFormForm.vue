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
                rules="required"
                >
                <v-text-field
                  :label="$t('CRFForms.name') + '*'"
                  data-cy="form-oid-name"
                  v-model="form.name"
                  :error-messages="errors"
                  dense
                  clearable
                  :readonly="readOnly"
                />
              </validation-provider>
            </v-col>
            <v-col cols="5">
              <validation-provider
                v-slot="{ errors }"
                >
                <v-text-field
                  :label="$t('CRFForms.oid')"
                  data-cy="form-oid"
                  v-model="form.oid"
                  :error-messages="errors"
                  dense
                  clearable
                  :readonly="readOnly"
                />
              </validation-provider>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="2">
              <validation-provider
                rules="required"
                >
                <v-radio-group
                  v-model="form.repeating"
                  :label="$t('CRFForms.repeating')"
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
                :disabled="readOnly"
                v-show="readOnly"/>
              <vue-editor
                v-model="engDescription.description"
                :editor-toolbar="customToolbar"
                :disabled="readOnly"
                :placeholder="$t('_global.description')"
                v-show="!readOnly"/>
            </v-col>
            <v-col cols="5">
              <div class="subtitle-2 text--disabled">{{ $t('CRFForms.impl_notes') }}</div>
              <vue-editor
                v-model="engDescription.sponsor_instruction"
                :editor-toolbar="customToolbar"
                :disabled="readOnly"
                data-cy="help-for-sponsor"
                v-show="readOnly"/>
              <vue-editor
                v-model="engDescription.sponsor_instruction"
                :editor-toolbar="customToolbar"
                :disabled="readOnly"
                :placeholder="$t('CRFForms.impl_notes')"
                v-show="!readOnly"
                data-cy="help-for-sponsor"/>
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
                data-cy="form-oid-displayed-text"
                v-model="engDescription.name"
                dense
                clearable
                :readonly="readOnly"
              />
            </v-col>
            <v-col cols="9">
              <div class="subtitle-2 text--disabled">{{ $t('CRFForms.compl_instructions') }}</div>
              <vue-editor
                v-model="engDescription.instruction"
                :editor-toolbar="customToolbar"
                :disabled="readOnly"
                v-show="readOnly"
                data-cy="form-help-for-site"/>
              <vue-editor
                v-model="engDescription.instruction"
                :editor-toolbar="customToolbar"
                :disabled="readOnly"
                :placeholder="$t('CRFForms.compl_instructions')"
                v-show="!readOnly"
                data-cy="form-help-for-site"/>
            </v-col>
          </v-row>
        </v-card>
      </validation-observer>
    </template>
    <template v-slot:step.extensions>
      <crf-extensions-management-table
        type="FormDef"
        :read-only="readOnly"
        :edit-extensions="selectedExtensions"
        @setExtensions="setExtensions"/>
    </template>
    <template v-slot:step.alias="{ step }">
      <validation-observer :ref="`observer_${step}`">
          <div class="mb-5">
            {{ $t('CRFForms.create') }}
          </div>
          <v-row>
            <v-col>
              <v-text-field
                :label="$t('CRFForms.context')"
                data-cy="form-context"
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
                :label="$t('CRFForms.name')"
                data-cy="form-alias-name"
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
            {{ $t('CRFForms.select') }}
          </div>
          <validation-provider
            v-slot="{ errors }"
            rules=""
            >
            <v-select
              v-model="form.alias_uids"
              :items="aliases"
              multiple
              :label="$t('CRFForms.aliases')"
              dense
              clearable
              :item-text="getAliasDisplay"
              item-value="uid"
              :error-messages="errors"
              :readonly="readOnly">
              <template v-slot:selection="{item, index}">
                <div v-if="index === 0" data-cy="form-aliases">
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
                  data-cy="form-change-description"
                  v-model="form.change_description"
                  :error-messages="errors"
                  clearable
                />
            </validation-provider>
          </v-col>
        </v-row>
      </validation-observer>
    </template>
    <template v-slot:actions>
      <actions-menu :actions="actions" :item="form" v-if="selectedForm"/>
    </template>
  </horizontal-stepper-form>
  <crf-activities-models-link-form
    :open="linkForm"
    @close="closeLinkForm"
    :item-to-link="selectedForm"
    item-type="form" />
  <confirm-dialog ref="confirm" :text-cols="6" :action-cols="5" />
</div>
</template>

<script>
import crfs from '@/api/crfs'
import CrfDescriptionTable from '@/components/library/crfs/CrfDescriptionTable'
import HorizontalStepperForm from '@/components/tools/HorizontalStepperForm'
import { bus } from '@/main'
import constants from '@/constants/libraries'
import { mapGetters } from 'vuex'
import { VueEditor } from 'vue2-editor'
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
    selectedForm: Object,
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
      if (this.isEdit()) {
        if (this.readOnly) {
          return this.$t('CRFForms.crf_form') + ' - ' + this.form.name
        }
        return this.$t('CRFForms.edit_form') + ' - ' + this.form.name
      }
      return this.$t('CRFForms.add_form')
    },
    formUrl () {
      if (this.isEdit()) {
        return `${window.location.href.replace('crf-tree', 'forms')}/form/${this.selectedForm.uid}`
      }
      return null
    }
  },
  data () {
    return {
      search: '',
      helpItems: [
        'CRFForms.name',
        'CRFForms.oid',
        'CRFForms.repeating',
        'CRFForms.description',
        'CRFForms.impl_notes',
        'CRFForms.displayed_text',
        'CRFForms.compl_instructions',
        'CRFForms.vendor_extensions',
        'CRFForms.aliases',
        'CRFForms.context'
      ],
      form: {
        oid: 'F.',
        repeating: 'No',
        alias_uids: []
      },
      aliases: [],
      alias: {},
      descriptionUids: [],
      createSteps: [
        { name: 'form', title: this.$t('CRFForms.form_details') },
        { name: 'extensions', title: this.$t('CRFForms.vendor_extensions'), belowDisplay: true },
        { name: 'description', title: this.$t('CRFForms.description_details'), belowDisplay: true },
        { name: 'alias', title: this.$t('CRFForms.alias_details') }
      ],
      editSteps: [
        { name: 'form', title: this.$t('CRFForms.form_details') },
        { name: 'extensions', title: this.$t('CRFForms.vendor_extensions'), belowDisplay: true },
        { name: 'description', title: this.$t('CRFForms.description_details'), belowDisplay: true },
        { name: 'alias', title: this.$t('CRFForms.alias_details') },
        { name: 'change_description', title: this.$t('CRFForms.change_desc') }
      ],
      desc: [],
      steps: [],
      customToolbar: [
        ['bold', 'italic', 'underline'],
        [{ script: 'sub' }, { script: 'super' }],
        [{ list: 'ordered' }, { list: 'bullet' }]
      ],
      engDescription: { library_name: 'Sponsor', language: parameters.ENG },
      readOnly: this.readOnlyProp,
      linkForm: false,
      selectedExtensions: [],
      actions: [
        {
          label: this.$t('_global.approve'),
          icon: 'mdi-check-decagram',
          iconColor: 'success',
          condition: (item) => !this.readOnly,
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.approve
        },
        {
          label: this.$t('_global.new_version'),
          icon: 'mdi-plus-circle-outline',
          iconColor: 'primary',
          condition: (item) => this.readOnly,
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.newVersion
        },
        {
          label: this.$t('_global.delete'),
          icon: 'mdi-delete-outline',
          iconColor: 'error',
          condition: (item) => item.possible_actions ? item.possible_actions.find(action => action === actions.DELETE) : false,
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.delete
        },
        {
          label: this.$t('CrfLinikingForm.link_activities'),
          icon: 'mdi-plus',
          iconColor: 'primary',
          condition: (item) => this.readOnly,
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.openLinkForm
        }
      ]
    }
  },
  async mounted () {
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
  methods: {
    getForm () {
      crfs.getForm(this.selectedForm.uid).then((resp) => {
        this.initForm(resp.data)
      })
    },
    openLinkForm () {
      this.linkForm = true
    },
    closeLinkForm () {
      this.linkForm = false
      this.getForm()
    },
    async newVersion () {
      let relationships = 0
      await crfs.getRelationships(this.selectedForm.uid, 'forms').then(resp => {
        if (resp.data.OdmTemplate && resp.data.OdmTemplate.length > 0) {
          relationships = resp.data.OdmTemplate.length
        }
      })
      const options = {
        type: 'warning',
        cancelLabel: this.$t('_global.cancel'),
        agreeLabel: this.$t('_global.continue')
      }
      if (relationships > 1 && await this.$refs.confirm.open(`${this.$t('CRFForms.new_version_warning')}`, options)) {
        crfs.newVersion('forms', this.selectedForm.uid).then((resp) => {
          this.$emit('updateForm', { type: crfTypes.FORM, element: resp.data })
          this.$emit('newVersion', this.selectedForm)
          this.readOnly = false
          this.getForm()
        })
      } else if (relationships <= 1) {
        crfs.newVersion('forms', this.selectedForm.uid).then((resp) => {
          this.$emit('updateForm', { type: crfTypes.FORM, element: resp.data })
          this.$emit('newVersion', this.selectedForm)
          this.readOnly = false
          this.getForm()
        })
      }
    },
    async approve () {
      this.$emit('approve', this.selectedForm)
      this.readOnly = true
      this.getForm()
    },
    async delete () {
      let relationships = 0
      await crfs.getRelationships(this.selectedForm.uid, 'forms').then(resp => {
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
        crfs.delete('forms', this.selectedForm.uid).then((resp) => {
          this.$emit('close')
        })
      } else if (relationships === 0) {
        crfs.delete('forms', this.selectedForm.uid).then((resp) => {
          this.$emit('close')
        })
      }
    },
    setDesc (desc) {
      this.desc = desc
    },
    getObserver (step) {
      return this.$refs[`observer_${step}`]
    },
    close () {
      this.form = {
        oid: 'F.',
        repeating: 'No',
        alias_uids: []
      }
      this.engDescription = { library_name: 'Sponsor', language: parameters.ENG }
      this.desc = []
      this.selectedExtensions = []
      this.$refs.stepper.reset()
      this.$emit('close')
    },
    async submit () {
      await this.createOrUpdateDescription()
      this.form.library_name = constants.LIBRARY_SPONSOR
      if (this.form.oid === 'F.') {
        this.$set(this.form, 'oid', '')
      }
      try {
        if (this.isEdit()) {
          this.form.alias_uids = this.form.alias_uids.map(alias => alias.uid ? alias.uid : alias)
          await crfs.updateForm(this.form, this.selectedForm.uid).then(async resp => {
            await this.linkExtensions(this.selectedForm.uid)
            bus.$emit('notification', { msg: this.$t('CRFForms.form_updated') })
            this.close()
          })
        } else {
          await crfs.createForm(this.form).then(async resp => {
            await this.linkExtensions(resp.data.uid)
            bus.$emit('notification', { msg: this.$t('CRFForms.form_created') })
            this.$emit('linkForm', resp)
            this.close()
          })
        }
      } finally {
        this.$refs.stepper.loading = false
      }
    },
    async createAlias () {
      this.alias.library_name = constants.LIBRARY_SPONSOR
      await crfs.createAlias(this.alias).then(resp => {
        this.form.alias_uids.push(resp.data.uid)
        crfs.getAliases().then(resp => {
          this.aliases = resp.data.items
          this.alias = {}
          bus.$emit('notification', { msg: this.$t('CRFForms.alias_created') })
        })
      })
    },
    async createOrUpdateDescription () {
      const descArray = []
      this.desc.forEach(e => {
        if (e.uid) {
          descArray.push(e)
        } else {
          e.library_name = constants.LIBRARY_SPONSOR
          descArray.push(e)
        }
      })
      if (!this.engDescription.name) {
        this.engDescription.name = this.form.name
      }
      descArray.push(this.engDescription)
      this.form.descriptions = descArray
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
      await crfs.setExtensions('forms', uid, data)
    },
    async initForm (item) {
      this.form = item
      this.form.alias_uids = item.aliases
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
      if (this.selectedForm) {
        return Object.keys(this.selectedForm).length !== 0
      }
      return false
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
      },
      immediate: true
    },
    selectedForm: {
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
