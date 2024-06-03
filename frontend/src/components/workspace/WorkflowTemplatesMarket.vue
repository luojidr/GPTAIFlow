<script setup>
import { onBeforeMount, defineComponent, ref, reactive, computed, nextTick, inject, watch } from "vue"
import { useI18n } from 'vue-i18n'
import { useRouter } from "vue-router"
import { message } from 'ant-design-vue'
import { storeToRefs } from 'pinia'
import { useUserSettingsStore } from '@/stores/userSettings'
import VueMarkdown from 'vue-markdown-render'
import { workflowTagAPI, workflowTemplateAPI } from '@/api/workflow'

defineComponent({
  name: 'WorkflowTemplatesMarket',
})

const { t } = useI18n()
const loading = ref(true)
const router = useRouter()
const userSettingsStore = useUserSettingsStore()
const { language } = storeToRefs(userSettingsStore)
const tags = ref([])
const pageSize = ref(12);
const current = ref(1);

onBeforeMount(async () => {
  loading.value = false
  const [templates, tagsResponse] = await Promise.all([
    workflowTemplates.load(),
    workflowTagAPI('list', {}),
  ])
  if (tagsResponse.status == 200) {
    tags.value = tagsResponse.data
    console.log('tagsResponse.data',tagsResponse.data)
  }
  loading.value = false
})

const workflowTemplates = reactive({
  data: [],
  loading: true,
  current: 1,
  pageSize: 100,
  total: 0,
  pagination: computed(() => ({
    total: workflowTemplates.total,
    current: workflowTemplates.current,
    pageSize: workflowTemplates.pageSize,
  })),
  selectTag: 'all',
  searching: false,
  searchText: '',
  selectTagChange: async () => {
    workflowTemplates.loading = true
    await workflowTemplates.load({
      tags: [workflowTemplates.selectTag],
    })
    workflowTemplates.loading = false
  },
  hoverRowWid: null,
  searchWorkflows: async () => {
    workflowTemplates.loading = true
    workflowTemplates.searching = true
    await workflowTemplates.load({ search_text: workflowTemplates.searchText })
    workflowTemplates.searching = false
    workflowTemplates.loading = false
  },
  clearSearch: async () => {
    workflowTemplates.loading = true
    workflowTemplates.searching = true
    workflowTemplates.searchText = ''
    await workflowTemplates.load({})
    workflowTemplates.searching = false
    workflowTemplates.loading = false
  },

  handleTableChange: (current, pageSize) => {
    console.log(current, pageSize)
    workflowTemplates.load({
      page_size: pageSize,
      page: current,
      tags: [workflowTemplates.selectTag],
      search_text: workflowTemplates.searchText
    })
  },
  load: async (params) => {
    workflowTemplates.loading = true
    const res = await workflowTemplateAPI('list', {
      client: 'PC',
      ...params
    })
    if (res.status == 200) {
      workflowTemplates.data = res.data.templates.map(item => {
        item.create_time = new Date(item.create_time).toLocaleString()
        item.update_time = new Date(item.update_time).toLocaleString()
        return item
      })
    } else {
      message.error(res.msg)
    }
    workflowTemplates.total = res.data.total
    workflowTemplates.pageSize = res.data.page_size
    workflowTemplates.current = res.data.page
    workflowTemplates.loading = false
  }
})

const deleteWorkflowTag = async () => {
  const response = await workflowTagAPI('delete', { tid: workflowTemplates.selectTag })
  if (response.status == 200) {
    message.success(t('workspace.workflowSpace.delete_success'))
    location.reload();
  } else {
    message.error(t('workspace.workflowSpace.delete_failed'))
  }
}

</script>

<template>
  <div v-if="loading">
    <a-skeleton active />
  </div>
  <a-row align="middle" :gutter="[16, 16]" v-else>
    <!-- <a-col :span="24">
      <a-row type="flex" align="middle" justify="space-between">
        <a-col flex="auto">
          <a-typography-title :title="3">
            {{ t('workspace.workflowSpaceMain.official_workflow_template') }}
          </a-typography-title>
        </a-col>
      </a-row>
    </a-col> -->
    <div style="position: relative;">
      <a-col :span="24" class="tag-column">
        <a-space>
          <!-- <a-typography-text>
            {{ t('workspace.workflowTemplate.workflow_template_tags') }}
          </a-typography-text> -->
          <a-radio-group v-model:value="workflowTemplates.selectTag" button-style="solid"
            @change="workflowTemplates.selectTagChange">
            <a-radio-button value="all">
              {{ t('common.all') }}
            </a-radio-button>
            <template v-for="tag in tags" :key="tag.tid">
              <a-radio-button :value="tag.tid">
                {{ tag.title }}
              </a-radio-button>
            </template>
          </a-radio-group>
        </a-space>

      </a-col>

      <a-divider style="margin-top: 50px;"/>
      <a-space class="search-container">
                <a-input-search v-model:value="workflowTemplates.searchText"
                  :placeholder="t('workspace.workflowSpaceMain.input_search_text')" enter-button
                  @search="workflowTemplates.searchWorkflows" class="search-input">
                </a-input-search>
                <!-- <a-button @click="workflowTemplates.clearSearch">
                  {{ t('workspace.workflowSpaceMain.reset_search') }}
                </a-button> -->
        </a-space>

    </div>

    <a-col :span="24">
      <a-spin :spinning="workflowTemplates.loading">
        <a-row :gutter="[16, 16]">
          <a-col :lg="6" :md="8" :sm="12" :xs="24" v-for="template in workflowTemplates.data" :key="template.tid"
            @click="router.push(`/workflow/template/${template.tid}`)">
            <a-card class="template-card" hoverable>
              <template #title>
                <div class="template-card-title-container">
                  <a-typography-title :level="4" class="card-title">
                    {{ template.title }}
                  </a-typography-title>
                  <a-tag v-for="(tag, index) in template.tags" :key="index" :color="tag.color">
                    {{ tag.title }}
                  </a-tag>
                </div>
              </template>
              <a-carousel autoplay arrows v-if="template.images.length > 0">
                <div v-for="(image, index) in template.images" :key="index">
                  <img :src="image" class="card-image" />
                </div>
              </a-carousel>
              <VueMarkdown v-highlight :source="template.brief" class="custom-scrollbar markdown-body custom-hljs"
                v-else />
            </a-card>
          </a-col>
        </a-row>
        <a-pagination
              class="pagination"
              v-model:current="current"
              v-model:pageSize="pageSize"
              show-size-changer
              :total="workflowTemplates.total"
              @change="workflowTemplates.handleTableChange"
            />
      </a-spin>
    </a-col>

  </a-row>
  <a-divider />
  <a-popconfirm placement="leftTop" :title="t('workspace.workflowSpace.delete_tag_confirm')"
            @confirm="deleteWorkflowTag">
    <a-button class='delete-button' type="primary" danger>
      {{ t('workspace.workflowSpace.delete_tag') }}
    </a-button>
  </a-popconfirm>
  <a-divider />
</template>

<style>
.template-card {
  height: 335px;
}

.template-card .template-card-title-container {
  margin-top: 10px;
  margin-bottom: 10px;
  word-break: break-all;
  word-wrap: break-word;
}

.template-card .ant-card-body {
  height: 250px;
}

.template-card .ant-card-body .markdown-body {
  height: 100%;
  overflow-y: scroll;
}

.delete-button{
  left: 90%;
  margin-bottom: 16px;
  position: relative;
}

.pagination{
  text-align: right; 
  margin-top: 64px;
}

.search-container{
  right: 0px;
  /* margin-bottom: 16px; */
  position: absolute;
  bottom: 32px
}

.tag-column{
  margin-bottom: 16px;
  /* position: absolute; */

}

</style>


<style scoped>
.card-image {
  width: 100%;
  height: 202px;
  object-fit: cover;
}

.search-input {
  min-width: 200px;
  max-width: 200px;
}

.card-title{
  white-space: pre-wrap !important
}

</style>