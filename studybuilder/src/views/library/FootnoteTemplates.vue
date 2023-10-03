<template>
<div class="px-4">
  <div class="page-title d-flex align-center">
    {{ $t('FootnoteTemplatesView.title') }}
    <help-button :help-text="$t('_help.FootnoteTemplatesTable.general')" />
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
      <footnote-template-table
        :key="type.term_uid"
        :footnote-type="type"
        />
    </v-tab-item>
  </v-tabs-items>
</div>
</template>

<script>
import FootnoteTemplateTable from '@/components/library/FootnoteTemplateTable'
import HelpButton from '@/components/tools/HelpButton'
import { mapActions } from 'vuex'
import terms from '@/api/controlledTerminology/terms'

export default {
  components: {
    FootnoteTemplateTable,
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
      this.footnoteTypes = resp.data.items
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
        name: 'FootnoteTemplates',
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
