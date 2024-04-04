<template>
  <div>
    <n-n-table
      :headers="headers"
      :items="items"
      :options.sync="options"
      :server-items-length="total"
      has-api
      hide-default-switches
      column-data-resource="projects"
      @filter="fetchProjects"
      item-key="project_number">
      <template v-slot:actions="">
      <slot name="extraActions"></slot>
      <v-btn
        fab
        dark
        small
        color="primary"
        data-cy="add-project"
        @click.stop="showForm"
        :title="$t('ProjectForm.title')"
        >
        <v-icon dark>
          mdi-plus
        </v-icon>
      </v-btn>
    </template>
    </n-n-table>
    <project-form
      :open="showProjectForm"
      @close="closeForm"/>
</div>
</template>

<script>
import NNTable from '@/components/tools/NNTable'
import projects from '@/api/projects'
import ProjectForm from '@/components/library/ProjectForm'
import filteringParameters from '@/utils/filteringParameters'

export default {
  components: {
    NNTable,
    ProjectForm
  },
  data () {
    return {
      headers: [
        { text: this.$t('Projects.name'), value: 'name' },
        { text: this.$t('Projects.project_number'), value: 'project_number' },
        { text: this.$t('Projects.clinical_programme'), value: 'clinical_programme.name' },
        { text: this.$t('Projects.description'), value: 'description' }
      ],
      items: [],
      options: {},
      total: 0,
      filters: '',
      showProjectForm: false
    }
  },
  methods: {
    fetchProjects (filters, sort, filtersUpdated) {
      if (!filters && this.filters) {
        filters = this.filters
      }
      const params = filteringParameters.prepareParameters(
        this.options, filters, sort, filtersUpdated)
      this.filters = filters
      projects.get(params).then(resp => {
        this.items = resp.data.items
        this.total = resp.data.total
      })
    },
    showForm () {
      this.showProjectForm = true
    },
    closeForm () {
      this.showProjectForm = false
      this.fetchProjects()
    }
  },
  watch: {
    options () {
      this.fetchProjects()
    }
  }
}
</script>
