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
          <v-col cols="6">
            <validation-provider
              v-slot="{ errors }"
              rules="required">
              <v-text-field
                :label="$t('CRFItems.name') + '*'"
                data-cy="item-name"
                v-model="form.name"
                :error-messages="errors"
                dense
                clearable
                :readonly="readOnly"
              />
            </validation-provider>
          </v-col>
          <v-col cols="6">
            <v-text-field
              :label="$t('CRFItems.oid')"
              data-cy="item-oid"
              v-model="form.oid"
              dense
              clearable
              :readonly="readOnly"
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="4">
            <validation-provider
              v-slot="{ errors }"
              rules="required">
              <v-select
                v-model="form.datatype"
                :label="$t('CRFItems.data_type') + '*'"
                data-cy="item-data-type"
                :items="dataTypes"
                item-text="code_submission_value"
                item-value="code_submission_value"
                :error-messages="errors"
                dense
                clearable
                class="mt-3"
                @change="checkIfNumeric()"
                :readonly="readOnly"
                />
            </validation-provider>
          </v-col>
          <v-col cols="4" v-if="lengthFieldCheck">
            <v-text-field
              v-if="form.datatype !== crfTypes.COMMENT"
              :label="$t('CRFItems.length')"
              data-cy="item-length"
              v-model="form.length"
              dense
              clearable
              class="mt-3"
              type="number"
              :readonly="readOnly"
              />
          </v-col>
          <v-col cols="4" v-if="digitsFieldCheck">
            <v-text-field
              :label="$t('CRFItems.significant_digits')"
              data-cy="item-significant-digits"
              v-model="form.significant_digits"
              dense
              clearable
              class="mt-3"
              type="number"
              :readonly="readOnly"
              />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="6">
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
          <v-col cols="6">
            <div class="subtitle-2 text--disabled">{{ $t('CRFItems.impl_notes') }}</div>
            <vue-editor
              v-model="engDescription.sponsor_instruction"
              :editor-toolbar="customToolbar"
              v-show="readOnly"
              :disabled="readOnly"/>
            <vue-editor
              v-model="engDescription.sponsor_instruction"
              :editor-toolbar="customToolbar"
              :placeholder="$t('CRFItems.impl_notes')"
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
              data-cy="form-oid-name"
              v-model="engDescription.name"
              dense
              clearable
              :readonly="readOnly"
            />
          </v-col>
          <v-col cols="9">
            <div class="subtitle-2 text--disabled">{{ $t('CRFItems.compl_instructions') }}</div>
            <vue-editor
              v-model="engDescription.instruction"
              :editor-toolbar="customToolbar"
              v-show="readOnly"
              :disabled="readOnly"/>
            <vue-editor
              v-model="engDescription.instruction"
              :editor-toolbar="customToolbar"
              :placeholder="$t('CRFItems.compl_instructions')"
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
            <v-text-field
              :label="$t('CRFItems.sas_name')"
              data-cy="item-sas-name"
              v-model="form.sas_field_name"
              dense
              clearable
              :readonly="readOnly"
            />
          </v-col>
          <v-col cols="6">
            <v-text-field
              :label="$t('CRFItems.sds_name')"
              data-cy="item-sds-name"
              v-model="form.sds_var_name"
              dense
              clearable
              :readonly="readOnly"
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="4" v-if="originFieldCheck">
            <v-select
              v-model="form.origin"
              :label="$t('CRFItems.origin')"
              data-cy="item-origin"
              :items="origins"
              item-text="nci_preferred_name"
              item-value="nci_preferred_name"
              dense
              clearable
              :readonly="readOnly"/>
          </v-col>
          <v-col cols="8">
            <v-text-field
              :label="$t('CRFItems.comment')"
              data-cy="item-comment"
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
      type="ItemDef"
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
              :label="$t('CRFItems.context')"
              data-cy="item-aliast-context"
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
              :label="$t('CRFItems.name')"
              data-cy="item-alias-name"
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
            data-cy="item-aliases"
            dense
            clearable
            :item-text="getAliasDisplay"
            item-value="uid"
            :error-messages="errors"
            :readonly="readOnly">
            <template v-slot:selection="{item, index}">
              <div v-if="index === 0">
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
  <template v-slot:step.codelist="{ step }">
    <validation-observer :ref="`observer_${step}`">
      <v-data-table
        :headers="selectedCodelistHeaders"
        :items="selectedCodelists"
        >
        <template v-slot:item.allowsMultiChoice>
          <v-checkbox
            v-model="form.allows_multi_choice">
          </v-checkbox>
        </template>
        <template v-slot:item.delete="{ item }">
          <v-btn
            icon
            class="mt-1"
            @click="removeCodelist(item)"
            :disabled="readOnly">
            <v-icon dark>
              mdi-trash-can
            </v-icon>
          </v-btn>
        </template>
      </v-data-table>
    </validation-observer>
  </template>
  <template v-slot:step.codelist.after>
    <v-col class="pt-0 mt-0">
      <n-n-table
        :headers="codelistHeaders"
        item-key="uid"
        :items="codelists"
        has-api
        hide-export-button
        hide-default-switches
        column-data-resource="ct/codelists"
        @filter="fetchCodelists"
        additional-margin>
        <template v-slot:item.add="{ item }">
          <v-btn
            icon
            class="mt-1"
            @click="addCodelist(item)"
            :disabled="readOnly">
            <v-icon dark>
              mdi-plus
            </v-icon>
          </v-btn>
        </template>
      </n-n-table>
    </v-col>
  </template>
  <template v-slot:step.terms="{ step }">
    <validation-observer :ref="`observer_${step}`">
      <v-data-table
        :headers="selectedTermsHeaders"
        :items="selectedTerms"
        >
        <template v-slot:item.mandatory="{ item }">
          <v-checkbox
            v-model="item.mandatory"
            :readonly="readOnly"
          />
        </template>
        <template v-slot:item.display_text="{ item }">
          <v-text-field
            v-model="item.display_text"
            :readonly="readOnly"
            dense/>
        </template>
        <template v-slot:item.delete="{ item }">
          <v-btn
            icon
            class="mt-1"
            @click="removeTerm(item)"
            :disabled="readOnly">
            <v-icon dark>
              mdi-trash-can
            </v-icon>
          </v-btn>
        </template>
      </v-data-table>
    </validation-observer>
  </template>
  <template v-slot:step.terms.after>
    <v-col class="pt-0 mt-0">
      <n-n-table
        :headers="termsHeaders"
        item-key="uid"
        :items="terms"
        hide-export-button
        only-text-search
        hide-default-switches
        additional-margin>
        <template v-slot:item.add="{ item }">
          <v-btn
            icon
            class="mt-1"
            @click="addTerm(item)"
            :disabled="readOnly">
            <v-icon dark>
              mdi-plus
            </v-icon>
          </v-btn>
        </template>
      </n-n-table>
    </v-col>
  </template>
  <template v-slot:step.unit="{ step }">
    <validation-observer :ref="`observer_${step}`">
      <n-n-table
        :headers="unitHeaders"
        item-key="uid"
        disable-filtering
        :items="choosenUnits"
        hide-export-button
        hide-default-switches>
          <template v-slot:actions="">
            <v-btn
              class="ml-2"
              fab
              dark
              small
              color="primary"
              @click.stop="addUnit"
              :label="$t('CRFItemGroups.new_translation')"
              :disabled="readOnly"
            >
              <v-icon dark>
                mdi-plus
              </v-icon>
            </v-btn>
          </template>
          <template v-slot:item.name="{ index }">
            <v-autocomplete
              v-model="choosenUnits[index].name"
              :items="units"
              :label="$t('CRFItems.unit_name')"
              data-cy="item-unit-name"
              dense
              class="mt-3"
              item-text="name"
              item-value="name"
              @change="setUnit(index)"
              return-object
              :readonly="readOnly">
            </v-autocomplete>
          </template>
          <template v-slot:item.mandatory="{ item }">
            <v-checkbox
              v-model="item.mandatory"
              :readonly="readOnly"
            ></v-checkbox>
          </template>
          <template v-slot:item.delete="{ index }">
              <v-btn
                icon
                class="mt-3"
                @click="removeUnit(index)"
                :disabled="readOnly">
                <v-icon dark>
                    mdi-trash-can
                </v-icon>
              </v-btn>
          </template>
      </n-n-table>
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
                :label="$t('CRFItems.change_desc')"
                data-cy="item-change-description"
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
    <actions-menu :actions="actions" :item="form" v-if="selectedItem"/>
  </template>
</horizontal-stepper-form>
<crf-activities-models-link-form
  :open="linkForm"
  @close="closeLinkForm"
  :item-to-link="selectedItem"
  item-type="item" />
<confirm-dialog ref="confirm" :text-cols="6" :action-cols="5" />
</div>
</template>

<script>
import crfs from '@/api/crfs'
import NNTable from '@/components/tools/NNTable'
import terms from '@/api/controlledTerminology/terms'
import HorizontalStepperForm from '@/components/tools/HorizontalStepperForm'
import { bus } from '@/main'
import controlledTerminology from '@/api/controlledTerminology'
import constants from '@/constants/libraries'
import CrfDescriptionTable from '@/components/library/crfs/CrfDescriptionTable'
import { VueEditor } from 'vue2-editor'
import { mapGetters } from 'vuex'
import crfTypes from '@/constants/crfTypes'
import ActionsMenu from '@/components/tools/ActionsMenu'
import CrfActivitiesModelsLinkForm from '@/components/library/crfs/CrfActivitiesModelsLinkForm'
import actions from '@/constants/actions'
import parameters from '@/constants/parameters'
import CrfExtensionsManagementTable from '@/components/library/crfs/CrfExtensionsManagementTable'
import ConfirmDialog from '@/components/tools/ConfirmDialog'

export default {
  components: {
    NNTable,
    HorizontalStepperForm,
    CrfDescriptionTable,
    VueEditor,
    ActionsMenu,
    CrfActivitiesModelsLinkForm,
    CrfExtensionsManagementTable,
    ConfirmDialog
  },
  props: {
    selectedItem: Object,
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
        ? (this.readOnly ? this.$t('CRFItems.crf_item') + ' - ' + this.form.name : this.$t('CRFItems.edit_item') + ' - ' + this.form.name)
        : this.$t('CRFItems.add_item')
    },
    formUrl () {
      if (this.isEdit()) {
        return `${window.location.href.replace('crf-tree', 'items')}/item/${this.selectedItem.uid}`
      }
      return null
    }
  },
  created () {
    this.crfTypes = crfTypes
  },
  data () {
    return {
      helpItems: [
        'CRFItems.name',
        'CRFItems.oid',
        'CRFItems.data_type',
        'CRFItems.length',
        'CRFItems.significant_digits',
        'CRFItems.impl_notes',
        'CRFItems.compl_instructions',
        'CRFItems.sas_name',
        'CRFItems.sds_name',
        'CRFItems.origin',
        'CRFItems.comment',
        'CRFItems.context',
        'CRFItems.name'
      ],
      form: {
        oid: 'I.',
        alias_uids: []
      },
      desc: [],
      selectedExtensions: [],
      selectedCodelistHeaders: [
        { text: this.$t('CtCatalogueTable.concept_id'), value: 'codelistUid' },
        { text: this.$t('CtCatalogueTable.cd_name'), value: 'attributes.name' },
        { text: this.$t('CtCatalogueTable.submission_value'), value: 'attributes.submissionValue' },
        { text: this.$t('CtCatalogueTable.nci_pref_name'), value: 'attributes.nciPreferredName' },
        { text: this.$t('CRFItems.multiple_choice'), value: 'allowsMultiChoice' },
        { text: '', value: 'delete' }
      ],
      codelistHeaders: [
        { text: this.$t('CtCatalogueTable.concept_id'), value: 'codelistUid' },
        { text: this.$t('CtCatalogueTable.cd_name'), value: 'attributes.name' },
        { text: this.$t('CtCatalogueTable.submission_value'), value: 'attributes.submissionValue' },
        { text: this.$t('CtCatalogueTable.nci_pref_name'), value: 'attributes.nciPreferredName' },
        { text: '', value: 'add' }
      ],
      unitHeaders: [
        { text: this.$t('CRFItemGroups.name'), value: 'name', width: '25%' },
        { text: this.$t('CRFItems.sponsor_unit'), value: 'oid', width: '20%' },
        { text: this.$t('UnitTable.ucum_unit'), value: 'ucum' },
        { text: this.$t('UnitTable.ct_units'), value: 'terms', width: '30%' },
        { text: this.$t('_global.mandatory'), value: 'mandatory' },
        { text: '', value: 'delete' }
      ],
      termsHeaders: [
        { text: this.$t('CtCatalogueTable.concept_id'), value: 'term_uid' },
        { text: this.$t('_global.name'), value: 'name.sponsor_preferred_name' },
        { text: '', value: 'add' }
      ],
      selectedTermsHeaders: [
        { text: this.$t('CtCatalogueTable.concept_id'), value: 'term_uid', width: '10%' },
        { text: this.$t('CRFItems.sponsor_pref_name'), value: 'name.sponsor_preferred_name', width: '40%' },
        { text: this.$t('_global.mandatory'), value: 'mandatory', width: '5%' },
        { text: this.$t('CRFItems.displayed_name'), value: 'display_text', width: '40%' },
        { text: '', value: 'delete', width: '5%' }
      ],
      aliases: [],
      alias: {},
      steps: [],
      createSteps: [
        { name: 'form', title: this.$t('CRFItems.item_details') },
        { name: 'extensions', title: this.$t('CRFForms.vendor_extensions'), belowDisplay: true },
        { name: 'description', title: this.$t('CRFItemGroups.description_details'), belowDisplay: true },
        { name: 'alias', title: this.$t('CRFItemGroups.alias_details') }
      ],
      editSteps: [
        { name: 'form', title: this.$t('CRFItems.item_details') },
        { name: 'extensions', title: this.$t('CRFForms.vendor_extensions'), belowDisplay: true },
        { name: 'description', title: this.$t('CRFItemGroups.description_details'), belowDisplay: true },
        { name: 'alias', title: this.$t('CRFItemGroups.alias_details') },
        { name: 'change_description', title: this.$t('CRFForms.change_desc') }
      ],
      origins: [],
      units: [],
      choosenUnits: [
        { name: '', mandatory: true }
      ],
      codelists: [],
      selectedCodelists: [],
      options: {},
      total: 0,
      filters: '',
      dataTypes: [],
      descKey: 0,
      customToolbar: [
        ['bold', 'italic', 'underline'],
        [{ script: 'sub' }, { script: 'super' }],
        [{ list: 'ordered' }, { list: 'bullet' }]
      ],
      engDescription: { library_name: constants.LIBRARY_SPONSOR, language: parameters.ENG },
      terms: [],
      selectedTerms: [],
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
      ],
      lengthFieldCheck: false,
      digitsFieldCheck: false,
      originFieldCheck: true
    }
  },
  mounted () {
    this.fetchCodelists()
    terms.getAttributesByCodelist('originType').then(resp => {
      this.origins = resp.data.items
    })
    terms.getAttributesByCodelist('dataType').then(resp => {
      this.dataTypes = resp.data.items
    })
    crfs.getAliases().then(resp => {
      this.aliases = resp.data.items
    })
    this.$store.dispatch('units/fetchUnits').then((resp) => {
      this.units = this.$store.getters['units/units'].items
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
    checkFieldAvailable (dataType) {
      this.lengthFieldCheck = false
      this.digitsFieldCheck = false
      this.originFieldCheck = true
      this.$set(this.form, 'length', null)
      switch (dataType) {
        case 'TEXT':
        case 'BOOLEAN':
        case 'URI':
          break
        case 'COMMENT':
          this.originFieldCheck = false
          break
        case 'FLOAT':
        case 'DOUBLE':
        case 'HEXBINARY':
        case 'BASE64BINARY':
        case 'HEXFLOAT':
        case 'BASE64FLOAT':
          this.lengthFieldCheck = true
          this.digitsFieldCheck = true
          break
        case 'DATE':
          this.lengthFieldCheck = true
          this.$set(this.form, 'length', 10)
          break
        case 'TIME':
          this.lengthFieldCheck = true
          this.$set(this.form, 'length', 5)
          break
        case 'DATETIME':
          this.lengthFieldCheck = true
          this.$set(this.form, 'length', 16)
          break
        default:
          this.lengthFieldCheck = true
      }
    },
    getItem () {
      crfs.getItem(this.selectedItem.uid).then((resp) => {
        this.initForm(resp.data)
      })
    },
    openLinkForm () {
      this.linkForm = true
    },
    closeLinkForm () {
      this.linkForm = false
      this.getItem()
    },
    async newVersion () {
      let relationships = 0
      await crfs.getRelationships(this.selectedItem.uid, 'items').then(resp => {
        if (resp.data.OdmItemGroup && resp.data.OdmItemGroup.length > 0) {
          relationships = resp.data.OdmItemGroup.length
        }
      })
      const options = {
        type: 'warning',
        cancelLabel: this.$t('_global.cancel'),
        agreeLabel: this.$t('_global.continue')
      }
      if (relationships > 1 && await this.$refs.confirm.open(`${this.$t('CRFForms.new_version_warning')}`, options)) {
        crfs.newVersion('items', this.selectedItem.uid).then((resp) => {
          this.$emit('updateItem', { type: crfTypes.ITEM, element: resp.data })
          this.$emit('newVersion', this.selectedItem)
          this.readOnly = false
          this.getItem()
        })
      } else if (relationships <= 1) {
        crfs.newVersion('items', this.selectedItem.uid).then((resp) => {
          this.$emit('updateItem', { type: crfTypes.ITEM, element: resp.data })
          this.$emit('newVersion', this.selectedItem)
          this.readOnly = false
          this.getItem()
        })
      }
    },
    async approve () {
      this.$emit('approve', this.selectedItem)
      this.readOnly = true
      this.getItem()
    },
    async delete () {
      let relationships = 0
      await crfs.getRelationships(this.selectedItem.uid, 'items').then(resp => {
        if (resp.data.OdmItemGroup && resp.data.OdmItemGroup.length > 0) {
          relationships = resp.data.OdmItemGroup.length
        }
      })
      const options = {
        type: 'warning',
        cancelLabel: this.$t('_global.cancel'),
        agreeLabel: this.$t('_global.continue')
      }
      if (relationships > 0 && await this.$refs.confirm.open(`${this.$t('CRFItems.delete_warning_1')} ${relationships} ${this.$t('CRFItems.delete_warning_2')}`, options)) {
        crfs.delete('items', this.selectedItem.uid).then((resp) => {
          this.$emit('close')
        })
      } else if (relationships === 0) {
        crfs.delete('items', this.selectedItem.uid).then((resp) => {
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
    checkIfNumeric () {
      if (this.form.datatype) {
        if ((this.form.datatype.indexOf('INTEGER') !== -1 || this.form.datatype.indexOf('FLOAT') !== -1 || this.form.datatype.indexOf('DOUBLE') !== -1)) {
          this.steps.splice(1, 0, { name: 'unit', title: this.$t('CRFItems.unit_details') })
          this.steps = this.steps.filter(function (obj) {
            return (obj.name !== 'codelist' && obj.name !== 'terms')
          })
        } else if (this.form.datatype.indexOf('STRING') !== -1) {
          this.steps = this.steps.filter(function (obj) {
            return obj.name !== 'unit'
          })
          this.steps.splice(1, 0, { name: 'codelist', title: this.$t('CRFItems.codelist_details') })
          this.steps.splice(2, 0, { name: 'terms', title: this.$t('CRFItems.codelist_subset') })
        }
        if (this.form.datatype.indexOf('STRING') === -1) {
          this.steps = this.steps.filter(function (obj) {
            return (obj.name !== 'codelist' && obj.name !== 'terms')
          })
        }
        if ((this.form.datatype.indexOf('INTEGER') === -1 && this.form.datatype.indexOf('FLOAT') === -1 && this.form.datatype.indexOf('DOUBLE') === -1)) {
          this.steps = this.steps.filter(function (obj) {
            return obj.name !== 'unit'
          })
        }
      } else {
        this.steps = this.steps.filter(function (obj) {
          return (obj.name !== 'unit' && obj.name !== 'codelist' && obj.name !== 'terms')
        })
      }
      const uniqueSteps = Array.from(new Set(this.steps.map(a => a.name))).map(name => {
        return this.steps.find(a => a.name === name)
      })
      this.steps = uniqueSteps
      this.checkFieldAvailable(this.form.datatype)
    },
    close () {
      this.form = {
        oid: 'I.',
        alias_uids: []
      }
      this.desc = []
      this.choosenUnits = []
      this.selectedCodelists = []
      this.selectedTerms = []
      this.selectedExtensions = []
      this.engDescription = { library_name: constants.LIBRARY_SPONSOR, language: parameters.ENG }
      this.$refs.stepper.reset()
      this.$emit('close')
    },
    getCodeListTerms (item) {
      if (item) {
        terms.getTermsByCodelistUid(item.codelist_uid).then(resp => {
          this.terms = resp.data.items
          if (this.form.terms) {
            this.form.terms.forEach((el, index) => {
              this.selectedTerms.push(this.terms.find(e => e.term_uid === el.term_uid))
              this.selectedTerms[index].display_text = el.display_text
              if (el.mandatory) {
                this.selectedTerms[index].mandatory = true
              }
            })
          }
          this.terms = this.terms.filter(ar => !this.selectedTerms.find(rm => (rm.term_uid === ar.term_uid)))
        })
      } else {
        this.terms = []
      }
    },
    addTerm (item) {
      item.mandatory = true
      if (!this.selectedTerms.some(el => el.term_uid === item.term_uid)) {
        this.selectedTerms.push(item)
        this.terms.splice(this.terms.indexOf(item), 1)
      }
    },
    removeTerm (item) {
      this.selectedTerms = this.selectedTerms.filter(el => el.term_uid !== item.term_uid)
      this.terms.unshift(item)
    },
    async submit () {
      await this.createOrUpdateDescription()
      this.form.library_name = constants.LIBRARY_SPONSOR
      if (this.form.oid === 'I.') {
        this.$set(this.form, 'oid', '')
      }
      this.choosenUnits = this.choosenUnits.filter(el => {
        return el.name !== ''
      })
      this.form.unit_definitions = this.choosenUnits.length === 0 ? [] : this.choosenUnits.map(e => ({ uid: e.uid, mandatory: e.mandatory }))
      if (this.form.datatype !== 'STRING') {
        this.form.codelistUid = null
        this.form.terms = []
      } else {
        this.form.codelist_uid = this.selectedCodelists[0] ? this.selectedCodelists[0].codelist_uid : null
        this.form.terms = this.selectedTerms.map(el => ({ uid: el.term_uid, mandatory: el.mandatory, display_text: el.display_text }))
      }
      try {
        if (this.isEdit()) {
          this.form.alias_uids = this.form.alias_uids.map(alias => alias.uid ? alias.uid : alias)
          await crfs.updateItem(this.form, this.selectedItem.uid).then(async resp => {
            await this.linkExtensions(this.selectedItem.uid)
            bus.$emit('notification', { msg: this.$t('CRFItems.item_updated') })
            this.close()
          })
        } else {
          await crfs.createItem(this.form).then(async resp => {
            await this.linkExtensions(resp.data.uid)
            bus.$emit('notification', { msg: this.$t('CRFItems.item_created') })
            this.$emit('linkItem', resp)
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
      await crfs.setExtensions('items', uid, data)
    },
    addUnit () {
      this.choosenUnits.push({ name: '', mandatory: true })
    },
    removeUnit (index) {
      this.choosenUnits.splice(index, 1)
    },
    setUnit (index) {
      this.choosenUnits[index].ucum = this.choosenUnits[index].name.ucum ? this.choosenUnits[index].name.ucum.name : ''
      this.choosenUnits[index].oid = this.choosenUnits[index].name.name
      this.choosenUnits[index].terms = this.choosenUnits[index].name.ct_units[0] ? this.choosenUnits[index].name.ct_units[0].name : ''
      this.choosenUnits[index].uid = this.choosenUnits[index].name.uid
    },
    async createAlias () {
      this.alias.library_name = constants.LIBRARY_SPONSOR
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
    async initForm (item) {
      this.form = item
      this.form.alias_uids = item.aliases
      if (item.descriptions.find(el => el.language === parameters.ENG)) {
        this.engDescription = item.descriptions.find(el => el.language === parameters.ENG)
      }
      this.desc = item.descriptions.filter((el) => el.language !== parameters.ENG)
      if (!item.unit_definitions || item.unit_definitions.length === 0) {
        this.choosenUnits = []
      } else {
        item.unit_definitions.forEach(e => {
          if (!this.choosenUnits.some(el => el.uid === e.uid)) {
            this.choosenUnits.unshift(
              {
                uid: e.uid,
                oid: e.name,
                name: e.name,
                ucum: e.ucum ? e.ucum.name : '',
                terms: e.ct_units[0] ? e.ct_units[0].name : '',
                mandatory: e.mandatory
              }
            )
          }
        })
      }
      if (this.selectedCodelists.length === 0 && item.codelist) {
        this.selectedCodelists.push(
          {
            codelist_uid: item.codelist.uid,
            attributes: {
              name: item.codelist.name,
              submission_value: item.codelist.submission_value,
              nci_preferred_name: item.codelist.preferred_term
            }
          }
        )
      }
      this.form.change_description = this.$t('_global.draft_change')
      this.checkIfNumeric()
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
      if (this.selectedItem) {
        return Object.keys(this.selectedItem).length !== 0
      }
      return false
    },
    fetchCodelists (filters, sort, filtersUpdated) {
      this.filters = filters
      if (this.filtersUpdated) {
        this.options.page = 1
      }
      const params = {
        page_number: (this.options.page),
        page_size: this.options.itemsPerPage,
        total_count: true,
        library: this.library
      }
      if (this.filters !== undefined) {
        params.filters = this.filters
      }
      controlledTerminology.getCodelists(params).then(resp => {
        this.codelists = resp.data.items.filter(ar => !this.selectedCodelists.find(rm => (rm.codelist_uid === ar.codelist_uid)))
        this.total = resp.data.total
      })
    },
    addCodelist (item) {
      if (this.selectedCodelists.length === 0) {
        this.selectedCodelists.push(item)
        this.codelists.splice(this.codelists.indexOf(item), 1)
      }
    },
    removeCodelist (item) {
      this.selectedCodelists = []
      this.codelists.unshift(item)
    }
  },
  watch: {
    readOnlyProp (value) {
      this.readOnly = value
    },
    selectedCodelists (value) {
      this.getCodeListTerms(value[0])
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
    selectedItem: {
      handler (value) {
        if (this.isEdit()) {
          this.steps = this.readOnly ? this.createSteps : this.editSteps
          if (value.datatype.indexOf('INTEGER') !== -1 || value.datatype.indexOf('FLOAT') !== -1 || value.datatype.indexOf('DOUBLE') !== -1) {
            this.steps.splice(3, 0, { name: 'unit', title: this.$t('CRFItems.unit_details') })
          }
          if (value.datatype.indexOf('STRING') !== -1) {
            this.steps.splice(1, 0, { name: 'codelist', title: this.$t('CRFItems.codelist_details') })
            this.steps.splice(2, 0, { name: 'terms', title: this.$t('CRFItems.codelist_subset') })
          }
          this.initForm(value)
        } else {
          this.steps = this.createSteps
        }
        if (!this.userData.multilingual) {
          this.steps = this.steps.filter(function (obj) {
            return obj.name !== 'description'
          })
        }
        const uniqueSteps = Array.from(new Set(this.steps.map(a => a.name))).map(name => {
          return this.steps.find(a => a.name === name)
        })
        this.steps = uniqueSteps
      },
      immediate: true
    },
    options: {
      handler () {
        this.fetchCodelists()
      },
      deep: true
    }
  }
}
</script>
