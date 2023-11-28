<template>
<simple-form-dialog
  ref="form"
  :title="title"
  :help-items="helpItems"
  @close="cancel"
  @submit="submit"
  :open="open"
  :form-url="formUrl"
  >
  <template v-slot:body>
    <validation-observer ref="observer">
      <v-row>
        <v-col>
          <validation-provider
            v-slot="{ errors }"
            rules="required"
            >
            <v-text-field
              :label="$t('CrfTemplates.name') + '*'"
              data-cy="crf-template-name"
              v-model="form.name"
              :error-messages="errors"
              dense
              clearable
              class="mt-3"
              :readonly="readOnly"
            />
          </validation-provider>
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-text-field
            :label="$t('CrfTemplates.oid')"
            data-cy="crf-template-oid"
            v-model="form.oid"
            dense
            clearable
            class="mt-3"
            :readonly="readOnly"
          />
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="6">
          <v-menu
            v-model="effectiveDateMenu"
            :close-on-content-click="false"
            offset-y
            max-width="290px"
            min-width="290px"
          >
            <template v-slot:activator="{ on }">
              <v-text-field
                :label="$t('CrfTemplates.effective_date')"
                data-cy="crf-template-effective-date"
                readonly
                :value="effectiveDateDisp"
                v-on="on"
              ></v-text-field>
            </template>
            <v-date-picker
              locale="en-in"
              v-model="form.effective_date"
              no-title
              @input="effectiveDateMenu = false"
              data-cy="crf-template-effective-date-picker"
              :readonly="readOnly"
            ></v-date-picker>
          </v-menu>
        </v-col>
        <v-col cols="6">
          <v-menu
            v-model="retiredDateMenu"
            :close-on-content-click="false"
            offset-y
            max-width="290px"
            min-width="290px"
          >
            <template v-slot:activator="{ on }">
              <v-text-field
                :label="$t('CrfTemplates.retired_date')"
                data-cy="crf-template-retired-date"
                readonly
                :value="retiredDateDisp"
                v-on="on"
              ></v-text-field>
            </template>
            <v-date-picker
              locale="en-in"
              v-model="form.retired_date"
              no-title
              @input="retiredDateMenu = false"
              data-cy="crf-template-retired-date-picker"
              :readonly="readOnly"
            ></v-date-picker>
          </v-menu>
        </v-col>
      </v-row>
    </validation-observer>
  </template>
  <template v-slot:actions>
    <v-btn
      @click="newVersion"
      class="primary mr-2"
      v-if="readOnly"
      >
      {{ $t('_global.new_version') }}
    </v-btn>
    <v-btn
      @click="approve"
      class="primary mr-2"
      v-else-if="selectedTemplate && selectedTemplate.status === statuses.DRAFT"
      >
      {{ $t('_global.approve') }}
    </v-btn>
  </template>
</simple-form-dialog>
</template>

<script>
import SimpleFormDialog from '@/components/tools/SimpleFormDialog'
import crfs from '@/api/crfs'
import { bus } from '@/main'
import _isEqual from 'lodash/isEqual'
import statuses from '@/constants/statuses'

export default {
  components: {
    SimpleFormDialog
  },
  props: {
    selectedTemplate: Object,
    open: Boolean,
    readOnlyProp: Boolean
  },
  computed: {
    title () {
      return (this.isEdit())
        ? this.$t('CrfTemplates.edit_template') + ' - ' + this.form.name
        : this.$t('CrfTemplates.add_template')
    },
    effectiveDateDisp () {
      return this.form.effective_date
    },
    retiredDateDisp () {
      return this.form.retired_date
    },
    formUrl () {
      if (this.isEdit()) {
        return `${window.location.href.replace('crf-tree', 'templates')}/template/${this.selectedTemplate.uid}`
      }
      return null
    }
  },
  data () {
    return {
      form: {},
      helpItems: [
        'CrfTemplates.name',
        'CrfTemplates.oid',
        'CrfTemplates.effective_date',
        'CrfTemplates.retired_date'
      ],
      effectiveDateMenu: false,
      retiredDateMenu: false,
      readOnly: this.readOnlyProp
    }
  },
  created () {
    this.statuses = statuses
  },
  methods: {
    newVersion () {
      crfs.newVersion('templates', this.selectedTemplate.uid).then((resp) => {
        this.readOnly = false
      })
    },
    approve () {
      crfs.approve('templates', this.selectedTemplate.uid).then((resp) => {
        this.readOnly = true
      })
    },
    async submit () {
      const isValid = await this.$refs.observer.validate()
      if (!isValid) return
      if (this.isEdit()) {
        crfs.updateTemplate(this.form, this.selectedTemplate.uid).then(resp => {
          bus.$emit('notification', { msg: this.$t('CrfTemplates.template_updated') })
          this.close()
        }, _err => {
          this.$refs.form.working = false
        })
      } else {
        crfs.createTemplate(this.form).then(resp => {
          bus.$emit('notification', { msg: this.$t('CrfTemplates.template_created') })
          this.close()
        }, _err => {
          this.$refs.form.working = false
        })
      }
    },
    async cancel () {
      if (this.$store.getters['form/form'] === '' || _isEqual(this.$store.getters['form/form'], JSON.stringify(this.form))) {
        this.close()
      } else {
        const options = {
          type: 'warning',
          cancelLabel: this.$t('_global.cancel'),
          agreeLabel: this.$t('_global.continue')
        }
        if (await this.$refs.form.confirm(this.$t('_global.cancel_changes'), options)) {
          this.close()
        }
      }
    },
    close () {
      this.form = {}
      this.$refs.observer.reset()
      this.$emit('close')
    },
    isEdit () {
      if (this.selectedTemplate) {
        return Object.keys(this.selectedTemplate).length !== 0
      }
      return false
    }
  },
  mounted () {
    if (this.isEdit()) {
      this.form = { ...this.selectedTemplate }
      this.$store.commit('form/SET_FORM', this.form)
    }
  },
  watch: {
    selectedTemplate (value) {
      if (value) {
        this.form = { ...value }
        this.$store.commit('form/SET_FORM', this.form)
      }
    },
    readOnlyProp (value) {
      this.readOnly = value
    }
  }
}
</script>
