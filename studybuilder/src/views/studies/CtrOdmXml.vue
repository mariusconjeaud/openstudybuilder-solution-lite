<template>
<div class="pa-4">
  <div class="mt-6 d-flex align-center">
    <span class="text-h6">{{ $t('CtrOdmXmlVue.title') }}</span>
    <v-spacer/>
    <span class="text-center font-italic">{{ loadingMessage }}</span>
    <v-spacer/>
    <div class="d-flex ml-4">
      <v-btn
        color="secondary"
        @click="downloadXml($event)"
        class="ml-3"
        :disabled="Boolean(loadingMessage)"
      >
        {{ $t('CtrOdmXmlVue.download') }}
      </v-btn>
    </div>
  </div>
  <div class="mt-4" v-html="htmlDocument" id="CtrOdmHtml"></div>
</div>
</template>

<script>
import { studySelectedNavigationGuard } from '@/mixins/studies'
import study from '@/api/study'
import exportLoader from '@/utils/exportLoader'
import axios from 'axios'

export default {
  mixins: [studySelectedNavigationGuard],
  components: {
  },
  props: {
    update: Number
  },
  computed: {
    stylesheetUrl () {
      if (process.env.NODE_ENV === 'development') {
        return `/${this.stylesheetPath}`
      } else {
        return `https://${location.host}/${this.stylesheetPath}`
      }
    }
  },
  data () {
    return {
      loadingMessage: '',
      htmlDocument: '',
      stylesheetPath: 'odm_template_sdtmcrf.xsl'
    }
  },
  mounted () {
    this.renderXml()
  },
  watch: {
    update (newVal, oldVal) {
      if (newVal !== oldVal) this.renderXml()
    }
  },
  methods: {
    renderXml () {
      this.loadingMessage = this.$t('CtrOdmXmlVue.loading')
      study.getCtrOdmXml(this.selectedStudy.uid).then(resp => {
        const parser = new DOMParser()
        const xml = parser.parseFromString(resp.data, 'text/xml')
        axios.get(this.stylesheetUrl).then(resp => {
          const xsltProcessor = new XSLTProcessor()
          xsltProcessor.importStylesheet(parser.parseFromString(resp.data, 'text/xml'))
          const doc = xsltProcessor.transformToDocument(xml)
          const bodies = doc.getElementsByTagName('body')
          if (bodies.length) {
            this.htmlDocument = new XMLSerializer().serializeToString(bodies[0])
          }
        })
      }).then(this.finally).catch(this.finally)
    },
    downloadXml () {
      this.loadingMessage = this.$t('CtrOdmXmlVue.downloading')
      study.downloadCtrOdmXml(this.selectedStudy.uid).then(response => {
        const blob = new Blob([response.data], {
          type: response.headers['content-type'] || 'text/xml'
        })
        const fileName = `${this.selectedStudy.uid} CTR-ODM.xml`
        exportLoader.generateDownload(blob, fileName)
      }).then(this.finally).catch(this.finally)
    },
    finally (error) {
      this.loadingMessage = ''
      if (error) throw error
    }
  }
}
</script>
