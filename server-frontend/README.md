# Flow Farm 服务器前端

## 功能概述
- 管理员登录界面
- 员工管理面板
- 工作量KPI仪表盘
- 设备状态监控
- 数据报表展示
- 实时数据更新

## 技术栈
- **框架**: React.js + TypeScript
- **UI库**: Ant Design / Material-UI
- **状态管理**: Redux Toolkit
- **图表库**: ECharts / Chart.js
- **HTTP客户端**: Axios
- **构建工具**: Vite
- **部署**: Nginx

## 目录结构
```
server-frontend/
├── public/                # 静态资源
├── src/                   # 源代码
│   ├── components/        # 可复用组件
│   ├── pages/            # 页面组件
│   ├── hooks/            # 自定义Hook
│   ├── services/         # API服务
│   ├── store/            # 状态管理
│   ├── utils/            # 工具函数
│   ├── types/            # 类型定义
│   └── styles/           # 样式文件
├── package.json          # 依赖配置
├── vite.config.ts        # Vite配置
└── README.md            # 说明文档
```

## 主要功能页面
- `/login` - 管理员登录
- `/dashboard` - 总览仪表盘
- `/employees` - 员工管理
- `/kpi` - KPI统计
- `/devices` - 设备监控
- `/reports` - 数据报表
- `/settings` - 系统设置
