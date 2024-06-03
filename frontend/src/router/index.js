/**
 * @Author: Bi Ying
 * @Date:   2022-02-05 01:38:00
 * @Last Modified by:   Bi Ying
 * @Last Modified time: 2023-07-13 02:15:54
 */
import { createRouter, createWebHashHistory } from 'vue-router'
import { WorkspaceLayout } from '@/layouts'


const routes = [
  {
    path: '/workflow/editor/:workflowId',
    name: 'WorkflowEditor',
    meta: {
      login: true
    },
    component: () => import('@/views/Workspace/WorkflowEditor.vue')
  },
  {
    path: '/',
    component: WorkspaceLayout,
    meta: {
      login: true
    },
    children: [
      {
        path: '',
        redirect: '/workflow',
      },
      {
        path: 'workflow',
        name: 'WorkflowSpace',
        meta: {
          title: 'router.workspace.children.workflow_space',
        },
        component: () => import('@/views/Workspace/WorkflowSpace.vue'),
        children: [
          {
            path: '',
            name: 'WorkflowSpaceMain',
            meta: {
              title: 'router.workspace.children.workflow_main',
            },
            component: () => import('@/views/Workspace/WorkflowSpaceMain.vue')
          },
          {
            path: 'template/:workflowTemplateId',
            name: 'WorkflowTemplate',
            meta: {
              title: 'router.workspace.children.workflow_template',
            },
            component: () => import('@/views/Workspace/WorkflowTemplate.vue')
          },
          {
            path: ':workflowId',
            name: 'WorkflowUse',
            meta: {
              title: 'router.workspace.children.workflow_use',
            },
            component: () => import('@/views/Workspace/WorkflowSpaceUse.vue')
          },
        ]
      },
      {
        path: 'data',
        name: 'DataSpace',
        meta: {
          title: 'router.workspace.children.data_space',
        },
        children: [
          {
            path: '',
            name: 'DataSpace',
            meta: {
              title: 'router.workspace.children.data_space',
            },
            component: () => import('@/views/Workspace/DataSpace.vue'),
          },
          {
            path: ':databaseId',
            name: 'DatabaseDetail',
            meta: {
              title: 'router.workspace.children.database_detail',
            },
            component: () => import('@/views/Workspace/DatabaseDetail.vue')
          },
          {
            path: ':databaseId/create',
            name: 'DatabaseObjectCreate',
            meta: {
              title: 'router.workspace.children.database_detail',
            },
            component: () => import('@/views/Workspace/DatabaseObjectCreate.vue')
          },
          {
            path: ':databaseId/object/:objectId',
            name: 'DatabaseObjectDetail',
            meta: {
              title: 'router.workspace.children.database_object_detail',
            },
            component: () => import('@/views/Workspace/DatabaseObjectDetail.vue')
          },
        ]
      },
    ]
  },
  {
    path: '/account',
    name: 'account',
    component: WorkspaceLayout,
    meta: {
      login: true
    },
    children: [
      {
        path: 'info',
        name: 'AccountInfo',
        meta: {
          title: 'router.account.children.account_info'
        },
        component: () => import('@/views/UserAccount/AccountInfo.vue')
      },
      {
        path: 'settings',
        name: 'AccountSettings',
        meta: {
          title: 'router.account.children.account_settings'
        },
        component: () => import('@/views/UserAccount/AccountSettings.vue')
      }
    ]
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/UserAccount/Login.vue')
  },
  {
    path: '/register',
    name: 'AccountRegister',
    component: () => import('@/views/UserAccount/AccountRegister.vue')
  },
  {
    path: '/admin',
    name: 'admin',
    component: WorkspaceLayout,
    meta: {
      admin: true
    },
    children: [
      // {
      //   path: 'tags',
      //   name: 'TagManager',
      //   meta: {
      //     title: 'router.account.children.account_info'
      //   },
      //   component: () => import('@/views/Admin/TagManager.vue')
      // },
    ]
  },

]

const router = createRouter({
  history: createWebHashHistory('/'),
  routes
})

function getURLParams(url) {
  let param = url.split('#')[0];           //获取#/之前的字符串
  var paramContent = param.split('?').pop();  //获取?之后的参数字符串
  console.log(paramContent);
  var paramsArray = paramContent.split('&');    //参数字符串分割为数组
  var paramResult = {};
  //遍历数组，拿到json对象
  paramsArray.forEach((item, index, paramsArray) => {
  paramResult[paramsArray[index].split('=')[0]] = paramsArray[index].split('=')[1];
  })
  return paramResult;
}

import { getUserId, loginWebcamUser } from '@/utils/user' 

router.beforeEach((to, from, next) => {
  // 而不是去检查每条路由记录
  // to.matched.some(record => record.meta.requiresAuth)
  console.log('getUserId():',getUserId())
  const redirectUrl = encodeURIComponent(`${window.location.origin}`) // 重定向url
  const appId = import.meta.env.VITE_APP_ID // 企业微信ID
  const scope = 'snsapi_base' // 授权类型，snsapi_base(静默授权)或snsapi_privateinfo（手动授权）
  let urlState = 'hc' // 用于防止CSRF攻击，可以是任意字符串
  const agentid = import.meta.env.VITE_AGENT_ID // 企业内应用id
  const params = getURLParams(window.location.href)
  const code = params.code // 链接中code
  const state = params.state // 链接中state
  console.log('code:',code)
  console.log('state:',state)
  console.log(params && code && state && getUserId()===undefined)
  if (state !== '') {
    urlState = state
  }
  const openUrl = `https://open.weixin.qq.com/connect/oauth2/authorize?appid=${appId}&redirect_uri=${redirectUrl}&response_type=code&scope=${scope}&state=${urlState}&agentid=${agentid}#wechat_redirect`
  setTimeout(async () => {
    var ua= window.navigator.userAgent.toLowerCase();
    // 第三方APP扫描登陆 state长度36 记录state值
    if ((params && code && state && getUserId()===undefined) || (state && state.length) === 36) {
      console.log('params:',params)
      try{
        await loginWebcamUser(code, state)
      } catch {
        console.log('error')
      }
    }
    if (to.meta.login & getUserId()===undefined) { // 没有token，去授权
      console.log(ua)
      if( (ua.match(/MicroMessenger/i) == 'micromessenger') && (ua.match(/wxwork/i) == 'wxwork' && !code) ){
        window.location.href = openUrl
      } else {
        next({
          path: '/login',
          // 保存我们所在的位置，以便以后再来
          query: { redirect: to.fullPath },
        })    
      }
    } else { // 已登录，有token
      next()
    }
  }, 0)
})

export default router
