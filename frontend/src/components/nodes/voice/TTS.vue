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
    "task_name": "voice.tts",
    "has_inputs": true,
    "template": {
      "input": {
        "required": true,
        "placeholder": "",
        "show": false,
        "multiline": true,
        "value": "",
        "password": false,
        "name": "input",
        "display_name": "input",
        "type": "str",
        "clear_after_run": true,
        "list": false,
        "field_type": "textarea"
      },
      "model": {
        "required": false,
        "placeholder": "",
        "show": false,
        "multiline": false,
        "value": "tts-1",
        "password": false,
        "options": [
        {
            "value": "tts-1",
            "label": "tts-1"
          },
          {
            "value": "tts-1-hd",
            "label": "tts-1-hd"
          },
        ],
        "name": "model",
        "display_name": "model",
        "type": "str",
        "clear_after_run": false,
        "list": true,
        "field_type": "select"
      },
      "voice": {
        "required": false,
        "placeholder": "",
        "show": false,
        "multiline": false,
        "value": "alloy",
        "password": false,
        "options": [
        {
            "value": "alloy",
            "label": "alloy"
          },
          {
            "value": "echo",
            "label": "echo"
          },
          {
            "value": "onyx",
            "label": "onyx"
          },
          {
            "value": "fable",
            "label": "fable"
          },
          {
            "value": "nova",
            "label": "nova"
          },
          {
            "value": "shimmer",
            "label": "shimmer"
          },
        ],
        "name": "voice",
        "display_name": "voice",
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
        "type": "str",
        "clear_after_run": true,
        "list": false,
        "field_type": ""
      },
    }
  },
})

const { t } = useI18n()

const fieldsData = ref(props.data.template)
</script>

<template>
  <BaseNode :nodeId="id" :title="t('components.nodes.voice.TTS.title')"
    :description="props.data.description" >
    <template #main>
      <a-row type="flex">
        <a-col :span="24">
          <BaseField id="input"  required
            type="target" v-model:show="fieldsData.input.show" v-model:name="fieldsData.input.display_name">
            <a-textarea class="field-content" v-model:value="fieldsData.input.value" :autoSize="true" :showCount="true"
              :placeholder="fieldsData.input.placeholder" />
          </BaseField>
        </a-col>
        <a-col :span="24">
          <BaseField id="model" :name="t('components.nodes.voice.TTS.model')" required type="target"
            v-model:show="fieldsData.model.show">
            <a-select style="width: 100%;" v-model:value="fieldsData.model.value" :options="fieldsData.model.options" />
          </BaseField>
        </a-col>
        <a-col :span="24">
          <BaseField id="model" :name="t('components.nodes.voice.TTS.voice')" required type="target"
            v-model:show="fieldsData.voice.show">
            <a-select style="width: 100%;" v-model:value="fieldsData.voice.value" :options="fieldsData.voice.options" />
          </BaseField>
        </a-col>
      </a-row>
    </template>
    <template #output>
      <BaseField id="output" :name="t('components.nodes.voice.TTS.output')" type="source" nameOnly>
      </BaseField>
    </template>
  </BaseNode>
</template>

<style></style>