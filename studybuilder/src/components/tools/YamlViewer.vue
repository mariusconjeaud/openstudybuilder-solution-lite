<template>
<div>
  <div class="d-flex ma-4">
    <v-text-field
      v-model="search"
      :label="$t('YamlViewer.search_content')"
      append-icon="mdi-magnify"
      hide-details
      clearable
      class="search-input"
      ></v-text-field>
  </div>

  <v-treeview
    :items="yamlTree"
    :search="search"
    dense
    open-on-click
    transition
    />
</div>
</template>

<script>
import YAML from 'yaml'

export default {
  props: {
    content: String
  },
  data () {
    return {
      search: null,
      yamlTree: null
    }
  },
  methods: {
    renderTreeView (obj, index) {
      const retValue = []

      if (!index) {
        index = 0
      }
      for (const key in obj) {
        index += 1
        if (typeof obj[key] === 'object') {
          retValue.push({ id: index, name: key, children: this.renderTreeView(obj[key], index) })
        } else {
          if (!isNaN(key)) {
            retValue.push({ id: index, name: obj[key] })
          } else {
            retValue.push({ id: index, name: key, children: [{ id: index, name: obj[key] }] })
          }
        }
      }
      this.yamlTree = retValue
      return retValue
    }
  },
  watch: {
    content: {
      handler (value) {
        if (value) {
          const parsed = YAML.parse(value)
          this.renderTreeView(parsed)
        }
      },
      immediate: true
    }
  }
}
</script>

<style lang="scss" scoped>
.search-input {
  min-width: 200px;
  max-width: 400px;
}
</style>
