<template>
<div class="px-4">
    <div class="d-flex page-title">
      {{ $t("CrfsView.title") }}
      <help-button
        :title="$t('_global.definition')"
        :help-text="$t('HelpMessages.crfs')"
      />
    </div>
    <v-tabs v-model="tab">
      <v-tab v-for="tab of tabs" :key="tab.tab" :href="tab.tab"><v-icon v-if="tab.icon" :color="tab.iconColor" class="mr-1">{{ tab.icon }}</v-icon>{{ tab.name }}</v-tab>
    </v-tabs>
    <v-tabs-items v-model="tab">
      <v-tab-item id="templates">
        <crf-template-table :elementProp="{uid: uid, type: type, tab: tab}" @clearUid="clearUid"/>
      </v-tab-item>
      <v-tab-item id="forms">
        <crf-form-table :elementProp="{uid: uid, type: type, tab: tab}" @clearUid="clearUid" @updateForm="updateElement"/>
      </v-tab-item>
      <v-tab-item id="item-groups">
        <crf-item-group-table :elementProp="{uid: uid, type: type, tab: tab}" @clearUid="clearUid" @updateItemGroup="updateElement"/>
      </v-tab-item>
      <v-tab-item id="items">
        <crf-item-table :elementProp="{uid: uid, type: type, tab: tab}" @clearUid="clearUid" @updateItem="updateElement"/>
      </v-tab-item>
      <v-tab-item id="crf-tree">
        <crf-tree :refresh="tab" @redirectToPage="redirectToPage" :updatedElement="updatedElement"/>
      </v-tab-item>
      <v-tab-item id="odm-viewer">
        <odm-viewer :elementProp="uid" @clearUid="clearUid" :refresh="tab"/>
      </v-tab-item>
      <v-tab-item id="alias">
        <crf-alias-table/>
      </v-tab-item>
      <v-tab-item id="extensions">
        <crf-extensions-table/>
      </v-tab-item>
    </v-tabs-items>
</div>
</template>

<script>
import HelpButton from '@/components/tools/HelpButton'
import CrfTemplateTable from '@/components/library/crfs/CrfTemplateTable'
import CrfFormTable from '@/components/library/crfs/CrfFormTable'
import CrfItemGroupTable from '@/components/library/crfs/CrfItemGroupTable'
import CrfItemTable from '@/components/library/crfs/CrfItemTable'
import CrfTree from '@/components/library/crfs/CrfTree'
import OdmViewer from '@/components/library/crfs/OdmViewer'
import CrfAliasTable from '@/components/library/crfs/CrfAliasTable'
import CrfExtensionsTable from '@/components/library/crfs/CrfExtensionsTable'
import { mapActions } from 'vuex'

export default {
  components: {
    HelpButton,
    CrfTemplateTable,
    CrfFormTable,
    CrfItemGroupTable,
    CrfItemTable,
    CrfTree,
    OdmViewer,
    CrfAliasTable,
    CrfExtensionsTable
  },
  data () {
    return {
      tab: 1,
      type: '',
      uid: '',
      updatedElement: {},
      tabs: [
        { tab: '#templates', name: this.$t('CrfsView.tab1_title'), icon: 'mdi-alpha-t-circle-outline', iconColor: 'crfTemplate' },
        { tab: '#forms', name: this.$t('CrfsView.tab2_title'), icon: 'mdi-alpha-f-circle-outline', iconColor: 'crfForm' },
        { tab: '#item-groups', name: this.$t('CrfsView.tab3_title'), icon: 'mdi-alpha-g-circle-outline', iconColor: 'crfGroup' },
        { tab: '#items', name: this.$t('CrfsView.tab4_title'), icon: 'mdi-alpha-i-circle-outline', iconColor: 'crfItem' },
        { tab: '#crf-tree', name: this.$t('CrfsView.tab5_title') },
        { tab: '#odm-viewer', name: this.$t('CrfsView.tab6_title') },
        { tab: '#alias', name: this.$t('CrfsView.tab7_title') },
        { tab: '#extensions', name: this.$t('CrfsView.tab8_title') }
      ]
    }
  },
  mounted () {
    this.tab = this.$route.params.tab
    this.type = this.$route.params.type
    this.uid = this.$route.params.uid
    const tabName = this.tab ? this.tabs.find(el => el.tab.substring(1) === this.tab).name : this.tabs[0].name
    setTimeout(() => {
      this.addBreadcrumbsLevel({
        text: tabName,
        to: { name: 'StudyProperties', params: { tab: tabName } },
        index: 3,
        replace: true
      })
    }, 100)
  },
  methods: {
    ...mapActions({
      addBreadcrumbsLevel: 'app/addBreadcrumbsLevel'
    }),
    redirectToPage (data) {
      this.uid = data.uid
      this.type = data.type
      this.tab = data.tab
    },
    clearUid () {
      this.uid = null
      this.type = null
    },
    updateElement (element) {
      this.updatedElement = element
    }
  },
  watch: {
    tab (newValue) {
      const params = { tab: newValue }
      if (this.uid && this.type) {
        params.type = this.type
        params.uid = this.uid
      }
      this.$router.push({
        name: 'Crfs',
        params: params
      })
      const tabName = newValue ? this.tabs.find(el => el.tab.substring(1) === newValue).name : this.tabs[0].name
      this.addBreadcrumbsLevel({
        text: tabName,
        index: 3,
        replace: true
      })
    }
  }
}
</script>
