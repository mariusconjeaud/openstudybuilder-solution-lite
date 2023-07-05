<template>
<div>
  <v-tabs v-model="tab">
    <v-tab v-for="tab of tabs" :key="tab.tab" :href="tab.tab">{{ tab.name }}</v-tab>
  </v-tabs>
  <v-tabs-items
    v-model="tab"
    >
    <v-tab-item id="sponsor">
      <generic-sponsor-template-table
        ref="sponsorTable"
        key="sponsorTable"
        :headers="headers"
        v-bind="$attrs"
        v-on="$listeners"
        has-api
        @refresh="$emit('refresh')"
        :url-prefix="urlPrefix"
        :object-type="objectType"
        >
        <template v-for="(_, slot) of $scopedSlots" v-slot:[slot]="scope">
          <slot :name="slot" v-bind="scope" />
        </template>
      </generic-sponsor-template-table>
    </v-tab-item>
    <v-tab-item id="pre-instances">
      <generic-sponsor-template-table
        ref="preInstanceTable"
        key="preInstanceTable"
        :headers="headers"
        v-bind="$attrs"
        v-on="$listeners"
        has-api
        pre-instance-mode
        :url-prefix="preInstanceUrlPrefix"
        :export-object-label="preInstanceExportLabel"
        :object-type="objectType"
        >
        <template v-for="(_, slot) of $scopedSlots" v-slot:[slot]="scope">
          <slot :name="slot" v-bind="scope" />
        </template>
      </generic-sponsor-template-table>
    </v-tab-item>
    <v-tab-item id="user">
      <generic-user-template-table
        v-bind="$attrs"
        v-on="$listeners"
        />
    </v-tab-item>
  </v-tabs-items>
</div>
</template>

<script>
import Vue from 'vue'
import GenericSponsorTemplateTable from './GenericSponsorTemplateTable'
import GenericUserTemplateTable from './GenericUserTemplateTable'
import { mapActions } from 'vuex'

export default Vue.extend({
  name: 'studybuilder-template-table',
  props: {
    headers: {
      type: Array,
      default: function () {
        return [
          {
            text: '',
            value: 'actions',
            sortable: false,
            width: '5%'
          },
          { text: this.$t('_global.sequence_number'), value: 'sequence_id' },
          { text: this.$t('_global.template'), value: 'name', width: '30%', filteringName: 'name_plain' },
          { text: this.$t('_global.modified'), value: 'start_date' },
          { text: this.$t('_global.status'), value: 'status' },
          { text: this.$t('_global.version'), value: 'version' }
        ]
      }
    },
    withPreInstances: {
      type: Boolean,
      default: true
    },
    doubleBreadcrumb: {
      type: Boolean,
      default: false
    },
    urlPrefix: {
      type: String,
      default: ''
    },
    objectType: {
      type: String,
      default: ''
    }
  },
  computed: {
    preInstanceUrlPrefix () {
      return this.urlPrefix.replace('-templates', '-pre-instances')
    },
    preInstanceExportLabel () {
      let result = this.objectType.replace('Templates', '')
      if (result === 'activity') {
        result = 'activity-instruction'
      }
      return result + 'PreInstances'
    }
  },
  components: {
    GenericSponsorTemplateTable,
    GenericUserTemplateTable
  },
  mounted () {
    this.tab = this.$route.params.tab
    if (!this.doubleBreadcrumb) {
      const tabName = this.tab ? this.tabs.find(el => el.tab.substring(1) === this.tab).name : this.tabs[0].name
      setTimeout(() => {
        this.addBreadcrumbsLevel({
          text: tabName,
          index: 3,
          replace: true
        })
      }, 100)
    } else {
      setTimeout(() => {
        let tabName = ''
        if (this.tabs.find(el => el.tab.substring(1) === this.tab)) {
          tabName = this.tabs.find(el => el.tab.substring(1) === this.tab).name
        } else {
          tabName = this.tabs[0].name
        }
        this.addBreadcrumbsLevel({
          text: tabName,
          index: 4,
          replace: true
        })
      }, 100)
    }
  },
  data () {
    const tabs = [
      { tab: '#sponsor', name: this.$t('GenericTemplateTable.sponsor_tab') },
      { tab: '#user', name: this.$t('GenericTemplateTable.user_tab') }
    ]
    if (this.withPreInstances) {
      tabs.splice(1, 0, { tab: '#pre-instances', name: this.$t('GenericTemplateTable.pre_instances_tab') })
    }
    return {
      tab: null,
      tabs
    }
  },
  methods: {
    ...mapActions({
      addBreadcrumbsLevel: 'app/addBreadcrumbsLevel'
    })
  },
  watch: {
    tab (newValue) {
      const params = { ...this.$route.params }
      params.tab = newValue
      this.$router.push({
        name: this.$route.name,
        params
      })
      if (!this.doubleBreadcrumb) {
        const tabName = newValue ? this.tabs.find(el => el.tab.substring(1) === newValue).name : this.tabs[0].name
        this.addBreadcrumbsLevel({
          text: tabName,
          index: 3,
          replace: true
        })
      } else {
        let tabName = ''
        if (this.tabs.find(el => el.tab.substring(1) === newValue)) {
          tabName = this.tabs.find(el => el.tab.substring(1) === newValue).name
        } else {
          tabName = this.tabs[0].name
        }
        this.addBreadcrumbsLevel({
          text: tabName,
          index: 4,
          replace: true
        })
      }
    },
    '$route.params.tab' (newValue) {
      this.tab = newValue
    }
  }
})
</script>
