<template>
<div class="px-4">
  <div class="d-flex page-title">
    {{ $t("CompoundsView.title") }}
    <help-button
      :title="$t('_global.definition')"
      :help-text="$t('_help.CompoundsView.general')"
      />
  </div>
  <v-tabs v-model="tab">
    <v-tab v-for="tab of tabs" :key="tab.tab" :href="tab.tab">{{ tab.name }}</v-tab>
  </v-tabs>
  <v-tabs-items v-model="tab">
    <v-tab-item id="compounds">
      <compound-table :tabClickedAt="compoundsTabClickedAt" />
    </v-tab-item>
    <v-tab-item id="aliases">
      <compound-alias-table :tabClickedAt="compoundAliasesTabClickedAt" />
    </v-tab-item>
  </v-tabs-items>
</div>
</template>

<script>
import CompoundAliasTable from '@/components/library/CompoundAliasTable'
import CompoundTable from '@/components/library/CompoundTable'
import HelpButton from '@/components/tools/HelpButton'
import { mapActions } from 'vuex'

export default {
  components: {
    CompoundAliasTable,
    CompoundTable,
    HelpButton
  },
  methods: {
    ...mapActions({
      addBreadcrumbsLevel: 'app/addBreadcrumbsLevel'
    })
  },
  data () {
    return {
      tab: 1,
      compoundAliasesTabClickedAt: 0,
      compoundsTabClickedAt: 0,
      tabs: [
        { tab: '#compounds', name: this.$t('CompoundsView.tab1_title') },
        { tab: '#aliases', name: this.$t('CompoundsView.tab2_title') }
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
    }, 1100)
  },
  watch: {
    tab (newValue) {
      switch (newValue) {
        case 'compounds':
          this.compoundsTabClickedAt = Date.now()
          break
        case 'aliases':
          this.compoundAliasesTabClickedAt = Date.now()
          break
      }
      this.$router.push({
        name: 'Compounds',
        params: { tab: newValue }
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
