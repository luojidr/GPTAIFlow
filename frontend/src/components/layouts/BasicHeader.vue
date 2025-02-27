<script setup>
import { GlobalOutlined, DownOutlined, MenuOutlined } from '@ant-design/icons-vue'
import { defineComponent, onBeforeMount, ref } from 'vue'
import { useRoute } from "vue-router"
import { useI18n } from 'vue-i18n'
import { storeToRefs } from 'pinia'
import logoUrl from "@/assets/logo.svg"
import { useUserSettingsStore } from '@/stores/userSettings'
import { getPageTitle } from '@/utils/title'
import { languageList } from '@/locales'
import SettingDrawer from '@/components/layouts/SettingDrawer.vue'
// import UserDropdown from '@/components/layouts/UserDropdown.vue'

defineComponent({
  name: 'BasicHeader',
})

const loading = ref(true)
const route = useRoute()
const userSettingsStore = useUserSettingsStore()
const { language } = storeToRefs(userSettingsStore)
const { locale, t, te } = useI18n({ useScope: "global" })

const handleLanguageChange = (value) => {
  userSettingsStore.setLanguage(value.key)
  locale.value = value.key
  document.title = getPageTitle(te, t, route.meta.title)
}

const screenWidth = ref(window.innerWidth)

onBeforeMount(() => {
  loading.value = false
  window.addEventListener("resize", () => {
    screenWidth.value = window.innerWidth
  })
})
</script>

<template>
  <a-layout-header style="background: #fff; width: 100%;padding: 0 50px;box-shadow: 0 2px 10px 0 rgb(0 0 0 / 8%);"
    class="basic-header">
    <a-row type="flex" align="middle" justify="space-between" :gutter="[16, 16]" style="width: 100%;"
      v-if="screenWidth > 960">
      <!-- <a-col flex="0 0" class="logo">
        <img alt="AIGC Chain" :src="logoUrl" />
      </a-col> -->

      <a-col flex="0 0">
        <router-link to="/workflow">
          <a-button type="link" id="header-workflow-button">
            {{ t('components.layout.basicHeader.workflow_space') }}
          </a-button>
        </router-link>
      </a-col>

      <!-- <a-col flex="0 0">
        <router-link to="/data">
          <a-button type="link" id="header-data-button">
            {{ t('components.layout.basicHeader.data_space') }}
          </a-button>
        </router-link>
      </a-col> -->

      <a-col flex="1 0" style="display: flex; justify-content: end; align-items: center; gap: 16px;">
        <!-- <SettingDrawer /> -->
        <!-- <a-dropdown>
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
        </a-dropdown> -->
        <!-- <UserDropdown /> -->
      </a-col>
    </a-row>
    <a-row style="width: 100%;" justify="space-between" v-else>
      <a-col>
        <a href="/" class="logo">
          <img alt="AIGC Chain" :src="logoUrl" />
        </a>
      </a-col>
      <!-- <a-col flex="1 0" style="display: flex; justify-content: end; align-items: center; gap: 16px;">
        <SettingDrawer />
      </a-col> -->
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
  </a-layout-header>
</template>

<style>
.basic-header {
  position: fixed;
  z-index: 1;
  width: 100%;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.logo img {
  height: 30px;
}
</style>