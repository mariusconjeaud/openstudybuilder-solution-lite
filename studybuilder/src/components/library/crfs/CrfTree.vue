<template>
<div>
  <v-row>
    <v-switch class="ml-6 mt-6" v-if="!loading" v-model="sortMode" :label="$t('CrfTree.reorder')"/>
  </v-row>
  <v-data-table
    ref="templatesTable"
    :headers="headers"
    item-key="uid"
    :options.sync="options"
    :server-items-length="total"
    :items="templates"
    export-data-url="concepts/odms/templates"
    show-expand
    light
    class="mt-5 tableMinWidth"
    :loading="loading"
    hide-default-header
    width="100%"
    :expanded="templatesExpand"
    sort-by="name"
    >
    <template v-slot:header="{ props: { headers } }">
      <thead>
        <tr>
          <th v-for="header in headers" v-bind:key="header.value" scope="col">
            <span>{{ header.text }}</span>
          </th>
        </tr>
      </thead>
    </template>
    <template v-slot:item="{ item, expand, isExpanded }">
      <tr style="background-color: var(--v-dfltBackgroundLight1-base)">
        <td width="1%">
          <v-btn @click="expand(!isExpanded), collapseTemplate(item)" v-if="isExpanded" icon>
            <v-icon dark>
              mdi-chevron-down
            </v-icon>
          </v-btn>
          <v-btn @click="expand(!isExpanded), expandTemplate(item)" v-else-if="!loading && item.forms.length > 0" icon>
            <v-icon dark>
              mdi-chevron-right
            </v-icon>
          </v-btn>
        </td>
        <td width="30%">
          <v-row>
            <div class="mt-3"><actions-menu :actions="actions" :item="item"/></div>
            <v-icon color="crfTemplate">mdi-alpha-t-circle</v-icon>
            <v-tooltip bottom>
              <template v-slot:activator="{ on, attrs }">
                <div class="mt-3 ml-1 mr-1" v-bind="attrs" v-on="on">{{ item.name.length > 40 ? item.name.substring(0, 40) + '...' : item.name }}</div>
              </template>
              <span>{{ item.name }}</span>
            </v-tooltip>
          </v-row>
        </td>
        <td width="10%"></td>
        <td width="10%"></td>
        <td width="15%"><status-chip :status="item.status" /></td>
        <td width="20%">{{ item.version }}</td>
        <td width="10%">
          <v-menu
            offset-y
            v-if="item.status !== statuses.FINAL"
            >
            <template v-slot:activator="{ on, attrs }">
              <div>
                <v-btn
                  width="150px"
                  dark
                  small
                  rounded
                  v-bind="attrs"
                  v-on="on"
                  color="crfForm"
                  :title="$t('CrfTree.link_forms')"
                  v-show="item.status !== statuses.FINAL"
                  >
                  <v-icon dark>
                    mdi-plus
                  </v-icon>
                  {{ $t('CrfTree.forms') }}
                </v-btn>
              </div>
            </template>
            <v-list>
              <v-list-item @click="openForm(item, 'forms')">
                <v-list-item-icon>
                  <v-icon>mdi-plus</v-icon>
                </v-list-item-icon>
                <v-list-item-content>
                  {{ $t('CrfTree.link_existing')}}
                </v-list-item-content>
              </v-list-item>
              <v-list-item @click="openFormsForm(item)">
                <v-list-item-icon>
                  <v-icon>mdi-pencil</v-icon>
                </v-list-item-icon>
                <v-list-item-content>
                  {{ $t('CrfTree.create_and_link')}}
                </v-list-item-content>
              </v-list-item>
            </v-list>
          </v-menu>
          <v-btn
            v-else
            width="150px"
            rounded
            dark
            small
            class="hide"
            >
          </v-btn>
        </td>
      </tr>
    </template>
    <template v-slot:expanded-item="{ headers, item }">
      <td :colspan="headers.length" class="pa-0">
        <v-data-table
          ref="formsTable"
          :headers="headers"
          :items="getForms(item)"
          item-key="uid"
          light
          hide-default-footer
          hide-default-header
          show-expand
          :expanded="formsExpand"
          sort-by="order_number"
          :key="formsTableKey"
          :items-per-page="-1"
          >
          <template v-slot:item="{ item, expand, isExpanded }">
            <tr style="background-color: var(--v-dfltBackgroundLight2-base)">
              <td width="1%">
                <v-btn @click="expand(!isExpanded), collapseForm(item)" v-if="isExpanded" icon>
                  <v-icon dark>
                    mdi-chevron-down
                  </v-icon>
                </v-btn>
                <v-btn @click="expand(!isExpanded), expandForm(item)" v-else-if="item.item_groups && item.item_groups.length > 0" icon>
                  <v-icon dark>
                    mdi-chevron-right
                  </v-icon>
                </v-btn>
                <v-btn v-else-if="!item.item_groups || item.item_groups.length == 0" icon/>
              </td>
              <td width="30%">
                <v-row>
                  <v-btn
                    class="mt-4 ml-3"
                    icon x-small
                    v-if="sortMode"
                    @click="reorderContent(item, -1)">
                    <v-icon>
                      mdi-arrow-up
                    </v-icon>
                  </v-btn>
                  <v-btn
                    class="mt-4"
                    icon
                    x-small
                    v-if="sortMode"
                    @click="reorderContent(item, 1)">
                    <v-icon>
                      mdi-arrow-down
                    </v-icon>
                  </v-btn>
                  <div class="ml-2 mt-3"><actions-menu :actions="actions" :item="item"/></div>
                  <v-icon color="crfForm">mdi-alpha-f-circle</v-icon>
                  <v-tooltip bottom>
                    <template v-slot:activator="{ on, attrs }">
                      <div class="mt-3 ml-1 mr-1" v-bind="attrs" v-on="on">{{ item.name.length > 40 ? item.name.substring(0, 40) + '...' : item.name }}</div>
                    </template>
                    <span>{{ item.name }}</span>
                  </v-tooltip>
                </v-row>
              </td>
              <td width="10%">
                <v-tooltip bottom>
                  <template v-slot:activator="{ on, attrs }">
                    <v-icon
                      color="darkGrey"
                      v-bind="attrs"
                      v-on="on"
                      v-if="item.locked === 'Yes'">
                        mdi-lock
                    </v-icon>
                  </template>
                  <span>{{ $t('CrfTree.locked') }}</span>
                </v-tooltip>
                <v-tooltip bottom>
                  <template v-slot:activator="{ on, attrs }">
                    <v-icon
                      color="darkGrey"
                      v-bind="attrs"
                      v-on="on"
                      v-if="item.mandatory === 'Yes'">
                        mdi-database-lock
                    </v-icon>
                  </template>
                  <span>{{ $t('CrfTree.mandatory') }}</span>
                </v-tooltip>
              </td>
              <td width="10%">
                <v-tooltip bottom
                    v-if="item.repeating === 'Yes'">
                  <template v-slot:activator="{ on, attrs }">
                    <v-icon
                      color="darkGrey"
                      v-bind="attrs"
                      v-on="on">
                        mdi-repeat
                    </v-icon>
                  </template>
                  <span>{{ $t('CrfTree.repeating') }}</span>
                </v-tooltip>
              </td>
              <td width="15%"><status-chip :status="item.status" /></td>
              <td width="20%">{{ item.version }}</td>
              <td width="10%">
                <v-menu
                  offset-y
                  v-if="item.status !== statuses.FINAL"
                  >
                  <template v-slot:activator="{ on, attrs }">
                    <div>
                      <v-btn
                        width="150px"
                        rounded
                        dark
                        small
                        v-bind="attrs"
                        v-on="on"
                        color="crfGroup"
                        :title="$t('CrfTree.link_item_groups')"
                        v-show="item.status !== statuses.FINAL"
                        >
                        <v-icon dark>
                          mdi-plus
                        </v-icon>
                        {{ $t('CrfTree.item_groups') }}
                      </v-btn>
                    </div>
                  </template>
                  <v-list>
                    <v-list-item @click="openForm(item, 'item-groups')">
                      <v-list-item-icon>
                        <v-icon>mdi-plus</v-icon>
                      </v-list-item-icon>
                      <v-list-item-content>
                        {{ $t('CrfTree.link_existing')}}
                      </v-list-item-content>
                    </v-list-item>
                    <v-list-item @click="openItemGroupForm(item)">
                      <v-list-item-icon>
                        <v-icon>mdi-pencil</v-icon>
                      </v-list-item-icon>
                      <v-list-item-content>
                        {{ $t('CrfTree.create_and_link')}}
                      </v-list-item-content>
                    </v-list-item>
                  </v-list>
                </v-menu>
                <v-btn
                  v-else
                  width="150px"
                  rounded
                  dark
                  small
                  class="hide"
                  >
                </v-btn>
              </td>
            </tr>
          </template>
          <template v-slot:expanded-item="{ headers, item }">
            <td :colspan="headers.length" class="pa-0">
              <v-data-table
                class="elevation-0"
                :headers="headers"
                :items="item.item_groups ? (expandedGroups.find(group => group.formUid === item.uid ) ? expandedGroups.find(group => group.formUid === item.uid ).groups : []) : []"
                item-key="uid"
                light
                hide-default-footer
                hide-default-header
                show-expand
                :expanded="groupsExpand"
                sort-by="order_number"
                :key="groupsTableKey"
                :items-per-page="-1"
                >
                <template v-slot:item="{ item, expand, isExpanded }">
                  <tr style="background-color: var(--v-dfltBackground-base)">
                    <td width="1%">
                      <v-btn @click="expand(!isExpanded), collapseGroup(item)" v-if="isExpanded" icon>
                        <v-icon dark>
                          mdi-chevron-down
                        </v-icon>
                      </v-btn>
                      <v-btn @click="expand(!isExpanded), expandGroup(item)" v-else-if="item.items && item.items.length > 0" icon>
                        <v-icon dark>
                          mdi-chevron-right
                        </v-icon>
                      </v-btn>
                      <v-btn v-else-if="!item.item_groups || item.item_groups.length == 0" icon/>
                    </td>
                    <td width="30%" class="pl-0">
                      <v-row>
                        <v-btn
                          class="mt-4 ml-7"
                          icon x-small
                          v-if="sortMode"
                          @click="reorderContent(item, -1)">
                          <v-icon>
                            mdi-arrow-up
                          </v-icon>
                        </v-btn>
                        <v-btn
                          class="mt-4"
                          icon
                          x-small
                          v-if="sortMode"
                          @click="reorderContent(item, 1)">
                          <v-icon>
                            mdi-arrow-down
                          </v-icon>
                        </v-btn>
                        <div class="mt-3 ml-8"><actions-menu :actions="actions" :item="item"/></div>
                        <v-icon color="crfGroup">mdi-alpha-g-circle</v-icon>
                        <v-tooltip bottom>
                          <template v-slot:activator="{ on, attrs }">
                            <div class="mt-3 ml-1 mr-1" v-bind="attrs" v-on="on">{{ item.name.length > 40 ? item.name.substring(0, 40) + '...' : item.name }}</div>
                          </template>
                          <span>{{ item.name }}</span>
                        </v-tooltip>
                      </v-row>
                    </td>
                    <td width="10%">
                      <v-tooltip bottom v-if="checkIfConditionExist(item)">
                        <template v-slot:activator="{ on, attrs }">
                          <v-icon
                            color="darkGrey"
                            v-bind="attrs"
                            v-on="on">
                            mdi-alert-circle-check-outline
                          </v-icon>
                        </template>
                        <span>{{ $t('CrfTree.condition_applied') }}</span>
                      </v-tooltip>
                      <v-tooltip bottom>
                        <template v-slot:activator="{ on, attrs }">
                          <v-icon
                            color="darkGrey"
                            v-bind="attrs"
                            v-on="on"
                            v-if="item.locked === 'Yes'">
                              mdi-lock
                          </v-icon>
                        </template>
                        <span>{{ $t('CrfTree.locked') }}</span>
                      </v-tooltip>
                      <v-tooltip bottom>
                        <template v-slot:activator="{ on, attrs }">
                          <v-icon
                            color="darkGrey"
                            v-bind="attrs"
                            v-on="on"
                            v-if="item.mandatory === 'Yes'">
                              mdi-database-lock
                          </v-icon>
                        </template>
                        <span>{{ $t('CrfTree.mandatory') }}</span>
                      </v-tooltip>
                      <v-tooltip bottom>
                        <template v-slot:activator="{ on, attrs }">
                          <v-icon
                            color="darkGrey"
                            v-bind="attrs"
                            v-on="on"
                            v-if="item.vendor.attributes.length > 0">
                              mdi-toy-brick-plus
                          </v-icon>
                        </template>
                        <span>{{ $t('CrfTree.vendor_extension_applied') }}</span>
                      </v-tooltip>
                    </td>
                    <td width="10%">
                      <v-tooltip bottom
                        v-if="item.repeating === 'Yes'">
                        <template v-slot:activator="{ on, attrs }">
                          <v-icon
                            color="darkGrey"
                            v-bind="attrs"
                            v-on="on">
                              mdi-repeat
                          </v-icon>
                        </template>
                        <span>{{ $t('CrfTree.repeating') }}</span>
                      </v-tooltip>
                      <v-tooltip bottom
                        v-if="item.isReferenceData === 'Yes'">
                        <template v-slot:activator="{ on, attrs }">
                          <v-icon
                            color="darkGrey"
                            v-bind="attrs"
                            v-on="on">
                              mdi-arrow-decision-outline
                          </v-icon>
                        </template>
                        <span>{{ $t('CrfTree.ref_data') }}</span>
                      </v-tooltip>
                      <v-tooltip bottom
                        v-if="item.vendor_attributes && (item.vendor_attributes.length + item.vendor_element_attributes.length + item.vendor_elements.length) > 0">
                        <template v-slot:activator="{ on, attrs }">
                          <v-icon
                            color="darkGrey"
                            v-bind="attrs"
                            v-on="on">
                              mdi-toy-brick-plus
                          </v-icon>
                        </template>
                        <span>{{ $t('CrfTree.vendor_extension_applied') }}</span>
                      </v-tooltip>
                    </td>
                    <td width="15%"><status-chip :status="item.status" /></td>
                    <td width="20%">{{ item.version }}</td>
                    <td width="10%">
                      <v-menu
                        offset-y
                        v-if="item.status !== statuses.FINAL"
                        >
                        <template v-slot:activator="{ on, attrs }">
                          <div>
                            <v-btn
                              width="150px"
                              rounded
                              dark
                              small
                              v-bind="attrs"
                              v-on="on"
                              color="crfItem"
                              :title="$t('CrfTree.link_items')"
                              v-show="item.status !== statuses.FINAL"
                              >
                              <v-icon dark>
                                mdi-plus
                              </v-icon>
                              {{ $t('CrfTree.items')}}
                            </v-btn>
                          </div>
                        </template>
                        <v-list>
                          <v-list-item @click="openForm(item, 'items')">
                            <v-list-item-icon>
                              <v-icon>mdi-plus</v-icon>
                            </v-list-item-icon>
                            <v-list-item-content>
                              {{ $t('CrfTree.link_existing')}}
                            </v-list-item-content>
                          </v-list-item>
                          <v-list-item @click="openItemForm(item)">
                            <v-list-item-icon>
                              <v-icon>mdi-pencil</v-icon>
                            </v-list-item-icon>
                            <v-list-item-content>
                              {{ $t('CrfTree.create_and_link')}}
                            </v-list-item-content>
                          </v-list-item>
                        </v-list>
                      </v-menu>
                      <v-btn
                        v-else
                        width="150px"
                        rounded
                        dark
                        small
                        class="hide"
                        >
                      </v-btn>
                    </td>
                  </tr>
                </template>
                <template v-slot:expanded-item="{ headers, item }">
                  <td :colspan="headers.length" class="pa-0">
                    <v-data-table
                      class="elevation-0"
                      :headers="headers"
                      :items="item.items ? (expandedItems.find(it => it.groupUid === item.uid ) ? expandedItems.find(it => it.groupUid === item.uid ).items : []) : []"
                      item-key="uid"
                      sort-by="order_number"
                      light
                      hide-default-footer
                      hide-default-header
                      :key="itemsTableKey"
                      :items-per-page="-1"
                      >
                      <template v-slot:item="{ item }">
                        <tr>
                          <td width="1%">
                            <v-btn icon>
                            </v-btn>
                          </td>
                          <td width="30%" class="pl-0">
                            <v-row>
                              <v-btn
                                class="mt-4 ml-7"
                                icon x-small
                                v-if="sortMode"
                                @click="reorderContent(item, -1)">
                                <v-icon>
                                  mdi-arrow-up
                                </v-icon>
                              </v-btn>
                              <v-btn
                                class="mt-4"
                                icon
                                x-small
                                v-if="sortMode"
                                @click="reorderContent(item, 1)">
                                <v-icon>
                                  mdi-arrow-down
                                </v-icon>
                              </v-btn>
                              <div class="mt-3 ml-10"><actions-menu :actions="actions" :item="item"/></div>
                              <v-icon color="crfItem">mdi-alpha-i-circle</v-icon>
                              <v-tooltip bottom>
                                <template v-slot:activator="{ on, attrs }">
                                  <div class="mt-3 ml-1 mr-1" v-bind="attrs" v-on="on">{{ item.name.length > 40 ? item.name.substring(0, 40) + '...' : item.name }}</div>
                                </template>
                                <span>{{ item.name }}</span>
                              </v-tooltip>
                            </v-row>
                          </td>
                          <td width="10%">
                            <v-tooltip bottom v-if="checkIfConditionExist(item)">
                              <template v-slot:activator="{ on, attrs }">
                                <v-icon
                                  color="darkGrey"
                                  v-bind="attrs"
                                  v-on="on">
                                  mdi-alert-circle-check-outline
                                </v-icon>
                              </template>
                              <span>{{ $t('CrfTree.condition_applied') }}</span>
                            </v-tooltip>
                            <v-tooltip bottom>
                              <template v-slot:activator="{ on, attrs }">
                                <v-icon
                                  color="darkGrey"
                                  v-bind="attrs"
                                  v-on="on"
                                  v-if="item.locked === 'Yes'">
                                    mdi-lock
                                </v-icon>
                              </template>
                              <span>{{ $t('CrfTree.locked') }}</span>
                            </v-tooltip>
                            <v-tooltip bottom>
                              <template v-slot:activator="{ on, attrs }">
                                <v-icon
                                  color="darkGrey"
                                  v-bind="attrs"
                                  v-on="on"
                                  v-if="item.mandatory === 'Yes'">
                                    mdi-database-lock
                                </v-icon>
                              </template>
                              <span>{{ $t('CrfTree.mandatory') }}</span>
                            </v-tooltip>
                            <v-tooltip bottom>
                              <template v-slot:activator="{ on, attrs }">
                                <v-icon
                                  color="darkGrey"
                                  v-bind="attrs"
                                  v-on="on"
                                  v-if="item.vendor.attributes.length > 0">
                                    mdi-toy-brick-plus
                                </v-icon>
                              </template>
                              <span>{{ $t('CrfTree.vendor_extension_applied') }}</span>
                            </v-tooltip>
                            <v-tooltip bottom>
                              <template v-slot:activator="{ on, attrs }">
                                <v-icon
                                  color="darkGrey"
                                  v-bind="attrs"
                                  v-on="on"
                                  v-if="item.sdv === 'Yes'">
                                    mdi-source-branch-check
                                </v-icon>
                              </template>
                              <span>{{ $t('CrfTree.sdv') }}</span>
                            </v-tooltip>
                            <v-tooltip bottom>
                              <template v-slot:activator="{ on, attrs }">
                                <v-icon
                                  color="darkGrey"
                                  v-bind="attrs"
                                  v-on="on"
                                  v-if="item.data_entry_required === 'Yes'">
                                    mdi-location-enter
                                </v-icon>
                              </template>
                              <span>{{ $t('CrfTree.entry_required') }}</span>
                            </v-tooltip>
                          </td>
                          <td width="10%">
                            <v-tooltip bottom>
                              <template v-slot:activator="{ on, attrs }">
                                <v-icon
                                  color="darkGrey"
                                  v-bind="attrs"
                                  v-on="on">
                                    {{ getDataTypeIcon(item) }}
                                </v-icon>
                              </template>
                              <span>{{ item.datatype + $t('CrfTree.data_type') }}</span>
                            </v-tooltip>
                            <v-tooltip bottom
                              v-if="item.vendor_attributes && (item.vendor_attributes.length + item.vendor_element_attributes.length + item.vendor_elements.length) > 0">
                              <template v-slot:activator="{ on, attrs }">
                                <v-icon
                                  color="darkGrey"
                                  v-bind="attrs"
                                  v-on="on">
                                    mdi-toy-brick-plus
                                </v-icon>
                              </template>
                              <span>{{ $t('CrfTree.vendor_extension_applied') }}</span>
                            </v-tooltip>
                          </td>
                          <td width="15%"><status-chip :status="item.status" /></td>
                          <td width="20%">{{ item.version }}</td>
                          <td width="10%">
                            <v-btn
                              width="150px"
                              rounded
                              small
                              class="hide"
                              />
                          </td>
                        </tr>
                      </template>
                    </v-data-table>
                  </td>
                </template>
              </v-data-table>
            </td>
          </template>
        </v-data-table>
      </td>
    </template>
  </v-data-table>
  <crf-link-form
    :open="showForm"
    @close="closeForm"
    @cancel="cancelForm"
    :itemToLink="itemToLink"
    :itemsType="linkedItemsType"
    />
  <v-dialog
    v-model="conditionForm"
    persistent
    content-class="fullscreen-dialog"
    >
    <crf-condition-form
      :itemToLink="itemToLink"
      @close="closeConditionForm"
      @cancel="cancelConditionForm"
      :crfForms="forms"
      :crfGroup="currentItemGroup"
      :crfGroups="itemGroups"
      :crfItems="items"/>
  </v-dialog>
  <crf-template-form
    :open="showTemplateForm"
    @close="closeTemplateForm"
    :selectedTemplate="elementToEdit"
    :readOnlyProp="elementToEdit && elementToEdit.status === statuses.FINAL"
    />
  <v-dialog
    v-model="showFormForm"
    persistent
    content-class="fullscreen-dialog"
    >
    <crf-form-form
      @close="closeFormsForm"
      @linkForm="linkForm"
      :selectedForm="elementToEdit"
      :readOnlyProp="elementToEdit && elementToEdit.status === statuses.FINAL"
      class="fullscreen-dialog"
      @newVersion="newVersion"
      @approve="approve"
      />
  </v-dialog>
  <v-dialog
    v-model="showItemGroupForm"
    persistent
    content-class="fullscreen-dialog"
    >
    <crf-item-group-form
      @close="closeItemGroupForm"
      @linkGroup="linkGroup"
      :selectedGroup="elementToEdit"
      :readOnlyProp="elementToEdit && elementToEdit.status === statuses.FINAL"
      class="fullscreen-dialog"
      @newVersion="newVersion"
      @approve="approve"
      />
  </v-dialog>
  <v-dialog
    v-model="showItemForm"
    persistent
    content-class="fullscreen-dialog"
    >
    <crf-item-form
      @close="closeItemForm"
      @linkItem="linkItem"
      :selectedItem="elementToEdit"
      :readOnlyProp="elementToEdit && elementToEdit.status === statuses.FINAL"
      class="fullscreen-dialog"
      @newVersion="newVersion"
      @approve="approve"
      />
  </v-dialog>
  <crf-references-form
    :open="attributesForm"
    :element="attributesElement"
    @close="closeAttributesForm"
    :read-only="attributesReadOnlyForm"
    />
  <v-dialog v-model="showDuplicationForm"
            @keydown.esc="closeDuplicateForm"
            max-width="800px"
            persistent>
    <crf-duplication-form
      @close="closeDuplicateForm"
      :item="duplicateElement"
      :type="type"
      />
  </v-dialog>
  <v-dialog v-model="showExportForm"
            @keydown.esc="closeExportForm"
            max-width="800px"
            persistent>
    <crf-export-form
      @close="closeExportForm"
      :item="exportElement"
      :type="type"
      />
  </v-dialog>
</div>
</template>

<script>
import crfs from '@/api/crfs'
import StatusChip from '@/components/tools/StatusChip'
import CrfLinkForm from '@/components/library/crfs/CrfLinkForm'
import CrfConditionForm from '@/components/library/crfs/CrfConditionForm'
import ActionsMenu from '@/components/tools/ActionsMenu'
import CrfItemGroupForm from '@/components/library/crfs/CrfItemGroupForm'
import CrfFormForm from '@/components/library/crfs/CrfFormForm'
import CrfItemForm from '@/components/library/crfs/CrfItemForm'
import CrfTemplateForm from '@/components/library/crfs/CrfTemplateForm'
import CrfReferencesForm from '@/components/library/crfs/CrfReferencesForm'
import parameters from '@/constants/parameters'
import crfTypes from '@/constants/crfTypes'
import statuses from '@/constants/statuses'
import CrfDuplicationForm from '@/components/library/crfs/CrfDuplicationForm'
import CrfExportForm from '@/components/library/crfs/CrfExportForm'
import { mapGetters } from 'vuex'

export default {
  components: {
    ActionsMenu,
    StatusChip,
    CrfLinkForm,
    CrfConditionForm,
    CrfItemGroupForm,
    CrfFormForm,
    CrfItemForm,
    CrfTemplateForm,
    CrfReferencesForm,
    CrfDuplicationForm,
    CrfExportForm
  },
  props: {
    source: String,
    refresh: String,
    updatedElement: Object
  },
  computed: {
    ...mapGetters({
      templates: 'crfs/templates',
      total: 'crfs/totalTemplates'
    })
  },
  created () {
    this.statuses = statuses
  },
  data () {
    return {
      headers: [
        { text: this.$t('CrfTree.items_for_linking'), value: 'name' },
        { text: this.$t('CrfTree.ref_attr'), value: 'refAttr' },
        { text: this.$t('CrfTree.def_attr'), value: 'defAttr' },
        { text: this.$t('_global.status'), value: 'status' },
        { text: this.$t('_global.version'), value: 'version' },
        { text: this.$t('CrfTree.link'), value: 'link' }
      ],
      options: {},
      forms: [],
      itemGroups: [],
      items: [],
      loading: false,
      showForm: false,
      itemToLink: {},
      linkedItemsType: '',
      currentItemGroup: {},
      conditionForm: false,
      actions: [
        {
          label: this.$t('CrfTree.edit_condition'),
          icon: 'mdi-pencil',
          click: this.openConditionForm,
          condition: (item) => (this.checkIfConditionExist(item) && !item.forms && !item.item_groups)
        },
        {
          label: this.$t('CrfTree.set_condition'),
          icon: 'mdi-pencil',
          click: this.openConditionForm,
          condition: (item) => (!this.checkIfConditionExist(item) && !item.forms && !item.item_groups)
        },
        {
          label: this.$t('CrfTree.delete_condition'),
          icon: 'mdi-delete',
          iconColor: 'error',
          click: this.deleteCondition,
          condition: (item) => (this.checkIfConditionExist(item) && !item.forms && !item.item_groups)
        },
        {
          label: this.$t('CrfTree.open_def'),
          icon: 'mdi-arrow-left',
          click: this.goToDefinition
        },
        {
          label: this.$t('CrfTree.edit_reference'),
          icon: 'mdi-pencil',
          click: this.editAttributes,
          condition: (item) => (item.status === statuses.DRAFT && !item.forms)
        },
        {
          label: this.$t('CrfTree.view_reference'),
          icon: 'mdi-eye-outline',
          click: this.viewAttributes,
          condition: (item) => (item.status === statuses.FINAL && !item.forms)
        },
        {
          label: this.$t('CrfTree.approve_all'),
          icon: 'mdi-check-decagram',
          click: this.approveAll,
          condition: (item) => (item.status === statuses.DRAFT)
        },
        {
          label: this.$t('_global.duplicate'),
          icon: 'mdi-content-copy',
          iconColor: 'primary',
          click: this.openDuplicateForm
        },
        {
          label: this.$t('CrfTree.preview_odm'),
          icon: 'mdi-file-xml-box',
          click: this.previewODM
        },
        {
          label: this.$t('CrfTree.expand'),
          icon: 'mdi-arrow-expand-down',
          condition: (item) => item.forms,
          click: this.expandWholeTemplate
        },
        {
          label: this.$t('CrfTree.expand'),
          icon: 'mdi-arrow-expand-down',
          condition: (item) => item.item_groups,
          click: this.expandWholeForm
        },
        {
          label: this.$t('_global.export'),
          icon: 'mdi-download',
          click: this.openExportForm
        }
      ],
      templatesExpand: [],
      formsExpand: [],
      groupsExpand: [],
      showFormForm: false,
      showTemplateForm: false,
      showItemGroupForm: false,
      showItemForm: false,
      sortMode: false,
      elementToEdit: {},
      type: '',
      formsTableKey: 0,
      groupsTableKey: 0,
      itemsTableKey: 0,
      attributesForm: false,
      attributesElement: {},
      showDuplicationForm: false,
      duplicateElement: {},
      attributesReadOnlyForm: false,
      doc: '',
      showExportForm: false,
      exportElement: {},
      expandedGroups: [],
      expandedItems: []
    }
  },
  methods: {
    openExportForm (item) {
      this.exportElement = item
      this.type = item.forms ? crfTypes.TEMPLATE : item.item_groups ? crfTypes.FORM : item.items ? crfTypes.GROUP : crfTypes.ITEM
      this.showExportForm = true
    },
    closeExportForm () {
      this.type = ''
      this.showExportForm = false
    },
    // Methods for fetching CRF Tree Data (Templates, Forms, Item Groups and Items)
    getTemplates (sort) {
      this.loading = true
      this.forms = []
      this.itemGroups = []
      this.items = []
      const params = {
        page_number: (this.options.page),
        page_size: this.options.itemsPerPage,
        total_count: true
      }
      this.$store.dispatch('crfs/fetchTemplates', params)
      this.loading = false
    },
    getTemplate (uid) {
      crfs.getTemplate(uid).then((resp) => {
        this.updateTemplate(resp.data)
      })
    },
    getForms (item) {
      // Checking if Template has any Forms
      if (item.forms && item.forms.length > 0) {
        const formsToGet = []
        item.forms.forEach(form => {
          // Checking if Form was already fetched from API, if not then it's added to an Object that holds Forms that we need to fetch
          if (!this.forms.find(el => el.uid === form.uid)) {
            formsToGet.push(form.uid)
          }
        })
        if (formsToGet.length > 0) {
          // Calling for Forms that were not yet fetched and saving them in forms Object so that we don't have to get them again for other Templates
          const params = {
            total_count: true,
            filters: { uid: { v: formsToGet } },
            page_size: 0
          }
          crfs.get('forms', { params }).then((resp) => {
            resp.data.items.forEach(form => {
              resp.data.items[resp.data.items.indexOf(form)].parentTemplateUid = item.uid
            })
            formsToGet.forEach(form => {
              this.forms.push(resp.data.items.find(el => el.uid === form))
            })
          })
        }
        const forms = []
        // Overwriting Forms for those from forms Object
        this.templates.find(el => el.uid === item.uid).forms.forEach((form) => {
          forms.push({ ...this.forms.find(el => el.uid === form.uid), ...form })
        })
        forms.forEach(form => {
          form.parentTemplateUid = item.uid
        })
        return forms
      }
      return []
      // Same logic was applied for Item Groups and Items
    },
    async getForm (uid) {
      let form = {}
      await crfs.getForm(uid).then((resp) => {
        this.updateForm(resp.data)
        form = resp.data
      })
      return form
    },
    async getItemGroups (item) {
      if (item.item_groups && item.item_groups.length > 0) {
        const groupsToGet = []
        item.item_groups.forEach(group => {
          if (!this.itemGroups.find(el => el.uid === group.uid)) {
            groupsToGet.push(group.uid)
          }
        })
        if (groupsToGet.length > 0) {
          const params = {
            total_count: true,
            filters: { uid: { v: groupsToGet } },
            page_size: 0
          }
          await crfs.get('item-groups', { params }).then((resp) => {
            resp.data.items.forEach(group => {
              resp.data.items[resp.data.items.indexOf(group)].parentFormUid = item.uid
            })
            groupsToGet.forEach(group => {
              this.itemGroups.push(resp.data.items.find(el => el.uid === group))
            })
          })
        }
        const groups = []
        this.forms.find(el => el.uid === item.uid).item_groups.forEach((group, index) => {
          groups.push({ ...this.itemGroups.find(el => el.uid === group.uid), ...group })
        })
        groups.forEach(group => {
          group.parentFormUid = item.uid
        })
        this.expandedGroups.push({ formUid: item.uid, groups: groups })
      }
    },
    async getItemGroup (uid) {
      let group = {}
      await crfs.getItemGroup(uid).then((resp) => {
        this.updateItemGroup(resp.data)
        group = resp.data
      })
      return group
    },
    async getItems (item) {
      if (item.items && item.items.length > 0) {
        const itemsToGet = []
        item.items.forEach(item => {
          if (!this.items.find(el => el.uid === item.uid)) {
            itemsToGet.push(item.uid)
          }
        })
        if (itemsToGet.length > 0) {
          const params = {
            total_count: true,
            filters: { uid: { v: itemsToGet } },
            page_size: 0
          }
          await crfs.get('items', { params }).then((resp) => {
            resp.data.items.forEach(group => {
              resp.data.items[resp.data.items.indexOf(group)].parentGroupUid = item.uid
            })
            itemsToGet.forEach(it => {
              this.items.push(resp.data.items.find(el => el.uid === it))
            })
          })
        }
        const items = []
        this.itemGroups.find(el => el.uid === item.uid).items.forEach((item, index) => {
          items.push({ ...this.items.find(el => el.uid === item.uid), ...item })
        })
        items.forEach(it => {
          it.parentGroupUid = item.uid
        })
        this.expandedItems.push({ groupUid: item.uid, items: items })
      }
    },
    getItem (uid) {
      crfs.getItem(uid).then((resp) => {
        this.updateItem(resp.data)
      })
    },
    updateTemplate (updatedTemplate) {
      const index = this.templates.indexOf(this.templates.find(template => template.uid === updatedTemplate.uid))
      if (index > -1) {
        this.$set(this.templates[index], 'name', updatedTemplate.name)
        this.$set(this.templates[index], 'status', updatedTemplate.status)
        this.$set(this.templates[index], 'version', updatedTemplate.version)
        this.$set(this.templates[index], 'forms', updatedTemplate.forms)
      }
      this.formsTableKey += 1
    },
    updateForm (updatedForm) {
      const index = this.forms.indexOf(this.forms.find(form => form.uid === updatedForm.uid))
      if (index > -1) {
        this.$set(this.forms[index], 'name', updatedForm.name)
        this.$set(this.forms[index], 'status', updatedForm.status)
        this.$set(this.forms[index], 'version', updatedForm.version)
        this.$set(this.forms[index], 'item_groups', updatedForm.item_groups)
      }
      this.groupsTableKey += 1
    },
    updateItemGroup (updatedGroup) {
      const index = this.itemGroups.indexOf(this.itemGroups.find(group => group.uid === updatedGroup.uid))
      if (index > -1) {
        this.$set(this.itemGroups[index], 'name', updatedGroup.name)
        this.$set(this.itemGroups[index], 'status', updatedGroup.status)
        this.$set(this.itemGroups[index], 'version', updatedGroup.version)
        this.$set(this.itemGroups[index], 'items', updatedGroup.items)
      }
      this.itemsTableKey += 1
    },
    updateItem (updatedItem) {
      const index = this.items.indexOf(this.items.find(item => item.uid === updatedItem.uid))
      if (index > -1) {
        this.$set(this.items[index], 'name', updatedItem.name)
        this.$set(this.items[index], 'status', updatedItem.status)
        this.$set(this.items[index], 'version', updatedItem.version)
      }
      this.itemsTableKey += 1
    },
    // Methods for expanding CRF Tree
    expandTemplate (item) {
      if (item.forms.length > 0) {
        this.templatesExpand.push(item)
      }
    },
    collapseTemplate (item) {
      this.templatesExpand = this.templatesExpand.filter(el => el.uid !== item.uid)
    },
    expandForm (item) {
      this.formsExpand.push(item)
      this.getItemGroups(item)
    },
    collapseForm (item) {
      this.formsExpand = this.formsExpand.filter(el => el.uid !== item.uid)
    },
    expandGroup (item) {
      this.groupsExpand.push(item)
      this.getItems(item)
    },
    collapseGroup (item) {
      this.groupsExpand = this.groupsExpand.filter(el => el.uid !== item.uid)
    },
    async expandWholeTemplate (item) {
      this.templatesExpand = [item]
      for (const form of item.forms) {
        const formToGet = await this.getForm(form.uid)
        if (formToGet.item_groups.length > 0) {
          this.expandForm(formToGet)
          for (const group of formToGet.item_groups) {
            const groupToGet = await this.getItemGroup(group.uid)
            if (groupToGet.items.length > 0) {
              this.expandGroup(groupToGet)
            }
          }
        }
      }
    },
    async expandWholeForm (item) {
      this.expandForm(item)
      for (const group of item.item_groups) {
        const groupToGet = await this.getItemGroup(group.uid)
        if (groupToGet.items.length > 0) {
          this.expandGroup(groupToGet)
        }
      }
    },
    // Methods for approving/creating new version of CRF Tree elements
    approve (item) {
      let type = ''
      if (item.parentTemplateUid) {
        type = 'forms'
      } else if (item.parentFormUid) {
        type = 'item-groups'
      } else if (item.parentGroupUid) {
        type = 'items'
      }
      crfs.approve(type, item.uid).then((resp) => {
        switch (type) {
          case 'forms':
            this.getForm(item.uid)
            break
          case 'item-groups':
            this.getItemGroup(item.uid)
            break
          case 'items':
            this.getItem(item.uid)
            break
        }
      })
    },
    newVersion (item) {
      let type = ''
      if (item.parentTemplateUid) {
        type = 'forms'
      } else if (item.parentFormUid) {
        type = 'item-groups'
      } else if (item.parentGroupUid) {
        type = 'items'
      }
      switch (type) {
        case 'forms':
          this.getForm(item.uid)
          break
        case 'item-groups':
          this.getItemGroup(item.uid)
          break
        case 'items':
          this.getItem(item.uid)
          break
      }
    },
    approveAll (item) {
      if (item.forms) {
        this.approveFormsAndTemplate(item)
      } else if (item.item_groups) {
        this.approveGroupsAndForm(item)
      } else {
        this.approveItemsAndGroup(item)
      }
    },
    async approveFormsAndTemplate (template) {
      for (const form of template.forms) {
        await this.approveGroupsAndForm(form)
      }
      if (template.status === statuses.DRAFT) {
        await crfs.approve('templates', template.uid).then((resp) => {
          template.status = statuses.FINAL
        })
      }
    },
    async approveGroupsAndForm (form) {
      if (!form.item_groups) {
        const formInObject = this.forms.find(f => f.uid === form.uid)
        formInObject ? form = formInObject : form = await this.getForm(form.uid)
      }
      for (const group of form.item_groups) {
        await this.approveItemsAndGroup(group)
      }
      if (form.status === statuses.DRAFT) {
        await crfs.approve('forms', form.uid).then((resp) => {
          form.status = statuses.FINAL
        })
      }
    },
    async approveItemsAndGroup (group) {
      if (!group.items) {
        const groupInObject = this.itemGroups.find(g => g.uid === group.uid)
        groupInObject ? group = groupInObject : group = await this.getItemGroup(group.uid)
      }
      const items = await this.getItems(group)
      for (const item of items) {
        if (item.status === statuses.DRAFT) {
          await crfs.approve('items', item.uid).then((resp) => {
            item.status = statuses.FINAL
          })
        }
      }
      if (group.status === statuses.DRAFT) {
        await crfs.approve('item-groups', group.uid).then((resp) => {
          group.status = statuses.FINAL
        })
      }
    },
    openDuplicateForm (item) {
      this.duplicateElement = item
      this.type = item.forms ? crfTypes.TEMPLATE : item.item_groups ? crfTypes.FORM : item.items ? crfTypes.GROUP : crfTypes.ITEM
      this.showDuplicationForm = true
    },
    closeDuplicateForm () {
      this.type = ''
      this.showDuplicationForm = false
    },
    editAttributes (item) {
      this.attributesElement = item
      this.attributesForm = true
    },
    viewAttributes (item) {
      this.attributesElement = item
      this.attributesReadOnlyForm = true
      this.attributesForm = true
    },
    closeAttributesForm () {
      if (this.attributesElement.parentTemplateUid) {
        this.getTemplate(this.attributesElement.parentTemplateUid)
      } else if (this.attributesElement.parentFormUid) {
        this.getForm(this.attributesElement.parentFormUid)
      } else {
        this.getItemGroup(this.attributesElement.parentGroupUid)
      }
      this.attributesElement = {}
      this.attributesReadOnlyForm = false
      this.attributesForm = false
    },
    reorderContent (item, direction) {
      if (item.order_number === 0 && direction === -1) {
        return
      }
      let payload = []
      const movedItemNewOrder = item.order_number + direction
      if (item.parentGroupUid) {
        const group = this.itemGroups.find(group => group.uid === item.parentGroupUid)
        const indexOfSwapItem = group.items.indexOf(group.items.find(item => item.order_number === movedItemNewOrder))
        payload = this.reorder(group.items, indexOfSwapItem, direction)
        crfs.addItemsToItemGroup(group.items, group.uid, true)
      } else if (item.parentFormUid) {
        const form = this.forms.find(form => form.uid === item.parentFormUid)
        const indexOfSwapItem = form.item_groups.indexOf(form.item_groups.find(group => group.order_number === movedItemNewOrder))
        payload = this.reorder(form.item_groups, indexOfSwapItem, direction)
        crfs.addItemGroupsToForm(form.item_groups, form.uid, true)
      } else if (item.parentTemplateUid) {
        const template = this.templates.find(template => template.uid === item.parentTemplateUid)
        const indexOfSwapItem = template.forms.indexOf(template.forms.find(form => form.order_number === movedItemNewOrder))
        payload = this.reorder(template.forms, indexOfSwapItem, direction)
        crfs.addFormsToTemplate(payload, template.uid, true)
      }
    },
    reorder (array, index, direction) {
      const payload = [];
      [array[index - direction], array[index]] = [array[index], array[index - direction]]
      array.forEach((el, index) => {
        el.order_number = index
        payload.push(el)
      })
      return payload
    },
    // Methods responsible for CRF elements conditions
    checkIfConditionExist (item) {
      return (item.collection_exception_condition_oid && item.collection_exception_condition_oid !== 'null' && item.collection_exception_condition_oid !== 'none')
    },
    openConditionForm (item) {
      this.itemToLink = item
      this.conditionForm = true
    },
    closeConditionForm () {
      this.itemToLink = {}
      this.conditionForm = false
      this.getTemplates()
    },
    cancelConditionForm () {
      this.itemToLink = {}
      this.conditionForm = false
    },
    deleteCondition (item) {
      const data = {}
      data.filters = `{"oid":{ "v": ["${item.collection_exception_condition_oid}"], "op": "co" }}`
      crfs.getConditionByOid(data).then(resp => {
        crfs.deleteCondition(resp.data.items[0].uid).then(resp => {
          this.getTemplates()
        })
      })
    },
    goToDefinition (item) {
      this.elementToEdit = item
      if (item.forms) {
        this.showTemplateForm = true
      } else if (item.item_groups) {
        this.showFormForm = true
      } else if (item.items) {
        this.showItemGroupForm = true
      } else {
        this.showItemForm = true
      }
    },
    previewODM (item) {
      const data = {
        tab: 'odm-viewer',
        uid: item.uid
      }
      if (item.forms) {
        data.type = crfTypes.TEMPLATE
      } else if (item.item_groups) {
        data.type = crfTypes.FORM
      } else if (item.items) {
        data.type = crfTypes.ITEM_GROUP
      } else {
        data.type = crfTypes.ITEM
      }
      this.$emit('redirectToPage', data)
    },
    getDataTypeIcon (item) {
      item.datatype = item.datatype ? item.datatype.toUpperCase() : item.datatype
      switch (item.datatype) {
        case 'URI':
          return 'mdi-web'
        case 'STRING':
          return 'mdi-format-list-bulleted-square'
        case 'COMMENT':
        case 'TEXT':
          return 'mdi-alphabetical'
        case 'BOOLEAN':
        case 'HEXBINARY':
        case 'BASE64BINARY':
          return 'mdi-order-bool-ascending'
        case 'INTEGER':
        case 'FLOAT':
        case 'DOUBLE':
        case 'HEXFLOAT':
        case 'BASE64FLOAT':
          return 'mdi-numeric'
      }
      return 'mdi-calendar-clock'
    },
    closeTemplateForm () {
      this.showTemplateForm = false
      this.getTemplate(this.elementToEdit.uid)
      this.itemToLink = {}
      this.elementToEdit = {}
    },
    openFormsForm (item) {
      this.itemToLink = item
      this.showFormForm = true
    },
    closeFormsForm () {
      this.showFormForm = false
      this.itemToLink = {}
      this.elementToEdit = {}
    },
    openItemGroupForm (item) {
      this.itemToLink = item
      this.showItemGroupForm = true
    },
    closeItemGroupForm () {
      this.showItemGroupForm = false
      this.itemToLink = {}
      this.elementToEdit = {}
    },
    openItemForm (item) {
      this.itemToLink = item
      this.showItemForm = true
    },
    closeItemForm () {
      this.showItemForm = false
      this.itemToLink = {}
      this.elementToEdit = {}
    },
    // Methods for linking Forms, Item Groups and Items to parents
    linkForm (form) {
      const payload = [{
        uid: form.data.uid,
        order_number: this.itemToLink.forms.length,
        mandatory: false,
        collection_exception_condition_oid: null
      }]
      crfs.addFormsToTemplate(payload, this.itemToLink.uid, false).then(resp => {
        this.getTemplates()
      })
    },
    linkGroup (group) {
      const payload = [{
        uid: group.data.uid,
        order_number: this.itemToLink.item_groups.length,
        mandatory: false,
        collection_exception_condition_oid: null
      }]
      crfs.addItemGroupsToForm(payload, this.itemToLink.uid, false).then(resp => {
        this.getTemplates()
      })
    },
    linkItem (item) {
      const payload = [{
        uid: item.data.uid,
        order_number: this.itemToLink.items.length,
        mandatory: false,
        collection_exception_condition_oid: null,
        key_sequence: parameters.NULL,
        methodOid: parameters.NULL,
        imputation_method_oid: parameters.NULL,
        role: parameters.NULL,
        role_codelist_oid: parameters.NULL,
        data_entry_required: 'No',
        sdv: 'No'
      }]
      crfs.addItemsToItemGroup(payload, this.itemToLink.uid, false).then(resp => {
        this.getTemplates()
      })
    },
    openForm (item, type) {
      this.linkedItemsType = type
      this.itemToLink = item
      this.showForm = true
    },
    closeForm () {
      switch (this.linkedItemsType) {
        case 'forms':
          this.expandTemplate(this.itemToLink)
          break
        case 'item-groups':
          this.expandForm(this.itemToLink)
          break
        case 'items':
          this.expandGroup(this.itemToLink)
      }
      this.showForm = false
      this.itemToLink = {}
      this.getTemplates()
    },
    cancelForm () {
      switch (this.linkedItemsType) {
        case 'forms':
          this.expandTemplate(this.itemToLink)
          break
        case 'item-groups':
          this.expandForm(this.itemToLink)
          break
        case 'items':
          this.expandGroup(this.itemToLink)
      }
      this.showForm = false
      this.itemToLink = {}
    }
  },
  watch: {
    options () {
      this.getTemplates()
    },
    updatedElement (element) {
      switch (element.type) {
        case crfTypes.FORM:
          this.updateForm(element.element)
          this.formsTableKey += 1
          return
        case crfTypes.GROUP:
          this.updateItemGroup(element.element)
          this.groupsTableKey += 1
          return
        case crfTypes.ITEM:
          this.updateItem(element.element)
          this.itemsTableKey += 1
      }
    }
  }
}
</script>
<style scoped>
.tableMinWidth {
  min-width: 1200px !important;
}
.templates {
  background-color: var(--v-dfltBackgroundLight1-base);
}
.group {
  background-color: var(--v-dfltBackgroundLight2-base);
}
.hide {
  opacity: 0;
}
</style>
