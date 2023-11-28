import { bus } from '@/main'
import { UserManager } from 'oidc-client-ts'
import roles from '@/constants/roles'
import { Buffer } from 'buffer'

let manager = null

const authInterface = {
  validateAccess: function (to, from, next) {
    manager.getUser().then(user => {
      if (!user || user.expired) {
        if (to.name !== 'Login') {
          sessionStorage.setItem('next', to.name)
          sessionStorage.setItem('nextParams', JSON.stringify(to.params))
        }
        manager.signinRedirect()
      }
    })
  },
  oauthLoginCallback: function () {
    return manager.signinRedirectCallback().then(() => {
      bus.$emit('userSignedIn')
    })
  },
  clear: function () {
    manager.clearStaleState()
  },
  getAccessToken: function () {
    return manager.getUser().then(user => {
      if (!user) {
        return null
      }
      return user.access_token
    })
  },
  getUserInfo: function () {
    return manager.getUser()
      .then(user => {
        if (!user || user.expired) {
          return null
        }
        return JSON.parse(Buffer.from(user.access_token.split('.')[1], 'base64').toString())
      })
  },
  oauthLogout: async function () {
    return manager.signoutRedirect()
  }
}

export default {
  async install (Vue, options) {
    manager = new UserManager({
      metadataUrl: Vue.prototype.$config.OAUTH_METADATA_URL,
      authority: 'studybuilder-frontend',
      client_id: Vue.prototype.$config.OAUTH_UI_APP_ID,
      redirect_uri: location.origin + '/oauth-callback',
      response_type: 'code',
      response_mode: 'fragment',
      post_logout_redirect_uri: location.origin,
      scope: `openid profile email offline_access api://${Vue.prototype.$config.OAUTH_API_APP_ID}/API.call`
    })
    Vue.prototype.$auth = authInterface
    Vue.prototype.$roles = roles
  }
}
