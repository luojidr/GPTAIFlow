/**
 * @Author: Bi Ying
 * @Date:   2022-12-01 17:43:11
 * @Last Modified by:   Bi Ying
 * @Last Modified time: 2023-05-11 17:24:19
 */
import { defineStore } from "pinia"

const USER_ACCOUNT = "userAccount"

const getUserAccountFromLocalStoreage = () => {
  try {
    return JSON.parse(localStorage.getItem("userAccount") || '{}')
  } catch (err) {
    return {}
  }
}

export const useUserAccountStore = defineStore('userAccount', {
  state: () => ({
    userAccount: getUserAccountFromLocalStoreage(),
  }),
  actions: {
    setUserAccount(userAccount) {
      this.userAccount = userAccount
      localStorage.setItem(USER_ACCOUNT, JSON.stringify(this.userAccount))
    },
    // 退出登录
    logout() {
      const accountInfo = JSON.parse(localStorage.getItem("userAccount") || '{}')
      accountInfo.user_id = undefined
      localStorage.setItem(USER_ACCOUNT, JSON.stringify(accountInfo))
    },
  },
})