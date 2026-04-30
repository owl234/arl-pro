<template>
  <div style="background-color: #fff; padding: 24px; min-height: calc(100vh - 64px);">

    <h2 style="font-size: 20px; font-weight: 500; margin-bottom: 24px;">{{ targetName }}相关资产</h2>

    <a-tabs v-model:activeKey="activeTab" type="card" class="arl-detail-tabs">
      <a-tab-pane key="site" tab="站点"></a-tab-pane>
      <a-tab-pane key="domain" tab="域名"></a-tab-pane>
      <a-tab-pane key="ip" tab="IP"></a-tab-pane>
      <a-tab-pane key="wih" tab="WIH"></a-tab-pane>
    </a-tabs>

    <div v-if="tabConfig[activeTab]?.searchFields" class="search-row" style="margin-bottom: 16px;">
      <div v-for="field in tabConfig[activeTab].searchFields" :key="field.key" class="search-item">
        <span class="label">{{ field.label }}：</span>

        <a-select
            v-if="field.type === 'select'"
            v-model:value="searchForm[field.key]"
            :placeholder="`请选择${field.label}进行搜索`"
            style="width: 180px;"
            allowClear
            @change="onSearch"
        >
          <a-select-option v-for="opt in field.options" :key="opt.value" :value="opt.value">{{ opt.label }}</a-select-option>
        </a-select>

        <a-range-picker
            v-else-if="field.type === 'dateRange'"
            v-model:value="searchForm[field.key]"
            :placeholder="['开始日期', '结束日期']"
            style="width: 260px;"
            @change="onSearch"
        />

        <a-input
            v-else
            v-model:value="searchForm[field.key]"
            :placeholder="`请输入${field.label}进行搜索`"
            style="width: 180px;"
            allowClear
            @pressEnter="onSearch"
        >
          <template #suffix><search-outlined @click="onSearch" style="cursor: pointer; color: rgba(0,0,0,0.25);" /></template>
        </a-input>
      </div>

      <div class="search-item" style="gap: 8px; margin-left: 4px;">
        <a-button @click="resetSearch">清 除</a-button>

        <a-button v-if="activeTab !== 'ip' && tabConfig[activeTab]?.exportUrl" type="primary" style="background-color: #00bcd4; border-color: #00bcd4;" @click="handleExport">导出{{ tabConfig[activeTab].tabName }}</a-button>

        <template v-if="activeTab === 'ip'">
          <a-button type="primary" style="background-color: #00bcd4; border-color: #00bcd4;" @click="handleIPExport('port')">导出 IP 端口</a-button>
          <a-button type="primary" style="background-color: #00bcd4; border-color: #00bcd4;" @click="handleIPExport('domain')">导出域名</a-button>
          <a-button type="primary" style="background-color: #00bcd4; border-color: #00bcd4;" @click="handleIPExport('ip')">导出IP</a-button>
        </template>

        <a-button v-if="activeTab === 'site'" type="primary" style="background-color: #00bcd4; border-color: #00bcd4;" @click="openRiskModal">风险任务下发</a-button>
      </div>

      <div v-if="activeTab === 'ip' || activeTab === 'wih'" style="margin-left: auto;">
        <a-button :disabled="!hasSelected" @click="handleBatchDelete">批量删除</a-button>
      </div>
    </div>

    <div v-if="activeTab === 'site' || activeTab === 'domain'" style="margin-bottom: 16px; display: flex; gap: 8px;">
      <a-button :disabled="!hasSelected" @click="handleBatchDelete">批量删除</a-button>
      <a-button v-if="activeTab === 'site'" type="primary" style="background-color: #00bcd4; border-color: #00bcd4;" @click="openAddSiteModal">添加站点</a-button>
      <a-button v-if="activeTab === 'domain'" type="primary" style="background-color: #00bcd4; border-color: #00bcd4;" @click="openAddDomainModal">添加子域名</a-button>
    </div>

    <a-table :row-selection="{ selectedRowKeys: selectedRowKeys, onChange: onSelectChange }" :loading="loading" :dataSource="dataSource" :columns="columns" :pagination="false" :scroll="{ x: 'max-content' }" size="middle" :rowKey="(record) => record._id || record.id">
      <template #bodyCell="{ column, record, index }">

        <template v-if="column.key === 'index'">
          <span style="color: #00bcd4;">{{ (pagination.current - 1) * pagination.pageSize + index + 1 }}</span>
        </template>

        <template v-else-if="column.key === 'site'">
          <div class="site-header">
            <a :href="record.site || record.url" target="_blank" style="color: #00bcd4; font-weight: 500;">
              <img v-if="record.favicon && record.favicon.data" :src="`data:image/png;base64,${record.favicon.data}`" class="site-img" />
              {{ record.site || record.url }}
            </a>
            <div class="mt5" style="display: flex; align-items: center; flex-wrap: wrap; gap: 4px;">
              <a-tag v-if="record.tag && record.tag.includes('入口')" closable style="background: #fafafa; color: #666; border-color: #d9d9d9;">入口</a-tag>
              <template v-for="(t, idx) in (record.tag || [])" :key="idx">
                <a-tag v-if="t !== '入口'" closable style="background: #fafafa; color: #666; border-color: #d9d9d9;">{{ t }}</a-tag>
              </template>
              <span class="add-tag">添加标签</span>
            </div>
          </div>
        </template>

        <template v-else-if="column.key === 'headers'"><div class="scroll-x"><pre>{{ record.headers }}</pre></div></template>
        <template v-else-if="column.key === 'finger'"><div v-if="record.finger"><p v-for="f in record.finger" :key="f.name" style="margin-bottom: 4px; color: rgba(0,0,0,0.65);">{{ f.name }}</p></div></template>

        <template v-else-if="column.key === 'record'">
          <div v-if="record.record && record.record.length"><div v-for="(r, i) in record.record" :key="i">{{ r }}</div></div>
          <span v-else-if="typeof record.record === 'string'">{{ record.record }}</span>
          <span v-else>-</span>
        </template>
        <template v-else-if="column.key === 'ips'">
          <div v-if="record.ips && record.ips.length">
            <a-tooltip v-if="record.ips.length > 5" placement="top" :overlayInnerStyle="{ maxHeight: '400px', overflowY: 'auto' }">
              <template #title><div v-for="(ip, i) in record.ips" :key="'all-ip-'+i">{{ ip }}</div></template>
              <div style="cursor: pointer;">
                <div v-for="(ip, i) in record.ips.slice(0, 5)" :key="i">{{ ip }}</div>
                <div style="color: #999; margin-top: 2px;">...等 {{ record.ips.length }} 个</div>
              </div>
            </a-tooltip>
            <div v-else><div v-for="(ip, i) in record.ips" :key="i">{{ ip }}</div></div>
          </div>
          <span v-else>-</span>
        </template>

        <template v-else-if="column.key === 'port_info'">
          <span>{{ record.port_info && record.port_info.length ? record.port_info.map(p => p.port_id).join(', ') : '-' }}</span>
        </template>
        <template v-else-if="column.key === 'os_info'"><span>{{ record.os_info?.name || '-' }}</span></template>
        <template v-else-if="column.key === 'geo_city'"><span>{{ record.geo_city ? `${record.geo_city.country_name || 'null'} / ${record.geo_city.city || 'null'}` : '-' }}</span></template>
        <template v-else-if="column.key === 'geo_asn'"><span>{{ record.geo_asn?.organization || '-' }}</span></template>
        <template v-else-if="column.key === 'domain' && Array.isArray(record.domain)">
          <div v-for="(dom, i) in record.domain" :key="i">{{ dom }}</div>
        </template>

        <template v-else-if="column.key === 'source'">
          <div style="word-break: break-all; color: rgba(0,0,0,0.85); line-height: 1.6;">
            <a :href="record.source" target="_blank" style="color: #333; text-decoration: none;">
              {{ record.source || '-' }}
            </a>
          </div>
        </template>

      </template>
    </a-table>

    <div v-if="tabConfig[activeTab]" style="display: flex; justify-content: space-between; align-items: center; padding: 0 16px; margin-top: 16px;">
      <div style="color: rgba(0,0,0,.65);">共 {{ Math.ceil(pagination.total / pagination.pageSize) || 1 }} 页 / {{ pagination.total }} 条数据</div>
      <a-pagination v-model:current="pagination.current" v-model:pageSize="pagination.pageSize" :total="pagination.total" show-size-changer @change="handleTableChange" />
    </div>

    <a-modal v-model:open="addSiteVisible" title="添加站点" @ok="submitAddSite" :confirmLoading="addSiteLoading" width="520px" okText="确 定" cancelText="取 消" destroyOnClose>
      <a-form ref="addSiteFormRef" :model="addSiteForm" :rules="addSiteRules" :label-col="{ span: 4 }" :wrapper-col="{ span: 19 }" style="margin-top: 20px;">
        <a-form-item label="站点" name="site">
          <a-textarea v-model:value="addSiteForm.site" :rows="4" placeholder="会对站点进行探测，获取标题、headers, finger等信息。示例：https://www.freebuf.com/" />
        </a-form-item>
        <a-form-item label="策略" name="policy_id">
          <a-select v-model:value="addSiteForm.policy_id" placeholder="请选择策略">
            <a-select-option v-for="p in policies" :key="p._id" :value="p._id">{{ p.name }}</a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>

    <a-modal v-model:open="riskModalVisible" title="添加风险巡航任务" @ok="submitRiskTask" :confirmLoading="riskLoading" width="520px" okText="确 定" cancelText="取 消" destroyOnClose>
      <a-form ref="riskFormRef" :model="riskForm" :rules="riskRules" :label-col="{ span: 5 }" :wrapper-col="{ span: 18 }" style="margin-top: 20px;">

        <a-form-item label="策略名称" name="policy_id">
          <a-select v-model:value="riskForm.policy_id" placeholder="请选择策略" @change="handleRiskPolicyChange">
            <a-select-option v-for="p in policies" :key="p._id" :value="p._id">
              {{ p.name }} (PoC : {{ getPocCount(p) }})
            </a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="任务名称" name="name">
          <a-input v-model:value="riskForm.name" placeholder="请输入任务名称" allowClear />
        </a-form-item>

        <a-form-item label="目标" style="margin-bottom: 0;">
          <span style="color: rgba(0,0,0,0.65);">选择目标数 {{ currentTargetCount }}</span>
        </a-form-item>

      </a-form>
    </a-modal>

    <a-modal v-model:open="addDomainVisible" title="添加子域名" @ok="submitAddDomain" :confirmLoading="addDomainLoading" width="520px" okText="确 定" cancelText="取 消" destroyOnClose>
      <a-form ref="addDomainFormRef" :model="addDomainForm" :rules="addDomainRules" :label-col="{ span: 4 }" :wrapper-col="{ span: 19 }" style="margin-top: 20px;">
        <a-form-item label="子域名" name="domain">
          <a-textarea v-model:value="addDomainForm.domain" :rows="4" placeholder="会对子域名自动下发侦察任务，获取子域名关联的ip、站点等信息。示例：live.freebuf.com" />
        </a-form-item>
        <a-form-item label="策略" name="policy_id">
          <a-select v-model:value="addDomainForm.policy_id" placeholder="请选择策略">
            <a-select-option v-for="p in policies" :key="p._id" :value="p._id">{{ p.name }}</a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>

  </div>
</template>

<script setup>
import { ref, onMounted, reactive, watch, computed, createVNode } from 'vue';
import { useRoute } from 'vue-router';
import request from '../utils/request';
import { message, Modal } from 'ant-design-vue';
import { SearchOutlined , ExclamationCircleOutlined} from '@ant-design/icons-vue';

const route = useRoute();
// 🚨 修复 1：使用 computed，让路由参数具备真正的响应式
const scope_id = computed(() => route.query.scope_id || '');
const targetName = computed(() => route.query.targetName || '未知资产');

const activeTab = ref('site');
const loading = ref(false);
const dataSource = ref([]);
const searchForm = ref({});
const pagination = reactive({ current: 1, pageSize: 10, total: 0 });

const selectedRowKeys = ref([]);
const hasSelected = computed(() => selectedRowKeys.value.length > 0);
const onSelectChange = (keys) => { selectedRowKeys.value = keys; };

// 💡 针对分组详情定制的 Config (以站点为例，去掉了截图，加了更新时间)
// 💡 完整版的 Config：涵盖站点、域名、IP、WIH
// 💡 修复版 Config：使用 asset_ 前缀的专属接口，并修正日期字段
const tabConfig = {
  site: {
    url: '/asset_site/', // 🚨 核心修复：加了 asset_ 前缀
    exportUrl: '/asset_site/export/', // 🚨 绑定抓包里的导出 URL
    tabName: '站点',
    searchFields: [
      { label: '站点', key: 'site', operator: '=' },
      { label: '主机名', key: 'hostname', operator: '=' },
      { label: '标题', key: 'title', operator: '=' },
      { label: 'Web Server', key: 'http_server', operator: '=' },
      { label: '状态码', key: 'status', operator: '=' },
      // 🚨 补充丢失的 4 个字段
      { label: '标头', key: 'headers', operator: '=' },
      { label: '指纹', key: 'finger.name', operator: '=' },
      { label: 'favicon hash', key: 'favicon.hash', operator: '=' },
      { label: '标签', key: 'tag', operator: '=' },
      { label: '更新时间', key: 'update_date', type: 'dateRange' }
    ],
    cols: [
      { title: '序号', key: 'index', width: 60, align: 'center' },
      { title: '站点', dataIndex: 'site', key: 'site', width: 250 },
      { title: '标题', dataIndex: 'title', key: 'title', width: 200 },
      { title: 'headers', key: 'headers', width: 400 },
      { title: 'finger', key: 'finger', width: 150 },
      { title: '更新时间', dataIndex: 'update_date', key: 'update_date', width: 180 } // 修正字段名
    ]
  },
  domain: {
    url: '/asset_domain/',
    exportUrl: '/asset_domain/export/',
    tabName: '域名',
    // 🚨 修复：严格对齐截图中的 6 个搜索框顺序和文案
    searchFields: [
      { label: '域名', key: 'domain', operator: '=' },
      { label: '记录值', key: 'record', operator: '=' },
      { label: '类型', key: 'type', operator: '=' }, // 调整到第 3 位
      { label: 'IP', key: 'ips', operator: '=' },    // 调整到第 4 位
      { label: '来源', key: 'source', operator: '=' },
      { label: '更新时间', key: 'update_date', type: 'dateRange' }
    ],
    cols: [
      // ... cols 保持不变，上一轮猜得完全正确 ...
      { title: '序号', key: 'index', width: 60, align: 'center' },
      { title: '域名', dataIndex: 'domain', key: 'domain', width: 220 },
      { title: '解析类型', dataIndex: 'type', key: 'type', width: 100 },
      { title: '记录值', key: 'record', width: 280 },
      { title: '关联IP', key: 'ips', width: 280 },
      { title: '来源', dataIndex: 'source', key: 'source', width: 150 },
      { title: '更新时间', dataIndex: 'update_date', key: 'update_date', width: 180 }
    ]
  },
  ip: {
    url: '/asset_ip/',
    tabName: 'IP',
    // 🚨 修复：完美对齐截图的 7 个搜索字段，首个为下拉框
    searchFields: [
      { label: 'IP类别', key: 'ip_type', type: 'select', options: [{label: 'PUBLIC', value: 'PUBLIC'}, {label: 'PRIVATE', value: 'PRIVATE'}] },
      { label: 'IP', key: 'ip', operator: '=' },
      { label: '端口', key: 'port_info.port_id', operator: '=' },
      { label: '操作系统', key: 'os_info.name', operator: '=' }, // ARL 默认 OS 字段名
      { label: '域名', key: 'domain', operator: '=' },
      { label: 'CDN', key: 'cdn_name', operator: '=' },
      { label: '更新时间', key: 'update_date', type: 'dateRange' }
    ],
    // 🚨 修复：移除原本多余的 CDN 列，严格对齐截图列名
    cols: [
      { title: '序号', key: 'index', width: 60, align: 'center' },
      { title: 'IP', dataIndex: 'ip', key: 'ip', width: 160 },
      { title: '操作系统', key: 'os_info', width: 150 },
      { title: '开放端口', key: 'port_info', width: 200 },
      { title: '关联域名', key: 'domain', width: 250 },
      { title: 'Geo', key: 'geo_city', width: 180 },
      { title: 'AS', key: 'geo_asn', width: 280 },
      { title: '更新时间', dataIndex: 'update_date', key: 'update_date', width: 180 }
    ]
  },
  wih: {
    url: '/asset_wih/',
    exportUrl: '/asset_wih/export/', // 🚨 激活“导出WIH”按钮
    tabName: 'WIH',
    // 🚨 完美对齐截图的 4 个搜索框，记录类型带下拉选择
    searchFields: [
      {
        label: '记录类型',
        key: 'record_type',
        type: 'select',
        options: [
          {label: 'domain', value: 'domain'}, {label: 'ip', value: 'ip'},
          {label: 'email', value: 'email'}, {label: 'phone', value: 'phone'},
          {label: 'idcard', value: 'idcard'}, {label: 'jwt', value: 'jwt'},
          {label: 'url', value: 'url'}, {label: 'path', value: 'path'}
        ]
      },
      { label: '内容', key: 'content', operator: '=' },
      { label: '来源 JS', key: 'source', operator: '=' },
      { label: '来源站点', key: 'site', operator: '=' }
    ],
    // 🚨 完美对齐抓包数据的列，特别是 source 键名
    cols: [
      { title: '序号', key: 'index', width: 60, align: 'center' },
      { title: '记录类型', dataIndex: 'record_type', key: 'record_type', width: 120 },
      { title: '内容', dataIndex: 'content', key: 'content', width: 250 },
      { title: '来源 JS', dataIndex: 'source', key: 'source', width: 450 }, // 绑定 source
      { title: '来源站点', dataIndex: 'site', key: 'site', width: 250 },
      { title: '更新时间', dataIndex: 'update_date', key: 'update_date', width: 180 }
    ]
  }
};

const columns = ref(tabConfig.site.cols);

const fetchData = async () => {
  const config = tabConfig[activeTab.value];
  if (!config) return;

  loading.value = true;
  try {
    // 🚨 修复 2：获取 computed 响应式对象的最新值
    const params = { page: pagination.current, size: pagination.pageSize, scope_id: scope_id.value };

    for (const key in searchForm.value) {
      if (searchForm.value[key] !== '' && searchForm.value[key] != null) {
        // 如果是时间范围数组，则特殊处理给后端
        if (key === 'update_date' && Array.isArray(searchForm.value[key])) {
          // 🚨 核心对齐：精准替换为 ARL 专属的 __dgt 和 __dlt 参数名，并格式化为全时分秒
          params.update_date__dgt = searchForm.value[key][0].format('YYYY-MM-DD HH:mm:ss');
          params.update_date__dlt = searchForm.value[key][1].format('YYYY-MM-DD HH:mm:ss');
        } else {
          params[key] = searchForm.value[key];
        }
      }
    }
    const res = await request.get(config.url, { params });
    if (res.code === 200) {
      dataSource.value = res.items || [];
      pagination.total = res.total || 0;
      selectedRowKeys.value = [];
    }
  } catch (error) {
    message.error('加载数据失败');
  } finally {
    loading.value = false;
  }
};

const onSearch = () => { pagination.current = 1; fetchData(); };
const resetSearch = () => { searchForm.value = {}; onSearch(); };
const handleTableChange = (page, pageSize) => { pagination.current = page; pagination.pageSize = pageSize; fetchData(); };

// ================= 批量删除功能 (兼容所有 Tab) =================
const handleBatchDelete = () => {
  Modal.confirm({
    title: '批量删除确认',
    icon: createVNode(ExclamationCircleOutlined),
    content: `确定要从当前分组中删除选中的 ${selectedRowKeys.value.length} 条资产吗？删除后不可恢复。`,
    okText: '确 定',
    okType: 'danger',
    cancelText: '取 消',
    onOk: async () => {
      try {
        const config = tabConfig[activeTab.value];
        if (!config || !config.url) return;

        // 🚨 动态拼接删除 API 路径：例如 /asset_domain/ -> /asset_domain/delete/
        const deleteUrl = `${config.url}delete/`;

        // 🚨 严格按照抓包 Payload：键名为 _id
        const res = await request.post(deleteUrl, {
          _id: selectedRowKeys.value
        });

        if (res.code === 200) {
          message.success('批量删除成功！');

          // 如果删光了当前页的数据且不在第一页，自动回退一页
          if (dataSource.value.length === selectedRowKeys.value.length && pagination.current > 1) {
            pagination.current -= 1;
          }

          selectedRowKeys.value = []; // 清空选中状态
          fetchData(); // 🚨 完美对齐抓包里的第二个请求：自动刷新表格数据
        } else {
          message.error('删除失败: ' + res.message);
        }
      } catch (error) {
        message.error('请求异常，删除失败');
      }
    }
  });
};
const openAction = (action) => { message.info(`准备开发弹窗: ${action}`); };

watch(activeTab, (newVal) => {
  if (tabConfig[newVal]) {
    columns.value = tabConfig[newVal].cols;
    searchForm.value = {};
    pagination.current = 1;
    fetchData();
  }
});

// 🚨 修复 3：监听 scope_id 的变化，无论是初次进入还是组件复用，只要 ID 变了就刷新数据！
watch(scope_id, (newId) => {
  if (newId) {
    pagination.current = 1;
    fetchData();
  }
}, { immediate: true }); // immediate: true 完美替代了 onMounted 的作用


// ================= 导出功能 (站点、域名、WIH 通用) =================
const handleExport = async () => {
  const config = tabConfig[activeTab.value];
  if (!config || !config.exportUrl) return;

  try {
    message.loading({ content: `正在生成导出文件...`, key: 'export_data' });

    // 🚨 动态映射真实的 tabIndex
    const tabIndexMap = { site: 0, domain: 1, ip: 2, wih: 3 };

    // 🚨 完美对齐 WIH 抓包：size 扩大到十万级 100000，并带上动态的 tabIndex
    const params = {
      page: 1,
      size: 100000,
      scope_id: scope_id.value,
      targetName: targetName.value,
      tabIndex: tabIndexMap[activeTab.value]
    };

    // 🚨 补全缺失的搜索参数：确保用户过滤后导出的数据也是精准的！
    for (const key in searchForm.value) {
      if (searchForm.value[key] !== '' && searchForm.value[key] != null) {
        if (key === 'update_date' && Array.isArray(searchForm.value[key])) {
          params.update_date__dgt = searchForm.value[key][0].format('YYYY-MM-DD HH:mm:ss');
          params.update_date__dlt = searchForm.value[key][1].format('YYYY-MM-DD HH:mm:ss');
        } else {
          params[key] = searchForm.value[key];
        }
      }
    }

    const res = await request.get(config.exportUrl, { params, responseType: 'blob' });

    const blob = new Blob([res], { type: 'text/plain;charset=utf-8' });
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = `ARL_Group_Export_${activeTab.value}_${new Date().getTime()}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);

    message.success({ content: `导出成功！`, key: 'export_data', duration: 2 });
  } catch (error) {
    message.error({ content: `导出异常`, key: 'export_data', duration: 2 });
  }
};



// ================= IP专属导出占位 =================
// ================= IP专属导出 =================
const handleIPExport = async (type) => {
  let exportUrl = '';
  let typeName = '';

  // 🚨 完美映射抓包里的 3 个真实 API 路径
  if (type === 'port') {
    exportUrl = '/asset_ip/export/';
    typeName = 'IP端口';
  } else if (type === 'domain') {
    exportUrl = '/asset_ip/export_domain/';
    typeName = '域名';
  } else if (type === 'ip') {
    exportUrl = '/asset_ip/export_ip/';
    typeName = 'IP';
  }

  if (!exportUrl) return;

  try {
    message.loading({ content: `正在打包生成文件...`, key: 'export_ip_data' });

    // 🚨 完美对齐 Payload，并自动带上当前所有的搜索过滤条件
    const params = {
      page: 1,
      size: 10000,
      scope_id: scope_id.value,
      targetName: targetName.value,
      tabIndex: 2
    };

    for (const key in searchForm.value) {
      if (searchForm.value[key] !== '' && searchForm.value[key] != null) {
        if (key === 'update_date' && Array.isArray(searchForm.value[key])) {
          params.update_date__dgt = searchForm.value[key][0].format('YYYY-MM-DD HH:mm:ss');
          params.update_date__dlt = searchForm.value[key][1].format('YYYY-MM-DD HH:mm:ss');
        } else {
          params[key] = searchForm.value[key];
        }
      }
    }

    // 发起 Blob 下载请求
    const res = await request.get(exportUrl, { params, responseType: 'blob' });

    // 触发浏览器的原生下载动作
    const blob = new Blob([res], { type: 'text/plain;charset=utf-8' });
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = `ARL_Group_Export_${typeName}_${new Date().getTime()}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);

    message.success({ content: `导出 ${typeName} 成功！`, key: 'export_ip_data', duration: 2 });
  } catch (error) {
    message.error({ content: `导出异常，请重试`, key: 'export_ip_data', duration: 2 });
  }
};


// ================= 添加站点弹窗 =================
const addSiteVisible = ref(false);
const addSiteLoading = ref(false);
const addSiteFormRef = ref();
const policies = ref([]);

const addSiteForm = reactive({ site: '', policy_id: undefined });
const addSiteRules = {
  site: [{ required: true, message: '请输入站点' }],
  policy_id: [{ required: true, message: '请选择策略' }]
};

const openAddSiteModal = async () => {
  addSiteForm.site = '';
  addSiteForm.policy_id = undefined;
  addSiteVisible.value = true;
  // 获取策略下拉列表
  if(policies.value.length === 0) {
    const res = await request.get('/policy/', { params: { size: 1000 } });
    if(res.code === 200) policies.value = res.items || [];
  }
};

const submitAddSite = async () => {
  await addSiteFormRef.value.validate();
  addSiteLoading.value = true;
  try {
    const res = await request.post('/asset_site/', {
      scope_id: scope_id.value,
      site: addSiteForm.site,
      policy_id: addSiteForm.policy_id
    });

    // 🚨 完美还原抓包：正常成功是 200，如果资产不在范围内是 802
    if (res.code === 200) {
      message.success('添加站点成功！');
      addSiteVisible.value = false;
      fetchData(); // 刷新表格
    } else if (res.code === 802) {
      message.error(res.message); // 弹出 "任务目标不在资产组中"
    } else {
      message.error('添加失败: ' + res.message);
    }
  } catch (e) {
    message.error('请求异常');
  } finally {
    addSiteLoading.value = false;
  }
};

// ================= 风险任务下发 =================
const riskModalVisible = ref(false);
const riskLoading = ref(false);
const riskFormRef = ref();
const currentResultSetId = ref(''); // 保存弹药箱 ID
const currentTargetCount = ref(0); // 保存查出来的目标数量

const riskForm = reactive({ name: '', policy_id: undefined });
const riskRules = {
  name: [{ required: true, message: '请输入任务名称' }],
  policy_id: [{ required: true, message: '请选择策略' }]
};
// 统计目标数量
const getPocCount = (policy) => {
  return policy.policy?.poc_config?.filter(poc => poc.enable)?.length || 0;
};

// 1. 打开弹窗：打包结果集 & 获取策略
const openRiskModal = async () => {
  try {
    message.loading({ content: '正在打包目标集合...', key: 'risk_task' });

    // 构建过滤参数（和搜索一模一样，确保下发的就是当前查出来的）
    const params = { scope_id: scope_id.value };
    for (const key in searchForm.value) {
      if (searchForm.value[key] !== '' && searchForm.value[key] != null) {
        if (key === 'update_date' && Array.isArray(searchForm.value[key])) {
          params.update_date__dgt = searchForm.value[key][0].format('YYYY-MM-DD HH:mm:ss');
          params.update_date__dlt = searchForm.value[key][1].format('YYYY-MM-DD HH:mm:ss');
        } else {
          params[key] = searchForm.value[key];
        }
      }
    }

    // 发起结果集保存请求
    const setRes = await request.get('/asset_site/save_result_set/', { params });
    if (setRes.code !== 200) throw new Error('生成结果集失败');

    currentResultSetId.value = setRes.data.result_set_id;
    // 🚨 将后端返回的真实数量赋给弹窗展示
    currentTargetCount.value = setRes.data.result_total || 0;

    // 复用之前的 policies 拉取逻辑，没有才去拉
    if (policies.value.length === 0) {
      const polRes = await request.get('/policy/', { params: { size: 1000 } });
      if (polRes.code === 200) policies.value = polRes.items || [];
    }

    message.success({ content: `成功锁定 ${setRes.data.result_total} 条资产准备下发`, key: 'risk_task' });

    // 初始化弹窗数据
    riskForm.name = '';
    riskForm.policy_id = undefined;
    riskModalVisible.value = true;
  } catch (e) {
    message.error({ content: '准备下发任务失败', key: 'risk_task' });
  }
};

// 2. 选择策略时：极客级自动推导任务名称
const handleRiskPolicyChange = (val) => {
  const selected = policies.value.find(p => p._id === val);
  if (selected) {
    // 🚨 调用公共函数获取 PoC 数量
    const pocCount = getPocCount(selected);
    riskForm.name = `风险巡航任务-${selected.name} (PoC : ${pocCount})`;
  }
};

// 3. 提交任务
const submitRiskTask = async () => {
  await riskFormRef.value.validate();
  riskLoading.value = true;
  try {
    const payload = {
      name: riskForm.name,
      task_tag: 'risk_cruising',
      target: '', // 因为用了结果集，所以 target 留空
      policy_id: riskForm.policy_id,
      result_set_id: currentResultSetId.value
    };

    const res = await request.post('/task/policy/', payload);

    if (res.code === 200) {
      message.success('风险任务下发成功！');
      riskModalVisible.value = false;
    } else {
      message.error('下发失败: ' + res.message);
    }
  } catch (e) {
    console.warn('请求异常', e);
  } finally {
    riskLoading.value = false;
  }
};

// ================= 添加子域名弹窗 =================
const addDomainVisible = ref(false);
const addDomainLoading = ref(false);
const addDomainFormRef = ref();

const addDomainForm = reactive({ domain: '', policy_id: undefined });
const addDomainRules = {
  domain: [{ required: true, message: '请输入子域名' }],
  policy_id: [{ required: true, message: '请选择策略' }]
};

const openAddDomainModal = async () => {
  addDomainForm.domain = '';
  addDomainForm.policy_id = undefined;
  addDomainVisible.value = true;

  // 复用之前写好的拉取策略逻辑，避免重复请求
  if(policies.value.length === 0) {
    const res = await request.get('/policy/', { params: { size: 1000 } });
    if(res.code === 200) policies.value = res.items || [];
  }
};

const submitAddDomain = async () => {
  await addDomainFormRef.value.validate();
  addDomainLoading.value = true;
  try {
    const res = await request.post('/asset_domain/', {
      scope_id: scope_id.value,
      domain: addDomainForm.domain, // 🚨 注意这里 payload 的 key 是 domain
      policy_id: addDomainForm.policy_id
    });

    // 🚨 完美拦截原版状态码：成功是 200，越界是 701
    if (res.code === 200) {
      message.success('添加子域名成功！');
      addDomainVisible.value = false;
      fetchData(); // 自动刷新当前页面的域名列表
    } else if (res.code === 701) {
      message.error(res.message); // 原汁原味抛出：域名不在给定的资产范围中
    } else {
      message.error('添加失败: ' + res.message);
    }
  } catch (e) {
    message.error('请求异常');
  } finally {
    addDomainLoading.value = false;
  }
};

</script>

<style scoped>
/* 🚨 将原本的 gap: 16px 24px 改为更紧凑的 16px 12px */
.search-row { display: flex; flex-wrap: wrap; gap: 16px 12px; align-items: center; }
.search-item { display: flex; align-items: center; }
.search-item .label { color: rgba(0,0,0,0.85); margin-right: 8px; min-width: 60px; text-align: right; white-space: nowrap; }
.scroll-x { width: 100%; max-width: 400px; overflow-x: auto; }
.scroll-x pre { margin: 0; font-family: Consolas, monospace; font-size: 12px; color: rgba(0, 0, 0, 0.65); }
:deep(.ant-tabs-card-bar .ant-tabs-tab) { border-radius: 2px 2px 0 0 !important; margin-right: 4px !important; border: 1px solid #e8e8e8 !important; background: #fafafa !important; }
:deep(.ant-tabs-card-bar .ant-tabs-tab-active) { background: #fff !important; color: #00bcd4 !important; font-weight: 500; border-bottom-color: transparent !important; }

.site-header { line-height: 1.5; }
.site-img { width: 16px; height: 16px; margin-right: 8px; vertical-align: middle; }
.add-tag { color: #666; cursor: pointer; font-size: 12px; border: 1px dashed #d9d9d9; padding: 0 7px; border-radius: 2px; background: #fafafa; transition: all 0.3s; }
.add-tag:hover { color: #00bcd4; border-color: #00bcd4; }
.mt5 { margin-top: 5px; }

</style>