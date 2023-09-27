<template>
<div class="px-4">
  <div class="page-title d-flex align-center">
    {{ $t('FootnotesView.title') }}
    <help-button :help-text="$t('_help.FootnotesTable.general')" />
  </div>
  <v-tabs v-model="tab">
    <v-tab
      v-for="type in footnoteTypes"
      :key="type.term_uid"
      :href="`#${type.sponsor_preferred_name}`"
      >
      {{ type.sponsor_preferred_name }}
    </v-tab>
  </v-tabs>
  <v-tabs-items v-model="tab">
    <v-tab-item
      v-for="type in footnoteTypes"
      :key="type.term_uid"
      :id="type.sponsor_preferred_name"
      >
      <footnote-table
        :footnote-type="type"
        :key="type.refreshKey"
        />
    </v-tab-item>
  </v-tabs-items>
</div>
</template>

<script>
import FootnoteTable from '@/components/library/FootnoteTable'
import HelpButton from '@/components/tools/HelpButton'
import terms from '@/api/controlledTerminology/terms'
import { mapActions } from 'vuex'

export default {
  components: {
    FootnoteTable,
    HelpButton
  },
  data () {
    return {
      footnoteTypes: [],
      tab: null
    }
  },
  mounted () {
    terms.getByCodelist('footnoteTypes').then(resp => {
      this.footnoteTypes = resp.data.items.map(item => {
        return { ...item, refreshKey: 1 }
      })
    })
    this.tab = this.$route.params.tab
  },
  methods: {
    ...mapActions({
      addBreadcrumbsLevel: 'app/addBreadcrumbsLevel'
    })
  },
  watch: {
    tab (newValue) {
      for (const type of this.footnoteTypes) {
        if (type.sponsor_preferred_name === newValue) {
          type.refreshKey++
          break
        }
      }
      this.$router.push({
        name: 'FootnoteInstances',
        params: { tab: newValue }
      })
      this.addBreadcrumbsLevel({
        text: newValue,
        index: 3,
        replace: true
      })
    }
  }
}
</script>
