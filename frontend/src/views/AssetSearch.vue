<template>
  <div style="background-color: #fff; padding: 24px; min-height: calc(100vh - 64px);">

    <a-tabs v-model:activeKey="activeTab" type="card" class="arl-detail-tabs">
      <a-tab-pane key="site" tab="站点"></a-tab-pane>
      <a-tab-pane key="domain" tab="子域名"></a-tab-pane>
      <a-tab-pane key="ip" tab="IP"></a-tab-pane>
    </a-tabs>

    <div v-if="tabConfig[activeTab]?.searchFields" class="search-row" style="margin-bottom: 16px;">
      <div v-for="field in tabConfig[activeTab].searchFields" :key="field.key" class="search-item">
        <span class="label">{{ field.label }}：</span>

        <a-select
            v-if="field.type === 'select'"
            v-model:value="searchForm[field.key]"
            :placeholder="`请选择${field.label}`"
            style="width: 200px;"
            allowClear
            @change="onSearch"
        >
          <a-select-option v-for="opt in field.options" :key="opt.value" :value="opt.value">
            {{ opt.label }}
          </a-select-option>
        </a-select>

        <a-input
            v-else
            v-model:value="searchForm[field.key]"
            :placeholder="`请输入${field.label}`"
            style="width: 200px;"
            allowClear
            @pressEnter="onSearch"
        >
          <template #suffix>
            <search-outlined @click="onSearch" style="cursor: pointer; color: rgba(0,0,0,0.25);" />
          </template>
        </a-input>
      </div>
    </div>

    <div style="margin-bottom: 16px;">
      <a-button style="margin-right: 16px;" @click="resetSearch">清 除</a-button>
      <a-button v-if="tabConfig[activeTab]?.exportName" type="primary" style="background-color: #00bcd4; border-color: #00bcd4; margin-right: 16px;" @click="handleExport">导出{{ tabConfig[activeTab].exportName }}</a-button>
      <a-button v-if="activeTab === 'site'" type="primary" style="background-color: #00bcd4; border-color: #00bcd4;" @click="openRiskModal">风险任务下发</a-button>
    </div>

    <a-table
        :loading="loading"
        :dataSource="dataSource"
        :columns="columns"
        :pagination="false"
        :scroll="{ x: 'max-content' }"
        size="middle"
        :rowKey="(record) => record._id || record.id"
    >
      <template #bodyCell="{ column, record, index }">
        <template v-if="column.key === 'index'">
          <span style="color: #00bcd4;">{{ (pagination.current - 1) * pagination.pageSize + index + 1 }}</span>
        </template>


        <template v-else-if="column.key === 'record'">
          <div v-if="record.record && record.record.length">
            <div v-for="(r, i) in record.record" :key="i">{{ r }}</div>
          </div>
          <span v-else-if="typeof record.record === 'string'">{{ record.record }}</span>
          <span v-else>-</span>
        </template>

        <template v-else-if="column.key === 'ips'">
          <div v-if="record.ips && record.ips.length">
            <a-tooltip v-if="record.ips.length > 5" placement="top" :overlayInnerStyle="{ maxHeight: '400px', overflowY: 'auto' }">
              <template #title>
                <div v-for="(ip, i) in record.ips" :key="'all-ip-'+i">{{ ip }}</div>
              </template>
              <div style="cursor: pointer;">
                <div v-for="(ip, i) in record.ips.slice(0, 5)" :key="i">{{ ip }}</div>
                <div style="color: #999; margin-top: 2px;">...等 {{ record.ips.length }} 个</div>
              </div>
            </a-tooltip>
            <div v-else>
              <div v-for="(ip, i) in record.ips" :key="i">{{ ip }}</div>
            </div>
          </div>
          <span v-else>-</span>
        </template>


        <template v-else-if="column.key === 'site'">
          <div class="site-header">
            <a :href="record.site || record.url" target="_blank" style="color: #00bcd4; font-weight: 500;">
              <img v-if="record.favicon && record.favicon.data" :src="`data:image/png;base64,${record.favicon.data}`" class="site-img" />
              <img v-else-if="typeof record.favicon === 'string'" :src="`data:image/png;base64,${record.favicon}`" class="site-img" />
              {{ record.site || record.url }}
            </a>
            <p v-if="record.favicon && record.favicon.hash" class="site-word">Favicon Hash: {{ record.favicon.hash }}</p>
            <p v-else-if="record.favicon_hash" class="site-word">Favicon Hash: {{ record.favicon_hash }}</p>
            <div class="mt5" style="display: flex; align-items: center; flex-wrap: wrap; gap: 4px;">
              <a-tag v-if="record.is_entry || record.isEntry" closable style="background: #fafafa; color: #666; border-color: #d9d9d9;">入口</a-tag>
              <template v-for="(t, idx) in (record.tags || record.tag || [])" :key="idx">
                <a-tag closable style="background: #fafafa; color: #666; border-color: #d9d9d9;">
                  {{ typeof t === 'string' ? t : (t.name || t.tag_name || t) }}
                </a-tag>
              </template>
              <span class="add-tag">添加标签</span>
            </div>
          </div>
        </template>

        <template v-else-if="column.key === 'headers'">
          <div class="scroll-x"><pre>{{ record.headers }}</pre></div>
        </template>

        <template v-else-if="column.key === 'finger'">
          <div v-if="record.finger">
            <p v-for="f in record.finger" :key="f.name" style="margin-bottom: 4px; color: rgba(0,0,0,0.65);">{{ f.name }}</p>
          </div>
        </template>

        <template v-else-if="column.key === 'screenshot'">
          <img v-if="record.screenshot" :src="`/api${record.screenshot}`" style="width: 280px; cursor: pointer; border: 1px solid #f0f0f0;" @click="handlePreview(`/api${record.screenshot}`)" />
          <span v-else>-</span>
        </template>

        <template v-else-if="column.key === 'domain'">
          <div v-if="Array.isArray(record.domain) && record.domain.length">
            <a-tooltip v-if="record.domain.length > 5" placement="top" :overlayInnerStyle="{ maxHeight: '400px', overflowY: 'auto' }">
              <template #title><div v-for="(dom, i) in record.domain" :key="'all-dom-'+i">{{ dom }}</div></template>
              <div style="cursor: pointer;">
                <div v-for="(dom, i) in record.domain.slice(0, 5)" :key="i">{{ dom }}</div>
                <div style="color: #999; margin-top: 2px;">...等 {{ record.domain.length }} 个</div>
              </div>
            </a-tooltip>
            <div v-else><div v-for="(dom, i) in record.domain" :key="i">{{ dom }}</div></div>
          </div>
          <span v-else-if="typeof record.domain === 'string'">{{ record.domain }}</span>
          <span v-else>-</span>
        </template>

        <template v-else-if="column.key === 'port_info'">
          <span>{{ record.port_info && record.port_info.length ? record.port_info.map(p => p.port_id).join(', ') : '-' }}</span>
        </template>
        <template v-else-if="column.key === 'os_info'"><span>{{ record.os_info?.name || '-' }}</span></template>
        <template v-else-if="column.key === 'geo_city'"><span>{{ record.geo_city ? `${record.geo_city.country_name || 'null'} / ${record.geo_city.city || 'null'}` : '-' }}</span></template>
        <template v-else-if="column.key === 'geo_asn'"><span>{{ record.geo_asn?.organization || '-' }}</span></template>

      </template>
    </a-table>

    <div v-if="tabConfig[activeTab]" style="display: flex; justify-content: space-between; align-items: center; padding: 0 16px; margin-top: 16px;">
      <div style="color: rgba(0,0,0,.65);">共 {{ Math.ceil(pagination.total / pagination.pageSize) || 1 }} 页 / {{ pagination.total }} 条数据</div>
      <a-pagination v-model:current="pagination.current" v-model:pageSize="pagination.pageSize" :total="pagination.total" show-size-changer @change="handleTableChange" @showSizeChange="handleTableChange" />
    </div>

    <a-modal v-model:open="previewVisible" :footer="null" width="85vw" centered @cancel="previewVisible = false" :bodyStyle="{ padding: '16px' }">
      <img :src="previewImage" style="width: 100%; max-height: 85vh; object-fit: contain; display: block;" />
    </a-modal>

    <a-modal v-model:open="riskVisible" title="添加风险巡航任务" @ok="submitRiskTask" :confirmLoading="riskSubmitLoading" width="520px" wrapClassName="arl-theme-modal" rootClassName="arl-theme-modal" okText="确 定" cancelText="取 消">
      <a-form :model="riskForm" :label-col="{ span: 5 }" :wrapper-col="{ span: 17 }" style="margin-top: 20px;">
        <a-form-item label="策略名称" name="policy_id" :rules="[{ required: true, message: '请选择策略' }]">
          <a-select v-model:value="riskForm.policy_id" placeholder="请选择策略" :options="policyOptions" show-search option-filter-prop="label" @change="handlePolicyChange"/>
        </a-form-item>
        <a-form-item label="任务名称" name="name" :rules="[{ required: true, message: '请输入任务名称' }]">
          <a-input v-model:value="riskForm.name" />
        </a-form-item>
        <div style="margin-left: 104px; color: rgba(0,0,0,0.85); margin-top: 16px;">目标：选择目标数 {{ targetCount }}</div>
      </a-form>
    </a-modal>

  </div>
</template>

<script setup>
import { ref, onMounted, reactive, watch } from 'vue';
import request from '../utils/request';
import { message } from 'ant-design-vue';
import { SearchOutlined } from '@ant-design/icons-vue';

const activeTab = ref('site');
const loading = ref(false);
const dataSource = ref([]);
const searchForm = ref({});
const pagination = reactive({ current: 1, pageSize: 10, total: 0 });

const previewVisible = ref(false);
const previewImage = ref('');
const handlePreview = (url) => { previewImage.value = url; previewVisible.value = true; };

// 💡 简化版 Config：仅保留全局搜索需要的配置，去除 deleteUrl
const tabConfig = {
  site: {
    url: '/site/',
    exportUrl: '/site/export/',
    exportName: '站点',
    searchFields: [
      { label: '站点', key: 'site', operator: '=' },
      { label: '主机名', key: 'hostname', operator: '=' },
      { label: '标题', key: 'title', operator: '=' },
      // 🚨 以下 4 个字段已根据抓包数据完美修正
      { label: 'Web Server', key: 'http_server', operator: '=' },
      { label: '状态码', key: 'status', operator: '=' },
      { label: '标头', key: 'headers', operator: '=' },
      { label: '指纹', key: 'finger.name', operator: '=' },
      { label: 'favicon hash', key: 'favicon.hash', operator: '=' },
      { label: '标签', key: 'tag', operator: '=' }
    ],
    cols: [
      { title: '序号', key: 'index', width: 60, align: 'center' },
      { title: '站点', key: 'site', width: 250 },
      { title: '标题', dataIndex: 'title', key: 'title', width: 200 },
      { title: 'headers', key: 'headers', width: 500 },
      { title: 'finger', key: 'finger', width: 50 },
      { title: '截图', key: 'screenshot', width: 280 }
    ]
  },
  domain: {
    url: '/domain/',
    exportUrl: '/domain/export/',
    exportName: '子域名',
    searchFields: [
      { label: '域名', key: 'domain', operator: '=' },
      { label: '记录值', key: 'record', operator: '=' },
      { label: '类型', key: 'type', operator: '=' },
      { label: 'IP', key: 'ips', operator: '=' },
      { label: '来源', key: 'source', operator: '=' }
    ],
    cols: [
      { title: '序号', key: 'index', width: 60, align: 'center' },
      { title: '域名', dataIndex: 'domain', key: 'domain', width: 250 },
      { title: '解析类型', dataIndex: 'type', key: 'type', width: 120 },
      { title: '记录值', key: 'record', width: 300 },
      { title: '关联IP', key: 'ips', width: 250 },
      { title: '来源', dataIndex: 'source', key: 'source', width: 150 }
    ]
  },
  ip: {
    url: '/ip/',
    exportUrl: '/ip/export/',
    exportName: ' IP 端口',
    searchFields: [
      { label: 'IP', key: 'ip', operator: '=' },
      { label: '端口', key: 'port_info.port_id', operator: '=' },
      { label: '操作系统', key: 'os_info.name', operator: '=' },
      { label: '域名', key: 'domain', operator: '=' },
      { label: 'CDN', key: 'cdn_name', operator: '=' },
    ],
    cols: [
      { title: '序号', key: 'index', width: 60, align: 'center' },
      { title: 'IP', dataIndex: 'ip', key: 'ip', width: 160 },
      { title: '操作系统', key: 'os_info', width: 150 },
      { title: '开放端口', key: 'port_info', width: 200 },
      { title: '关联域名', key: 'domain', width: 250 },
      { title: 'CDN', dataIndex: 'cdn_name', key: 'cdn_name', width: 150 },
      { title: 'Geo', key: 'geo_city', width: 180 },
      { title: 'AS', key: 'geo_asn', width: 280 }
    ]
  }
};

const columns = ref(tabConfig.site.cols);

// 🚨 核心逻辑调整：去掉 task_id 参数，纯净的全局搜索
const fetchData = async () => {
  const config = tabConfig[activeTab.value];
  if (!config) return;

  loading.value = true;
  try {
    const params = { page: pagination.current, size: pagination.pageSize };
    for (const key in searchForm.value) {
      if (searchForm.value[key] !== '' && searchForm.value[key] != null) {
        params[key] = searchForm.value[key];
      }
    }
    const res = await request.get(config.url, { params });
    if (res.code === 200) {
      dataSource.value = res.items || [];
      pagination.total = res.total || 0;
    }
  } catch (error) {
    message.error('加载资产数据失败');
  } finally {
    loading.value = false;
  }
};

const handleExport = async () => {
  const config = tabConfig[activeTab.value];
  if (!config || !config.exportUrl) return;

  try {
    message.loading({ content: `正在生成${config.exportName}导出文件...`, key: 'export_data' });
    const params = { page: 1, size: 100000 };
    for (const key in searchForm.value) {
      if (searchForm.value[key] !== '' && searchForm.value[key] != null) {
        params[key] = searchForm.value[key];
      }
    }
    const res = await request.get(config.exportUrl, { params, responseType: 'blob' });
    const blob = new Blob([res], { type: 'text/plain;charset=utf-8' });
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = `ARL_Global_${activeTab.value}_Export.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
    message.success({ content: `${config.exportName}导出成功！`, key: 'export_data', duration: 2 });
  } catch (error) {
    message.error({ content: '导出异常', key: 'export_data', duration: 2 });
  }
};

const onSearch = () => { pagination.current = 1; fetchData(); };
const resetSearch = () => { searchForm.value = {}; onSearch(); };
const handleTableChange = (page, pageSize) => { pagination.current = page; pagination.pageSize = pageSize; fetchData(); };

watch(activeTab, (newVal) => {
  if (tabConfig[newVal]) {
    columns.value = tabConfig[newVal].cols;
    searchForm.value = {};
    pagination.current = 1;
    fetchData();
  }
});

onMounted(fetchData);

// 风险任务下发 (全局模式)
const riskVisible = ref(false);
const riskSubmitLoading = ref(false);
const policyOptions = ref([]);
const riskForm = reactive({ policy_id: undefined, name: '' });
const targetCount = ref(0);
const currentResultSetId = ref('');

const openRiskModal = async () => {
  targetCount.value = pagination.total;
  if (targetCount.value === 0) return message.warning('当前没有可下发的资产目标！');

  riskForm.policy_id = undefined;
  riskForm.name = '';
  currentResultSetId.value = '';
  message.loading({ content: '正在打包全局资产...', key: 'risk_prepare' });

  try {
    const policyPromise = request.get('/policy/', { params: { size: 1000 } });
    const setParams = { ...searchForm.value }; // 全局模式直接传搜索参数
    const resultSetPromise = request.get('/site/save_result_set/', { params: setParams });
    const [policyRes, resultSetRes] = await Promise.all([policyPromise, resultSetPromise]);

    if (policyRes.code === 200) {
      policyOptions.value = (policyRes.items || []).map(item => ({
        value: item._id, label: `${item.name} (PoC : ${item.policy?.poc_config?.length || 0})`
      }));
    }
    if (resultSetRes.code === 200) currentResultSetId.value = resultSetRes.data.result_set_id;

    message.success({ content: '准备就绪', key: 'risk_prepare', duration: 2 });
    riskVisible.value = true;
  } catch (error) {
    message.error({ content: '准备数据失败', key: 'risk_prepare', duration: 2 });
  }
};

const handlePolicyChange = (val, option) => { if (option) riskForm.name = `风险巡航任务-${option.label}`; };

const submitRiskTask = async () => {
  if (!riskForm.policy_id || !riskForm.name) return message.warning('请填写完整信息');
  riskSubmitLoading.value = true;
  try {
    const res = await request.post('/task/policy/', {
      name: riskForm.name, task_tag: 'risk_cruising', target: '',
      policy_id: riskForm.policy_id, result_set_id: currentResultSetId.value
    });
    if (res.code === 200) {
      message.success('风险任务下发成功 🚀');
      riskVisible.value = false;
    } else message.error('下发失败: ' + res.message);
  } catch (error) { message.error('下发异常'); }
  finally { riskSubmitLoading.value = false; }
};
</script>

<style scoped>
.site-header { line-height: 1.5; }
.site-img { width: 16px; height: 16px; margin-right: 8px; vertical-align: middle; }
.site-word { color: rgba(0, 0, 0, 0.85) !important; font-size: 14px !important; margin-top: 4px; margin-bottom: 0; line-height: 1.5; }
.add-tag { color: #666; cursor: pointer; font-size: 12px; margin-left: 8px; border: 1px dashed #d9d9d9; padding: 0 7px; border-radius: 2px; background: #fafafa; transition: all 0.3s; }
.add-tag:hover { color: #00bcd4; border-color: #00bcd4; }
.mt5 { margin-top: 5px; }

.search-row { display: flex; flex-wrap: wrap; gap: 16px 24px; }
.search-item { display: flex; align-items: center; }
.search-item .label { color: rgba(0,0,0,0.85); margin-right: 8px; min-width: 80px; text-align: right; }

.scroll-x { background: transparent; border: none; padding: 8px; width: 100%; max-width: 600px; overflow-x: auto; overflow-y: hidden; }
.scroll-x pre { margin: 0; padding: 0; background-color: transparent; border: none; font-family: Consolas, Menlo, Courier, monospace; font-size: 12px; line-height: 1.5; color: rgba(0, 0, 0, 0.65); white-space: pre; word-wrap: normal; }
.scroll-x::-webkit-scrollbar { height: 6px; }
.scroll-x::-webkit-scrollbar-track { background: transparent; }
.scroll-x::-webkit-scrollbar-thumb { background-color: rgba(144, 147, 153, 0.3); border-radius: 4px; }
.scroll-x::-webkit-scrollbar-thumb:hover { background-color: rgba(144, 147, 153, 0.6); }

:deep(.ant-tabs-card-bar .ant-tabs-tab) { border-radius: 2px 2px 0 0 !important; margin-right: 4px !important; border: 1px solid #e8e8e8 !important; background: #fafafa !important; transition: all 0.3s; }
:deep(.ant-tabs-card-bar .ant-tabs-tab-active) { background: #fff !important; border-bottom-color: transparent !important; color: #00bcd4 !important; font-weight: 500; }
:deep(.ant-tabs-tab:hover) { color: #00bcd4 !important; }
</style>