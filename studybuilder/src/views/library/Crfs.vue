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
      <v-tab href="#templates">{{ $t("CrfsView.tab1_title") }}</v-tab>
      <v-tab href="#forms">{{ $t("CrfsView.tab2_title") }}</v-tab>
      <v-tab href="#item-groups">{{ $t("CrfsView.tab3_title") }}</v-tab>
      <v-tab href="#items">{{ $t("CrfsView.tab4_title") }}</v-tab>
      <v-tab href="#crf-tree">{{ $t("CrfsView.tab5_title") }}</v-tab>
      <v-tab href="#odm-viewer">{{ $t("CrfsView.tab6_title") }}</v-tab>
      <v-tab href="#alias">{{ $t("CrfsView.tab7_title") }}</v-tab>
    </v-tabs>
    <v-tabs-items v-model="tab">
      <v-tab-item id="templates">
        <crf-template-table :elementProp="{uid: uid, type: type, tab: tab}" @clearUid="clearUid"/>
      </v-tab-item>
      <v-tab-item id="forms">
        <crf-form-table :elementProp="{uid: uid, type: type, tab: tab}" @clearUid="clearUid"/>
      </v-tab-item>
      <v-tab-item id="item-groups">
        <crf-item-group-table :elementProp="{uid: uid, type: type, tab: tab}" @clearUid="clearUid"/>
      </v-tab-item>
      <v-tab-item id="items">
        <crf-item-table :elementProp="{uid: uid, type: type, tab: tab}" @clearUid="clearUid"/>
      </v-tab-item>
      <v-tab-item id="crf-tree">
        <crf-tree :refresh="tab" @redirectToPage="redirectToPage"/>
      </v-tab-item>
      <v-tab-item id="odm-viewer">
        <odm-viewer :elementProp="uid"/>
      </v-tab-item>
      <v-tab-item id="alias">
        <crf-alias-table/>
      </v-tab-item>
    </v-tabs-items>
</div>
</template>

<script>
import HelpButton from '@/components/tools/HelpButton'
import CrfTemplateTable from '@/components/library/CrfTemplateTable'
import CrfFormTable from '@/components/library/CrfFormTable'
import CrfItemGroupTable from '@/components/library/CrfItemGroupTable'
import CrfItemTable from '@/components/library/CrfItemTable'
import CrfTree from '@/components/library/CrfTree'
import OdmViewer from '@/components/library/OdmViewer'
import CrfAliasTable from '@/components/library/CrfAliasTable'

export default {
  components: {
    HelpButton,
    CrfTemplateTable,
    CrfFormTable,
    CrfItemGroupTable,
    CrfItemTable,
    CrfTree,
    OdmViewer,
    CrfAliasTable
  },
  data () {
    return {
      tab: 1,
      type: '',
      uid: ''
    }
  },
  mounted () {
    this.tab = this.$route.params.tab
    this.type = this.$route.params.type
    this.uid = this.$route.params.uid
  },
  methods: {
    redirectToPage (data) {
      this.uid = data.uid
      this.type = data.type
      this.tab = data.tab
    },
    clearUid () {
      this.uid = null
      this.type = null
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
    }
  }
}
</script>
