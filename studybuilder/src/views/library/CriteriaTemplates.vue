<template>
<div class="px-4">
  <div class="page-title d-flex align-center">
    {{ $t('CriteriaTemplatesView.title') }}
    <help-button :help-text="$t('_help.CriteriaTemplatesTable.general')" />
  </div>
  <v-tabs v-model="tab">
    <v-tab
      v-for="type in criteriaTypes"
      :key="type.term_uid"
      :href="`#${type.sponsor_preferred_name}`"
      >
      {{ type.sponsor_preferred_name }}
    </v-tab>
  </v-tabs>
  <v-tabs-items v-model="tab">
    <v-tab-item
      v-for="type in criteriaTypes"
      :key="type.term_uid"
      :id="type.sponsor_preferred_name"
      >
      <criteria-template-table
        :key="type.term_uid"
        :criteria-type="type"
        />
    </v-tab-item>
  </v-tabs-items>
</div>
</template>

<script>
import CriteriaTemplateTable from '@/components/library/CriteriaTemplateTable'
import HelpButton from '@/components/tools/HelpButton'
import terms from '@/api/controlledTerminology/terms'
import { mapActions } from 'vuex'

export default {
  components: {
    CriteriaTemplateTable,
    HelpButton
  },
  data () {
    return {
      criteriaTypes: [],
      tab: null
    }
  },
  mounted () {
    terms.getByCodelist('criteriaTypes').then(resp => {
      this.criteriaTypes = resp.data.items
      this.criteriaTypes.forEach(type => {
        type.sponsor_preferred_name = type.sponsor_preferred_name.replace(' Criteria', '')
      })
    })
    this.tab = this.$route.params.type
    setTimeout(() => {
      this.addBreadcrumbsLevel({
        text: this.tab,
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
      const params = { ...this.$route.params }
      params.type = newValue
      this.$router.push({
        name: 'CriteriaTemplates',
        params
      })
      this.addBreadcrumbsLevel({
        text: newValue,
        index: 3,
        replace: true
      })
    },
    '$route.params.type' (newValue) {
      this.tab = newValue
    }
  }
}
</script>

<style scoped>
.v-tabs-items {
  min-height: 50vh;
}
</style>
