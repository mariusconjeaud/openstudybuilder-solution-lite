<template>
<div>
  <v-tabs v-model="tab">
    <v-tab v-for="tab of tabs" :key="tab.tab" :href="tab.tab">{{ tab.name }}</v-tab>
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
  </v-tabs-items>
</div>
</template>

<script>
import UnderConstruction from '../../components/layout/UnderConstruction.vue'
import { mapActions } from 'vuex'

export default {
  components: {

    UnderConstruction
  },
  data () {
    return {
      tab: null,
      tabs: [
        { tab: '#tab-0', name: this.$t('Sidebar.study.blank_crf') },
        { tab: '#tab-1', name: this.$t('Sidebar.study.cdash_crf') },
        { tab: '#tab-2', name: this.$t('Sidebar.study.sdtm_crf') }
      ]
    }
  },
  mounted () {
    this.tab = localStorage.getItem('templatesTab') || 'tab-0'
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
    tab (value) {
      localStorage.setItem('templatesTab', value)
      const tabName = value ? this.tabs.find(el => el.tab.substring(1) === value).name : this.tabs[0].name
      this.addBreadcrumbsLevel({
        text: tabName,
        index: 3,
        replace: true
      })
    }
  }
}
</script>
