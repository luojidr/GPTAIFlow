<script setup>
import { defineComponent, ref, reactive, computed } from "vue"
import { useI18n } from 'vue-i18n'
import { message } from 'ant-design-vue'
import { HistoryOutlined, ControlOutlined, FieldTimeOutlined, FlagOutlined, PayCircleOutlined,InfoCircleOutlined, NumberOutlined,DollarCircleOutlined, RedoOutlined, TagFilled, TagOutlined } from '@ant-design/icons-vue'
import { workflowRunRecordAPI, workflowAPI } from "@/api/workflow"
import { getUIDesignFromWorkflow, nonFormItemsTypes } from '@/utils/workflow'
import ListFieldUse from "@/components/workspace/ListFieldUse.vue"
import UploaderFieldUse from "@/components/workspace/UploaderFieldUse.vue"
import TemperatureInput from '@/components/nodes/TemperatureInput.vue'

defineComponent({
  name: 'WorkflowRunRecordsDrawer',
})

const { t } = useI18n()
const loading = ref(true)

const props = defineProps({
  workflowId: {
    type: String,
    required: false,
    default: '',
  },
  buttonType: {
    type: String,
    required: false,
    default: 'primary',
  },
  drawerType: {
    type: String,
    required: false,
    default: 'button',
  },
  showWorkflowTitle: {
    type: Boolean,
    required: false,
    default: false,
  },
  openType: {
    type: String,
    required: false,
    default: 'detail', // detail or simple
  },
})

const drawerWidth = props.showWorkflowTitle ? '80vw' : '70vw'

const statusColor = {
  NOT_STARTED: 'purple',
  QUEUED: 'orange',
  RUNNING: 'blue',
  FINISHED: 'green',
  FAILED: 'red',
}

const open = ref(false)

const showDrawer = async () => {
  open.value = true
  await workflowRunRecords.load({})
  loading.value = false
}

const onClose = () => {
  open.value = false
}

const emit = defineEmits(['open-record'])
const statusOptions = [
  { text: t('components.workspace.workflowRunRecordsDrawer.status_not_started'), value: 'NOT_STARTED' },
  { text: t('components.workspace.workflowRunRecordsDrawer.status_queued'), value: 'QUEUED' },
  { text: t('components.workspace.workflowRunRecordsDrawer.status_running'), value: 'RUNNING' },
  { text: t('components.workspace.workflowRunRecordsDrawer.status_finished'), value: 'FINISHED' },
  { text: t('components.workspace.workflowRunRecordsDrawer.status_failed'), value: 'FAILED' },
]
const columns = ref([{
  title: t('components.workspace.workflowRunRecordsDrawer.start_time'),
  key: 'start_time',
  dataIndex: 'start_time',
  sorter: true,
  sortDirections: ['descend', 'ascend'],
  width: '156px',
}, {
  title: t('components.workspace.workflowRunRecordsDrawer.end_time'),
  key: 'end_time',
  dataIndex: 'end_time',
  sorter: true,
  sortDirections: ['descend', 'ascend'],
  width: '156px',
}, {
  title: t('components.workspace.workflowRunRecordsDrawer.cost'),
  key: 'cost',
  dataIndex: 'cost',
  sorter: true,
  sortDirections: ['descend', 'ascend'],
  width: '70px',
}, {
  title: t('components.workspace.workflowRunRecordsDrawer.status'),
  key: 'status',
  dataIndex: 'status',
  filters: statusOptions,
  width: '70px',
},  {
  title: t('components.workspace.workflowRunRecordsDrawer.input_tag'),
  key: 'input_tag',
  width: '180px',
}, 
{
  title: t('components.workspace.workflowRunRecordsDrawer.output_tag'),
  key: 'output_tag',
  width: '100px',
}, {
  title: t('common.action'),
  key: 'action',
  width: '100px',
}])
if (props.showWorkflowTitle) {
  columns.value.splice(0, 0, {
    title: t('components.workspace.workflowRunRecordsDrawer.workflow_title'),
    key: 'workflow_title',
    dataIndex: 'workflow_title',
    width: '100px',
  })
}
const workflowRunRecords = reactive({
  data: [],
  loading: false,
  current: 1,
  pageSize: 10,
  total: 0,
  pagination: computed(() => ({
    total: workflowRunRecords.total,
    current: workflowRunRecords.current,
    pageSize: workflowRunRecords.pageSize,
  })),
  handleTableChange: (page, filters, sorter) => {
    workflowRunRecords.load({
      page_size: page.pageSize,
      page: page.current,
      sort_field: sorter.field,
      sort_order: sorter.order,
      status: filters.status,
    })
  },
  load: async (params) => {
    workflowRunRecords.loading = true
    const res = await workflowRunRecordAPI('list', {
      wid: props.workflowId,
      ...params
    })
    if (res.status == 200) {
      workflowRunRecords.data = res.data.records.map(item => {
        item.start_time = item.start_time ? new Date(item.start_time).toLocaleString() : '-'
        item.end_time = item.end_time ? new Date(item.end_time).toLocaleString() : '-'
        return item
      })
    } else {
      message.error(res.msg)
    }
    workflowRunRecords.total = res.data.total
    workflowRunRecords.pageSize = res.data.page_size
    workflowRunRecords.current = res.data.page
    workflowRunRecords.loading = false
  }
})

const getWorkflowRunRecordDetail = async (rid, workflow) => {
  loading.value = true
  if (props.openType == 'detail') {
    const res = await workflowRunRecordAPI('get', {
      rid: rid
    })
    if (res.status == 200) {
      emit('open-record', res.data)
      open.value = false
    } else {
      message.error(res.msg)
    }
  } else {
    emit('open-record', { rid, wid: workflow.wid })
    open.value = false
  }
  loading.value = false
}

const redoWorkflow = async (params) => {
  // console.log('redo', params)
  const res = await workflowAPI('redo', params)
  alert('任务已重试，请刷新运行记录');
}

const getWorkflowInput= async (workflowId) => {
  const getWorkflowRequest = workflowAPI('get', { wid: workflowId })
  const workflowResponse = await getWorkflowRequest
  if (workflowResponse.status != 200) {
    message.error(t('workspace.workflowSpace.get_workflow_failed'))
    return
  }
  currentWorkflow.value = workflowResponse.data
  uiDesign = getUIDesignFromWorkflow(currentWorkflow.value)
  }

</script>

<template>
  <a-button v-if="props.drawerType == 'button'" :type="props.buttonType" @click="showDrawer">
    {{ t('components.workspace.workflowRunRecordsDrawer.workflows_run_records') }}
  </a-button>
  <a-menu-item v-else>
          <a target="record_blank" @click="showDrawer">
            <HistoryOutlined />
            {{ t('components.workspace.workflowRunRecordsDrawer.workflows_run_records') }}
          </a>
  </a-menu-item>

  <a-drawer :title="t('components.workspace.workflowRunRecordsDrawer.my_workflows_run_records')" :width="drawerWidth"
    :open="open" @close="onClose">
    <a-spin :spinning="loading">
      <a-row justify="space-between" align="middle">
        <a-col :span="24">
          <a-table :loading="workflowRunRecords.loading" :columns="columns" :customRow="workflowRunRecords.customRow"
            :data-source="workflowRunRecords.data" :pagination="workflowRunRecords.pagination"
            @change="workflowRunRecords.handleTableChange">
            <template #headerCell="{ column }">
              <template v-if="column.key === 'workflow_title'">
                <NumberOutlined />
                {{ t('components.workspace.workflowRunRecordsDrawer.workflow_title') }}
              </template>
              <template v-else-if="column.key === 'start_time'">
                <FieldTimeOutlined />
                {{ t('components.workspace.workflowRunRecordsDrawer.start_time') }}
              </template>
              <template v-else-if="column.key === 'end_time'">
                <FieldTimeOutlined />
                {{ t('components.workspace.workflowRunRecordsDrawer.end_time') }}
              </template>
              <template v-else-if="column.key === 'cost'">
                <DollarCircleOutlined />
                {{ t('components.workspace.workflowRunRecordsDrawer.cost') }}
              </template>
              <template v-else-if="column.key === 'status'">
                <FlagOutlined />
                {{ t('components.workspace.workflowRunRecordsDrawer.status') }}
              </template>
              <template v-else-if="column.key === 'used_credits'">
                <PayCircleOutlined />
                {{ t('components.workspace.workflowRunRecordsDrawer.used_credits') }}
              </template>
              <template v-else-if="column.key === 'input_tag'">
                <TagFilled />
                {{ t('components.workspace.workflowRunRecordsDrawer.input_tag') }}
              </template>
              <template v-else-if="column.key === 'output_tag'">
                <TagOutlined />
                {{ t('components.workspace.workflowRunRecordsDrawer.output_tag') }}
              </template>
              <template v-else-if="column.key === 'action'">
                <ControlOutlined />
                {{ t('common.action') }}
              </template>
            </template>

            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'workflow_title'">
                {{ record.workflow.title }}
              </template>
              <template v-if="column.key === 'input_tag'">
                <div v-for="item in record.general_details.input_tag">
                  <div v-if="item" class="tag">
                    <span class="input_tag_content">{{ item.length > 10 ? item.slice(0,10)+'...':item }}</span>
                  </div>
                </div>
              </template>
              <template v-if="column.key === 'output_tag'">
                <div v-if="record.general_details.output_tag" class="tag">
                  <span class="output_tag_content">{{ record.general_details.output_tag }}</span>
                </div>
                <!-- </div> -->
              </template>
              <template v-else-if="column.key === 'status'">
                <a-popover v-if="record.status === 'FAILED'" placement="top" title="错误信息">
                  <template #content>
                    <div v-if="record.general_details">
                      {{record.general_details.error_detail}}
                    </div>
                  </template>
                  <a-tag :color="statusColor[record.status]">
                    {{ t(`components.workspace.workflowRunRecordsDrawer.status_${record.status.toLowerCase()}`) }}<InfoCircleOutlined />
                  </a-tag>
                  <RedoOutlined @click="redoWorkflow(record)"/>

                </a-popover>
                <a-tag :color="statusColor[record.status]" v-else>
                  {{ t(`components.workspace.workflowRunRecordsDrawer.status_${record.status.toLowerCase()}`) }}
                </a-tag>

              </template>
              <template v-else-if="column.key === 'action'">
                <div class="action-container">
                  <a-typography-link @click.prevent="getWorkflowRunRecordDetail(record.rid, record.workflow)">
                    {{ t('components.workspace.workflowRunRecordsDrawer.check_record') }}
                  </a-typography-link>
                </div>
                <a-popover v-if="record.general_details" title="Title" trigger="hover">
                  <template #content>
                    <a-col v-if="record.general_details.ui_design" :span="24">
                      <a-form layout="vertical">
                        <div v-for="( field, fieldIndex ) in record.general_details.ui_design.inputFields " :key="`field-${field}-${fieldIndex}`">
                          <a-form-item v-if="!nonFormItemsTypes.includes(field.field_type)">
                            <template #label>
                              {{ field.display_name }}
                            </template>
                            <TemperatureInput v-model="field.value" v-if="field.category == 'llms' && field == 'temperature'" />
                            <a-select v-model:value="field.value" :options="field.options"
                              v-else-if="field.field_type == 'select'" />
                            <a-textarea v-model:value="field.value" :autoSize="true" :showCount="true"
                              :placeholder="field.placeholder" v-else-if="field.field_type == 'textarea'" />
                            <a-input v-model:value="field.value" :placeholder="field.placeholder"
                              v-else-if="field.field_type == 'input'" />
                            <a-input-number v-model:value="field.value" :placeholder="field.placeholder"
                              v-else-if="field.field_type == 'number'" />
                            <a-checkbox v-model:checked="field.value" v-else-if="field.field_type == 'checkbox'" />
                            <UploaderFieldUse v-model="field.value" v-else-if="field.field_type == 'file'" />
                            <ListFieldUse v-model="field.value" v-else-if="field.field_type == 'list'" />
                          </a-form-item>
                          <a-row v-if="field.field_type == 'typography-paragraph'">
                            <a-col :span="24" class="ui-special-item-container">
                              <vue-markdown v-highlight :source="field.value" class="markdown-body custom-hljs ui-special-item" />
                            </a-col>
                          </a-row>
                        </div>
                      </a-form>
                    </a-col>
                  </template>
                  <a-button>输入</a-button>
                </a-popover>
              </template>
            </template>
          </a-table>
        </a-col>
      </a-row>
    </a-spin>
  </a-drawer>
</template>

<style scoped>
.input_tag_content {
  display: inline-block;
  padding: 0.25em 0.75em;
  font-size: 0.875em;
  color: #ffffff;
  background-color: #007bff;
  border-radius: 0.25rem;
  margin: 0.125rem;
  border: 1px solid transparent;
}

.tag {
  display: inline-block;
}
.output_tag_content {
  display: inline-block;
  padding: 0.25em 0.75em;
  font-size: 0.875em;
  color: hsl(263, 83%, 16%);
  background-color: #9fec87;
  border-radius: 0.25rem;
  margin: 0.125rem;
  border: 1px solid transparent;
}

.tag {
  display: inline-block;
}
</style>