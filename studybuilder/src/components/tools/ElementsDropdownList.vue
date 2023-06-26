<template>
<div>
  <v-row v-if="editMode">
    <v-select
      v-model="element"
      :items="studyElements"
      label="Element"
      item-text="name"
      item-value="element_uid"
      dense
      clearable
      class="mt-6 cellWidth"
      @input="updateElement"
      @click:clear="deleteElement"/>
  </v-row>
  <div v-else>
    <v-tooltip bottom>
      <template v-slot:activator="{ on, attrs }">
        <span
          v-bind="attrs"
          v-on="on">
          {{ getElementShortName(element) }}</span>
      </template>
        <span>{{ getElementName(element) }}</span>
    </v-tooltip>
  </div>
</div>
</template>
<script>
import { mapGetters } from 'vuex'

export default {
  components: {},
  props: {
    epoch: String,
    arm: String,
    armBranch: String,
    studyElements: Array,
    cells: Object,
    editMode: Boolean,
    saveObject: Boolean
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy'
    })
  },
  data () {
    return {
      element: '',
      cell: {},
      data: {}
    }
  },
  methods: {
    updateElement () {
      if (this.cell && this.element) {
        this.data = {
          method: 'PATCH',
          content: {
            study_element_uid: this.element,
            study_design_cell_uid: this.cell.design_cell_uid
          }
        }
        this.armBranch ? this.data.study_branch_arm_uid = this.armBranch : this.data.study_arm_uid = this.arm
      } else if (this.element) {
        this.data = {
          method: 'POST',
          content: {
            study_arm_uid: this.arm,
            study_epoch_uid: this.epoch,
            study_element_uid: this.element,
            study_branch_arm_uid: this.armBranch
          }
        }
      }
    },
    deleteElement () {
      if (this.cell) {
        this.data = {
          method: 'DELETE',
          content: {
            uid: this.cell.design_cell_uid
          }
        }
        this.cell = undefined
      }
    },
    findCell (cell) {
      return (cell.study_epoch_uid === this.epoch && (cell.study_arm_uid ? (cell.study_arm_uid === this.arm) : (cell.study_branch_arm_uid === this.armBranch)))
    },
    getElementShortName (elementUid) {
      const element = this.studyElements.find(el => el.element_uid === elementUid)
      return element ? element.short_name : ''
    },
    getElementName (elementUid) {
      const element = this.studyElements.find(el => el.element_uid === elementUid)
      return element ? element.name : ''
    }
  },
  mounted () {
    this.cell = this.cells.data.find(this.findCell)
    if (this.cell) {
      this.element = this.cell.study_element_uid
    }
  },
  watch: {
    saveObject (value) {
      if (value) {
        this.$emit('addToObject', this.data)
        this.data = {}
      }
    }
  }

}
</script>
<style scoped>
  .cellWidth {
    max-width: 250px;
  }
</style>
