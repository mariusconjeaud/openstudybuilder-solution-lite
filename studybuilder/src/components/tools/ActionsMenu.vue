<template>
<v-menu
  offset-y
  v-if="item && checkActionsPermissions">
  <template v-slot:activator="{ on, attrs }">
    <div>
      <v-btn
        data-cy="table-item-action-button"
        v-if="!badge"
        icon
        plain
        v-bind="attrs"
        v-on="on"
        class="pb-3"
        >
        <v-icon>mdi-dots-vertical</v-icon>
      </v-btn>
      <v-badge
        v-else
        bordered
        :color="badge.color"
        :icon="badge.icon"
        overlap
        >
        <v-btn
          icon
          v-bind="attrs"
          v-on="on"
          class="pb-3"
          >
          <v-icon>mdi-dots-vertical</v-icon>
        </v-btn>
      </v-badge>
    </div>
  </template>
  <v-list>
    <template v-for="(action, index) in actions">
      <v-list-item
        v-if="action.condition === undefined || action.condition(item)"
        @click="action.click(item, source)"
        :key="index"
        :disabled="action.accessRole && !checkPermission(action.accessRole)"
        >
        <v-list-item-icon>
          <v-icon v-if="action.iconColor" :color="action.iconColor">{{ action.icon }}</v-icon>
          <v-icon v-else-if="action.iconColorFunc" :color="action.iconColorFunc(item)">{{ action.icon }}</v-icon>
          <v-icon v-else>{{ action.icon }}</v-icon>
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title :data-cy=action.label>{{ action.label }}</v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </template>
  </v-list>
</v-menu>
</template>

<script>
import { accessGuard } from '@/mixins/accessRoleVerifier'

export default {
  mixins: [accessGuard],
  props: {
    actions: Array,
    item: Object,
    source: String,
    badge: {
      type: Object,
      required: false
    },
    accessRole: String
  },
  computed: {
    checkActionsPermissions () {
      return this.accessRole ? this.checkPermission(this.accessRole) : true
    }
  }
}
</script>
