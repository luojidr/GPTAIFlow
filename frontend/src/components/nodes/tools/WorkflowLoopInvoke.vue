<script setup>
import { ref, reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import { nonFormItemsTypes } from '@/utils/workflow'
import BaseNode from '@/components/nodes/BaseNode.vue'
import BaseField from '@/components/nodes/BaseField.vue'
import WorkflowSelect from '@/components/workspace/WorkflowSelect.vue'
import CodeEditorModal from '@/components/CodeEditorModal.vue'

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
        "task_name": "tools.loop_invoke",
        "has_inputs": true,
        "template": {
            "workflow_id": {
                "required": true,
                "placeholder": "",
                "show": false,
                "multiline": false,
                "value": "",
                "password": false,
                "name": "workflow_id",
                "display_name": "workflow_id",
                "type": "str",
                "clear_after_run": true,
                "list": false,
                "field_type": "input",
            },
            "loop_end_exp_code": {
                "required": true,
                "placeholder": "some code...",
                "show": false,
                "multiline": true,
                "value": "",
                "password": false,
                "name": "loop_end_exp_code",
                "display_name": "loop_end_exp_code",
                "type": "str",
                "clear_after_run": true,
                "list": false,
                "field_type": "textarea"
            },
            "loop_count": {
                "show": false,
                "required": true,
                "value": 3,
                "name": "loop_count",
                "multiline": false,
                "display_name": "loop_count",
                "password": false,
                "type": "int",
                "clear_after_run": true,
                "field_type": "number",
                "list": false,
            },
            "loop_output": {
                "is_output": true,
                "required": true,
                "placeholder": "",
                "show": false,
                "multiline": true,
                "value": [],
                "password": false,
                "name": "loop_output",
                "display_name": "loop_output",
                "type": "list|str",
                "clear_after_run": true,
                "list": false,
                "field_type": "list"
            }
        }
    }
})

const { t } = useI18n()

const fieldsData = ref(props.data.template)
const seletedWorkflowTitle = ref(props.data.seleted_workflow_title)
const codeEditorModal = reactive({
  open: false,
  code: '',
})
const workflowSelectModal = reactive({
    open: false,
    data: {},
    onWorkflowSelect: () => {
        props.data.seleted_workflow_title = workflowSelectModal.data.title
        seletedWorkflowTitle.value = workflowSelectModal.data.title
        fieldsData.value.workflow_id.value = workflowSelectModal.data.wid
        Object.keys(fieldsData.value).forEach((field) => {
        if (!['workflow_id', 'loop_count', 'loop_output', 'loop_end_exp_code'].includes(field)) {
            delete fieldsData.value[field]
        }
        })
        workflowSelectModal.data.inputFields.forEach((field) => {
        if (nonFormItemsTypes.includes(field.field_type)) return
            fieldsData.value[field.name] = JSON.parse(JSON.stringify(field))
            fieldsData.value[field.name].node = fieldsData.value[field.name].nodeId
        })
        workflowSelectModal.open = false
    },
})
</script>

<template>
    <BaseNode :nodeId="id" :title="t('components.nodes.tools.WorkflowLoopInvoke.title')"
        :description="props.data.description" documentLink="https://vectorvein.com/help/docs/tools#h2-12">
        <template #main>
            <a-row type="flex">

                <a-col :span="24" style="padding: 5px 10px;">
                    <template v-if="seletedWorkflowTitle">
                        <a-typography-text type="secondary">
                            {{ t('components.nodes.tools.WorkflowLoopInvoke.selected_workflow') }}:
                        </a-typography-text>
                        <a-typography-text>
                            {{ seletedWorkflowTitle }}
                        </a-typography-text>
                    </template>
                    <a-button type="primary" block @click="workflowSelectModal.open = true">
                        {{ t('components.nodes.tools.WorkflowLoopInvoke.select_workflow') }}
                    </a-button>
                    <a-modal :open="workflowSelectModal.open"
                        :title="t('components.nodes.tools.WorkflowLoopInvoke.select_workflow')" width="80vw"
                        @cancel="workflowSelectModal.open = false" :footer="null">
                        <WorkflowSelect v-model="workflowSelectModal.data"
                            @selected="workflowSelectModal.onWorkflowSelect" />
                    </a-modal>
                </a-col>
                <a-col :span="24">
                    <BaseField id="workflow_id" :name="t('components.nodes.tools.WorkflowLoopInvoke.workflow_id')"
                        required type="target" v-model:show="fieldsData.workflow_id.show">
                        <a-input disabled v-model:value="fieldsData.workflow_id.value"
                            :placeholder="fieldsData.workflow_id.placeholder" />
                    </BaseField>
                </a-col>

                <a-col :span="24">
                    <BaseField id="loop_count" :name="t('components.nodes.tools.WorkflowLoopInvoke.loop_count')"
                        required type="target" v-model:show="fieldsData.loop_count.show">
                        <a-input-number style="width: 100%;" v-model:value="fieldsData.loop_count.value" :step="1" :max="10"
                            :min="1" :keyboard="false" />
                    </BaseField>
                </a-col>
                
                <a-col :span="24">
                    <BaseField id="loop_end_exp_code" :name="t('components.nodes.tools.WorkflowLoopInvoke.loop_end_exp_code')" required type="target"
                        v-model:show="fieldsData.loop_end_exp_code.show">
                        <a-typography-paragraph :ellipsis="{ row: 1, expandable: false }"
                        :content="fieldsData.loop_end_exp_code.value"></a-typography-paragraph>
                        <a-button type="primary" @click="codeEditorModal.open = true">
                        {{ t('components.nodes.tools.WorkflowLoopInvoke.loop_end_exp') }}
                        </a-button>
                        <CodeEditorModal language="python" v-model:open="codeEditorModal.open"
                        v-model:code="fieldsData.loop_end_exp_code.value" />
                    </BaseField>
                </a-col>

                <a-divider>
                    {{ t('components.nodes.tools.WorkflowLoopInvoke.workflow_fields') }}
                </a-divider>

                <template v-for="(field, fieldIndex) in Object.keys(fieldsData)" :key="fieldIndex">
                    <a-col :span="24"
                        v-if="!['workflow_id', 'loop_count', 'loop_end_exp_code'].includes(field) && !fieldsData[field].is_output">
                        <BaseField :id="field" :name="`${fieldsData[field].display_name}: ${fieldsData[field].type}`"
                            required type="target" deletable @delete="removeField(field)"
                            v-model:show="fieldsData[field].show">
                            <a-select style="width: 100%;" v-model:value="fieldsData[field].value"
                                :options="fieldsData[field].options" v-if="fieldsData[field].field_type == 'select'" />
                            <a-textarea v-model:value="fieldsData[field].value" :autoSize="true" :showCount="true"
                                :placeholder="fieldsData[field].placeholder"
                                v-else-if="fieldsData[field].field_type == 'textarea'" />
                            <a-input v-model:value="fieldsData[field].value"
                                :placeholder="fieldsData[field].placeholder"
                                v-else-if="fieldsData[field].field_type == 'input'" />
                            <a-checkbox v-model:checked="fieldsData[field].value"
                                v-else-if="fieldsData[field].field_type == 'checkbox'">
                            </a-checkbox>
                            <a-input-number v-model:value="fieldsData[field].value" :step="0.1" :max="10" :min="1"
                                :keyboard="false" v-else-if="fieldsData[field].field_type == 'number'" />
                        </BaseField>
                    </a-col>
                </template>

            </a-row>

        </template>
        <template #output>
            <a-row type="flex" style="width: 100%;">
                <template v-for="(field, fieldIndex) in Object.keys(fieldsData)" :key="field">
                    <a-col :span="24" v-if="fieldsData[field].is_output">
                        <BaseField :id="field" :name="fieldsData[field].display_name" type="source" nameOnly>
                        </BaseField>
                    </a-col>
                </template>
            </a-row>
        </template>
    </BaseNode>
</template>

<style></style>