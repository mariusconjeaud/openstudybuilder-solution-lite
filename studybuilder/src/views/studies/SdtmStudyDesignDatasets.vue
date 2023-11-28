<template>
<div class="px-4" v-if="selectedStudyVersion === null">
  <div class="page-title d-flex align-center">
    {{ $t('Sidebar.study.sdtm_study') }}
    <help-button :help-text="$t('_help.SdtmSpecificationTable.general')" />
  </div>
  <v-tabs v-model="tab">
    <v-tab v-for="tab of tabs" :key="tab.tab" :href="tab.tab">{{ tab.name }}</v-tab>
  </v-tabs>
  <v-tabs-items v-model="tab">
    <v-tab-item id="tab-0">
      <sdtm-design-table type="TA"/>
    </v-tab-item>
    <v-tab-item id="tab-1">
      <sdtm-design-table type="TE"/>
    </v-tab-item>
    <v-tab-item id="tab-2">
      <sdtm-design-table type="TV"/>
    </v-tab-item>
    <v-tab-item id="tab-3">
      <sdtm-design-table type="TI"/>
    </v-tab-item>
    <v-tab-item id="tab-4">
      <sdtm-design-table type="TDM"/>
    </v-tab-item>
    <v-tab-item id="tab-5">
      <sdtm-design-table type="TS"/>
    </v-tab-item>
  </v-tabs-items>
</div>
<div v-else>
  <under-construction :message="$t('UnderConstruction.not_supported')"/>
</div>
</template>

<script>
import SdtmDesignTable from '@/components/studies/SdtmDesignTable'
import HelpButton from '@/components/tools/HelpButton'
import { mapActions, mapGetters } from 'vuex'
import UnderConstruction from '@/components/layout/UnderConstruction'

export default {
  components: {
    SdtmDesignTable,
    HelpButton,
    UnderConstruction
  },
  computed: {
    ...mapGetters({
      selectedStudyVersion: 'studiesGeneral/selectedStudyVersion'
    })
  },
  data () {
    return {
      tab: null,
      tabs: [
        { tab: '#tab-0', name: this.$t('SdtmDesignTable.trial_arm') },
        { tab: '#tab-1', name: this.$t('SdtmDesignTable.trial_elem') },
        { tab: '#tab-2', name: this.$t('SdtmDesignTable.trial_visits') },
        { tab: '#tab-3', name: this.$t('SdtmDesignTable.trial_incl_excl') },
        { tab: '#tab-4', name: this.$t('SdtmDesignTable.trial_disease') },
        { tab: '#tab-5', name: this.$t('SdtmDesignTable.trial_summary') }
      ]
    }
  },
  mounted () {
    this.tab = this.$route.params.tab
    const tabName = this.tab ? this.tabs.find(el => el.tab.substring(1) === this.tab).name : this.tabs[0].name
    setTimeout(() => {
      this.addBreadcrumbsLevel({
        text: tabName,
        index: 3,
        replace: true
      })
    }, 100)
  },
  methods: {
    ...mapActions({
      addBreadcrumbsLevel: 'app/addBreadcrumbsLevel'
    })
  },
  watch: {
    tab (newValue) {
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
