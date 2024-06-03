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
    "task_name": "llms.Qwen",
    "has_inputs": true,
    "template": {
      "prompt": {
        "required": true,
        "placeholder": "",
        "show": true,
        "multiline": false,
        "value": "",
        "password": false,
        "name": "prompt",
        "display_name": "prompt",
        "type": "str",
        "clear_after_run": true,
        "list": false,
        "field_type": "input"
      },
      "llm_model": {
        "required": false,
        "placeholder": "",
        "show": false,
        "multiline": false,
        "value": "qwen-32",
        "password": false,
        "options": [
          {
            "value": "qwen-32",
            "label": "qwen-32"
          },
          {
            "value": "qwen-110",
            "label": "qwen-110"
          },
        ],
        "name": "llm_model",
        "display_name": "llm_model",
        "type": "str",
        "clear_after_run": false,
        "list": true,
        "field_type": "select"
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
        "type": "str|dict",
        "clear_after_run": true,
        "list": false,
        "field_type": "textarea"
      },
    }
  },
})

const { t } = useI18n()

const fieldsData = ref(props.data.template)

</script>

<template>
  <BaseNode :nodeId="id" :title="t('components.nodes.llms.Qwen.title')"
    :description="props.data.description">
    <template #main>
      <a-row type="flex">
        <a-col :span="24">
          <BaseField id="prompt" :name="t('components.nodes.llms.Qwen.prompt')" required type="target"
            v-model:show="fieldsData.prompt.show">
            <a-input v-model:value="fieldsData.prompt.value" />
          </BaseField>
        </a-col>
        <a-col :span="24">
          <BaseField id="llm_model" :name="t('components.nodes.llms.Qwen.llm_model')" required type="target"
            v-model:show="fieldsData.llm_model.show">
            <a-select style="width: 100%;" v-model:value="fieldsData.llm_model.value"
              :options="fieldsData.llm_model.options" />
          </BaseField>
        </a-col>
      </a-row>
    </template>
    <template #output>
      <a-row type="flex" style="width: 100%;">
        <a-col :span="24">
          <BaseField id="output" :name="t('components.nodes.llms.Qwen.output')" type="source"
            nameOnly>
          </BaseField>
        </a-col>
      </a-row>
    </template>
  </BaseNode>
</template>

<style></style>