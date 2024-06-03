<script setup>
import { defineComponent, defineEmits  } from 'vue'
import { useI18n } from 'vue-i18n'
import { InboxOutlined, DeleteOutlined, FileOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import axios from "axios"
import { ref } from 'vue';
import { useUserAccountStore } from '@/stores/userAccount'
import { storeToRefs } from 'pinia'

defineComponent({
  name: 'UploaderFieldUse',
})

const props = defineProps({
  multiple: {
    type: Boolean,
    required: false,
    default: true,
  },
  disabled: {
    type: Boolean,
    required: false,
    default: false,
  }
})

const emit = defineEmits(['upload-success', 'remove-success']);

const files = defineModel()

const { t } = useI18n()

const loading = ref(false);

const remove = file => {
  const index = files.value.indexOf(file)
  files.value.splice(index, 1)
  emit('remove-success');
}

const upload = async () => {
  try {
    const selectedFiles = await window.pywebview.api.open_file_dialog(props.multiple)
    selectedFiles.forEach(file => {
      message.success(t('components.workspace.uploaderFieldUse.upload_success', { file: file }))
      files.value.push(file)
      if (!props.multiple && files.value.length > 1) {
        files.value.splice(0, 1)
      }
    })
  } catch (error) {
    console.log(error)
    message.error(t('components.workspace.uploaderFieldUse.upload_failed'))
  }
}

const uploadFiles = async (info) => {
  try{
    //初始化文件信息
    const fileInfo = {
      uid: info.file.uid,
      name: info.file.name,
      status: "uploading",
      response: "",
      url: "",
    };
    //开始真正上传
    const url = import.meta.env.VITE_BACKEND_ENDPOINT
    //上传接口
    let uploadApiUrl = url+"/upload";
    const userAccountStore = useUserAccountStore()
    const { userAccount } = storeToRefs(userAccountStore)

    let formData = new FormData();
    formData.append("file", info.file);
    formData.append("file_name", info.file.name);
    formData.append("user_name", userAccount.value.user_id);
    //添加请求头
    const headers = {
      "Content-Type": "multipart/form-data",
    };
    //配置头
    const request = axios.create({
      headers: headers,
    });
    loading.value = true
    //开始上传
    return request
      .post(uploadApiUrl, formData, {timeout: 0})
      .then((response) => {
        message.success(t('components.workspace.uploaderFieldUse.upload_success', { file: response.data.file_path }))
        files.value.push(response.data.file_path)
      //   if (!props.multiple && files.value.length > 1) {
      //     files.value.splice(0, 1)
      //  }
        loading.value = false
        emit('upload-success');
        return Promise.resolve(response.data);
      })
      .catch((error) => {
        return Promise.reject(error);
      });
  } catch (error) {
    console.log(error)
    message.error(t('components.workspace.uploaderFieldUse.upload_failed'))
  }
}

</script>
<template>
  <a-row :gutter="[16, 16]">
    <a-col :span="24">
      <a-upload
        :customRequest="uploadFiles"
        :showUploadList=false
        :multiple="props.multiple"
        :disabled="props.disabled"
      >
        <a-button :loading="loading" type="primary" block >
          <template #icon>
            <InboxOutlined />
          </template>
          {{ t('components.workspace.uploaderFieldUse.upload') }}
        </a-button>
      </a-upload>
    </a-col>
    <a-col :span="24">
      <a-list :data-source="files" :loading="loading">
        <template #renderItem="{ item }">
          <a-list-item>
            <template #actions>
              <a-typography-link @click="remove(item)">
                <DeleteOutlined />
              </a-typography-link>
            </template>
            <a-list-item-meta>
              <template #title>
                <a-typography-text>{{ item }}</a-typography-text>
              </template>
              <template #avatar>
                <FileOutlined />
              </template>
            </a-list-item-meta>
          </a-list-item>
        </template>
      </a-list>
    </a-col>
  </a-row>
</template>