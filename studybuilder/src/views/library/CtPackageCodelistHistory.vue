<template>
<div class="px-4">
  <div class="page-title">{{ $t('CtPackageCodelistHistoryView.title') }}</div>
  <ct-package-codelist-history
    :catalogue-name="$route.params.catalogue_name"
    :codelist-uid="$route.params.codelist_id"
    :from-date="$route.query.fromDate"
    :to-date="$route.query.toDate"
    />
</div>
</template>

<script>
import { mapActions } from 'vuex'
import CtPackageCodelistHistory from '@/components/library/CtPackageCodelistHistory'

export default {
  components: {
    CtPackageCodelistHistory
  },
  methods: {
    ...mapActions({
      addBreadcrumbsLevel: 'app/addBreadcrumbsLevel'
    })
  },
  mounted () {
    this.addBreadcrumbsLevel({
      text: this.$route.params.codelist_id
    })
  }
}
</script>
