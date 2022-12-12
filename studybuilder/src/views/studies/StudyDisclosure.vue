<template>
<div>
  <v-tabs v-model="tab">
    <v-tab href="#tab-0">{{ $t('Sidebar.study.cdisc_ctr') }}</v-tab>
    <v-tab href="#tab-1">{{ $t('Sidebar.study.clinical_trials_gov') }}</v-tab>
    <v-tab href="#tab-2">{{ $t('Sidebar.study.eudra_ct') }}</v-tab>
    <v-tab href="#tab-3">{{ $t('Sidebar.study.who_ictrp') }}</v-tab>
  </v-tabs>
  <v-tabs-items v-model="tab">
    <v-tab-item id="tab-0">
      <UnderConstruction />
    </v-tab-item>
    <v-tab-item id="tab-1">
       <UnderConstruction />
    </v-tab-item>
     <v-tab-item id="tab-2">
       <UnderConstruction />
    </v-tab-item>
     <v-tab-item id="tab-3">
       <UnderConstruction />
    </v-tab-item>
  </v-tabs-items>
</div>
</template>

<script>
import UnderConstruction from '../../components/layout/UnderConstruction.vue'

export default {
  components: {

    UnderConstruction
  },
  data () {
    return {
      tab: null
    }
  },
  mounted () {
    this.tab = localStorage.getItem('templatesTab') || 'tab-0'
  },
  watch: {
    tab (value) {
      localStorage.setItem('templatesTab', value)
    }
  }
}
</script>
