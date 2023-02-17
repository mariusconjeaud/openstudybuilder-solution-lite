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
    <template v-slot:step.extensions="{ step }">
      <validation-observer :ref="`observer_${step}`">
        <v-data-table
          :headers="selectedExtensionsHeaders"
          :items="selectedExtensions"
          >
          <template v-slot:item.parent="{ item }">
            {{ item.vendor_namespace ? item.vendor_namespace.name : (item.vendor_element ? item.vendor_element.name : '') }}
          </template>
          <template v-slot:item.value="{ index }">
            <v-text-field
              v-model="selectedExtensions[index].value"
              :label="$t('_global.value')"
              dense
              class="mt-3"
              :readonly="readOnly">
            </v-text-field>
          </template>
          <template v-slot:item.delete="{ item }">
            <v-btn
              icon
              class="mt-1"
              :disabled="readOnly"
              @click="removeExtension(item)">
              <v-icon dark>
                mdi-trash-can
              </v-icon>
            </v-btn>
          </template>
        </v-data-table>
      </validation-observer>
    </template>
    <template v-slot:step.extensions.after>
      <v-row>
        <v-col cols="12">
          <v-text-field
            v-model="search"
            dense
            append-icon="mdi-magnify"
            :label="$t('_global.search')"
            single-line
            @input="fullTextSearch(search)"/>
        </v-col>
        <v-col cols="6" class="pt-0 mt-0">
          <v-card
            elevation="4"
            class="mx-auto pa-4">
            <div class="text-h5 mb-4">{{ $t('CrfExtensions.elements') }}</div>
          <n-n-table
            :headers="elementsHeaders"
            item-key="uid"
            :items="elements"
            hide-export-button
            only-text-search
            hide-default-switches
            additional-margin
            disable-filtering>
            <template v-slot:item.parent="{ item }">
              {{ item.vendor_namespace.name }}
            </template>
            <template v-slot:item.add="{ item }">
              <v-btn
                icon
                class="mt-1"
                :disabled="readOnly"
                @click="addExtension(item)">
                <v-icon dark>
                  mdi-plus
                </v-icon>
              </v-btn>
            </template>
          </n-n-table></v-card>
        </v-col>
        <v-col cols="6" class="pt-0 mt-0">
          <v-card
            elevation="4"
            class="mx-auto pa-4">
            <div class="text-h5 mb-4">{{ $t('CrfExtensions.attributes') }}</div>
          <n-n-table
            :headers="attributesHeaders"
            item-key="uid"
            :items="attributes"
            hide-export-button
            only-text-search
            hide-default-switches
            additional-margin
            disable-filtering>
            <template v-slot:item.parent="{ item }">
              {{ item.vendor_namespace ?  item.vendor_namespace.name : item.vendor_element.name }}
            </template>
            <template v-slot:item.add="{ item }">
              <v-btn
                icon
                class="mt-1"
                :disabled="readOnly"
                @click="addExtension(item)">
                <v-icon dark>
                  mdi-plus
                </v-icon>
              </v-btn>
            </template>
          </n-n-table>
          </v-card>
        </v-col>
      </v-row>
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
</div>
</template>

<script>
import crfs from '@/api/crfs'
import CrfDescriptionTable from '@/components/tools/CrfDescriptionTable'
import HorizontalStepperForm from '@/components/tools/HorizontalStepperForm'
import { bus } from '@/main'
import constants from '@/constants/libraries'
import { mapGetters } from 'vuex'
import { VueEditor } from 'vue2-editor'
import ActionsMenu from '@/components/tools/ActionsMenu'
import CrfActivitiesModelsLinkForm from '@/components/library/CrfActivitiesModelsLinkForm'
import actions from '@/constants/actions'
import parameters from '@/constants/parameters'
import NNTable from '@/components/tools/NNTable'

export default {
  components: {
    HorizontalStepperForm,
    CrfDescriptionTable,
    VueEditor,
    ActionsMenu,
    CrfActivitiesModelsLinkForm,
    NNTable
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
        { name: 'description', title: this.$t('CRFForms.description_details'), belowDisplay: true },
        { name: 'extensions', title: this.$t('CRFForms.vendor_extensions'), belowDisplay: true },
        { name: 'alias', title: this.$t('CRFForms.alias_details') }
      ],
      editSteps: [
        { name: 'form', title: this.$t('CRFForms.form_details') },
        { name: 'description', title: this.$t('CRFForms.description_details'), belowDisplay: true },
        { name: 'extensions', title: this.$t('CRFForms.vendor_extensions'), belowDisplay: true },
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
      attributes: [],
      elements: [],
      selectedExtensions: [],
      attributesHeaders: [
        { text: this.$t('CrfExtensions.parent'), value: 'parent' },
        { text: this.$t('_global.name'), value: 'name' },
        { text: this.$t('CrfExtensions.data_type'), value: 'data_type' },
        { text: '', value: 'add' }
      ],
      elementsHeaders: [
        { text: this.$t('CrfExtensions.namespace'), value: 'vendor_namespace.name' },
        { text: this.$t('CrfExtensions.parent'), value: 'parent' },
        { text: this.$t('_global.name'), value: 'name' },
        { text: '', value: 'add' }
      ],
      selectedExtensionsHeaders: [
        { text: this.$t('CrfExtensions.namespace'), value: 'vendor_namespace.name' },
        { text: this.$t('CrfExtensions.parent'), value: 'parent' },
        { text: this.$t('_global.name'), value: 'name' },
        { text: this.$t('_global.type'), value: 'type' },
        { text: this.$t('CrfExtensions.data_type'), value: 'data_type' },
        { text: this.$t('_global.value'), value: 'value' },
        { text: '', value: 'delete' }
      ],
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
          icon: 'mdi-delete',
          iconColor: 'error',
          condition: (item) => item.possible_actions ? item.possible_actions.find(action => action === actions.DELETE) : false,
          click: this.delete
        },
        {
          label: this.$t('CrfLinikingForm.link_activities'),
          icon: 'mdi-plus',
          iconColor: 'primary',
          condition: (item) => this.readOnly,
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
      this.initForm(this.selectedForm)
    } else {
      this.steps = this.createSteps
      await this.getExtensionData()
    }
    if (!this.userData.multilingual) {
      this.steps = this.steps.filter(function (obj) {
        return obj.name !== 'description'
      })
    }
  },
  methods: {
    fullTextSearch (search) {
      const filter = `{"*": {"v": ["${search}"]}}`
      const data = {}
      data.filters = filter
      crfs.getAllAttributes(data).then(resp => {
        this.attributes = resp.data.items
        this.selectedExtensions.forEach(ex => {
          const attr = this.attributes.find(attr => attr.uid === ex.uid)
          if (attr) {
            this.attributes.splice(this.attributes.indexOf(attr), 1)
          }
        })
        this.attributes.forEach(attr => {
          attr.type = 'Attribute'
        })
      })
      crfs.getAllElements(data).then(resp => {
        this.elements = resp.data.items
        this.selectedExtensions.forEach(ex => {
          const ele = this.elements.find(ele => ele.uid === ex.uid)
          if (ele) {
            this.elements.splice(this.elements.indexOf(ele), 1)
          }
        })
        this.elements.forEach(el => {
          el.type = 'Element'
        })
      })
    },
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
      this.$emit('newVersion', this.selectedForm)
      this.readOnly = false
      this.getForm()
    },
    async approve () {
      this.$emit('approve', this.selectedForm)
      this.readOnly = true
      this.getForm()
    },
    async delete () {
      let relationships = 0
      await crfs.getFormRelationship(this.selectedForm.uid).then(resp => {
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
    addExtension (item) {
      if (!this.selectedExtensions.some(el => el.uid === item.uid)) {
        this.selectedExtensions.push(item)
        if (item.type === 'Element') {
          this.elements.splice(this.elements.indexOf(item), 1)
        } else {
          this.attributes.splice(this.attributes.indexOf(item), 1)
          if (item.vendor_element) {
            const parentElement = this.elements.find(el => el.uid === item.vendor_element.uid)
            if (parentElement) {
              this.selectedExtensions.push(parentElement)
              this.elements.splice(this.elements.indexOf(parentElement), 1)
            }
          }
        }
      }
    },
    removeExtension (item) {
      this.selectedExtensions = this.selectedExtensions.filter(el => el.uid !== item.uid)
      if (item.type === 'Element') {
        this.elements.unshift(item)
        const attrs = this.selectedExtensions.filter(el => el.vendor_element ? el.vendor_element.uid === item.uid : null)
        this.attributes = this.attributes.concat(attrs)
        this.selectedExtensions = this.selectedExtensions.filter(el => el.vendor_element ? el.vendor_element.uid !== item.uid : el)
      } else {
        this.attributes.unshift(item)
      }
    },
    async linkExtensions (uid) {
      const elements = this.selectedExtensions.filter(el => el.type === 'Element')
      const elementAttributes = this.selectedExtensions.filter(el => el.vendor_element)
      const namespaceAttributes = this.selectedExtensions.filter(el => el.type === 'Attribute' && el.vendor_namespace)
      await crfs.setElements('forms', uid, elements)
      await crfs.setAttributes('forms', uid, namespaceAttributes)
      await crfs.setElementAttributes('forms', uid, elementAttributes)
    },
    async getExtensionData () {
      await crfs.getAllAttributes().then(resp => {
        this.attributes = resp.data.items
        this.attributes.forEach(attr => {
          attr.type = 'Attribute'
        })
      })
      await crfs.getAllElements().then(resp => {
        this.elements = resp.data.items
        this.elements.forEach(el => {
          el.type = 'Element'
        })
      })
    },
    async initForm (item) {
      this.form = item
      this.form.alias_uids = item.aliases
      this.form.change_description = ''
      if (item.descriptions.find(el => el.language === parameters.ENG)) {
        this.engDescription = item.descriptions.find(el => el.language === parameters.ENG)
      }
      this.desc = item.descriptions.filter((el) => el.language !== parameters.ENG)
      await this.getExtensionData()
      this.selectedExtensions = [...item.vendor_attributes, ...item.vendor_element_attributes, ...item.vendor_elements]
      this.selectedExtensions = this.selectedExtensions.map(ex => {
        if (this.attributes.find(el => el.uid === ex.uid)) {
          const attr = JSON.parse(JSON.stringify(this.attributes.find(el => el.uid === ex.uid)))
          this.attributes.splice(this.attributes.indexOf(this.attributes.find(el => el.uid === ex.uid)), 1)
          attr.value = ex.value
          return attr
        } else {
          const ele = JSON.parse(JSON.stringify(this.elements.find(el => el.uid === ex.uid)))
          this.elements.splice(this.elements.indexOf(this.elements.find(el => el.uid === ex.uid)), 1)
          ele.value = ex.value
          return ele
        }
      })
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
