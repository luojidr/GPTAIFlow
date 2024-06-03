<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import BaseNode from '@/components/nodes/BaseNode.vue'
import BaseField from '@/components/nodes/BaseField.vue'

const props = defineProps({
  id: {
    type: String,
    required: true,
  },
  data: {
    type: Object,
    required: true,
  },
  templateData: {
    "description": "description",
    "task_name": "tools.task_monitor",
    "has_inputs": true,
    "template": {
      "urls": {
        "required": true,
        "placeholder": "",
        "show": false,
        "multiline": true,
        "value": "",
        "password": false,
        "name": "prompt",
        "display_name": "urls",
        "type": "str",
        "clear_after_run": true,
        "list": false,
        "field_type": "textarea"
      },
      "filter": {
        "required": true,
        "placeholder": "",
        "show": false,
        "multiline": true,
        "value": "",
        "password": false,
        "name": "filter",
        "display_name": "filter",
        "type": "str",
        "clear_after_run": true,
        "list": false,
        "field_type": "textarea"
      },
      "output": {
        "required": true,
        "placeholder": "",
        "show": false,
        "multiline": true,
        "value": "",
        "password": false,
        "name": "output",
        "display_name": "output",
        "type": "str",
        "clear_after_run": true,
        "list": false,
        "field_type": ""
      }
    },
  }
})

const { t } = useI18n()

const fieldsData = ref(props.data.template)


</script>

<template>
  <BaseNode :nodeId="id" :title="t('components.nodes.tools.TaskMonitor.title')" :description="t('components.nodes.tools.TaskMonitor.description')">
    <template #main>
      <a-row type="flex">
        <a-col :span="24">
          <BaseField id="urls" :name="t('components.nodes.tools.TaskMonitor.urls')" type="target"
            v-model:show="fieldsData.urls.show">
            <a-textarea v-model:value="fieldsData.urls.value" :autoSize="true" :showCount="true"
              :placeholder="fieldsData.urls.placeholder" />
          </BaseField>
        </a-col>
        <a-col :span="24">
          <BaseField id="filter" :name="t('components.nodes.tools.TaskMonitor.filter')" type="target"
            v-model:show="fieldsData.filter.show">
            <a-textarea v-model:value="fieldsData.filter.value" :autoSize="true" :showCount="true"
              :placeholder="fieldsData.filter.placeholder" />
          </BaseField>
        </a-col>
      </a-row>
    </template>
    <template #output>
      <a-row type="flex" style="width: 100%;">
        <a-col :span="24">
          <BaseField id="output" :name="t('components.nodes.tools.TaskMonitor.output')" type="source" nameOnly>
      </BaseField>
        </a-col>
      </a-row>
    </template>
  </BaseNode>
</template>

<style scoped>
/* 在这里添加你的样式 */
</style>
