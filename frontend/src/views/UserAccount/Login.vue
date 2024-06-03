<template>
  <div class="space-container">
    <a-layout class="layout">
      <a-form :model="formState" name="basic" :label-col="{ span: 8 }" :wrapper-col="{ span: 10 }" autocomplete="off"
        class="login-form" @finish="onFinish" @finishFailed="onFinishFailed">
        <a-form-item label="用户名" name="user_name" :rules="[{ required: true, message: 'Please input your username!' }]">
          <a-input v-model:value="formState.user_name" />
        </a-form-item>

        <a-form-item label="密码" name="password" :rules="[{ required: true, message: 'Please input your password!' }]">
          <a-input-password v-model:value="formState.password" />
        </a-form-item>

        <a-form-item name="remember" :wrapper-col="{ offset: 8, span: 16 }">
          <a-checkbox v-model:checked="formState.remember">记住密码</a-checkbox>
        </a-form-item>
        <!-- <a class="login-form-forgot" href="">忘记密码</a>     -->

        <a-form-item :wrapper-col="{ offset: 8, span: 16 }">
          <a-button type="primary" html-type="submit">登录</a-button>
          <!-- <a-button style="margin-left: 10px" @click="registerAccount">注册</a-button> -->
        </a-form-item>
      </a-form>
    </a-layout>
  </div>
</template>
  
<script lang="ts" setup>
import { defineComponent, reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import { storeToRefs } from 'pinia'
import { useUserAccountStore } from '../../stores/userAccount'
import { useRouter, useRoute } from 'vue-router';
import { userInfoAPI } from "../../api/user"
import { message } from 'ant-design-vue'

defineComponent({
  name: 'Login',
})
const userAccountStore = useUserAccountStore()
const { userAccount } = storeToRefs(userAccountStore)
const { t } = useI18n()
const router = useRouter();
const route = useRoute();

interface FormState {
  user_name: string;
  password: string;
  remember: boolean;
}

const formState = reactive<FormState>({
  user_name: userAccount.value.user_name,
  password: userAccount.value.password,
  remember: userAccount.value.remember,
});
const onFinish = (values: any) => {
  console.log(`Web Success login: ${values}`);
  const { query: { redirect } } = route
  const res = userInfoAPI('login', formState)
  res.then(res => {
    if (res.status == 200) {
      values.user_id = res.data.user_id
      values.role = res.data.role
      if (redirect === undefined) {
        router.push('/workflow')
      } else {
        router.push(redirect)
      }
    }
    else {
      message.error(t('userAuth.login.account_not_exists_title'))
    }
  }).finally(() => {
      userAccountStore.setUserAccount(values);
      console.log(`>>> login success <<<`)
      // console.log(values)
  })
};

const onFinishFailed = (errorInfo: any) => {
  console.log('Failed:', errorInfo);
};

const registerAccount = () => {
  router.push('/register')
}

</script>

<style scoped>
.space-container {
  height: calc(100vh - 64px);
}

.space-container .layout {
  height: 100%;
  padding: 24px 0;
  background: #fff;
}

.login-form {
  background: #fff;
  border: 1px solid #fff;
  border-radius: 5px;
  width: 600px;
  position: relative;
  margin: 0 auto;
  padding: 80px 0 80px 80px;
  top: 50%;
  transform: translateY(-50%);
}

#components-form-demo-normal-login .login-form-forgot {
  float: right;
}
</style>
  