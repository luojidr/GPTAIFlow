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
    "task_name": "web_crawlers.tvmao_crawler",
    "has_inputs": true,
    "template": {
      "series_name": {
        "required": true,
        "placeholder": "",
        "show": true,
        "multiline": false,
        "value": "",
        "password": false,
        "name": "series_name",
        "display_name": "series_name",
        "type": "str",
        "clear_after_run": true,
        "list": false,
        "field_type": "input"
      },
      "output_episodes": {
        "required": true,
        "placeholder": "",
        "show": false,
        "multiline": true,
        "value": "",
        "password": false,
        "name": "output_episodes",
        "display_name": "output_episodes",
        "type": "str|dict",
        "clear_after_run": true,
        "list": false,
        "field_type": "textarea"
      },
      "output_info": {
        "required": true,
        "placeholder": "",
        "show": false,
        "multiline": true,
        "value": "",
        "password": false,
        "name": "output_info",
        "display_name": "output_info",
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
  <BaseNode :nodeId="id" :title="t('components.nodes.webCrawlers.TVmaoCrawler.title')"
    :description="props.data.description">
    <template #main>
      <a-row type="flex">
        <a-col :span="24">
          <BaseField id="series_name" :name="t('components.nodes.webCrawlers.TVmaoCrawler.series_name')" required type="target"
            v-model:show="fieldsData.series_name.show">
            <a-input v-model:value="fieldsData.series_name.value" placeholder="电视剧名" />
          </BaseField>
        </a-col>
      </a-row>
    </template>
    <template #output>
      <a-row type="flex" style="width: 100%;">
        <a-col :span="24">
          <BaseField id="output_episodes" :name="t('components.nodes.webCrawlers.TVmaoCrawler.output_episodes')" type="source"
            nameOnly>
          </BaseField>
        </a-col>
        <a-col :span="24">
          <BaseField id="output_info" :name="t('components.nodes.webCrawlers.TVmaoCrawler.output_info')" type="source"
            nameOnly>
          </BaseField>
        </a-col>
      </a-row>
    </template>
  </BaseNode>
</template>

<style></style>