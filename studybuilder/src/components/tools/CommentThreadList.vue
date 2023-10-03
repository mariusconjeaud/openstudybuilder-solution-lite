<template>
  <div v-show="false" class="comments-wrapper" :class="{transparent: isTransparent}">
    <v-divider class="mb-8" :class="isTransparent ? 'mt-12' : 'mt-8'" ></v-divider>
    <v-sheet class="py-0 title elevation-0" rounded>
      <div class="text-right">
        <v-menu location="bottom" offset-y>
          <template v-slot:activator="{ on, attrs }">
            <v-btn class="no-uppercase" v-bind="attrs" v-on="on">
              {{ $t(`Comments.filter_by_${filterThreadsBy}`) }} ({{ commentTreadsFiltered.length }})
              <v-icon right>mdi-chevron-down</v-icon>
            </v-btn>
          </template>
          <v-list>
            <v-list-item
              v-for="(item, index) in getFilteringOptions()"
              :key="index"
              :value="index"
              @click="filterThreads(item.value)"
            >
              <v-list-item-title>{{ $t(`Comments.filter_by_${item.value}`) }} ({{ getThreadCountByFilter(item.value) }})</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
      </div>

      <v-card-title class="comments-list-title mt-n8">{{ $t('Comments.comments_headline') }}</v-card-title>
      <v-progress-linear v-show="loading" indeterminate color="primary" class="mb-4"></v-progress-linear>
      <v-list class="my-0 py-0">
        <v-list-item v-for="thread in commentTreadsFiltered" :key="thread.uid" class="comment-thread">
          <v-card class="py-0 mb-4" rounded elevation="1" outlined>
            <div @mouseover="thread._hovered = true" @mouseout="thread._hovered = false">
              <v-row class="mx-5 mt-3 mb-2">
                <v-col cols="8" class="py-1 px-0">
                  {{ thread.author_display_name }}
                  <span class="timestamp text-subtitle-1">
                    {{ thread.created_at | date }} {{ isModified(thread.modified_at) }}
                  </span>
                </v-col>

                <v-col cols="4" class="px-0 py-1 text-right comment-actions">
                  <div class="d-inline-block">
                    <div v-show="thread._hovered && isAuthor(thread)">
                      <v-btn fab x-small @click.stop="thread._editMode = true" :title="$t('Comments.comment_edit')">
                        <v-icon>mdi-pencil-outline</v-icon>
                      </v-btn>
                      <v-btn fab x-small @click="deleteThread(thread.uid)" class="ml-4" :title="$t('Comments.comment_delete')">
                        <v-icon>mdi-delete-outline</v-icon>
                      </v-btn>
                    </div>
                  </div>
                  <div class="d-inline-block ml-4">
                    <v-menu location="bottom" offset-y>
                      <template v-slot:activator="{ on, attrs }">
                        <v-btn
                          :class="thread.status  == statuses.COMMENT_STATUS_ACTIVE ? 'orange lighten-2' : 'white'"
                          class="no-uppercase"
                          v-bind="attrs" v-on="on">
                          {{ $t(`Comments.comment_status_${thread.status}`) }}
                          <v-icon right>mdi-chevron-down</v-icon>
                        </v-btn>
                      </template>
                      <v-list>
                        <v-list-item
                          v-for="(item, index) in getActions(thread)"
                          :key="index"
                          :value="index"
                          @click="setThreadStatus(thread.uid, item.newStatus)"
                        >
                          <v-list-item-title>{{ $t(`Comments.comment_status_${item.newStatus}`) }}</v-list-item-title>
                        </v-list-item>
                      </v-list>
                    </v-menu>
                  </div>
                </v-col>
              </v-row>

              <v-card-text class="pt-0 pb-3 px-5" v-show="!thread._editMode">
                {{ thread.text }}
              </v-card-text>

              <div v-show="thread._editMode" class="mx-5">
                <v-textarea auto-grow outlined v-model="thread._newText" :label="$t('Comments.comment_edit')"></v-textarea>
                <div v-show="!loading" class="mt-n4 pb-4">
                  <v-btn class="secondary-btn" color="white" @click="thread._editMode = false; thread._newText = thread.text;">{{ $t('_global.cancel') }}</v-btn>
                  <v-btn class="primary-btn mx-4" color="secondary" :disabled="thread.text == thread._newText" @click="editThread(thread.uid, thread._newText)">{{ $t('Comments.comment_edit') }}</v-btn>
                </div>
                <v-progress-linear v-show="loading" indeterminate color="primary" class="mb-10"></v-progress-linear>
              </div>
            </div>

            <!-- Replies -->
            <v-list class="ml-8 mr-0 py-0">
              <v-list-item v-for="reply in thread.replies" :key="reply.uid" class="comment-thread-reply" @mouseover="reply._hovered = true" @mouseout="reply._hovered = false">
                <v-divider class="mx-5 mt-2"></v-divider>
                <v-row class="mx-5 mt-3 mb-2">
                  <v-col cols="8" class="py-1 px-0">
                    {{ reply.author_display_name }}
                    <span class="timestamp text-subtitle-1">
                      {{ reply.created_at | date }} {{ isModified(reply.modified_at) }}
                    </span>
                  </v-col>
                  <v-col cols="4" class="pa-0 text-right">
                    <div v-show="reply._hovered && isAuthor(reply)">
                      <v-btn fab x-small @click.stop="reply._editMode = true" :title="$t('Comments.reply_edit')">
                        <v-icon>mdi-pencil-outline</v-icon>
                      </v-btn>
                      <v-btn fab x-small @click.stop="deleteReply(thread.uid, reply.uid)" class="ml-4" :title="$t('Comments.reply_delete')">
                        <v-icon>mdi-delete-outline</v-icon>
                      </v-btn>
                    </div>
                  </v-col>
                </v-row>

                <v-card-text class="pt-0 pb-3 px-5" v-show="!reply._editMode">
                  {{ reply.text }}
                </v-card-text>

                <div v-show="reply._editMode" class="mx-5">
                  <v-textarea auto-grow outlined v-model="reply._newText" :label="$t('Comments.reply_edit')"></v-textarea>
                  <div v-show="!loading" class="mt-n4 pb-4">
                    <v-btn class="secondary-btn" color="white" @click="reply._editMode = false; reply._newText = reply.text;">{{ $t('_global.cancel') }}</v-btn>
                    <v-btn class="primary-btn mx-4" color="secondary" :disabled="reply.text == reply._newText" @click="editReply(thread.uid, reply.uid, reply._newText)">{{ $t('Comments.reply_edit') }}</v-btn>
                  </div>
                  <v-progress-linear v-show="loading" indeterminate color="primary" class="mb-10"></v-progress-linear>
                </div>
              </v-list-item>
            </v-list>
            <!-- /Replies -->

            <comment-reply-add :threadId="thread.uid" :threadStatus="thread.status" @commentReplyAdded="getThreads" :isTransparent="isTransparent"></comment-reply-add>
          </v-card>
        </v-list-item>
      </v-list>
      <comment-add :topicPath="topicPath" @commentThreadAdded="getThreads" :isTransparent="isTransparent"></comment-add>
    </v-sheet>
    <confirm-dialog ref="confirm" :text-cols="6" :action-cols="5" />
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import comments from '@/api/comments'
import CommentAdd from './CommentAdd'
import CommentReplyAdd from './CommentReplyAdd'
import ConfirmDialog from './ConfirmDialog.vue'
import statuses from '@/constants/statuses'

export default {
  components: {
    CommentAdd,
    CommentReplyAdd,
    ConfirmDialog
  },
  props: {
    topicPath: {
      type: String,
      required: true
    },
    isTransparent: {
      type: Boolean,
      default: true
    }
  },
  data () {
    return {
      statuses: statuses,
      commentTreads: [],
      commentTreadsFiltered: [],
      filterThreadsBy: 'ALL',
      loading: false
    }
  },
  methods: {
    isModified (modifiedAt) {
      if (modifiedAt) {
        return ' (edited) '
      }
    },
    isAuthor (obj) {
      return this.userInfo.preferred_username.startsWith(obj.author + '@')
    },
    getActions (thread) {
      const actions = []
      if (thread.status === statuses.COMMENT_STATUS_ACTIVE) {
        actions.push({ newStatus: statuses.COMMENT_STATUS_RESOLVED })
      } else {
        actions.push({ newStatus: statuses.COMMENT_STATUS_ACTIVE })
      }
      return actions
    },
    getFilteringOptions () {
      const options = [
        { value: 'ALL' },
        { value: statuses.COMMENT_STATUS_ACTIVE },
        { value: statuses.COMMENT_STATUS_RESOLVED }
      ]
      return options
    },
    filterThreads (filter) {
      this.filterThreadsBy = filter
      switch (filter) {
        case statuses.COMMENT_STATUS_RESOLVED:
          this.commentTreadsFiltered = this.commentTreads.filter(thread => thread.status === statuses.COMMENT_STATUS_RESOLVED)
          break
        case statuses.COMMENT_STATUS_ACTIVE:
          this.commentTreadsFiltered = this.commentTreads.filter(thread => thread.status === statuses.COMMENT_STATUS_ACTIVE)
          break
        default:
          this.commentTreadsFiltered = this.commentTreads
      }
    },
    getThreadCountByFilter (filter) {
      switch (filter) {
        case statuses.COMMENT_STATUS_RESOLVED:
          return this.commentTreads.filter(thread => thread.status === statuses.COMMENT_STATUS_RESOLVED).length
        case statuses.COMMENT_STATUS_ACTIVE:
          return this.commentTreads.filter(thread => thread.status === statuses.COMMENT_STATUS_ACTIVE).length
        default:
          return this.commentTreads.length
      }
    },
    async getThreads () {
      if (!this.topicPath) {
        return
      }
      this.loading = true
      comments.getThreads(this.topicPath)
        .then(items => {
          /*
          _hovered: true indicates that the edit/delete buttons are visible
          _editMode: true indicates that the thread/reply edit form is visible
          _newText: model for the new text of the thread/reply in case of edit
          */
          this.commentTreads = items.map(thread => {
            thread._newText = thread.text
            thread._hovered = false
            thread._editMode = false
            for (const reply of thread.replies) {
              reply._newText = reply.text
              reply._hovered = false
              reply._editMode = false
            }
            return thread
          })
          this.filterThreads(this.filterThreadsBy)
          this.loading = false
        }, (_err) => {
          this.loading = false
        })
    },
    async editThread (threadId, newText) {
      this.loading = true

      comments.editThread(threadId, { text: newText })
        .then(() => {
          this.getThreads()
        }, (_err) => {
          this.loading = false
        })
    },
    async setThreadStatus (threadId, newStatus) {
      this.loading = true

      comments.editThread(threadId, { status: newStatus })
        .then(() => {
          this.getThreads()
        }, (_err) => {
          this.loading = false
        })
    },
    async editReply (threadId, replyId, newText) {
      this.loading = true
      comments.editReply(threadId, replyId, { text: newText })
        .then(() => {
          this.getThreads()
        }, (_err) => {
          this.loading = false
        })
    },
    async deleteThread (threadId) {
      const options = {
        type: 'warning',
        cancelLabel: this.$t('_global.cancel'),
        agreeLabel: this.$t('Comments.comment_delete')
      }
      if (await this.$refs.confirm.open(this.$t('Comments.comment_delete_approve'), options)) {
        this.loading = true
        comments.deleteThread(threadId)
          .then(() => {
            this.getThreads()
          }, (_err) => {
            this.loading = false
          })
      }
    },
    async deleteReply (threadId, replyId) {
      const options = {
        type: 'warning',
        cancelLabel: this.$t('_global.cancel'),
        agreeLabel: this.$t('Comments.reply_delete')
      }
      if (await this.$refs.confirm.open(this.$t('Comments.reply_delete_approve'), options)) {
        this.loading = true
        comments.deleteReply(threadId, replyId)
          .then(() => {
            this.getThreads()
          }, (_err) => {
            this.loading = false
          })
      }
    }
  },
  mounted () {
    this.getThreads()
  },
  watch: {
    topicPath: function () {
      this.getThreads()
    }
  },
  computed: {
    ...mapGetters({
      userInfo: 'auth/userInfo'
    })
  }
}
</script>

<style scoped>
.comments-wrapper {
  .comment-thread, .comment-thread-reply {
    width: 100%;
    display: block;
  }

  .comment-thread-reply.v-list-item {
    padding-left: 0px !important;
    padding-right: 0px !important;
  }

  .timestamp {
    font-weight: 100;
    padding-left: 10px;
  }
}

.comments-wrapper.transparent {
  .comments-list-title {
    padding-left: 0px !important;
    padding-top: 0px !important;
  }
  .v-sheet, .v-list, .v-list-item  {
    background-color: transparent;
    padding-left: 0px !important;
    padding-right: 0px !important;
  }
  .v-list-item {
    background-color: white;
  }
}

.no-uppercase {
     text-transform: unset !important;
}

</style>
