import { useUserAccountStore } from '../stores/userAccount'
import { storeToRefs } from 'pinia'
import { userInfoAPI } from "../api/user"
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();

import axios from "axios";

export function getUserId() {
    const userAccountStore = useUserAccountStore()
    const { userAccount } = storeToRefs(userAccountStore)
    return userAccount.value.user_id
}

export function getUserRole() {
  const userAccountStore = useUserAccountStore()
  const { userAccount } = storeToRefs(userAccountStore)
  return userAccount.value.role
}


export async function loginWebcamUser(code, state) {
    console.log("logining qyweixin")
    const userAccountStore = useUserAccountStore()
    // 
    const res = await userInfoAPI('login',{code: code, state: state})
    const values = {user_id:""}
    console.log("res",res)
    if (res.status == 200) {
      console.log("values",values)
      values.user_id = res.data.user_id
      userAccountStore.setUserAccount(values)
    }
  }