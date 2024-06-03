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
    "task_name": "image_generation.dall_e",
    "has_inputs": true,
    "template": {
      "prompt": {
        "required": true,
        "placeholder": "",
        "show": false,
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
      "model": {
        "required": false,
        "placeholder": "",
        "show": false,
        "multiline": false,
        "value": "dall-e-3",
        "password": false,
        "options": [
          {
            "value": "dall-e-3",
            "label": "dall-e-3"
          },
        ],
        "name": "model",
        "display_name": "model",
        "type": "str",
        "clear_after_run": false,
        "list": true,
        "field_type": "select"
      },
      "size": {
        "required": true,
        "placeholder": "",
        "show": false,
        "multiline": true,
        "value": "1024x1024",
        "password": false,
        "options": [
          {
            "value": "1792x1024",
            "label": "1792x1024"
          },
          {
            "value": "1024x1024",
            "label": "1024x1024"
          },
          {
            "value": "1024x1792",
            "label": "1024x1792"
          }
        ],
        "name": "size",
        "display_name": "size",
        "type": "float",
        "clear_after_run": true,
        "list": false,
        "field_type": "select"
      },
      "style": {
        "required": true,
        "placeholder": "",
        "show": false,
        "multiline": true,
        "value": "vivid",
        "password": false,
        "options": [
          {
            "value": "vivid",
            "label": "vivid"
          },
          {
            "value": "natural",
            "label": "natural"
          }
        ],
        "name": "style",
        "display_name": "style",
        "type": "float",
        "clear_after_run": true,
        "list": false,
        "field_type": "select"
      },
      "quality": {
        "required": true,
        "placeholder": "",
        "show": false,
        "multiline": true,
        "value": "standard",
        "password": false,
        "options": [
          {
            "value": "standard",
            "label": "standard"
          },
          {
            "value": "hd",
            "label": "hd"
          }
        ],
        "name": "quality",
        "display_name": "quality",
        "type": "float",
        "clear_after_run": true,
        "list": false,
        "field_type": "select"
      },
      "output_type": {
        "required": false,
        "placeholder": "",
        "show": false,
        "multiline": false,
        "value": "only_link",
        "password": false,
        "options": [
          {
            "value": "only_link",
            "label": "only_link"
          },
          {
            "value": "markdown",
            "label": "markdown"
          },
          {
            "value": "html",
            "label": "html"
          },
        ],
        "name": "output_type",
        "display_name": "output_type",
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
fieldsData.value.output_type.options = fieldsData.value.output_type.options.map(item => {
  item.label = t(`components.nodes.imageGeneration.DallE.output_type_${item.value}`)
  return item
})
</script>

<template>
  <BaseNode :nodeId="id" :title="t('components.nodes.imageGeneration.DallE.title')"
    :description="props.data.description" >
    <template #main>
      <a-row type="flex">
        <a-col :span="24">
          <BaseField id="prompt"  required
            type="target" v-model:show="fieldsData.prompt.show" v-model:name="fieldsData.prompt.display_name">
            <a-textarea class="field-content" v-model:value="fieldsData.prompt.value" :autoSize="true" :showCount="true"
              :placeholder="fieldsData.prompt.placeholder" />
          </BaseField>
        </a-col>
        <a-col :span="24">
          <BaseField id="model" :name="t('components.nodes.imageGeneration.DallE.model')" required type="target"
            v-model:show="fieldsData.model.show">
            <a-select style="width: 100%;" v-model:value="fieldsData.model.value" :options="fieldsData.model.options" />
          </BaseField>
        </a-col>
        <a-col :span="24">
          <BaseField id="model" :name="t('components.nodes.imageGeneration.DallE.size')" required type="target"
            v-model:show="fieldsData.size.show">
            <a-select style="width: 100%;" v-model:value="fieldsData.size.value" :options="fieldsData.size.options" />
          </BaseField>
        </a-col>
        <a-col :span="24">
          <BaseField id="model" :name="t('components.nodes.imageGeneration.DallE.quality')" required type="target"
            v-model:show="fieldsData.quality.show">
            <a-select style="width: 100%;" v-model:value="fieldsData.quality.value" :options="fieldsData.quality.options" />
          </BaseField>
        </a-col>
        <a-col :span="24">
          <BaseField id="model" :name="t('components.nodes.imageGeneration.DallE.style')" required type="target"
            v-model:show="fieldsData.style.show">
            <a-select style="width: 100%;" v-model:value="fieldsData.style.value" :options="fieldsData.style.options" />
          </BaseField>
        </a-col>
        <a-col :span="24">
          <BaseField id="output_type" :name="t('components.nodes.imageGeneration.DallE.output_type')" required
            type="target" v-model:show="fieldsData.output_type.show">
            <a-select style="width: 100%;" v-model:value="fieldsData.output_type.value"
              :options="fieldsData.output_type.options" />
          </BaseField>
        </a-col>
      </a-row>
    </template>
    <template #output>
      <BaseField id="output" :name="t('components.nodes.imageGeneration.StableDiffusion.output')" type="source" nameOnly>
      </BaseField>
    </template>
  </BaseNode>
</template>

<style></style>