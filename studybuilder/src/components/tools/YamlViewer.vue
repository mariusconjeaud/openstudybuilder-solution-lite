<template>
<div>
  <div class="d-flex align-end mb-4">
    <v-text-field
      v-model="search"
      :label="$t('YamlViewer.search_content')"
      append-icon="mdi-magnify"
      hide-details
      clearable
      class="search-input mr-6"
      dense
      ></v-text-field>
    <v-switch
      :label="$t('YamlViewer.expand_all')"
      @change="toggleTreeview"
      hide-details
      class="mr-auto"
      />
  </div>

  <v-treeview
    ref="tree"
    :items="yamlTree"
    :search="search"
    dense
    open-on-click
    transition
    :open-all="expanded"
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
      expanded: false,
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
    },
    toggleTreeview () {
      this.expanded = !this.expanded
      this.$refs.tree.updateAll(this.expanded)
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
