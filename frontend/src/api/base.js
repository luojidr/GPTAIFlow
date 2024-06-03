/**
 * @Author: Bi Ying
 * @Date:   2023-07-06 17:21:20
 * @Last Modified by:   Bi Ying
 * @Last Modified time: 2023-07-06 17:29:06
 */

import axios from "axios";
import { storeToRefs } from 'pinia'
// import { message } from 'ant-design-vue'
import {useUserAccountStore} from '@/stores/userAccount'
// import router from '@/router'

// 重试次数，共请求2次
axios.defaults.retry = 2

// 请求的间隙
axios.defaults.retryDelay = 2000

axios.defaults.timeout = 20000;

// jwt token 时使用
// axios.interceptors.request.use(
//   config => {
//     console.log('interceptors request coming......');
//     const token = localStorage.getItem('token') || '';
//     console.log(`>>>> token: ${token}`)
//
//     if (token) {
//       config.headers.Authorization = `Bearer ${token}`;
//     } else {
//       console.log(config)
//       console.log('no token')
//     }
//     return config;
//   },
//
//   error => {
//     console.log('error in request');
//     return Promise.reject(error);
//   }
// );

axios.interceptors.response.use(
  response => {
    console.log('interceptors.response ......')
    // console.log(response)
    const {data} = response;

    // jwt token 时使用
    // if (data.status !== 200) {
    //   message.error(data.msg || "网络错误");
    // }
    //
    // if (data.status === 5000) {
    //   // token is expired
    //   localStorage.removeItem("token")
    //   router.push('/login')
    // }

    return response
  },
  err => {
    console.log('interceptors.response error......')
    console.log(err)
    var config = err.config;
    // If config does not exist or the retry option is not set, reject
    if(!config || !config.retry) return Promise.reject(err);

    // Set the variable for keeping track of the retry count
    config.__retryCount = config.__retryCount || 0;

    // Check if we've maxed out the total number of retries
    if(config.__retryCount >= config.retry) {
        // Reject with the error
        return Promise.reject(err);
    }

    // Increase the retry count
    config.__retryCount += 1;

    // Create new promise to handle exponential backoff
    var backOff = new Promise(function(resolve) {
        setTimeout(function() {
            resolve();
        }, config.retryDelay || 1);
    });

    // Return the promise in which recalls axios to retry the request
    return backOff.then(function() {
        return axios(config);
    });
});

export default async function baseAPI(path, parameter) {
  console.log(`baseAPI path: ${path}`)
    // if (!window.pywebview) {
    //     await new Promise(resolve => setTimeout(resolve, 100))
    // }
  const userAccountStore = useUserAccountStore()
  const { userAccount } = storeToRefs(userAccountStore)
  const url = import.meta.env.VITE_BACKEND_ENDPOINT
  
  return await  axios.post(url+'/root', { 
    path: path,
    parameter: parameter,
    user_id: userAccount.value.user_id
  })
  .then(response => {
    // 处理响应数据
    return response.data
  })
  .catch(error => {
    // 处理请求错误
  });
    // return await window.pywebview.api[path](parameter)
}

export async function getToken(username, password) {
  const endpoint = import.meta.env.VITE_BACKEND_ENDPOINT
  const baseApi = endpoint.endsWith('/') ? endpoint.substring(0, endpoint.length - 1): endpoint;

  return await axios.post(
    `${baseApi}/auth/token/get`,
    {
      user_name: username,
      password: password
    }
  ).then(response => {
    const {data: {access_token}} = response.data;
    return access_token;
  }).catch(error => {
    console.log('get token error')
    console.log(error)
  });
}

export async function getUserinfoByToken() {
  const endpoint = import.meta.env.VITE_BACKEND_ENDPOINT
  const baseApi = endpoint.endsWith('/') ? endpoint.substring(0, endpoint.length - 1): endpoint;

  return await axios.post(
    `${baseApi}/auth/userinfo/get`
  ).then(response => {
    const {data} = response;
    console.log("getUserinfoByToken ///////////////")
    console.log(data)
    return data;
  }).catch(error => {
    console.log('get userinfo error')
    console.log(error)
  });
}