import { mapGetters } from 'vuex'

export const accessGuard = {

  computed: {
    ...mapGetters({
      userInfo: 'auth/userInfo'
    })
  },
  methods: {
    checkPermission (permission) {
      if (this.$config.AUTH_ENABLED === '1') {
        return this.userInfo.roles.includes(permission)
      }
      return true
    }
  }
}
