<script setup>
import { defineComponent, provide, watch, ref, h } from 'vue'
import { useI18n } from 'vue-i18n'
import "echarts"
import VChart, { THEME_KEY } from "vue-echarts"

defineComponent({
  name: 'TableRenderer',
})

const props = defineProps({
  output: {
    type: String,
    required: true,
    default: '',
  },
})

const { t } = useI18n()
const output = ref(props.output)
const selectedColumns = ref([])
const parseOption = (output) => {
  let parsedOption = output;
  if (typeof output === 'string') {
    try {
      parsedOption = JSON.parse(output);
      parsedOption.tableColumns = parsedOption.tableColumns.map(col => {
        const newCol = {
          ...col,
          sorter: (a, b) => ('' + a[col.dataIndex]).localeCompare('' + b[col.dataIndex]),
        };

        if (col.title === '小说名称') {
          newCol.customRender = ({ text, record }) => {
            const protocol = window.location.protocol;
            const hostname = window.location.hostname;
            const port = window.location.port;
            const baseUrl = `${protocol}//${hostname}${port ? ':' + port : ''}`
            const basePattern = /^http:\/\/[^/]+/;
            const updatedUrl = record.url.replace(basePattern, baseUrl);
            console.log(updatedUrl)
            console.log(baseUrl)
            return h('a', {
              href: updatedUrl,
              target: '_blank',
            }, text);
          };
        }

        return newCol;
      });
      
      parsedOption.filteredColumn = parsedOption.tableColumns.filter(item => item.showColumn && item.title !== 'book_url');
      console.log(parsedOption.filteredColumn)
      selectedColumns.value = parsedOption.filteredColumn.map(column => column.dataIndex);
      console.log(selectedColumns.value)
    } catch (e) {
      console.log(e);
      parsedOption = {};
    }
  }
  return parsedOption;
};


const parsedOption = ref(parseOption(output.value))

const handleSelectChange = value => {
  parsedOption.value.tableColumns = parsedOption.value.tableColumns.map(column => ({
    ...column,
    showColumn: value.includes(column.dataIndex)
  }))
  parsedOption.value.filteredColumn = parsedOption.value.tableColumns.filter(item => item.showColumn)
};

const handleResizeColumn = (w, col) => {
  col.width = w;
}

const filteredColumn = () =>{
  console.log("column",parsedOption.value.tableColumns)
  // return parsedOption.value.tableColumns.filter(item => item.showColumn)
  return parsedOption.value.tableColumns
}

const handleTableChange = (pagination, filters, sorter) => {
  console.log('params', pagination, filters, sorter);
};

watch(() => props.output, () => {
  output.value = props.output
  parsedOption.value = parseOption(output.value)
})

provide(THEME_KEY, "light")

</script>

<template>
  <a-row>
    <a-col :span="24">
      <!-- <a-table :dataSource="parsedOption.tableData" :columns="parsedOption.tableColumns" :rowKey="record => record.Index">
      </a-table> -->
      <a-select v-model:value="selectedColumns" mode="multiple" style="width: 100%" placeholder="请选择列" @change="handleSelectChange">
        <a-select-option v-for="col in parsedOption.tableColumns" :key="col.dataIndex">
          {{ col.title }}
        </a-select-option>
      </a-select>
      
      <a-table :dataSource="parsedOption.tableData" :columns="parsedOption.filteredColumn" @resizeColumn="handleResizeColumn" @change="handleTableChange">
        <!-- <a-table-column
          v-for="(column, index) in parsedOption.tableColumns.filter(item => item.showColumn)"
          :key="index"
          :title="column.title"
          :dataIndex="column.dataIndex" v-if="parsedOption.tableColumns"
          :resizable="column.resizable"
          :width="column.width">
        </a-table-column> -->
      </a-table>
    </a-col>
  </a-row>
</template>

<style>
.index {
  display: none;
}
</style>

