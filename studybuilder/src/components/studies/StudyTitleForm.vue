<template>
<v-card elevation="0" class="nn-grey">
  <v-card-title>
    <span class="page-title">{{ $t('StudyTitleForm.title') }} ({{ studyId }})</span>
    <v-spacer></v-spacer>
    <v-btn
      class="secondary-btn"
      color="white"
      @click="close"
      >
      {{ $t('_global.cancel') }}
    </v-btn>
    <v-btn
      data-cy="save-button"
      color="secondary"
      @click="submit"
      :loading="working"
      class="ml-3"
      >
      {{ $t('_global.save') }}
    </v-btn>
  </v-card-title>
  <v-card-text class="mt-4" ref="container" v-resize="onWindowResized">
    <div class="white pa-4 mb-6">
      <validation-observer ref="observer">
        <div class="d-flex">
          <label class="v-label">{{ $t('StudyTitleForm.title_label') }}</label>
          <v-spacer />
          <span>{{ currentTitleLength }} / {{ maxTitleLength }}</span>
        </div>
        <validation-provider
          v-slot="{ errors }"
          rules="required">
          <v-textarea
            :data-cy="$t('StudyTitleForm.title_label')"
            v-model="form.study_title"
            :maxlength="maxTitleLength"
            :hint="$t('StudyTitleForm.title_hint')"
            persistent-hint
            rows="1"
            auto-grow
            :error-messages="errors"
            ref="titlearea"
            />
        </validation-provider>
        <div class="d-flex mt-6">
          <label class="v-label">{{ $t('StudyTitleForm.short_title') }}</label>
          <v-spacer />
          <span>{{ currentShortTitleLength }} / {{ maxTitleLength/2 }}</span>
        </div>
        <validation-provider
          v-slot="{ errors }"
          rules="required">
          <v-textarea
            v-model="form.study_short_title"
            :maxlength="maxTitleLength/2"
            :hint="$t('StudyTitleForm.short_title_hint')"
            persistent-hint
            rows="1"
            auto-grow
            :error-messages="errors"
            ref="shorttitlearea"
            />
        </validation-provider>
      </validation-observer>
    </div>
      <div class="grey--text font-italic mx-4 mb-0">{{ $t('StudyTitleForm.global_help') }}</div>
    <n-n-table
      :headers="headers"
      :items="studies"
      height="30vh"
      hide-actions-menu
      hide-default-switches
      >
      <template v-slot:item.actions="{ item }">
        <v-btn
          data-cy="copy-title"
          icon
          color="primary"
          @click="copyTitle(item)"
          :title="$t('StudyTitleForm.copy_title')"
          >
          <v-icon>mdi-content-copy</v-icon>
        </v-btn>
      </template>
    </n-n-table>
  </v-card-text>
  <confirm-dialog ref="confirm" :text-cols="6" :action-cols="5" />
</v-card>
</template>

<script>
import { mapGetters } from 'vuex'
import { bus } from '@/main'
import study from '@/api/study'
import NNTable from '@/components/tools/NNTable'
import _isEqual from 'lodash/isEqual'
import ConfirmDialog from '@/components/tools/ConfirmDialog'

export default {
  props: ['description'],
  components: {
    NNTable,
    ConfirmDialog
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy'
    }),
    studyId () {
      return (this.selectedStudy.current_metadata.identification_metadata.study_number !== undefined &&
              this.selectedStudy.current_metadata.identification_metadata.study_number !== null)
        ? this.selectedStudy.current_metadata.identification_metadata.study_id
        : this.selectedStudy.current_metadata.identification_metadata.study_acronym
    },
    currentTitleLength () {
      if (this.form.study_title) {
        return this.form.study_title.length
      }
      return 0
    },
    currentShortTitleLength () {
      if (this.form.study_short_title) {
        return this.form.study_short_title.length
      }
      return 0
    }
  },
  data () {
    return {
      form: {},
      headers: [
        { text: '', value: 'actions', width: '5%' },
        { text: this.$t('StudyTitleForm.project_id'), value: 'current_metadata.identification_metadata.project_number' },
        { text: this.$t('StudyTitleForm.project_name'), value: 'current_metadata.identification_metadata.project_name' },
        { text: this.$t('StudyTitleForm.study_id'), value: 'current_metadata.identification_metadata.study_id' },
        { text: this.$t('StudyTitleForm.study_title'), value: 'current_metadata.study_description.study_title' },
        { text: this.$t('StudyTitleForm.short_title'), value: 'current_metadata.study_description.study_short_title' }
      ],
      maxTitleLength: 600,
      studies: [],
      working: false
    }
  },
  methods: {
    // Workaround for getting the textareas to resize properly
    // when opening the form and resizing the window.
    // Without this it only grows/shrinks when typing.
    onWindowResized () {
      this.$refs.titlearea.calculateInputHeight()
      this.$refs.shorttitlearea.calculateInputHeight()
    },
    async close () {
      if (_isEqual(this.form, this.description)) {
        this.$emit('close')
        return
      }
      const options = {
        type: 'warning',
        cancelLabel: this.$t('_global.cancel'),
        agreeLabel: this.$t('_global.continue')
      }
      if (await this.$refs.confirm.open(this.$t('_global.cancel_changes'), options)) {
        this.form = this.description
        this.$emit('close')
      }
    },
    copyTitle (study) {
      this.form.study_title = study.current_metadata.study_description.study_title
      this.form.study_short_title = study.current_metadata.study_description.study_short_title
    },
    async submit () {
      const isValid = await this.$refs.observer.validate()
      if (!isValid) return
      if (_isEqual(this.form, this.description)) {
        bus.$emit('notification', { msg: this.$t('_global.no_changes'), type: 'info' })
        this.close()
        return
      }
      this.working = true
      try {
        await study.updateStudyDescription(this.selectedStudy.uid, this.form)
        this.$emit('updated')
        bus.$emit('notification', { msg: this.$t('StudyTitleForm.update_success') })
        this.$emit('close')
      } finally {
        this.working = false
      }
    }
  },
  mounted () {
    study.getAll().then(resp => {
      this.studies = resp.data.items
    })
  },
  watch: {
    description: {
      handler (value) {
        if (value) {
          this.form = JSON.parse(JSON.stringify(value))
        }
      },
      immediate: true
    }
  }
}
</script>
