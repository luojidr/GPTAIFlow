<script setup>
import { HomeOutlined, StarOutlined, MenuOutlined, UserOutlined } from '@ant-design/icons-vue'
import { defineComponent, onBeforeMount, ref, watch } from 'vue'
import { useRoute,useRouter } from "vue-router"
import { useI18n } from 'vue-i18n'
import { storeToRefs } from 'pinia'
import logoUrl from "@/assets/logo.svg"
import { useUserSettingsStore } from '@/stores/userSettings'
import { useUserWorkflowsStore } from "@/stores/userWorkflows"
import { getPageTitle } from '@/utils/title'
import { languageList } from '@/locales'
import SettingDrawer from '@/components/layouts/SettingDrawer.vue'
import UserMenu from '@/components/layouts/UserMenu.vue'
import { workflowAPI } from "@/api/workflow"
import NewWorkflowModal from '@/components/workspace/NewWorkflowModal.vue'
import WorkflowRunRecordsDrawer from "@/components/workspace/WorkflowRunRecordsDrawer.vue"

defineComponent({
  name: 'RightContent',
})

const loading = ref(true)
const route = useRoute()
const router = useRouter()
const userSettingsStore = useUserSettingsStore()
const { language } = storeToRefs(userSettingsStore)
const userWorkflowsStore = useUserWorkflowsStore()
const { userFastAccessWorkflows } = storeToRefs(userWorkflowsStore)
const { locale, t, te } = useI18n({ useScope: "global" })

const workflowId = ref(route.params.workflowId)
watch(route, (route) => {
  workflowId.value = route.params.workflowId
  selectedKeys.value = [route.params.workflowId]
})
const selectedKeys = ref([workflowId.value])
const openKeys = ref(['user-workflows'])

const handleLanguageChange = (value) => {
  userSettingsStore.setLanguage(value.key)
  locale.value = value.key
  document.title = getPageTitle(te, t, route.meta.title)
}

const screenWidth = ref(window.innerWidth)

const newWorkflowIndex = ref(1)
const newWorkflowModal = ref()
const openNewWorkflowModal = () => {
  newWorkflowModal.value.showModal()
}
const add = async (template) => {
  console.log('add')
  const response = await workflowAPI('create', {
    title: t('workspace.workflowSpace.new_workflow') + newWorkflowIndex.value,
    language: language.value,
  })
  if (response.status != 200) {
    message.error(response.msg)
    return
  }
  const workflow = response.data
  workflow.update_time = new Date(workflow.update_time).toLocaleString()
  workflow.create_time = new Date(workflow.create_time).toLocaleString()
  userWorkflowsStore.addUserWorkflow(workflow)

  nextTick(() => {
    selectedKeys.value = [workflow.wid]
    router.push(`/workflow/${workflow.wid}`)
  })
}

const openRecord = async (record) => {
  await router.push(`/workflow/${record.wid}?rid=${record.rid}`)
}

onBeforeMount(() => {
  loading.value = false
  window.addEventListener("resize", () => {
    screenWidth.value = window.innerWidth
  })
})
</script>

<template>
  <a-layout-sider class="right-content" width="200" theme="dark" :style="{ overflow: 'auto', height: '100vh', position: 'fixed', left: 0, top: 0, bottom: 0 }" breakpoint="lg" collapsed-width="0">
    <div class="logo" />
    <a-skeleton active v-if="loading" />
    <a-menu  v-model:selectedKeys="selectedKeys" v-model:openKeys="openKeys" mode="inline" theme="dark" v-else>
      <a-menu-item key="my_index">
          <router-link to="/workflow/">
          <HomeOutlined />
          {{ t('workspace.workflowSpace.workflow_index') }}
          </router-link>
      </a-menu-item>
      <WorkflowRunRecordsDrawer drawerType="menu" openType="simple" :showWorkflowTitle="true"
              @open-record="openRecord" />
      <UserMenu />
      <a-sub-menu key="user-workflows">
          <template #title>
          <span>
              <StarOutlined />
              {{ t('workspace.workflowSpace.user_fast_access_workflows') }}
          </span>
          </template>
          <a-menu-item :key="workflow.wid" v-for="workflow in userFastAccessWorkflows">
          <a-tooltip placement="topLeft" :title="workflow.title">
              <router-link :to="`/workflow/${workflow.wid}`">
              {{ workflow.title }}
              </router-link>
          </a-tooltip>
          </a-menu-item>

          <a-menu-item key="add" @click="openNewWorkflowModal">
          + {{ t('workspace.workflowSpace.add_new_workflow') }}
          </a-menu-item>
          <NewWorkflowModal ref="newWorkflowModal" @create="add" />
      </a-sub-menu>
    </a-menu>
  </a-layout-sider>


  <!-- <a-layout-header style="background: #fff; width: 100%;padding: 0 50px;box-shadow: 0 2px 10px 0 rgb(0 0 0 / 8%);"
    class="basic-header">
    <a-row type="flex" align="middle" justify="space-between" :gutter="[16, 16]" style="width: 100%;"
      v-if="screenWidth > 960">
      <a-col flex="0 0" class="logo">
        <img alt="AIGC Chain" :src="logoUrl" />
      </a-col>

      <a-col flex="0 0">
        <router-link to="/workflow">
          <a-button type="link" id="header-workflow-button">
            {{ t('components.layout.basicHeader.workflow_space') }}
          </a-button>
        </router-link>
      </a-col>

      <a-col flex="0 0">
        <router-link to="/data">
          <a-button type="link" id="header-data-button">
            {{ t('components.layout.basicHeader.data_space') }}
          </a-button>
        </router-link>
      </a-col>

      <a-col flex="1 0" style="display: flex; justify-content: end; align-items: center; gap: 16px;">
        <SettingDrawer />
        <a-dropdown>
          <a class="ant-dropdown-link" @click.prevent>
            <GlobalOutlined />
            International - {{ languageList[language] }}
            <DownOutlined />
          </a>
          <template #overlay>
            <a-menu @click="handleLanguageChange">
              <a-menu-item v-for="(value) in Object.keys(languageList)" :key="value">
                {{ languageList[value] }}
              </a-menu-item>
            </a-menu>
          </template>
        </a-dropdown>
        <UserDropdown />
      </a-col>
    </a-row>
    <a-row style="width: 100%;" justify="space-between" v-else>
      <a-col>
        <a href="/" class="logo">
          <img alt="AIGC Chain" :src="logoUrl" />
        </a>
      </a-col>
      <a-col flex="1 0" style="display: flex; justify-content: end; align-items: center; gap: 16px;">
        <SettingDrawer />
      </a-col>
      <a-col>
        <a-dropdown>
          <a-button>
            <MenuOutlined />
          </a-button>
          <template #overlay>
            <a-menu>
              <a-menu-item key="1">
                <router-link to="/workflow">
                  <a-button type="link">
                    {{ t('components.layout.basicHeader.workflow_space') }}
                  </a-button>
                </router-link>
              </a-menu-item>
              <a-menu-item key="2">
                <router-link to="/data">
                  <a-button type="link">
                    {{ t('components.layout.basicHeader.data_space') }}
                  </a-button>
                </router-link>
              </a-menu-item>
              <a-sub-menu key="3">
                <template #title>
                  <GlobalOutlined />
                  International - {{ languageList[language] }}
                </template>
                <a-menu-item v-for="(value) in Object.keys(languageList)" :key="value"
                  @click.prevent="handleLanguageChange({ key: value })">
                  {{ languageList[value] }}
                </a-menu-item>
              </a-sub-menu>
            </a-menu>
          </template>
        </a-dropdown>
      </a-col>
    </a-row>
  </a-layout-header> -->
</template>

<style>
.basic-header {
  position: fixed;
  z-index: 1;
  width: 100%;
}

.logo {
  height: 64px;
  background: rgba(255, 255, 255, 0.2);
  margin: 16px;
}

.logo img {
  height: 30px;
}
</style>