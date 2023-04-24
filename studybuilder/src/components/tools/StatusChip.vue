<template>
<v-chip :color="color" :outlined="outlined" :dark="!outlined">{{ status }}</v-chip>
</template>

<script>
import statuses from '@/constants/statuses'

export default {
  props: {
    status: String,
    outlined: {
      type: Boolean,
      default: true
    }
  },
  computed: {
    color () {
      if (this.status === statuses.FINAL || this.status === statuses.STUDY_DRAFT) {
        return 'green'
      }
      if (this.status === statuses.RETIRED) {
        return 'orange'
      }
      if (this.status === statuses.RELEASED) {
        return 'info'
      }
      if (this.status === statuses.STUDY_LOCKED) {
        return 'red'
      }
      return 'secondary'
    }
  }
}
</script>
