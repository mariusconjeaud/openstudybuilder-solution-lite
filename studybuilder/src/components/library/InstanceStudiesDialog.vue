<template>
<v-card color="dfltBackground">
  <v-card-title>
    <span class="dialog-title">{{ $t('InstanceStudiesDialog.title', { type }) }}</span>
  </v-card-title>
  <v-card-text>
    <v-row class="mt-4">
      <v-col cols="2">
        <strong>{{ $t('InstanceStudiesDialog.template', { type: capitalizedType }) }}</strong>
      </v-col>
      <v-col cols="10">
        <n-n-parameter-highlighter :name="template" :show-prefix-and-postfix="false" />
      </v-col>
      <v-col cols="2">
        <strong>{{ $t('InstanceStudiesDialog.text', { type: capitalizedType }) }}</strong>
      </v-col>
      <v-col cols="10">
        <n-n-parameter-highlighter :name="text" :show-prefix-and-postfix="false" />
      </v-col>
    </v-row>
    <n-n-table
      class="mt-4"
      :headers="headers"
      :items="studies"
      height="40vh"
      >
      <template v-slot:item.redirect="{ item }">
        <v-btn
          class="pb-3"
          fab
          dark
          small
          color="primary"
          @click="goToStudy(item)"
          icon
          >
          <v-icon dark>
            mdi-eye-arrow-right-outline
          </v-icon>
        </v-btn>
      </template>
      </n-n-table>
  </v-card-text>
  <v-card-actions>
    <v-spacer></v-spacer>
    <v-btn
      color="secondary"
      @click="close"
      >
      {{ $t('_global.close') }}
    </v-btn>
  </v-card-actions>
</v-card>
</template>

<script>
import NNParameterHighlighter from '@/components/tools/NNParameterHighlighter'
import NNTable from '@/components/tools/NNTable'

export default {
  components: {
    NNParameterHighlighter,
    NNTable
  },
  props: {
    template: String,
    text: String,
    type: String,
    studies: Array
  },
  computed: {
    capitalizedType () {
      return this.type.charAt(0).toUpperCase() + this.type.slice(1)
    }
  },
  data () {
    return {
      headers: [
        { text: this.$t('InstanceStudiesDialog.view'), value: 'redirect', width: '5%' },
        { text: this.$t('InstanceStudiesDialog.project_id'), value: 'current_metadata.identification_metadata.project_number' },
        { text: this.$t('InstanceStudiesDialog.project_name'), value: 'current_metadata.identification_metadata.project_name' },
        { text: this.$t('InstanceStudiesDialog.brand_name'), value: 'current_metadata.identification_metadata.brand_name' },
        { text: this.$t('InstanceStudiesDialog.study_number'), value: 'current_metadata.identification_metadata.study_number' },
        { text: this.$t('InstanceStudiesDialog.study_id'), value: 'current_metadata.identification_metadata.study_id' },
        { text: this.$t('InstanceStudiesDialog.study_acronym'), value: 'current_metadata.identification_metadata.study_acronym' },
        { text: this.$t('_global.status'), value: 'current_metadata.version_metadata.study_status' }
      ]
    }
  },
  methods: {
    close () {
      this.$emit('close')
    },
    goToStudy (study) {
      this.$store.dispatch('studiesGeneral/selectStudy', { studyObj: study })
      this.$router.push({ name: 'StudyPurpose', params: { study_id: study.uid, tab: this.type + 's' } })
      this.$router.go()
    }
  }
}
</script>
