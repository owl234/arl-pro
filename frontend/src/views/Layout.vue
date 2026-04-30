<template>
  <a-layout style="min-height: 100vh">
    <a-layout-sider v-model:collapsed="collapsed" collapsible :trigger="null" width="170" style="background: #001529;">
      <div class="logo-container" style="height: 64px; display: flex; align-items: center; justify-content: center; background: #002140;">
        <DeploymentUnitOutlined class="logo-icon" :style="{ color: '#00bcd4', fontSize: '20px' }" />
        <span class="logo-text" v-show="!collapsed" style="color: #fff; font-size: 16px; margin-left: 8px; font-weight: bold;">资产灯塔系统</span>
      </div>

      <a-menu v-model:selectedKeys="selectedKeys" theme="dark" mode="inline" @click="handleMenuClick">
        <a-menu-item key="/taskList"><GlobalOutlined /><span>任务管理</span></a-menu-item>
        <a-menu-item key="/asset-search"><SearchOutlined /><span>资产搜索</span></a-menu-item>
        <a-menu-item key="/assetsMonitor"><DesktopOutlined /><span>资产监控</span></a-menu-item>
        <a-menu-item key="/group"><AppstoreOutlined /><span>资产分组</span></a-menu-item>
        <a-menu-item key="/policy"><SettingOutlined /><span>策略配置</span></a-menu-item>
        <a-menu-item key="/fingerprint"><TagsOutlined /><span>指纹管理</span></a-menu-item>
        <a-menu-item key="/pocList"><BugOutlined /><span>PoC信息</span></a-menu-item>
        <a-menu-item key="/planningTasks"><ClockCircleOutlined /><span>计划任务</span></a-menu-item>
        <a-menu-item key="/GitHubTasks/GitHubTasksList"><GithubOutlined /><span>GitHub管理</span></a-menu-item>
        <a-menu-item key="/GitHubMonitor/GitHubMonitorList"><EyeOutlined /><span>GitHub监控</span></a-menu-item>
      </a-menu>
    </a-layout-sider>

    <a-layout>
      <a-layout-header style="background: #fff; padding: 0 24px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 1px 4px rgba(0,21,41,.08); z-index: 10;">
        <div style="display: flex; align-items: center;">
          <span class="trigger" @click="() => (collapsed = !collapsed)" style="font-size: 18px; cursor: pointer; margin-right: 24px;">
            <menu-unfold-outlined v-if="collapsed" /><menu-fold-outlined v-else />
          </span>
          <span style="font-size: 16px; font-weight: 500; color: rgba(0,0,0,.85);">任务管理</span>
        </div>

        <div style="display: flex; align-items: center; color: #555;">
          <a-avatar style="background-color: #87d068; margin-right: 12px;" size="small"><template #icon><UserOutlined /></template></a-avatar>
          <span style="margin-right: 24px;">{{ currentUsername }}</span>
          <LogoutOutlined style="font-size: 16px; cursor: pointer; margin-right: 24px; color: #555;" @click="handleLogout" />
          <span style="cursor: pointer; color: #555;">修改密码</span>
        </div>
      </a-layout-header>

      <a-layout-content style="margin: 16px; display: flex; flex-direction: column;">
        <div style="background: #fff; flex: 1;">
          <router-view></router-view>
        </div>
        <div style="text-align: center; padding: 16px 0; color: rgba(0,0,0,.45); font-size: 12px;">
          Powered by TCC(Tophant Competence Center) ARL 2.6.2
        </div>
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
// 补全所有需要的图标
import { MenuUnfoldOutlined, MenuFoldOutlined, UserOutlined, LogoutOutlined, GlobalOutlined, SearchOutlined, DesktopOutlined, AppstoreOutlined, SettingOutlined, TagsOutlined, BugOutlined, ClockCircleOutlined, GithubOutlined, EyeOutlined, DeploymentUnitOutlined } from '@ant-design/icons-vue';

const route = useRoute();
const router = useRouter();
const collapsed = ref(false);
const selectedKeys = ref([route.path]);
const currentUsername = ref('admin');

onMounted(() => {
  const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');
  if (userInfo.username) currentUsername.value = userInfo.username;
});

const handleMenuClick = (e) => router.push(e.key);

const handleLogout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('userInfo');
  router.push('/login');
};

// 监听路由变化，保持左侧菜单高亮的一致性
watch(() => route.path, (newPath) => {
  // 如果当前在详情页，依然让“任务管理”菜单亮起
  if (newPath.startsWith('/taskList')) {
    selectedKeys.value = ['/taskList'];
  } else {
    selectedKeys.value = [newPath];
  }
}, { immediate: true });

// 动态计算页面标题
const currentPageTitle = computed(() => {
  if (route.path.includes('taskDetail')) return '任务详情'; // 详情页标题
  const titleMap = {
    '/taskList': '任务管理',
    '/search': '资产搜索',
    // ... 其他映射
  };
  return titleMap[route.path] || '资产灯塔系统';
});


</script>