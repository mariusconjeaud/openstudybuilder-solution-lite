<template>
<div class="px-4">
  <div class="page-title d-flex align-center">
    {{ $t('StudyTitleView.title') }} ({{ studyId }})
    <help-button-with-panels
      :help-text="$t('_help.StudyTitleView.general')"
      :items="helpItems"
      />
  </div>
  <div class="d-flex">
    <v-spacer />
    <v-btn
      class="mb-2"
      fab
      small
      color="primary"
      @click.stop="showForm = true"
      :title="$t('StudyTitleView.edit_title')"
      :data-cy="$t('StudyTitleView.edit_title')"
      :disabled="selectedStudyVersion !== null"
      >
      <v-icon>
        mdi-pencil-outline
      </v-icon>
    </v-btn>
  </div>
  <v-sheet
    elevation="0"
    class="pa-4 title"
    rounded
    >
    {{$t('StudyTitleView.title')}}<br>
    <span data-cy="study-title-field" class="text-body-1 mb-3">{{ description.study_title }}</span><br><br>
    {{$t('StudyTitleView.short_title')}}<br>
    <span data-cy="study-title-field" class="text-body-1">{{ description.study_short_title }}</span>
  </v-sheet>
  <v-dialog
    v-model="showForm"
    @keydown.esc="showForm = false"
    persistent
    fullscreen
    hide-overlay
    >
    <study-title-form
      :description="description"
      @updated="fetchStudyDescription"
      @close="showForm = false" />
  </v-dialog>
  <comment-thread-list :topicPath="'/studies/' + selectedStudy.uid + '/study_title'" :isTransparent="true"></comment-thread-list>
</div>
</template>

<script>
import study from '@/api/study'
import { studySelectedNavigationGuard } from '@/mixins/studies'
import StudyTitleForm from '@/components/studies/StudyTitleForm'
import HelpButtonWithPanels from '@/components/tools/HelpButtonWithPanels'
import CommentThreadList from '@/components/tools/CommentThreadList'

export default {
  mixins: [studySelectedNavigationGuard],
  components: {
    StudyTitleForm,
    HelpButtonWithPanels,
    CommentThreadList
  },
  data () {
    return {
      description: {},
      showForm: false,
      helpItems: [
        'StudyTitleView.title'
      ]
    }
  },
  methods: {
    fetchStudyDescription () {
      study.getStudyDescriptionMetadata(this.selectedStudy.uid, this.selectedStudyVersion).then(resp => {
        this.description = resp.data.current_metadata.study_description
      })
    }
  },
  mounted () {
    this.fetchStudyDescription()
  }
}
</script>

<style scoped>
.title {
  min-height: 200px !important;
}
</style>
