<template>
<v-card>
  <v-card-title>
    {{ $t('CrfDuplicationForm.duplicate') }}
  </v-card-title>
  <v-card-text>
      <validation-observer ref="observer">
    <v-row>
      <v-col cols="2" v-if="type !== crfTypes.ITEM">
        <v-checkbox
          v-model="relations"
          :label="$t('CrfDuplicationForm.include')"
          class="mt-6 ml-2"/>
      </v-col>
      <v-col cols="10" v-if="type !== crfTypes.ITEM">
        <odm-references-tree
        :item="item"
        :type="type"
        no-title
        no-actions
        :full-data="false"
        :open-all="relations"/>
      </v-col>
    </v-row>
    <v-row>
      <div class="ml-4">{{ $t('CrfDuplicationForm.attributes') }}</div>
    </v-row>
    <v-row>
      <v-col cols="4">
        <validation-provider
          v-slot="{ errors }"
          rules="required"
          >
          <v-text-field
            :label="$t('_global.name')"
            v-model="name"
            dense
            clearable
            :error-messages="errors"
          />
        </validation-provider>
      </v-col>
      <v-col cols="4">
        <v-text-field
          :label="$t('_global.oid')"
          v-model="oid"
          dense
          clearable
        />
      </v-col>
      <v-col cols="4">
        <validation-provider
          v-slot="{ errors }"
          rules="required"
          v-if="type !== crfTypes.TEMPLATE"
          >
          <v-autocomplete
            v-model="itemToLinkTo"
            :items="itemsToLinkTo"
            :label="$t('CrfDuplicationForm.item_to_link')"
            item-text="name"
            item-value="uid"
            dense
            clearable
            :error-messages="errors"
            return-object>
          </v-autocomplete>
        </validation-provider>
      </v-col>
    </v-row>
    </validation-observer>
  </v-card-text>
  <v-card-actions>
    <v-spacer></v-spacer>
    <v-btn
      class="primary"
      @click="save()"
      >
      {{ $t('_global.save') }}
    </v-btn>
    <v-btn
      class="secondary-btn"
      color="white"
      @click="close()"
      >
      {{ $t('_global.close') }}
    </v-btn>
  </v-card-actions>
</v-card>
</template>

<script>
import OdmReferencesTree from '@/components/library/crfs/OdmReferencesTree'
import crfs from '@/api/crfs'
import crfTypes from '@/constants/crfTypes'

export default {
  components: {
    OdmReferencesTree
  },
  props: {
    open: Boolean,
    item: Object,
    type: String
  },
  data () {
    return {
      relations: false,
      name: '',
      oid: '',
      form: {},
      itemsToLinkTo: [],
      itemToLinkTo: null
    }
  },
  created () {
    this.crfTypes = crfTypes
  },
  mounted () {
    this.getElementsToLinkTo()
  },
  methods: {
    getElementsToLinkTo () {
      if (this.type === crfTypes.FORM) {
        crfs.get('study-events', {}).then((resp) => {
          this.itemsToLinkTo = resp.data.items
        })
      } else if (this.type === crfTypes.GROUP) {
        crfs.getCrfForms().then(resp => {
          this.itemsToLinkTo = resp.data
        })
      } else if (this.type === crfTypes.ITEM) {
        crfs.getCrfGroups().then(resp => {
          this.itemsToLinkTo = resp.data
        })
      }
    },
    close () {
      this.$emit('close')
    },
    async save () {
      const isValid = await this.$refs.observer.validate()
      if (!isValid) return
      let resp
      this.form = Object.assign(this.form, this.item)
      this.$set(this.form, 'name', this.name)
      this.$set(this.form, 'oid', this.oid)
      if (this.type === crfTypes.TEMPLATE) {
        resp = await crfs.createTemplate(this.form)
        if (this.relations) {
          await crfs.addFormsToTemplate(this.item.forms, resp.data.uid, true)
        }
        this.close()
      } else if (this.type === crfTypes.FORM) {
        this.form.alias_uids = this.form.aliases.map(alias => alias.uid)
        resp = await crfs.createForm(this.form)
        this.$set(this.form, 'uid', resp.uid)
        if (this.relations) {
          crfs.addItemGroupsToForm(this.item.item_groups, resp.data.uid, true)
        }
        await crfs.addFormsToTemplate([this.form], this.itemToLinkTo.uid, false)
        this.close()
      } else if (this.type === crfTypes.GROUP) {
        this.form.alias_uids = this.form.aliases.map(alias => alias.uid)
        this.form.sdtm_domain_uids = this.form.sdtm_domains.map(sdtm => sdtm.uid)
        resp = await crfs.createItemGroup(this.form)
        this.$set(this.form, 'uid', resp.uid)
        if (this.relations) {
          crfs.addItemsToItemGroup(this.item.items, resp.data.uid, true)
        }
        await crfs.addItemGroupsToForm([this.form], this.itemToLinkTo.uid, false)
        this.close()
      } else {
        this.form.alias_uids = this.form.aliases.map(alias => alias.uid)
        if (this.form.codelist) {
          this.$set(this.form, 'codelist_uid', this.form.codelist.uid)
        }
        if (this.form.unit_definitions) {
          for (const unit of this.form.unit_definitions) {
            this.form.unit_definitions[this.form.unit_definitions.indexOf(unit)].mandatory = (unit.mandatory !== null && unit.mandatory !== false)
          }
        }
        this.form.terms.forEach(term => {
          term.uid = term.term_uid
          delete term.term_uid
        })
        resp = await crfs.createItem(this.form)
        this.$set(this.form, 'uid', resp.uid)
        crfs.addItemsToItemGroup([this.form], this.itemToLinkTo.uid, false)
        this.close()
      }
    }
  },
  watch: {
    type () {
      this.getElementsToLinkTo()
    }
  }
}
</script>
