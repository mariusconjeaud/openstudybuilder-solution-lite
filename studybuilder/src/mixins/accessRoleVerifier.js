import { mapGetters } from 'vuex'

export const accessGuard = {

  computed: {
    ...mapGetters({
      userInfo: 'auth/userInfo'
    })
  },
  methods: {
    checkPermission (permission) {
      if (this.$config.OAUTH_ENABLED) {
        return this.userInfo.roles.includes(permission)
      }
      return true
    }
  }
}
