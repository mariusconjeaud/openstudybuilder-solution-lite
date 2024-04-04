<template>
<div class="pa-4">
  <div class="mt-6 d-flex align-center">
    <span class="text-h6">{{ $t('ProtocolFlowchart.title') }}</span>
    <v-spacer/>
    <span class="text-center font-italic">{{ loadingMessage }}</span>
    <v-spacer/>
    <v-switch
      v-model="detailed"
      :label="$t('ProtocolFlowchart.detailed')"
      hide-details
      class="mx-2 mr-6"
      :disabled="Boolean(loadingMessage)"
      />
      |
    <label class="v-label theme--light ml-6 mr-4">
      {{ $t('ProtocolFlowchart.preferred_time_unit') }}
    </label>
    <v-radio-group
      v-model="preferredTimeUnit"
      row
      hide-details
      @change="updatePreferredTimeUnit"
      :disabled="selectedStudyVersion !== null"
      >
      <v-radio
        :label="$t('ProtocolFlowchart.day')"
        value="day"
        ></v-radio>
      <v-radio
        :label="$t('ProtocolFlowchart.week')"
        value="week"
        ></v-radio>
    </v-radio-group>
    <v-menu rounded offset-y>
      <template v-slot:activator="{ attrs, on }">
        <v-btn
          fab
          small
          color="nnGreen1"
          class="ml-2 white--text"
          v-bind="attrs"
          v-on="on"
          :title="$t('DataTableExportButton.export')"
          >
          <v-icon>mdi-download-outline</v-icon>
        </v-btn>
      </template>
      <v-list>
        <v-list-item
          link
          @click="downloadCSV"
          >
          <v-list-item-title>CSV</v-list-item-title>
        </v-list-item>
        <v-list-item
          link
          @click="downloadDocx"
          >
          <v-list-item-title>DOCX</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>
  </div>
  <div class="mt-4" v-html="protocolFlowchart" id="protocolFlowchart"></div>
</div>
</template>

<script>
import study from '@/api/study'
import exportLoader from '@/utils/exportLoader'
import { mapGetters } from 'vuex'
import units from '@/api/units'
import unitConstants from '@/constants/units'

export default {
  props: {
    update: Number
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy',
      selectedStudyVersion: 'studiesGeneral/selectedStudyVersion',
      soaPreferredTimeUnit: 'studiesGeneral/soaPreferredTimeUnit'
    })
  },
  data () {
    return {
      protocolFlowchart: '',
      loadingMessage: '',
      detailed: false,
      preferredTimeUnit: null,
      preferredTimeUnits: []
    }
  },
  methods: {
    async updatePreferredTimeUnit (value) {
      for (const timeUnit of this.preferredTimeUnits) {
        if (timeUnit.name === value) {
          await this.$store.dispatch('studiesGeneral/setStudyPreferredTimeUnit', { timeUnitUid: timeUnit.uid, protocolSoa: true })
          this.updateFlowchart()
          break
        }
      }
    },
    updateFlowchart () {
      this.loadingMessage = this.$t('ProtocolFlowchart.loading')
      const params = {
        detailed: this.detailed,
        study_value_version: this.selectedStudyVersion
      }
      study.getStudyProtocolFlowchartHtml(this.selectedStudy.uid, params).then(resp => {
        this.protocolFlowchart = resp.data
      }).then(this.finally).catch(this.finally)
    },
    downloadDocx () {
      this.loadingMessage = this.$t('ProtocolFlowchart.downloading')
      const params = {
        detailed: this.detailed,
        study_value_version: this.selectedStudyVersion
      }
      study.getStudyProtocolFlowchartDocx(this.selectedStudy.uid, params).then(response => {
        let filename = this.selectedStudy.current_metadata.identification_metadata.study_id
        if (this.detailed) {
          filename += ' detailed'
        }
        filename += ' flowchart.docx'
        exportLoader.downloadFile(response.data, response.headers['content-type'] ||
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document', filename)
      }).then(this.finally).catch(this.finally)
    },
    downloadCSV () {
      study.exportStudyProtocolSoa(this.selectedStudy.uid, this.selectedStudyVersion).then(response => {
        const filename = this.selectedStudy.current_metadata.identification_metadata.study_id + ' flowchart.csv'
        exportLoader.downloadFile(response.data, response.headers['content-type'], filename)
      })
    },
    finally (error) {
      this.loadingMessage = ''
      if (error) throw error
    }
  },
  mounted () {
    this.updateFlowchart()
    units.getBySubset(unitConstants.TIME_UNIT_SUBSET_STUDY_PREFERRED_TIME_UNIT).then(resp => {
      this.preferredTimeUnits = resp.data.items
    })
    if (this.soaPreferredTimeUnit) {
      this.preferredTimeUnit = this.soaPreferredTimeUnit.time_unit_name
    }
  },
  watch: {
    soaPreferredTimeUnit () {
      this.preferredTimeUnit = this.soaPreferredTimeUnit.time_unit_name
    },
    detailed (newVal, oldVal) {
      if (newVal !== oldVal) this.updateFlowchart()
    },
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
