<template>
<div>
  <horizontal-stepper-form
    ref="stepper"
    :title="title"
    :steps="steps"
    @close="close"
    @save="submit"
    :form-observer-getter="getObserver"
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
      <actions-menu :actions="actions" :item="form" v-if="editItem"/>
    </template>
  </horizontal-stepper-form>
  <crf-activities-models-link-form
    :open="linkForm"
    @close="closeLinkForm"
    :item-to-link="editItem"
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
import statuses from '@/constants/statuses'
import parameters from '@/constants/parameters'

export default {
  components: {
    HorizontalStepperForm,
    CrfDescriptionTable,
    VueEditor,
    ActionsMenu,
    CrfActivitiesModelsLinkForm
  },
  props: {
    editItem: {},
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
      return (this.isEdit(this.editItem))
        ? (this.readOnly ? this.$t('CRFForms.crf_form') + ' - ' + this.form.name : this.$t('CRFForms.edit_form') + ' - ' + this.form.name)
        : this.$t('CRFForms.add_form')
    }
  },
  data () {
    return {
      helpItems: [],
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
        { name: 'alias', title: this.$t('CRFForms.alias_details') }
      ],
      editSteps: [
        { name: 'form', title: this.$t('CRFForms.form_details') },
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
      actions: [
        {
          label: this.$t('_global.approve'),
          icon: 'mdi-check-decagram',
          iconColor: 'success',
          condition: (item) => item.possible_actions ? item.possible_actions.find(action => action === actions.APPROVE) : false,
          click: this.approve
        },
        {
          label: this.$t('_global.new_version'),
          icon: 'mdi-plus-circle-outline',
          iconColor: 'primary',
          condition: (item) => item.possible_actions ? item.possible_actions.find(action => action === actions.NEW_VERSION) : false,
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
          condition: (item) => item.status === statuses.FINAL,
          click: this.openLinkForm
        }
      ]
    }
  },
  methods: {
    getForm () {
      crfs.getForm(this.editItem.uid).then((resp) => {
        this.form = resp.data
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
      await crfs.newVersion('forms', this.editItem.uid)
      this.readOnly = false
      this.getForm()
    },
    async approve () {
      await crfs.approve('forms', this.editItem.uid)
      this.readOnly = true
      this.getForm()
    },
    async delete () {
      let relationships = 0
      await crfs.getFormRelationship(this.editItem.uid).then(resp => {
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
        crfs.delete('forms', this.editItem.uid).then((resp) => {
          this.$emit('close')
        })
      } else if (relationships === 0) {
        crfs.delete('forms', this.editItem.uid).then((resp) => {
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
        if (this.isEdit(this.editItem)) {
          this.form.alias_uids = this.form.alias_uids.map(alias => alias.uid ? alias.uid : alias)
          await crfs.updateForm(this.form, this.editItem.uid).then(resp => {
            bus.$emit('notification', { msg: this.$t('CRFForms.form_updated') })
            this.close()
          })
        } else {
          await crfs.createForm(this.form).then(resp => {
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
    initForm (item) {
      this.form.alias_uids = item.aliases
      this.form.change_description = ''
      if (item.descriptions.find(el => el.language === parameters.ENG)) {
        this.engDescription = item.descriptions.find(el => el.language === parameters.ENG)
      }
      this.desc = item.descriptions.filter((el) => el.language !== parameters.ENG)
    },
    getAliasDisplay (item) {
      return `${item.context} - ${item.name}`
    },
    isEdit (value) {
      return Object.keys(value).length !== 0
    }
  },
  mounted () {
    crfs.getAliases().then(resp => {
      this.aliases = resp.data.items
    })
    if (this.isEdit(this.editItem)) {
      this.steps = this.readOnly ? this.createSteps : this.editSteps
      this.form = this.editItem
      this.initForm(this.editItem)
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
    editItem: {
      handler (value) {
        if (this.isEdit(value)) {
          this.steps = this.readOnly ? this.createSteps : this.editSteps
          this.form = value
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
