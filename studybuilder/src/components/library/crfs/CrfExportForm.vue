<template>
<v-card>
  <v-card-title>
    {{ $t('OdmViewer.export') + item.name }}
  </v-card-title>
  <v-card-text>
    <validation-observer ref="observer">
        <v-row>
          <v-col cols="4">
            <validation-provider
              v-slot="{ errors }"
              rules="required"
              >
              <v-select
                class="mt-5"
                v-model="format"
                :label="$t('OdmViewer.format')"
                :items="formats"
                dense
                clearable
                :error-messages="errors"
                />
              </validation-provider>
          </v-col>
          <v-col cols="2">
            <v-switch
              class="mt-6"
              v-model="draft"
              :label="$t('_global.draft')"
              />
          </v-col>
          <v-col cols="4">
            <label>{{$t('OdmViewer.stylesheet')}}</label>
            <v-radio-group
              v-model="exportParams.stylesheet"
              >
              <v-radio :label="$t('OdmViewer.sdtm')" value="sdtm" />
              <v-radio :label="$t('OdmViewer.blank')" value="blank" />
            </v-radio-group>
          </v-col>
        </v-row>
    </validation-observer>
  </v-card-text>
  <v-card-actions>
    <v-spacer></v-spacer>
    <v-btn
      class="primary"
      @click="exportElement()"
      :loading="loading"
      >
      {{ $t('_global.export') }}
    </v-btn>
    <v-btn
      class="secondary-btn"
      color="white"
      @click="close()"
      >
      {{ $t('_global.close') }}
    </v-btn>
  </v-card-actions>
</v-card>
</template>

<script>
import crfs from '@/api/crfs'
import exportLoader from '@/utils/exportLoader'
import { DateTime } from 'luxon'
import statuses from '@/constants/statuses'

export default {
  components: {
  },
  props: {
    open: Boolean,
    item: Object,
    type: String
  },
  data () {
    return {
      formats: ['PDF', 'HTML', 'XML'],
      draft: false,
      format: '',
      exportParams: {
        target_type: '',
        stylesheet: 'sdtm',
        export_to: 'v1',
        target_uid: '',
        status: ''
      },
      loading: false
    }
  },
  methods: {
    async exportElement () {
      const isValid = await this.$refs.observer.validate()
      if (!isValid) return
      this.loading = true
      this.setExportParams(this.item)
      switch (this.format) {
        case 'PDF':
          this.exportPdf()
          break
        case 'HTML':
          this.exportHtml()
          break
        case 'XML':
          this.exportXml()
      }
    },
    exportPdf () {
      crfs.getPdf(this.exportParams).then(resp => {
        exportLoader.downloadFile(resp.data, 'application/pdf', this.getDownloadFileName())
        this.loading = false
        this.close()
      })
    },
    exportHtml () {
      crfs.getXml(this.exportParams).then(async resp => {
        const parser = new DOMParser()
        const xml = parser.parseFromString(resp.data, 'application/xml')
        const xsltProcessor = new XSLTProcessor()
        crfs.getXsl(this.exportParams.stylesheet).then(resp => {
          const xmlDoc = parser.parseFromString(resp.data, 'text/xml')
          xsltProcessor.importStylesheet(xmlDoc)
          exportLoader.downloadFile(new XMLSerializer().serializeToString(xsltProcessor.transformToDocument(xml)), 'text/html', this.getDownloadFileName())
          this.loading = false
          this.close()
        })
      })
    },
    exportXml () {
      crfs.getXml(this.exportParams).then(resp => {
        exportLoader.downloadFile(resp.data, 'text/xml', this.getDownloadFileName())
        this.loading = false
        this.close()
      })
    },
    setExportParams () {
      this.$set(this.exportParams, 'target_uid', this.item.uid)
      this.$set(this.exportParams, 'target_type', this.type)
      this.$set(this.exportParams, 'status', this.draft ? `${statuses.FINAL}&status=${statuses.DRAFT}`.toLowerCase() : statuses.FINAL.toLowerCase())
    },
    getDownloadFileName () {
      const stylesheet = this.type === 'sdtm' ? '_sdtm_crf_' : '_blank_crf_'
      const templateName = this.item.name
      return `${templateName + stylesheet + DateTime.local().toFormat('yyyy-MM-dd HH:mm')}`
    },
    close () {
      this.$emit('close')
    }
  }
}
</script>
