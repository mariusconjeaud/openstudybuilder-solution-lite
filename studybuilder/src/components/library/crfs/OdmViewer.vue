<template>
  <div>
    <v-app-bar
      flat
      color="#e5e5e5"
      class="mt-2"
      style="height: 60px"
      >
      <v-row class="mt-2" v-if="doc === ''">
        <v-col cols="3">
          <v-select
            v-model="params.target_type"
            :items="types"
            @change="setElements()"
            :label="$t('OdmViewer.odm_element_type')"
            dense
            clearable
            item-text="name"
            item-value="value"
            class="mt-2">
          </v-select>
        </v-col>
        <v-col cols="3">
          <v-select
            :items="elements"
            :label="$t('OdmViewer.odm_element_name')"
            v-model="params.target_uid"
            dense
            clearable
            class="mt-2"
            item-text="name"
            item-value="uid">
          </v-select>
        </v-col>
        <v-col cols="1">
          <v-checkbox
            v-model="draft"
            :label="$t('OdmViewer.include_draft')">
          </v-checkbox>
        </v-col>
        <v-col cols="5">
          <v-row>
            <v-radio-group
              v-model="params.stylesheet"
              :label="$t('OdmViewer.stylesheet')"
              row
              class="mt-7">
              <v-radio :label="$t('OdmViewer.blank')" value="blank" />
              <v-radio :label="$t('OdmViewer.sdtm')" value="sdtm" />
            </v-radio-group>
              <v-btn
                class="mt-7"
                dark
                small
                color="primary"
                :label="$t('_global.load')"
                @click="loadXml"
                v-show="params.target_uid && params.stylesheet">
                {{ $t('OdmViewer.load')}}
              </v-btn>
            </v-row>
        </v-col>
      </v-row>
      <v-row class="mt-0" v-else>
        <v-btn
          class="ml-2 mt-1"
          dark
          small
          color="primary"
          :label="$t('_global.load')"
          @click="clearXml"
          v-show="params.target_uid && params.stylesheet">
          {{ $t('OdmViewer.load_another')}}
        </v-btn>
        <v-btn
          fab
          small
          v-show="doc !== ''"
          color="nnGreen1"
          class="ml-4 white--text"
          :title="$t('DataTableExportButton.export_xml')"
          @click="downloadXml"
          :loading="xmlDownloadLoading"
          >
          <v-icon>mdi-file-xml-box</v-icon>
        </v-btn>
        <v-btn
          fab
          small
          v-show="doc !== ''"
          color="nnGreen1"
          class="ml-4 white--text"
          :title="$t('DataTableExportButton.export_pdf')"
          @click="downloadPdf"
          :loading="pdfDownloadLoading"
          >
          <v-icon>mdi-file-pdf-box</v-icon>
        </v-btn>
        <v-btn
          fab
          small
          v-show="doc !== ''"
          color="nnGreen1"
          class="ml-4 white--text"
          :title="$t('DataTableExportButton.export_html')"
          @click="downloadHtml"
          :loading="htmlDownloadLoading"
          >
          <v-icon>mdi-file-document</v-icon>
        </v-btn>
      </v-row>
    </v-app-bar>
    <div v-show="loading">
      <v-row align="center"
        justify="center"
        style="text-align: -webkit-center">
        <v-col cols="12" sm="4">
          <div class="text-h5">{{$t('OdmViewer.loading_message')}}</div>
          <v-progress-circular
            color="primary"
            indeterminate
            size="128"
            class="ml-4"
            />
        </v-col>
      </v-row>
    </div>
    <div v-html="doc"/>
  </div>
</template>

<script>
import crfs from '@/api/crfs'
import statuses from '@/constants/statuses'
import exportLoader from '@/utils/exportLoader'
import { DateTime } from 'luxon'

export default {
  props: {
    typeProp: String,
    elementProp: String,
    refresh: String
  },
  data () {
    return {
      elements: [],
      uri: '',
      xml: '',
      doc: '',
      params: {
        target_type: 'template',
        stylesheet: 'sdtm',
        export_to: 'v1'
      },
      loading: false,
      xmlDownloadLoading: false,
      pdfDownloadLoading: false,
      htmlDownloadLoading: false,
      type: '',
      types: [
        { name: this.$t('OdmViewer.template'), value: 'template' },
        { name: this.$t('OdmViewer.form'), value: 'form' },
        { name: this.$t('OdmViewer.item_group'), value: 'item_group' },
        { name: this.$t('OdmViewer.item'), value: 'item' }
      ],
      draft: true,
      url: ''
    }
  },
  mounted () {
    this.automaticLoad()
  },
  methods: {
    automaticLoad () {
      this.$set(this.params, 'target_type', this.$route.params.type)
      this.$set(this.params, 'target_uid', this.$route.params.uid)
      this.setElements()
      if (this.params.target_type && this.params.target_uid) {
        this.loadXml()
      }
    },
    setElements () {
      switch (this.params.target_type) {
        case 'template':
          crfs.get('templates').then((resp) => {
            this.elements = resp.data.items.filter(this.checkIfDraft)
          })
          return
        case 'form':
          crfs.get('forms').then((resp) => {
            this.elements = resp.data.items.filter(this.checkIfDraft)
          })
          return
        case 'item_group':
          crfs.get('item-groups').then((resp) => {
            this.elements = resp.data.items.filter(this.checkIfDraft)
          })
          return
        case 'item':
          crfs.get('items').then((resp) => {
            this.elements = resp.data.items.filter(this.checkIfDraft)
          })
      }
    },
    checkIfDraft (item) {
      return this.draft ? (item.status === statuses.FINAL || item.status === statuses.DRAFT) : item.status === statuses.FINAL
    },
    async loadXml () {
      this.doc = ''
      this.loading = true
      this.params.status = this.draft ? 'final&status=draft' : 'final'
      crfs.getXml(this.params).then(resp => {
        const parser = new DOMParser()
        this.xml = parser.parseFromString(resp.data, 'application/xml')
        const xsltProcessor = new XSLTProcessor()
        crfs.getXsl(this.params.stylesheet).then(resp => {
          const xmlDoc = parser.parseFromString(resp.data, 'text/xml')
          xsltProcessor.importStylesheet(xmlDoc)
          this.doc = new XMLSerializer().serializeToString(xsltProcessor.transformToDocument(this.xml))
          this.loading = false
        })
      })
      this.$router.push({
        name: 'Crfs',
        params: { tab: 'odm-viewer', type: this.params.target_type, uid: this.params.target_uid }
      })
      this.url = `${window.location.href}`
      this.$emit('clearUid')
    },
    getDownloadFileName () {
      const stylesheet = this.params.stylesheet === 'odm_template_sdtmcrf.xsl' ? '_sdtm_crf_' : '_blank_crf_'
      const templateName = this.elements.filter(el => el.uid === this.params.target_uid)[0].name
      return `${templateName + stylesheet + DateTime.local().toFormat('yyyy-MM-dd HH:mm')}`
    },
    downloadHtml () {
      this.htmlDownloadLoading = true
      exportLoader.downloadFile(this.doc, 'text/html', this.getDownloadFileName())
      this.htmlDownloadLoading = false
    },
    downloadXml () {
      this.xmlDownloadLoading = true
      crfs.getXml(this.params).then(resp => {
        exportLoader.downloadFile(resp.data, 'text/xml', this.getDownloadFileName())
        this.xmlDownloadLoading = false
      })
    },
    downloadPdf () {
      this.pdfDownloadLoading = true
      crfs.getPdf(this.params).then(resp => {
        exportLoader.downloadFile(resp.data, 'application/pdf', this.getDownloadFileName())
        this.pdfDownloadLoading = false
      })
    },
    clearXml () {
      this.doc = ''
      this.url = ''
      this.$router.push({ name: 'Crfs', params: { tab: 'odm-viewer' } })
    }
  },
  watch: {
    refresh () {
      if (this.refresh === 'odm-viewer' && this.url !== '') {
        const stateObj = { id: '100' }
        window.history.replaceState(stateObj, 'Loaded CRF', this.url)
      }
    },
    elementProp () {
      this.automaticLoad()
    },
    draft () {
      this.setElements()
    }
  }
}
</script>
