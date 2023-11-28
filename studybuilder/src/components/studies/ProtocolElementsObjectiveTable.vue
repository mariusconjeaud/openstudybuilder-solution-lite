<template>
<div class="pa-4" v-if="selectedStudyVersion === null">
  <div class="mt-6 d-flex align-center">
    <span class="text-h6">{{ $t('ProtocolElementsObjectiveTable.title') }}</span>
    <v-spacer/>
    <span class="text-center font-italic">{{ loadingMessage }}</span>
    <v-spacer/>
    <div class="d-flex ml-4">
      <v-btn
        color="secondary"
        @click="downloadDocx($event)"
        class="ml-3"
        :disabled="Boolean(loadingMessage)"
      >
        {{ $t('_global.download_docx') }}
      </v-btn>
    </div>
  </div>
  <div class="mt-4" v-html="document" id="ProtocolElementsObjective"></div>
</div>
<div v-else>
  <under-construction :message="$t('UnderConstruction.not_supported')"/>
</div>
</template>

<script>
import study from '@/api/study'
import exportLoader from '@/utils/exportLoader'
import { mapGetters } from 'vuex'
import UnderConstruction from '@/components/layout/UnderConstruction'

export default {
  components: {
    UnderConstruction
  },
  computed: {
    ...mapGetters({
      selectedStudyVersion: 'studiesGeneral/selectedStudyVersion'
    })
  },
  props: {
    studyUid: String,
    update: Number
  },
  data () {
    return {
      document: '',
      loadingMessage: ''
    }
  },
  methods: {
    updateDocument () {
      this.loadingMessage = this.$t('ProtocolElementsObjectiveTable.loading')
      study.getStudyObjectivesHtml(this.studyUid).then(resp => {
        this.document = resp.data
      }).then(this.finally).catch(this.finally)
    },
    downloadDocx () {
      this.loadingMessage = this.$t('ProtocolElementsObjectiveTable.downloading')
      study.getStudyObjectivesDocx(this.studyUid).then(response => {
        exportLoader.downloadFile(response.data, response.headers['content-type'] ||
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document', `${this.studyUid} study-objectives.docx`)
      }).then(this.finally).catch(this.finally)
    },
    finally (error) {
      this.loadingMessage = ''
      if (error) throw error
    }
  },
  mounted () {
    this.updateDocument()
  },
  watch: {
    update (newVal, oldVal) {
      if (newVal !== oldVal) this.updateDocument()
    }
  }
}
</script>

<style lang="scss">
#ObjectivesEndpointsTable {
  width: 100%;
  text-align: left;
  border: 1px solid black;
  border-spacing: 0px;
  border-collapse: collapse;
  table-layout: auto;
  resize: both;

  & TH {
      text-align: center;
      font-weight: bold;
  }

  &, & TH, & TD {
    border: 1px solid black;
    padding: 4px;
  }

  & THEAD {
    background-color: var(--v-greyBackground-base);
    text-align: center;
  }

  & TBODY {
    & TH.objective-level, & TH.endpoint-level {
      text-align: left;
      font-style: italic;
    }

    & TR TD {
      vertical-align: middle;
    }

    & TR TD:first-child {
      vertical-align: top;
    }

  }
}
</style>
