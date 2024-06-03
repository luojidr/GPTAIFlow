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
    "task_name": "output.table",
    "has_inputs": false,
    "template": {
      "text": {
        "required": true,
        "placeholder": "",
        "show": true,
        "multiline": true,
        "value": "",
        "password": false,
        "name": "text",
        "display_name": "text",
        "type": "str",
        "clear_after_run": true,
        "list": false,
        "field_type": "textarea"
      },
      "delimeter": {
        "required": true,
        "placeholder": "|",
        "show": false,
        "multiline": false,
        "value": "|",
        "password": false,
        "name": "delimeter",
        "display_name": "delimeter",
        "type": "str",
        "clear_after_run": true,
        "list": false,
        "field_type": "textarea"
      },
      "show_table": {
        "required": false,
        "placeholder": "",
        "show": false,
        "multiline": false,
        "value": true,
        "password": false,
        "name": "show_table",
        "display_name": "show_table",
        "type": "bool",
        "clear_after_run": false,
        "list": false,
        "field_type": "checkbox"
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
  <BaseNode :nodeId="id" :title="t('components.nodes.outputs.Table.title')" :description="props.data.description"
    documentLink="https://vectorvein.com/help/docs/outputs#h2-14">
    <template #main>
      <a-row type="flex">
        <a-col :span="24">
          <BaseField id="text" :name="t('components.nodes.outputs.Table.text')" required type="target"
            v-model:show="fieldsData.text.show">
            <a-textarea v-model:value="fieldsData.text.value" :autoSize="true" :showCount="true"
              :placeholder="fieldsData.text.placeholder" />
          </BaseField>
        </a-col>

        <a-col :span="24">
          <BaseField id="delimeter" :name="t('components.nodes.outputs.Table.delimeter')" required type="target"
            v-model:show="fieldsData.delimeter.show">
            <a-input class="field-content" v-model:value="fieldsData.delimeter.value"
              :placeholder="fieldsData.delimeter.placeholder" />
          </BaseField>
        </a-col>

        <a-col :span="24">
          <BaseField id="show_table" :name="t('components.nodes.outputs.Table.show_table')" required type="target"
            v-model:show="fieldsData.show_table.show">
            <a-checkbox v-model:checked="fieldsData.show_table.value">
              {{ t('components.nodes.outputs.Table.show_table') }}
            </a-checkbox>
          </BaseField>
        </a-col>
      </a-row>
    </template>
    <template #output>
      <BaseField id="output" :name="t('components.nodes.outputs.Table.output')" type="source" nameOnly>
      </BaseField>
    </template>
  </BaseNode>
</template>

<style></style>