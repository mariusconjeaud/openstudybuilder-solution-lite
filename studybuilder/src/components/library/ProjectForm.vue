<template>
<simple-form-dialog
  ref="form"
  :title="$t('ProjectForm.title')"
  :help-items="helpItems"
  :help-text="$t('_help.ClinicalProgrammeForm.general')"
  @close="close"
  @submit="submit"
  :open="open"
  >
  <template v-slot:body>
    <validation-observer ref="observer">
        <v-row>
        <v-col cols="11">
        <validation-provider
            v-slot="{ errors }"
            name="ClinicalProgramme"
            rules="required"
            >
          <v-autocomplete
            v-model="form.clinical_programme_uid"
            :label="$t('ProjectForm.clinical_programme')"
            data-cy="template-activity-group"
            :items="programmes"
            item-text="name"
            item-value="uid"
            :error-messages="errors"
            dense
            clearable
            />
        </validation-provider>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12">
          <validation-provider
            v-slot="{ errors }"
            name="Name"
            rules="required"
            >
            <v-text-field
              id="name"
              :label="$t('ProjectForm.name')"
              v-model="form.name"
              :error-messages="errors"
              dense
              clearable
              data-cy="project-name"
              />
          </validation-provider>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12">
          <validation-provider
            v-slot="{ errors }"
            name="ProjectNumber"
            rules="required"
            >
            <v-text-field
              id="project-number"
              :label="$t('ProjectForm.project_number')"
              v-model="form.project_number"
              :error-messages="errors"
              dense
              clearable
              data-cy="project-number"
              />
          </validation-provider>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12">
          <validation-provider
            v-slot="{ errors }"
            name="Description"
            rules="required"
            >
            <v-text-field
              id="description"
              :label="$t('ProjectForm.description')"
              v-model="form.description"
              :error-messages="errors"
              dense
              clearable
              data-cy="project-description"
              />
          </validation-provider>
        </v-col>
      </v-row>
    </validation-observer>
  </template>
</simple-form-dialog>
</template>

<script>
// import { mapGetters } from 'vuex'
import { bus } from '@/main'
import SimpleFormDialog from '@/components/tools/SimpleFormDialog'
import programmes from '@/api/clinicalProgrammes'
import projects from '@/api/projects'

export default {
  components: {
    SimpleFormDialog
  },
  props: {
    editedStudy: Object,
    open: Boolean
  },
  data () {
    return {
      form: {},
      helpItems: [
        'ProjectForm.clinical_programme',
        'ProjectForm.name',
        'ProjectForm.project_number',
        'ProjectForm.description'
      ]
    }
  },
  methods: {
    async close () {
      if (this.form.name || this.form.clinical_programme_uid || this.form.description || this.form.project_number) {
        const options = {
          type: 'warning',
          cancelLabel: this.$t('_global.cancel'),
          agreeLabel: this.$t('_global.continue')
        }
        if (await this.$refs.form.confirm(this.$t('_global.cancel_changes'), options)) {
          this.$emit('close')
        }
      } else {
        this.$emit('close')
      }
      this.initForm()
    },
    initForm () {
      this.form = {}
    },
    async addProject () {
      const data = JSON.parse(JSON.stringify(this.form))
      const resp = await projects.create(data)
      bus.$emit('notification', { msg: this.$t('Projects.add_success') })
      this.$emit('created', resp.data)
    },
    async submit () {
      try {
        await this.addProject()
        this.$emit('close')
      } finally {
        this.$refs.form.working = false
      }
      this.initForm()
    },
    fetchProgrammes () {
      programmes.get({ page_size: 0 }).then(resp => {
        this.programmes = resp.data.items
      })
    }
  },
  mounted () {
    this.fetchProgrammes()
    this.initForm()
  },
  watch: {
  }
}
</script>
