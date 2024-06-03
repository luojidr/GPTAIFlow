<script setup>
import { defineComponent, ref, reactive, onBeforeMount } from "vue"
import { UserOutlined } from '@ant-design/icons-vue'
import { useI18n } from 'vue-i18n'
import { storeToRefs } from 'pinia'
import VueMarkdown from 'vue-markdown-render'
import { useUserSettingsStore } from '@/stores/userSettings'
import { useUserAccountStore } from '@/stores/userAccount'
import { useRouter } from 'vue-router';
import WorkflowRunRecordsDrawer from "@/components/workspace/WorkflowRunRecordsDrawer.vue"

defineComponent({
  name: 'UserMenu',
})

const { t } = useI18n()
const userSettingsStore = useUserSettingsStore()
const router = useRouter();


onBeforeMount(() => {
})

const userAccountStore = useUserAccountStore()

const accountLogout = () => {
  userAccountStore.logout()
  router.push('/login')
}

</script>

<template>
  <a-sub-menu key="user-manager">
    <template #title>
    <span>
        <UserOutlined />
        {{ t('components.layout.UserDropdown.account') }}
    </span>
    </template>
    <!-- <WorkflowRunRecordsDrawer openType="simple" :showWorkflowTitle="true"
                @open-record="openRecord" /> -->
    <a-menu-item>
          <a target="_blank" @click="accountLogout">
            {{ t('components.layout.UserDropdown.logout') }}
          </a>
    </a-menu-item>
  </a-sub-menu>

  <!-- <a-dropdown>
    <a class="ant-dropdown-link" @click.prevent>
      {{ t('components.layout.UserDropdown.account') }}
      <DownOutlined />
    </a>
    <template #overlay>
      <a-menu>
        <a-menu-item>
          <a target="_blank" @click="accountLogout">
            {{ t('components.layout.UserDropdown.logout') }}
          </a>
        </a-menu-item>
      </a-menu>
    </template>
  </a-dropdown> -->
</template>