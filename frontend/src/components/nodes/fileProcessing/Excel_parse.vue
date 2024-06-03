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
    "task_name": "file_processing.excel_parse",
    "has_inputs": true,
    "template": {
      "files": {
        "required": true,
        "placeholder": "",
        "show": true,
        "multiline": true,
        "value": [],
        "password": false,
        "name": "files",
        "display_name": "files",
        "type": "str",
        "clear_after_run": true,
        "list": false,
        "field_type": "file"
      },
      "prompt": {
        "required": true,
        "placeholder": "",
        "show": true,
        "multiline": true,
        "value": "",
        "password": false,
        "name": "prompt",
        "display_name": "prompt",
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
      },
    }
  }
})

const { t } = useI18n()
const fieldsData = ref(props.data.template)
</script>

<template>
  <BaseNode :nodeId="id" :title="t('components.nodes.fileProcessing.Excel_parse.title')"
    :description="props.data.description" documentLink="https://vectorvein.com/help/docs/file-processing#h2-0">
    <template #main>
      <a-row type="flex">
        <a-col :span="24">
          <BaseField id="prompt" :name="t('components.nodes.fileProcessing.Excel_parse.prompt')" required type="target"
            v-model:show="fieldsData.prompt.show">
            <a-textarea class="field-content" v-model:value="fieldsData.prompt.value" :autoSize="true" :showCount="true"
              :placeholder="fieldsData.prompt.placeholder" />
          </BaseField>
        </a-col>
        <a-col :span="24">
          <BaseField id="files" :name="t('components.nodes.fileProcessing.Excel_parse.files')" required type="target"
            v-model:show="fieldsData.files.show">
          </BaseField>
        </a-col>
      </a-row>
    </template>
    <template #output>
      <BaseField id="output" :name="t('components.nodes.fileProcessing.Excel_parse.output')" type="source" nameOnly>
      </BaseField>
    </template>
  </BaseNode>
</template>

<style></style>