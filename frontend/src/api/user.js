/**
 * @Author: Bi Ying
 * @Date:   2022-05-25 01:29:38
 * @Last Modified by:   Bi Ying
 * @Last Modified time: 2023-07-06 17:23:56
 */
import baseAPI from './base'
// import {getToken, getUserinfoByToken} from './base'

export async function userInfoAPI(action, parameter) {
    return await baseAPI(`user_info__${action}`, parameter)

    // jwt token 时使用
    // 企微【智创助手】+ web 登录
    // 先获取 token, 载使用 token 获取
    // const token = localStorage.getItem("token") || '';
    // console.log(`login token: ${token}`)
    //
    // if (!token) {
    //     const accessToken = await getToken(parameter.user_name, parameter.password);
    //     console.log(`accessToken: ${accessToken}`)
    //     if (accessToken) {
    //         localStorage.setItem("token", accessToken);
    //     }
    // }
    //
    // return await getUserinfoByToken();
}

export async function settingAPI(action, parameter) {
    return await baseAPI(`setting__${action}`, parameter)
}
