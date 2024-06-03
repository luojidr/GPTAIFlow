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
    "task_name": "output.audio",
    "has_inputs": true,
    "template": {
      "byte_stream": {
        "required": true,
        "placeholder": "",
        "show": false,
        "multiline": false,
        "value": "",
        "password": false,
        "name": "option",
        "display_name": "option",
        "type": "str|list",
        "clear_after_run": true,
        "list": false,
        "field_type": "textarea"
      },
      "show_audio": {
        "required": false,
        "placeholder": "",
        "show": false,
        "multiline": false,
        "value": true,
        "password": false,
        "name": "show_audio",
        "display_name": "show_audio",
        "type": "bool",
        "clear_after_run": false,
        "list": false,
        "field_type": "checkbox"
      },
    }
  },
})

const { t } = useI18n()

const fieldsData = ref(props.data.template)
</script>

<template>
  <BaseNode :nodeId="id" :title="t('components.nodes.outputs.Audio.title')" :description="props.data.description">
    <template #main>
      <a-row type="flex">
        <a-col :span="24">
          <BaseField id="byte_stream" :name="t('components.nodes.outputs.Audio.byte_stream')" required type="target"
            v-model:show="fieldsData.byte_stream.show">
            <a-textarea v-model:value="fieldsData.byte_stream.value" :autoSize="true" :showCount="true"
              :placeholder="fieldsData.byte_stream.placeholder" />
          </BaseField>
        </a-col>

        <a-col :span="24">
          <BaseField id="show_audio" :name="t('components.nodes.outputs.Audio.show_audio')" required type="target"
            v-model:show="fieldsData.show_audio.show">
            <a-checkbox v-model:checked="fieldsData.show_audio.value">
              {{ t('components.nodes.outputs.Audio.show_audio') }}
            </a-checkbox>
          </BaseField>
        </a-col>
      </a-row>
    </template>

  </BaseNode>
</template>

<style></style>