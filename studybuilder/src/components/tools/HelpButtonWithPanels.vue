<template>
<v-menu
  :close-on-click="false"
  :close-on-content-click="false"
  max-height="800px"
  max-width="500px"
  offset-y
  v-model="open"
  content-class="right">
  <template v-slot:activator="{ on, attrs }">
    <div>
      <v-btn
        icon
        v-bind="attrs"
        v-on="on"
        color="primary">
        <v-icon>mdi-help-circle-outline</v-icon>
      </v-btn>
    </div>
  </template>
  <v-card max-width="500px">
    <v-card-title class="dialog-title">{{ $t('_global.online_help') }}
      <v-spacer/>
      <v-btn
        color="secondary"
        @click="open = false"
        icon
        >
      <v-icon>mdi-close</v-icon>
    </v-btn>
    </v-card-title>
    <v-divider/>
    <v-list>
      <template>
        <v-list-item>
          <v-list-item-content>
            <v-expansion-panels>
              <v-expansion-panel v-for="item in items" :key="item.key || item">
                <v-expansion-panel-header>
                  {{ getItemLabel(item) }}
                </v-expansion-panel-header>
                <v-expansion-panel-content>
                  <div v-html="getItemHelp(item)"/>
                </v-expansion-panel-content>
              </v-expansion-panel>
            </v-expansion-panels>
          </v-list-item-content>
        </v-list-item>
        </template>
    </v-list>
  </v-card>
</v-menu>
</template>

<script>
export default {
  components: {},
  props: {
    items: Array
  },
  data () {
    return {
      open: false
    }
  },
  methods: {
    getItemLabel (item) {
      if (typeof item === 'string') {
        return this.$t(item)
      }
      return this.$t(item.key)
    },
    getItemHelp (item) {
      if (typeof item === 'string') {
        return this.$t(`_help.${item}`)
      }
      return this.$t(`_help.${item.key}`, item.context())
    }
  }
}
</script>
<style>
.right{
  right: 10px;
  left: auto !important;
}
</style>
