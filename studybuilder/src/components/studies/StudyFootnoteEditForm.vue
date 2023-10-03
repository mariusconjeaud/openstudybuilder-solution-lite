<template>
<study-selection-edit-form
  v-if="studyFootnote"
  ref="form"
  :title="$t('StudyFootnoteEditForm.title')"
  :study-selection="studyFootnote"
  :template="template"
  :library-name="library.name"
  object-type="footnote"
  :open="open"
  :get-object-from-selection="selection => selection.footnote"
  @initForm="initForm"
  @submit="submit"
  @close="$emit('close')"
  :prepare-template-payload-func="prepareTemplatePayload"
  >
  <template v-slot:formFields="{}">
    <p class="mt-6 secondary--text text-h6">
      {{$t('StudyFootnoteEditForm.linked_items')}}
    <v-btn
      icon
      color="primary"
      @click="redirectToDetailedSoA"
      :title="$t('StudyFootnoteEditForm.link_items')"
      >
      <v-icon>mdi-table-plus</v-icon>
    </v-btn>
    </p>
    <v-row>
      <v-col cols="12">
        <v-text-field
          v-if="referencedActivities.length > 0"
          :label="$t('StudyFootnoteEditForm.ref_activities')"
          v-model="referencedActivities"
          dense
          disabled
          readonly
          />
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <v-text-field
          v-if="referencedEpochsAndVisits.length > 0"
          :label="$t('StudyFootnoteEditForm.ref_epochs_visits')"
          v-model="referencedEpochsAndVisits"
          dense
          disabled
          readonly
          />
      </v-col>
    </v-row>
  </template>

</study-selection-edit-form>
</template>

<script>
import _isEmpty from 'lodash/isEmpty'
import { bus } from '@/main'
import formUtils from '@/utils/forms'
import instances from '@/utils/instances'
import { mapGetters } from 'vuex'
import study from '@/api/study'
import StudySelectionEditForm from './StudySelectionEditForm'
import terms from '@/api/controlledTerminology/terms'
import footnoteConstants from '@/constants/footnotes'

export default {
  props: {
    studyFootnote: Object,
    open: Boolean
  },
  components: {
    StudySelectionEditForm
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy'
    }),
    template () {
      return this.studyFootnote.footnote ? this.studyFootnote.footnote.footnote_template : this.studyFootnote.footnote_template
    },
    library () {
      return this.studyFootnote.footnote ? this.studyFootnote.footnote.library : this.studyFootnote.footnote_template.library
    }
  },
  data () {
    return {
      referencedActivities: [],
      referencedEpochsAndVisits: []
    }
  },
  mounted () {
    terms.getByCodelist('footnoteTypes').then(resp => {
      for (const type of resp.data.items) {
        if (type.sponsor_preferred_name === footnoteConstants.FOOTNOTE_TYPE_SOA) {
          this.footnoteType = type
          break
        }
      }
    })
  },
  methods: {
    redirectToDetailedSoA () {
      this.$router.push({ name: 'StudyActivities', params: { tab: 'detailed', footnote: this.studyFootnote } })
      this.$refs.form.close()
    },
    initForm (form) {
      this.originalForm = JSON.parse(JSON.stringify(form))
      this.referencedActivities = []
      this.referencedEpochsAndVisits = []
      this.studyFootnote.referenced_items.forEach(item => {
        if (['StudyActivity', 'StudyActivityGroup', 'StudyActivitySubGroup'].indexOf(item.item_type) > -1) {
          this.referencedActivities.push(item.item_name)
        } else if (['StudyVisit', 'StudyEpoch'].indexOf(item.item_type) > -1) {
          this.referencedEpochsAndVisits.push(item.item_name)
        }
      })
      this.referencedActivities = this.referencedActivities.join(', ')
      this.referencedEpochsAndVisits = this.referencedEpochsAndVisits.join(', ')
    },
    prepareTemplatePayload (data) {
      data.type_uid = this.footnoteType.term_uid
    },
    async getStudyFootnoteNamePreview (parameters) {
      const footnoteData = {
        footnote_template_uid: this.studyFootnote.footnote.footnote_template.uid,
        parameter_terms: await instances.formatParameterValues(parameters),
        library_name: this.studyFootnote.footnote.library.name
      }
      const resp = await study.getStudyFootnotePreview(this.selectedStudy.uid, { footnote_data: footnoteData })
      return resp.data.footnote.name
    },
    async submit (newTemplate, form, parameters) {
      const payload = formUtils.getDifferences(this.originalForm, form)
      if (!this.studyFootnote.footnote) {
        payload.parameters = parameters
      } else {
        const namePreview = await this.getStudyFootnoteNamePreview(parameters)
        if (namePreview !== this.studyFootnote.footnote.name) {
          payload.parameters = parameters
        }
      }
      if (_isEmpty(payload) && !newTemplate) {
        bus.$emit('notification', { msg: this.$t('_global.no_changes'), type: 'info' })
        this.$refs.form.close()
        return
      }
      const args = {
        studyUid: this.selectedStudy.uid,
        studyFootnoteUid: this.studyFootnote.uid,
        form: payload,
        library: this.library
      }
      if (newTemplate) {
        args.template = newTemplate
      } else {
        args.template = this.template
      }
      await this.$store.dispatch('studyFootnotes/updateStudyFootnote', args)
      bus.$emit('notification', { msg: this.$t('StudyFootnoteEditForm.update_success') })
      this.$emit('updated')
      this.$refs.form.close()
    }
  }
}
</script>
