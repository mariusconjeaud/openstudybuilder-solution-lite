<template>
  <div class="mt-6 text-center">
    <h1>{{ message }}</h1>
    <v-btn class="mt-4" color="primary" @click="navigateToRoot" text>{{ $t('UnderConstruction.back_home') }}</v-btn>
  </div>
</template>

<script>
import i18n from '@/plugins/i18n'

export default {
  props: {
    message: {
      type: String,
      default: () => i18n.t('UnderConstruction.title')
    }
  },
  methods: {
    navigateToRoot () {
      this.$store.commit('app/SET_SECTION', '')
      this.$router.push('/')
    }
  }
}
</script>
