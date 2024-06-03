<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { storeToRefs } from 'pinia'
import { useUserDatabasesStore } from "@/stores/userDatabase"
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
    "task_name": "databases.query_data",
    "has_inputs": true,
    "template": {
      "table_name": {
        "required": true,
        "placeholder": "",
        "show": true,
        "multiline": false,
        "value": "",
        "password": false,
        "name": "table",
        "display_name": "table",
        "type": "str",
        "clear_after_run": true,
        "list": false,
        "field_type": "textarea"
      },
      "exclude": {
        "required": false,
        "placeholder": "",
        "show": false,
        "multiline": false,
        "value": "",
        "password": false,
        "name": "exclude",
        "display_name": "exclude",
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
      "query": {
        "required": false,
        "placeholder": "",
        "show": false,
        "multiline": false,
        "value": "",
        "password": false,
        "name": "query",
        "display_name": "query",
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
    }
  },
})

const { t } = useI18n()

const fieldsData = ref(props.data.template)
</script>

<template>
  <BaseNode :nodeId="id" :title="t('components.nodes.databases.QueryData.title')" :description="props.data.description"
    documentLink="https://vectorvein.com/help/docs/vector-db#h2-0">
    <template #main>
      <a-row type="flex">
        <a-col :span="24">
          <BaseField id="table_name" :name="t('components.nodes.databases.QueryData.table_name')" required
            type="target" v-model:show="fieldsData.table_name.show">
            <a-input class="field-content" v-model:value="fieldsData.table_name.value"
              :placeholder="fieldsData.table_name.placeholder" />
          </BaseField>
        </a-col>

        <a-col :span="24">
          <BaseField id="delimeter" :name="t('components.nodes.databases.QueryData.delimeter')" required type="target"
            v-model:show="fieldsData.delimeter.show">
            <a-input class="field-content" v-model:value="fieldsData.delimeter.value"
              :placeholder="fieldsData.delimeter.placeholder" />
          </BaseField>
        </a-col>

        <a-col :span="24">
          <BaseField id="exclude" :name="t('components.nodes.databases.QueryData.exclude')" required type="target"
            v-model:show="fieldsData.exclude.show">
            <a-input class="field-content" v-model:value="fieldsData.exclude.value"
              :placeholder="fieldsData.exclude.placeholder" />
          </BaseField>
        </a-col>

        <a-col :span="24">
          <BaseField id="query" :name="t('components.nodes.databases.QueryData.query')" type="target"
            v-model:show="fieldsData.query.show">
            <a-input class="field-content" v-model:value="fieldsData.query.value"
              :placeholder="fieldsData.query.placeholder" />
          </BaseField>
        </a-col>

      </a-row>
    </template>

    <template #output>
      <BaseField id="output" :name="t('components.nodes.databases.QueryData.output')" type="source" nameOnly>
      </BaseField>
    </template>
  </BaseNode>
</template>

<style></style>