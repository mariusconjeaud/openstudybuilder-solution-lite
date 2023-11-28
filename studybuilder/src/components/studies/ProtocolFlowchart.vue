<template>
<div class="pa-4">
  <div class="mt-6 d-flex align-center">
    <span class="text-h6">{{ $t('ProtocolFlowchart.title') }}</span>
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
  <div class="mt-4" v-html="protocolFlowchart" id="protocolFlowchart"></div>
</div>
</template>

<script>
import study from '@/api/study'
import exportLoader from '@/utils/exportLoader'
import { mapGetters } from 'vuex'

export default {
  props: {
    update: Number
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy',
      selectedStudyVersion: 'studiesGeneral/selectedStudyVersion'
    })
  },
  data () {
    return {
      protocolFlowchart: '',
      loadingMessage: ''
    }
  },
  methods: {
    updateFlowchart () {
      this.loadingMessage = this.$t('ProtocolFlowchart.loading')
      study.getStudyProtocolFlowchartHtml(this.selectedStudy.uid, this.selectedStudyVersion).then(resp => {
        this.protocolFlowchart = resp.data
      }).then(this.finally).catch(this.finally)
    },
    downloadDocx () {
      this.loadingMessage = this.$t('ProtocolFlowchart.downloading')
      study.getStudyProtocolFlowchartDocx(this.selectedStudy.uid, this.selectedStudyVersion).then(response => {
        exportLoader.downloadFile(response.data, response.headers['content-type'] ||
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document', `${this.selectedStudy.current_metadata.identification_metadata.study_id} flowchart.docx`)
      }).then(this.finally).catch(this.finally)
    },
    finally (error) {
      this.loadingMessage = ''
      if (error) throw error
    }
  },
  mounted () {
    this.updateFlowchart()
  },
  watch: {
    update (newVal, oldVal) {
      if (newVal !== oldVal) this.updateFlowchart()
    }
  }
}
</script>

<style lang="scss">
#protocolFlowchart {
  TABLE {
    width: 100%;
    border-collapse: collapse;
    table-layout: auto;
    resize: both;

    &, & TH, & TD {
      border: 1px solid #ebe8e5;
      padding: 1px 3px;
    }

    & THEAD {
      background-color: var(--v-tableGray-base);

      & TH {
        border-color: white;
      }

      & .header1:nth-child(n+2) {
        vertical-align: top;
        writing-mode: sideways-lr;
        text-orientation: mixed;
      }

      & TH:first-child {
        text-align: left;
      }
    }

    & TBODY {
      & TH {
        text-align: left;
        font-weight: normal;
      }

      & TR TD:nth-child(n+2) {
        text-align: center;
        vertical-align: middle;
      }

      & .soaGroup {
        text-transform: uppercase;
        background-color: #b1d5f2;
        font-weight: bold;
      }

      & .soaGroup ~ TD {
        background-color: #b1d5f2;
      }

      & .group {
        background-color: #d8eaf8;
        font-weight: bold;
      }

      & .group ~ TD {
        background-color: #d8eaf8;
      }

      & .subGroup:first-child {
        font-weight: bold;
        padding-left: 1em;
      }

      & .activity:first-child {
        padding-left: 1em;
      }
    }
  }

  DL.footnotes {
    margin: 1em;

    display: grid;
    grid-template-columns: 1em auto;

    DT {
      font-size: 70%;
      vertical-align: top;
    }

  }
}
</style>
