import Qwen from "../components/nodes/llms/Qwen.vue";
import TaskMonitor from "../components/nodes/tools/TaskMonitor.vue";

/**
 * @Author: Bi Ying
 * @Date:   2022-05-24 13:48:55
 * @Last Modified by:   Bi Ying
 * @Last Modified time: 2023-08-27 01:36:02
 */
export default {
  lang: '中文',
  meta: {
    'title': 'AIGC影视剧本智能创作系统',
    'description': '基于 AI 的知识库 + 项目管理系统',
  },
  router: {
    base: 'AIGC影视剧本智能创作系统',
    basic: {
      children: {
        'index': '首页',
      }
    },
    workspace: {
      children: {
        'workflow_space': '我的项目空间',
        'data_space': '我的数据空间',
        'workflow_main': '项目主页',
        'workflow_use': '项目使用',
        'workflow_template': '项目模板',
        'database_detail': '数据库详情',
        'database_object_create': '创建对象',
        'database_object_detail': '数据库对象详情',
      }
    },
    account: {
      children: {
        'info': '我的账号信息',
        'settings': '我的账号设置',
      }
    },
    user: {
      children: {
        'login': '登录',
        'register': '注册',
        'register_result': '注册结果',
      }
    },
  },
  common: {
    'AIGC_chain': 'AIGC影视剧本智能创作系统',
    'time_length': '{hours}小时{minutes}分钟',
    'refresh': '刷新',
    'index': '首页',
    'update_log': '更新日志',
    'my': '我的',
    'all': '全部',
    'add': '添加',
    'create': '创建',
    'delete': '删除',
    'status': '状态',
    'tags': '标签',
    'action': '操作',
    'output': '输出',
    'support_inquiries': '问题咨询：',
    'notice': '注意',
    'ok': '好的',
    'save': '保存',
    'pay_channel': '支付方式',
    'credits': '积分',
    'total_price': '总价格',
    'total_credits': '总积分',
    'bonus_credits': '奖励积分',
    'available_credits': '可用积分',
    'pay': '付款',
    'warning': '警告',
    'copy_success': '复制成功',
    'alipay': '支付宝',
    'wechatpay': '微信支付',
    'create_time': '创建时间',
    'update_time': '更新时间',
    'update_time_format': '更新时间: {time}',
    'back': '返回',
    'previous_step': '上一步',
    'next_step': '下一步',
    'preview': '预览',
  },
  email: {
    verify: {
      'email_verify_success': '邮箱验证成功！',
      'email_verify_success_subtitle': '您的邮箱验证成功，快来试用一下吧！',
      'check_control_panel': '查看控制台',
      'email_verify_failed': '邮箱验证失败！',
      'email_verify_failed_subtitle': '验证链接有误，请重新检查并刷新',
      'email_verify_expired_subtitle': '链接已超时，请重新发送',
      'resend_email': '重新发送邮件',
      'email_already_verified': '邮箱已验证！',
      'email_already_verified_subtitle': '该链接已验证，请直接登陆',
      'please_verify_your_email': '请验证您的邮箱',
      'please_verify_your_email_subtitle': '为保证您的账号安全，我们需要确认您的邮箱地址：',
      'sending_failed': '发送失败',
      'too_frequently_resend': '您的邮件发送过于频繁，请稍后再试',
      'sending_successfull': '发送成功',
      'please_relogin_after_verify': '验证成功后请重新登录网站',
    }
  },
  userAuth: {
    common: {
      'please_enter': '请输入',
      'username': '用户名',
      'email': 'Email电子邮箱',
      'mobile': '手机',
      'verification_code': '验证码',
      'send_verification_code': '发送验证码',
      'password': '密码',
      'login': '登录',
      'logout': '登出',
      'or': '或',
      'register': '注册新账号',
      'sign_up': '注册新账号',
      'ref_code': '邀请码（可选）',
      'error': '服务器错误',
    },
    login: {
      'please_enter_username': '请输入手机号或用户名',
      'please_enter_email': '请输入邮箱',
      'please_enter_password': '请输入密码',
      'remember_account': '记住账号',
      'forget_password': '忘记密码',
      'account_not_exists_title': '密码错误或账号不存在',
      'account_not_exists_content': '请检查账号密码是否正确或注册新账号',
      'mobileLogin': '手机号登录',
      'wechatLogin': '微信登录',
      'email_login': '邮箱登录',
    },
    register: {
      'region_search_or_select': '请搜索或选择您的区域',
      'please_select_your_region': '请选择您的区域',
      'human_verification_error': '人机验证失败！',
      'connection_error': '连接错误！',
      'email_already_exists': '该邮箱已注册，请直接登录',
      'username_already_exists': '该用户名已被使用',
      'register_success': '注册成功，请验证邮件',
      'password_inconsistent': '两次输入密码不一致',
      'register_failed': '注册失败'
    },
    registerResult: {
      'check_email': '查看邮箱',
      'back_to_login': '返回登录',
      'verification_email_sent': '激活邮件已发送到你的邮箱中，邮件有效期为24小时。请及时登录邮箱，点击邮件中的链接激活帐户。',
      'your_email_account_register_success': '你的账户：{email} 注册成功',
    },
    forgetPassword: {
      'verify_email': '验证邮箱',
      'enter_new_password': '输入新密码',
      'verify': '验证',
      'verification_code_send_success': '验证码已发送',
      'human_verification_error': '人机验证失败！',
      'connection_error': '连接错误！',
      'email_not_exists': '该邮箱未注册',
      'reset_password': '重置密码',
      'reset_success': '重置密码成功',
    }
  },
  userAccount: {
    accountInfo: {
      'my_account': '我的账号',
      'my_credits': '我的积分',
    },
    accountSettings: {
      'account_email': '账号邮箱',
      'account_settings': '账号设置',
    }
  },
  workspace: {
    workflowSpace: {
      'workflow_index': '首页',
      'user_fast_access_workflows': '收藏项目',
      'add_new_workflow': '新建项目',
      'new_workflow': '新项目',
      'share_workflow': '发布',
      'clone_workflow': '复制',
      'clone_success': '克隆成功',
      'clone_failed': '克隆失败',
      'add_to_fast_access': '添加到收藏',
      'add_to_fast_access_confirm': '确认添加该项目到收藏？',
      'delete_from_fast_access': '从收藏删除',
      'delete_from_fast_access_confirm': '确认从收藏删除该项目？',
      'add_to_fast_access_success': '添加到收藏成功',
      'add_to_fast_access_failed': '添加到收藏失败',
      'delete_from_fast_access_success': '从收藏删除成功',
      'delete_from_fast_access_failed': '从收藏删除失败',
      'update_time': '更新时间: {time}',
      'inputs': '输入',
      'outputs': '输出',
      'triggers': '触发器',
      'run': '运行',
      'edit': '编辑',
      'delete': '删除',
      'delete_tag': '删除标签',
      'delete_confirm': '确认删除该项目？',
      'delete_tag_confirm': '将从所有用户与模版项目中删除该标签，确认删除？',
      'delete_success': '删除成功',
      'delete_failed': '删除失败',
      'save_success': '保存成功',
      'save_failed': '保存失败',
      'workflow_cant_invoke_itself': '项目不能调用自身',
      'get_workflow_failed': '获取项目失败，项目不存在或者权限不足',
      'get_workflow_record_failed': '获取项目运行记录失败',
      'submit_workflow_success': '已提交项目运行请求',
      'submit_workflow_failed': '提交项目运行请求失败',
      'run_workflow_success': '运行项目成功',
      'run_workflow_failed': '运行项目失败',
      'update_schedule_success': '更新定时设置成功',
      'update_schedule_failed': '更新定时设置失败',
      'delete_schedule_trigger_confirm': '确认删除该定时设置？',
      'delete_schedule_success': '删除定时设置成功',
      'delete_schedule_failed': '删除定时设置失败',
      'brief': '简介',
      'field_is_empty': '{field} 不能为空',
      'record_status': '项目运行记录状态: {status}',
      'record_error_task': '出错任务: {task}',
      'record_error_detail': '错误信息: {detail}',
      'maximize_output': '最大化输出区域',
      'normalize_output': '恢复输出区域尺寸',
    },
    workflowEditor: {
      'exit_not_saved_confirm': '项目尚未保存，确认退出？',
      'save_and_exit': '保存并退出',
      'exit_without_save': '不保存退出',
      'workflow_info': '基本信息',
      'workflow_canvas': '项目画布',
      'workflow_ui_design': '界面设计',
      'tags': '标签',
      'brief_info': '简介信息',
      'brief_images': '简介图片',
      'edit_code': '编辑代码',
      'workflow_check_warning': '项目检查警告',
      'workflow_has_no_inputs': '项目没有输入（请勾选需要显示在使用界面的字段）',
      'workflow_has_no_outputs': '项目没有输出（请从输出里面拖拽一个节点到画布上并连接）',
      'workflow_has_no_triggers': '项目没有触发器（请从触发器里面拖拽一个节点到画布上并连接）',
    },
    workflowSpaceMain: {
      'my_workflows': '我的项目',
      'workflow_title': '项目',
      'tags': '标签',
      'tags_filter': '标签筛选',
      'update_time': '更新时间',
      'create_workflow': '创建项目',
      'official_workflow_template': '公共模板',
      'community_workflow_template': '社区分享项目模板',
      'input_search_text': '输入待搜索的标题、简介等信息',
      'reset_search': '重置',
      'no_workflows_1': '你还没有添加或创建项目',
      'no_workflows_2': '到这里添加一个项目看看吧',
    },
    workflowTemplate: {
      'template': '模板',
      'add_to_my_workflows': '添加到我的项目',
      'add_success': '添加成功',
      'add_failed': '添加失败',
      'author': '作者: {author}',
      'used_count': '{count} 人已使用',
      'workflow_template_tags': '项目模板标签',
      'edit_template': '编辑模板',
      'update_success': '更新成功',
      'update_failed': '更新失败',
    },
    dataSpace: {
      'create': '新建',
      'create_success': '创建成功',
      'create_failed': '创建失败',
      'database_name': '数据库名称',
      'status_invalid': '无效',
      'status_expired': '已过期',
      'status_deleted': '已删除',
      'status_valid': '有效',
      'status_error': '错误',
      'status_creating': '创建中',
      'status_deleting': '删除中',
      'delete': '删除',
      'delete_confirm': '确认删除该数据库？删除后不可恢复！',
      'delete_success': '删除成功',
      'delete_failed': '删除失败',
    },
    databaseDetail: {
      'add_object': '添加数据',
      'object_title': '数据名称',
      'object_source_url': '来源链接',
      'object_type': '数据类型',
      'add_method': '添加方式',
      'add_method_url': '从链接抓取',
      'add_method_files': '上传文件',
      'add_method_text': '输入文本',
      'crawl_data_from_url': '从链接爬取数据',
      'use_oversea_crawler': '使用海外爬虫节点',
      'object_content': '数据内容',
      'content_empty': '内容为空！',
      'create_success': '添加成功',
      'create_failed': '添加失败',
      'delete_success': '删除成功',
      'delete_failed': '删除失败',
      'check_detail_data': '查看详细数据',
      'source_url': '来源链接',
      'data_type': '数据类型',
      'data_type_TEXT': '文本',
      'data_type_IMAGE': '图片',
      'data_type_AUDIO': '音频',
      'data_type_VIDEO': '视频',
      'data_type_OTHER': '其他',
      'delete_confirm': '确认删除该数据？',
      'delete': '删除',
    },
    databaseObjectCreate: {
      'add_object': '添加数据',
      'add_method': '添加方式',
      'add_method_url': '从链接抓取',
      'add_method_files': '上传文件',
      'add_method_text': '输入文本',
      'split_method': '分割方式',
      'split_method_general': '通用分割',
      'split_method_delimeter': '分隔符分割',
      'split_method_markdown': 'Markdown 分割',
      'split_method_table': '表格分割',
      'split_method_chapter': '章节分割',
      'chunk_length': '分段长度',
      'remove_url_and_email': '移除链接和邮箱',
      'use_oversea_crawler': '使用海外爬虫节点',
      'object_source_url': '来源链接',
      'object_files': '文件',
      'object_title': '数据名称',
      'object_content': '数据内容',
      'process_rules': '处理规则',
      'delimiter': '分隔符',
      'finish': '完成',
      'content_empty': '内容为空！',
      'create_success': '添加成功',
      'create_failed': '添加失败',
      question: {
        'chunk_length': {
          '1': '分段长度表示将文本按照多长进行分段，比如 1000 表示每 1000 个字符分成一段。',
          '2': '向量数据库在进行搜索时会找到最相关的段落返回回来。',
          '3': '注意这里的分段长度不是严格遵守的，而是大致接近。',
        },
      },
    },
    databaseObjectDetail: {
      'source_url': '来源链接',
      'segments': '分段内容',
      'full_document': '完整文档',
      'params_info': '参数信息',
      'segment_index': '分段索引',
      'segment_text': '文本',
      'segment_keywords': '关键词',
      'segment_tokens': 'Token 数',
      'segment_word_counts': '字符数',
      'paragraph_counts': '段落数',
      'word_counts': '字符数',
    },
  },
  components: {
    layout: {
      basicHeader: {
        'workflow_space': '首页',
        'data_space': '数据集',
      },
      settingDrawer: {
        'open': '打开设置',
        'close': '关闭设置',
        'save': '保存设置',
        'save_success': '保存成功',
        'my_setting': '我的设置',
        'openai_api_type': 'OpenAI API 类型',
        'openai': 'OpenAI',
        'azure': 'Azure',
        'openai_api_key': 'OpenAI API Key',
        'openai_api_base': 'OpenAI API Base',
        'openai_chat_engine': 'OpenAI Chat Engine',
        'openai_embedding_engine': 'OpenAI Embedding Engine',
        'chatglm6b_api_base': 'ChatGLM-6B API Base',
        'baichuan13b_api_base': 'BaiChuan-13B API Base',
        'output_folder': '输出文件夹',
        'select_folder': '选择文件夹',
        'email_settings': '邮件设置',
        'email_user': '邮箱账号',
        'email_password': '邮箱密码',
        'email_smtp_host': '发信服务器',
        'email_smtp_port': '发信端口号',
        'email_smtp_ssl': 'SMTP SSL',
        'pexels_api_key': 'Pexels API Key',
        'stable_diffusion_base_url': 'Stable Diffusion URL',
        'use_system_proxy': '使用系统代理',
      },
      helpDropdown: {
        'help': '帮助',
        'about': '关于',
        'documentation': '文档',
        'software_update': '软件更新',
        'check_update': '检查更新',
        'update_available': '有新版本可用',
        'new_version': '新版本 {version} {releaseDatetime}',
        'about_vectorvein': '关于向量脉络',
        'about_vectorvein_description': '### 利用 AI 的力量构建您的自动化项目程\n#### 无需编程，只需拖拽即可创建强大的项目，自动化所有任务。\n\n向量脉络（VectorVein）开源版由 Maker毕 开发，可用于个人使用，不可用于商业使用。',
      },
      UserDropdown: {
        'account': '我的账号',
        'logout': '登出'
      }
    },
    markdownEditor: {
      'raw_text': '无格式文本',
      'markdown_text': 'Markdown 文本',
    },
    workspace: {
      workflowEditor: {
        'add_node': '添加节点',
        'add_tag': '添加标签',
        'brief_editor': '描述编辑器',
        'brief_images': '图片',
      },
      uiDesign: {
        'typography-paragraph': {
          'title': '文字内容',
          'placeholder': '支持 Markdown 语法，在使用界面中会被直接渲染',
          'tip': '可用于在使用界面中放置提示性信息',
        }
      },
      uploaderFieldUse: {
        'upload': '上传',
        'upload_success': '{file} 上传成功',
        'upload_failed': '{file} 上传失败',
        'uploader_text': '点击或拖拽文件到此区域上传',
        'uploader_hint': '目前支持的文件类型：{fileTypes}',
      },
      mindmapRenderer: {
        'download_svg': '下载 SVG',
      },
      echartsRenderer: {
        'download_image': '下载图片',
      },
      newWorkflowModal: {
        'create_new_workflow': '创建新项目',
        'empty_workflow': '新建空项目',
      },
      shareWorkflowModal: {
        'share_workflow': '发布项目',
        'title': '标题',
        'brief': '描述',
        'brief_min_require': '描述至少{count}个字符',
        'brief_hint1': '介绍该项目的用途、输入输出等信息，以便其他用户更好地了解该项目。',
        'brief_hint2': '支持 Markdown 格式。',
        'share_to_community': '分享到社区',
        'share_to_community_brief': '分享到社区后，其他用户可以在社区中搜索到该项目。否则仅可通过分享链接访问。',
        'share_success': '发布成功',
        'share_success_brief': '发布到公共模版后，其他用户可以将其添加到自己的项目。',
      },
      tagInput: {
        'select_tags': '选择标签',
      },
      workflowRunRecordsDrawer: {
        'workflows_run_records': '项目运行记录',
        'my_workflows_run_records': '我的项目运行记录',
        'start_time': '开始时间',
        'cost': 'token开销',
        'end_time': '结束时间',
        'used_credits': '消耗积分',
        'status': '状态',
        'status_not_started': '未开始',
        'status_queued': '排队中',
        'status_running': '运行中',
        'status_finished': '已完成',
        'status_failed': '运行失败',
        'check_record': '查看记录',
        'check_record_and_error_task': '查看记录及错误任务',
        'workflow_title': '项目标题',
        'input_tag': "输入标签",
        "output_tag": "输出标签"
      },
      vueFlowStyleSettings: {
        'title': '风格设置',
        'edge_type': '连线类型',
        'edge_type_bezier': '贝塞尔曲线',
        'edge_type_step': '直角台阶',
        'edge_type_smoothstep': '圆角台阶',
        'edge_type_straight': '直线',
        'edge_animated': '连线动画',
      },
    },
    codeEditorModal: {
      'title': '代码编辑器',
      'please_enter_code': '请输入代码，函数名固定为 main，输入参数与设定名称请一致。',
      'copy_code': '复制代码',
      'copy_success': '复制成功',
    },
    templateEditorModal: {
      'title': '模板编辑器',
      'variable_fields': '变量字段',
      'template': '模板',
      'drag_to_insert': '拖拽插入',
    },
    nodes: {
      common: {
        'input': '输入',
        'output': '输出',
      },
      baseNode: {
        'document_link': '文档链接',
        'clone_node': '克隆节点',
        'delete_node': '删除节点',
      },
      baseField: {
        'show_in_use_interface': '是否在使用界面显示',
        'show': '显示',
        'hide': '隐藏',
      },
      listField: {
        'add_item': '添加项',
      },
      assistedNodes: {
        'title': '辅助节点',
        CommentNode: {
          'title': '注释节点',
          'description': '用于添加注释，不会对项目运行产生任何影响。',
          'comment': '注释',
        },
      },
      fileProcessing: {
        'title': '文件处理',
        FileLoader: {
          'title': '读取文件',
          'prompt': '文本内容',
          'description': '读取文件内容。',
          'files': '文件',
          'output': '输出',
        },
        Excel_parse: {
          'title': '批量任务下发',
          'description': '用于批量解析Execl文件，包括：（xls，xlsx）类型',
          'files': '请输入execl文件',
          'prompt': "项目名称",
          'output': '输出',
        }
      },
      textProcessing: {
        title: '文本处理',
        TemplateCompose: {
          'title': '文本合成',
          'description': '将多个变量合成为一段文字。',
          'template': '模板',
          'output': '输出',
          'add_field': '添加变量',
          'add_field_type': '输入类型',
          'field_type_input': '单行输入框',
          'field_type_textarea': '多行输入框',
          'field_type_select': '列表选择输入',
          'add_field_display_name': '显示名称',
          'add_field_list_options': '列表选项',
          'click_to_add_to_template': '点击可将变量添加到模板',
          'open_template_editor': '打开模板编辑器',
        },
        MarkdownToHtml: {
          'title': 'MD 转 HTML',
          'description': '将 Markdown 格式的文本转换为 HTML 格式。',
          'markdown': 'Markdown',
          'html': 'HTML',
        },
        TextSplitters: {
          'title': '文本分割',
          'description': '将文本按照指定的方法分割成多个文本。',
          'text': '文本',
          'split_method': '分割方法',
          'split_method_general': '通用分割',
          'split_method_delimiter': '分隔符分割',
          'split_method_markdown': 'Markdown 分割',
          'split_method_chapter': '章节分割',
          'delimiter': '分隔符',
          'chapter': '章节',
          'chunk_length': '分割长度',
          'chunk_overlap': '分割重叠',
          'output': '输出',
        },
        ListRender: {
          'title': '列表渲染',
          'description': '将列表渲染成文本。',
          'list': '列表',
          'add_item': '添加项',
          'separator': '合并项分隔符',
          'output_type': '输出类型',
          'output_type_text': '文本',
          'output_type_list': '列表',
          'output': '输出',
        },
        TextInOut: {
          'title': '文本输入输出',
          'description': '将输入的文本原样输出。用于多个地方需要同样的文本时。',
          'text': '文本',
          'output': '输出',
        },
        TextTruncation: {
          'title': '文本截断',
          'description': '将文本截取为指定长度。',
          'text': '文本',
          'truncate_method': '截取方法',
          'truncate_method_general': '通用截取',
          'truncate_method_markdown': 'Markdown 截取',
          'truncate_length': '截取范围',
          'floating_range': '浮动范围',
          'output': '输出',
        },
      },
      llms: {
        title: 'AI模型',
        OpenAI: {
          'title': 'OpenAI',
          'description': 'OpenAI 是一个非营利性的研究机构，致力于推动人工智能的安全发展。OpenAI 的研究团队由世界顶级的人工智能专家组成，他们致力于开发人工智能技术，以解决人类面临的最重要的挑战。',
          'prompt': '输入内容（Prompt）',
          'llm_model': '模型',
          'temperature': 'AI 偏好（温度）',
          'creative': '创意',
          'balanced': '平衡',
          'precise': '精准',
          'ignore_error_rate': '报错忽略率',
          'output': '输出',
        },
        Webpilot: {
          'title': 'Webpilot',
          'description': '使用Webpilot获取网络结果',
          'prompt': '提示词',
          'llm_model': '模型',
          'output': '输出',
        },
        ChatGLM: {
          'title': 'ChatGLM',
          'description': 'ChatGLM 系列模型，通过注入代码预训练，有监督微调等技术对齐人类意图，具备问答、多轮对话、代码生成等能力。',
          'prompt': '输入内容（Prompt）',
          'llm_model': '模型',
          'temperature': 'AI 偏好（温度）',
          'creative': '创意',
          'balanced': '平衡',
          'precise': '精准',
          'output': '输出',
        },
        BaiChuan: {
          'title': 'BaiChuan',
          'description': 'BaiChuan 系列模型，通过注入代码预训练，有监督微调等技术对齐人类意图，具备问答、多轮对话、代码生成等能力。',
          'prompt': '输入内容（Prompt）',
          'llm_model': '模型',
          'temperature': 'AI 偏好（温度）',
          'creative': '创意',
          'balanced': '平衡',
          'precise': '精准',
          'output': '输出',
        },
        AsrParaformer: {
          'title': 'AsrParaformer',
          'description': 'AsrParaformer 系列模型，通过注入代码预训练，可以将音频文件转化为文本。',
          'prompt': '输入内容（Prompt）',
          'llm_model': '模型',
          'temperature': 'AI 偏好（温度）',
          'creative': '创意',
          'balanced': '平衡',
          'precise': '精准',
          'output': '输出',
        },
        DeepSeek: {
          'title': 'DeepSeek',
          'description': '使用DeepSeek获取网络结果',
          'prompt': '输入内容',
          'llm_model': '模型',
          'output': '输出',
        },
        Qwen: {
          'title': 'Qwen',
          'description': '使用通义千问模型获取网络结果',
          'prompt': '输入内容',
          'llm_model': '模型',
          'output': '输出',
        },
      },
      imageGeneration: {
        title: '图像生成',
        StableDiffusion: {
          'title': 'Stable Diffusion',
          'description': 'Stable Diffusion 是2022年发布的深度学习文本到图像生成模型。',
          'prompt': '提示词',
          'negative_prompt': '负面提示词',
          'model': '模型',
          'cfg_scale': '提示遵循强度',
          'sampler': '采样器',
          'width': '宽度',
          'height': '高度',
          'output_type': '输出类型',
          'output_type_only_link': '仅路径',
          'output_type_markdown': 'Markdown',
          'output_type_html': 'HTML',
          'output': '输出',
        },
        DallE: {
          'title': 'Dall-e-3',
          'description': 'DALL-E是由OpenAI开发的人工智能模型，它基于GPT-3和VQ-VAE-2技术，能够生成与文本描述相匹配的新颖图像。',
          'prompt': '提示词',
          'model': '模型',
          'size': '尺寸',
          'quality': '质量',
          'output_type': '输出类型',
          'output_type_only_link': '仅路径',
          'output_type_markdown': 'Markdown',
          'output_type_html': 'HTML',
          'output': '输出',
          'style': '风格',
        },
        
      },
      outputs: {
        title: '输出',
        Text: {
          'title': '文本呈现',
          'description': '用于在用户使用界面呈现文本。',
          'text': '文本内容',
          'output_title': '文本标题（用于在使用界面区分模块）',
          'render_markdown': '渲染 Markdown',
          'output': '输出',
        },
        Table: {
          'title': '表格',
          'description': '用于在用户使用界面呈现表格。',
          'text': '文本内容',
          'show_table': '显示表格',
          'delimeter': '分隔符',
          'output': '输出',
        },
        Email: {
          'title': '邮件',
          'description': '用于发送邮件。',
          'to_email': '收件人',
          'subject': '主题',
          'content_html': '内容（HTML）',
        },
        Document: {
          'title': '文档',
          'description': '用于生成文档文件。',
          'file_name': '文件名',
          'content': '内容（文本类建议输入 Markdown 格式内容）',
          'export_type': '文档类型',
          'output_type': '输出类型',
          'output_type_only_path': '仅生成文件路径',
          'output_type_markdown': 'Markdown',
          'output_type_html': 'HTML',
          'show_local_file': '显示本地文件',
          'output': '输出',
        },
        Audio: {
          'title': '音频',
          'description': '用于生成音频文件。',
          'content': '文字内容',
          'show_player': '显示播放器',
          'output_type': '输出类型',
          'output_type_only_link': '仅下载链接文字',
          'output_type_markdown': 'Markdown',
          'output_type_html': 'HTML',
          'output': '输出',
        },
        Mindmap: {
          'title': '思维导图',
          'description': '用于生成思维导图。',
          'content': 'Markdown 内容',
          'show_mind_map': '显示思维导图',
          'output_type': '输出类型',
          'output': '输出',
        },
        Mermaid: {
          'title': 'Mermaid',
          'description': '用于生成 Mermaid 图表。',
          'content': 'Mermaid 内容',
          'show_mermaid': '显示 Mermaid',
          'output_type': '输出类型',
          'output': '输出',
        },
        Echarts: {
          'title': '图表',
          'description': '用于生成 Echarts 图表。',
          'option': 'Echarts 配置项',
          'show_echarts': '显示图表',
          'output_type': '输出类型',
          'output': '输出',
        },
        WorkflowInvokeOutput: {
          'title': '项目调用输出',
          'description': '用于被项目调用节点调用时显示的输出，不显示在使用界面。',
          'value': '数据',
          'display_name': '显示名称',
        },
        Audio: {
          'title': '音频',
          'description': '用于生成音频。',
          'byte_stream': '字节流',
          'show_audio': '显示音频',
          'output': '输出',
        },

      },
      webCrawlers: {
        title: '网络爬虫',
        TextCrawler: {
          'title': '文本爬虫',
          'description': '用于爬取网页中的文本。',
          'url': '网址',
          'output_type': '输出类型',
          'text': '文本',
          'json': 'JSON',
          'use_oversea_crawler': '使用海外爬虫（速度较慢）',
          'output_text': '网页正文文本',
          'output_title': '网页标题',
        },
        TVmaoCrawler: {
          'title': '电视猫爬虫',
          'description': '用于爬取电视猫的分集剧情。',
          'series_name': '电视剧名',
          'output_episodes': '分集剧情',
          'output_info': '相关信息',
        },
        BilibiliCrawler: {
          'title': 'Bilibili爬虫',
          'description': '用于爬取 Bilibili 视频信息。',
          'url_or_bvid': '视频网址或 BVID',
          'output_type': '输出类型',
          'str': '文本',
          'list': '列表',
          'output_subtitle': '字幕',
          'output_title': '标题',
        },
        YoutubeCrawler: {
          'title': 'Youtube爬虫',
          'description': '用于爬取 Youtube 视频信息。',
          'url_or_video_id': '视频网址或视频 ID',
          'output_type': '输出类型',
          'str': '文本',
          'list': '列表',
          'output_subtitle': '字幕',
          'output_title': '标题',
        },
        NovelCrawler: {
          'title': '小说爬虫',
          'description': '用于爬取各类小说网站的排行榜信息。',
          "websiteType": "小说平台",
          "qdSexOptions": "起点榜单类型",
          "rankOptions": "番茄榜单类型",
          "dbListType": "豆瓣榜单类型",
          'prompt': "达标分数",
          'origin_content_output': '原始内容输出',
          "output": "分数过滤输出"
        }
      },
      triggers: {
        title: '触发器',
        ButtonTrigger: {
          'title': '按钮触发器',
          'description': '用于触发项目运行，作为特殊节点，可以不需要与其它节点连接。',
          'button_text': '按钮文字',
          'run': '运行',
          'output': '输出',
        },
        ScheduleTrigger: {
          'title': '定时触发器',
          'description': '用于定时触发项目运行。',
          'schedule': '定时',
          'schedule_settings': '定时设置',
          'save_schedule_settings': '保存定时设置',
          'output': '输出',
        },
      },
      vectorDb: {
        title: '向量数据库',
        AddData: {
          'title': '添加数据',
          'description': '用于向向量数据库中添加数据。',
          'text': '文本',
          'content_title': '标题',
          'source_url': '来源网址',
          'data_type': '数据类型',
          'database': '数据库',
          'split_method': '分割方法',
          'split_method_general': '通用分割',
          'chunk_length': '分割长度',
          'output': '输出',
          'object_id': '数据对象ID',
        },
        DeleteData: {
          'title': '删除数据',
          'description': '用于向向量数据库中删除数据。',
          'object_id': '数据对象 ID',
          'database': '数据库',
          'delete_success': '删除成功',
        },
        Search: {
          'title': '搜索数据',
          'description': '用于搜索向量数据库中的数据。',
          'search_text': '搜索文本',
          'data_type': '数据类型',
          'database': '数据库',
          'count': '搜索结果数量',
          'output_type': '输出类型',
          'text': '文本',
          'list': '列表',
          'output': '输出',
        },
      },
      databases: {
        title: 'sql数据库',
        QueryData: {
          'title': '数据查询',
          'description': '从sql数据库中查询数据',
          'table_name': '表名',
          'delimeter': '分隔符',
          'query': '查询指令',
          'output': '输出',
          'exclude': '排除',
        },
      },
      tools: {
        title: '工具',
        ProgrammingFunction: {
          'title': '编程函数',
          'description': '用于执行编程函数。',
          'language': '编程语言',
          'code': '代码',
          'open_editor': '打开代码编辑器',
          'add_parameter': '添加输入参数',
          'add_parameter_type': '参数类型',
          'parameter_type_str': '字符串',
          'parameter_type_int': '整数',
          'parameter_type_float': '浮点数',
          'parameter_type_bool': '布尔值',
          'parameter_type_list': '列表',
          'add_parameter_name': '参数名称',
          'list_input': '列表形式输入',
          'output': '输出',
        },
        ImageSearch: {
          'title': '图片搜索',
          'description': '用于搜索图片。',
          'search_text': '搜索词',
          'search_engine': '搜索引擎',
          'search_engine_bing': 'Bing',
          'search_engine_pexels': 'Pexels',
          'count': '搜索结果数量',
          'output_type': '输出类型',
          'output_type_text': '文本',
          'output_type_markdown': 'Markdown',
          'output': '输出',
        },
        WorkflowInvoke: {
          'title': '项目调用',
          'description': '用于调用项目并获取结果。',
          'select_workflow': '选择项目',
          'selected_workflow': '已选择项目',
          'workflow_id': '项目 ID',
          'fail_all': '该节点失败则项目整体失败',
          'list_input': '列表形式输入',
          'workflow_fields': '项目字段',
        },
        WorkflowLoopInvoke: {
          'title': '项目循环调用',
          'description': '用于循环调用项目并获取结果。被调用的项目需要有一个文本输出节点。',
          'select_workflow': '选择项目',
          'selected_workflow': '已选择项目',
          'loop_count': '执行次数',
          'loop_output': '输出',
          'loop_end_exp': '设置循环结束条件',
          'loop_end_exp_code': '循环控制代码',
          'workflow_id': '项目 ID',
          'fail_all': '该节点失败则项目整体失败',
          'list_input': '列表形式输入',
          'workflow_fields': '项目字段',
        },
        TaskMonitor: {
          'title': '任务监控',
          'description': '用于监控任务状态，并根据筛选条件获取任务的的属性',
          "urls": "任务url",
          "filter": "筛选条件",
          "output": "输出"
        }
      },
      controlFlows: {
        title: '控制流',
        Empty: {
          'title': '空节点',
          'description': '用于需要确保项目顺序执行的情况。',
          'input': '输入',
          'output': '输出（不改变被连接节点的值）',
        },
        Conditional: {
          'title': '条件判断',
          'description': '用于根据条件判断执行不同的操作。',
          'field_type': '数据类型',
          'field_type_string': '字符串',
          'field_type_number': '数字',
          'left_field': '左侧数据',
          'right_field': '右侧数据',
          'operator': '条件判断运算符',
          'operator_equal': '等于',
          'operator_not_equal': '不等于',
          'operator_greater_than': '大于',
          'operator_less_than': '小于',
          'operator_greater_than_or_equal': '大于等于',
          'operator_less_than_or_equal': '小于等于',
          'operator_include': '左边包含右边',
          'operator_not_include': '左边不包含右边',
          'operator_is_empty': '为空',
          'operator_is_not_empty': '不为空',
          'operator_starts_with': '左边以右边开头',
          'operator_ends_with': '左边以右边结尾',
          'true_output': '满足条件时的输出',
          'false_output': '不满足条件时的输出',
          'output': '输出',
        },
        RandomChoice: {
          'title': '随机选择',
          'description': '用于从列表中随机选择一个元素。',
          'input': '输入',
          'output': '输出',
        },
        JsonProcess: {
          'title': 'JSON 处理',
          'description': '用于处理 JSON 或 Python 的字典数据。',
          'input': '输入',
          'process_mode': '处理模式',
          'process_mode_get_value': '根据 Key 获取值',
          'process_mode_list_values': '列表形式列出所有值',
          'process_mode_list_keys': '列表形式列出所有 Key',
          'key': 'Key',
          'default_value': '默认值（当 Key 不存在时）',
          'output': '输出',
        },
      },
      voice: {
        title: '音频处理',
        TTS: {
          'title': '文本转语音',
          'description': '文本转换为mp3字节流',
          'input': '输入文本',
          'voice': '声线',
          'model': '模型',
          'output': '字节流输出',
        },
      }
    },
  },
  layouts: {
    workspaceLayout: {
      tour: {
        'workflow_button_title': '切换项目界面',
        'workflow_button_description': '点击此按钮可以切换到项目界面。您的项目以及官方模板等均可在此找到。',
        'database_button_title': '切换知识库/数据库界面',
        'database_button_description': '点击此按钮可以切换到数据界面。您可以在此创建您的个人知识库并上传您的数据以在项目中使用。',
      },
    },
  },
}