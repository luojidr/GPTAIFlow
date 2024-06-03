<template>
    <div class="space-container">
        <a-layout class="layout">
            <a-form :model="formState" name="basic" :label-col="{ span: 8 }" :wrapper-col="{ span: 10 }" autocomplete="off"
                class="register-form" @finish="onFinish" @finishFailed="onFinishFailed">
                <a-form-item label="用户名" name="user_name" :rules="[{ required: true, message: 'Please input your username!' }]">
                    <a-input v-model:value="formState.user_name" />
                </a-form-item>

                <a-form-item label="密码" name="password"
                    :rules="[{ required: true, message: 'Please input your password!' }]">
                    <a-input-password v-model:value="formState.password" />
                </a-form-item>

                <a-form-item label="确认密码" name="confirm_password"
                    :rules="[{ required: true, message: 'Please reinput your password!' }, { validator: validateEqual, trigger:'blur'}]">
                    <a-input-password v-model:value="formState.confirm_password" />
                </a-form-item>

                <a-form-item :wrapper-col="{ offset: 8, span: 16 }">
                    <a-button type="primary" html-type="submit">注册</a-button>
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
import { useRouter } from 'vue-router';
import { userInfoAPI } from "../../api/user"
import { message } from 'ant-design-vue'
import { Rule } from 'ant-design-vue/es/form';

defineComponent({
    name: 'Login',
})
const userAccountStore = useUserAccountStore()
const { userAccount } = storeToRefs(userAccountStore)
const { t } = useI18n()
const router = useRouter();

interface FormState {
    user_name: string;
    password: string;
    confirm_password: string;
}

const formState = reactive<FormState>({
    user_name: "",
    password: "",
    confirm_password: "",
});

const onFinish = (values: any) => {
    console.log('Success:', values);
    const res = userInfoAPI('create', formState)
    res.then(res => {
        if (res.status == 200) {
            values.user_id = res.data.user_id
            values.role = res.data.role
            userAccountStore.setUserAccount(values)
            router.push('/login')
        }
        else {
            message.error(t('userAuth.register.register_failed'))
        }
    })

};

const onFinishFailed = (errorInfo: any) => {
    console.log('Failed:', errorInfo);
};


const validateEqual = async (_rule:Rule, value: string) => {
    if (value === formState.password){
        return Promise.resolve();
    } else {
        return Promise.reject(t('userAuth.register.password_inconsistent'))
    }
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
    