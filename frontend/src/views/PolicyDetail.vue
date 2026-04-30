<template>
  <div style="background-color: #fff; padding: 24px; min-height: calc(100vh - 64px);">
    <div style="display: flex; align-items: center; margin-bottom: 24px; border-bottom: 1px solid #f0f0f0; padding-bottom: 16px;">
      <a-button type="link" @click="goBack" style="padding: 0; margin-right: 16px; color: #00bcd4;">&lt; 返回列表</a-button>
      <h2 style="margin: 0; font-size: 18px; font-weight: 500;">{{ isEdit ? '编辑策略' : '新建配置' }}</h2>
    </div>

    <a-form :model="policyForm" :label-col="{ span: 4 }" :wrapper-col="{ span: 16 }" style="max-width: 1000px; margin: 0 auto;">

      <a-form-item label="策略名称" required>
        <a-input v-model:value="policyForm.name" placeholder="请输入策略名称" />
      </a-form-item>
      <a-form-item label="策略描述">
        <a-input v-model:value="policyForm.desc" placeholder="请输入策略描述" />
      </a-form-item>

      <a-collapse v-model:activeKey="activePanels" :bordered="false" style="background: transparent; margin-bottom: 40px;">

        <a-collapse-panel key="1" header="域名和IP配置">
          <a-form-item label="域名爆破类型" required>
            <a-select v-model:value="policyForm.domain_config.domain_brute_type">
              <a-select-option value="test">测试字典</a-select-option>
              <a-select-option value="big">大字典</a-select-option>
            </a-select>
          </a-form-item>

          <a-form-item label="端口扫描类型" required>
            <a-select v-model:value="policyForm.ip_config.port_scan_type">
              <a-select-option value="test">测试</a-select-option>
              <a-select-option value="top100">TOP100</a-select-option>
              <a-select-option value="top1000">TOP1000</a-select-option>
              <a-select-option value="all">全端口</a-select-option>
              <a-select-option value="custom">自定义</a-select-option>
            </a-select>
          </a-form-item>

          <a-form-item v-if="policyForm.ip_config.port_scan_type === 'custom'" label="自定义端口" required>
            <a-input v-model:value="policyForm.ip_config.port_custom" placeholder="请输入自定义端口，例如: 80,443,1000-2000" />
          </a-form-item>

          <a-form-item :wrapper-col="{ offset: 4, span: 16 }">
            <div style="display: flex; justify-content: space-between; margin-top: 10px; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid #f0f0f0;">
              <a-checkbox :checked="isAllDomainSelected" @change="toggleAllDomain">全选</a-checkbox>
              <a-input v-model:value="domainSearch" placeholder="请输入关键字进行查询" style="width: 250px;" allowClear>
                <template #suffix><search-outlined style="color: rgba(0,0,0,0.25);" /></template>
              </a-input>
            </div>
            <div style="display: flex; flex-direction: column; gap: 12px;">
              <a-checkbox v-show="matchSearch('1. 域名爆破', domainSearch)" v-model:checked="policyForm.domain_config.domain_brute">1. 域名爆破</a-checkbox>
              <a-checkbox v-show="matchSearch('2. DNS字典智能生成', domainSearch)" v-model:checked="policyForm.domain_config.alt_dns">2. DNS字典智能生成</a-checkbox>
              <a-checkbox v-show="matchSearch('3. ARL 历史查询', domainSearch)" v-model:checked="policyForm.domain_config.arl_search">3. ARL 历史查询</a-checkbox>
              <a-checkbox v-show="matchSearch('4. 域名查询插件', domainSearch)" v-model:checked="policyForm.domain_config.dns_query_plugin">4. 域名查询插件</a-checkbox>
              <a-checkbox v-show="matchSearch('5. 端口扫描', domainSearch)" v-model:checked="policyForm.ip_config.port_scan">5. 端口扫描</a-checkbox>
              <a-checkbox v-show="matchSearch('6. 服务识别', domainSearch)" v-model:checked="policyForm.ip_config.service_detection">6. 服务识别</a-checkbox>
              <a-checkbox v-show="matchSearch('7. 操作系统识别', domainSearch)" v-model:checked="policyForm.ip_config.os_detection">7. 操作系统识别</a-checkbox>
              <a-checkbox v-show="matchSearch('8. SSL 证书获取', domainSearch)" v-model:checked="policyForm.ip_config.ssl_cert">8. SSL 证书获取</a-checkbox>
              <a-checkbox v-show="matchSearch('9. 跳过CDN', domainSearch)" v-model:checked="policyForm.ip_config.skip_scan_cdn_ip">9. 跳过CDN</a-checkbox>
              <a-checkbox v-show="matchSearch('10. 服务(python)识别', domainSearch)" v-model:checked="policyForm.npoc_service_detection">10. 服务(python)识别</a-checkbox>
            </div>
          </a-form-item>
        </a-collapse-panel>

        <a-collapse-panel key="2" header="IP高级配置">
          <a-form-item label="主机超时时间" required>
            <a-select v-model:value="policyForm.ip_config.host_timeout_type">
              <a-select-option value="default">默认(900s)</a-select-option>
              <a-select-option value="custom">自定义</a-select-option>
            </a-select>
          </a-form-item>

          <a-form-item v-if="policyForm.ip_config.host_timeout_type === 'custom'" label="超时时间(秒)" required>
            <a-input-number v-model:value="policyForm.ip_config.host_timeout" :min="1" style="width: 100%" placeholder="请输入超时时间" />
          </a-form-item>

          <a-form-item label="探测报文并行度" required>
            <a-input-number v-model:value="policyForm.ip_config.port_parallelism" style="width: 100%" />
          </a-form-item>
          <a-form-item label="最少发包速率" required>
            <a-input-number v-model:value="policyForm.ip_config.port_min_rate" style="width: 100%" />
          </a-form-item>
          <a-form-item label="排除端口">
            <a-input v-model:value="policyForm.ip_config.exclude_ports" placeholder="排除指定端口，不对其进行扫描，如：9100,9102,1-100" />
          </a-form-item>
        </a-collapse-panel>

        <a-collapse-panel key="3" header="站点和风险配置">
          <a-form-item :wrapper-col="{ offset: 4, span: 16 }">
            <div style="display: flex; justify-content: space-between; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid #f0f0f0;">
              <a-checkbox :checked="isAllSiteSelected" @change="toggleAllSite">全选</a-checkbox>
              <a-input v-model:value="siteSearch" placeholder="请输入关键字进行查询" style="width: 250px;" allowClear>
                <template #suffix><search-outlined style="color: rgba(0,0,0,0.25);" /></template>
              </a-input>
            </div>
            <div style="display: flex; flex-direction: column; gap: 12px;">
              <a-checkbox v-show="matchSearch('1. 站点识别', siteSearch)" v-model:checked="policyForm.site_config.site_identify">1. 站点识别</a-checkbox>
              <a-checkbox v-show="matchSearch('2. 搜索引擎调用', siteSearch)" v-model:checked="policyForm.site_config.search_engines">2. 搜索引擎调用</a-checkbox>
              <a-checkbox v-show="matchSearch('3. 站点爬虫', siteSearch)" v-model:checked="policyForm.site_config.site_spider">3. 站点爬虫</a-checkbox>
              <a-checkbox v-show="matchSearch('4. 站点截图', siteSearch)" v-model:checked="policyForm.site_config.site_capture">4. 站点截图</a-checkbox>
              <a-checkbox v-show="matchSearch('5. 文件泄露', siteSearch)" v-model:checked="policyForm.file_leak">5. 文件泄露</a-checkbox>
              <a-checkbox v-show="matchSearch('6. nuclei 调用', siteSearch)" v-model:checked="policyForm.site_config.nuclei_scan">6. nuclei 调用</a-checkbox>
              <a-checkbox v-show="matchSearch('7. WIH 调用', siteSearch)" v-model:checked="policyForm.site_config.web_info_hunter">7. WIH 调用</a-checkbox>
            </div>
          </a-form-item>
        </a-collapse-panel>

        <a-collapse-panel key="4" header="PoC配置">
          <div style="display: flex; justify-content: space-between; margin-bottom: 16px; padding: 0 16px;">
            <a-checkbox :checked="isAllPocSelected" @change="toggleAllPoc">全选</a-checkbox>
            <a-input v-model:value="pocSearch" placeholder="请输入关键字进行查询" style="width: 250px;">
              <template #suffix><search-outlined style="color: rgba(0,0,0,0.25);" /></template>
            </a-input>
          </div>
          <a-row :gutter="[16, 16]" style="padding: 0 16px;">
            <a-col :span="12" v-for="(item, index) in filteredPocList" :key="item._id">
              <a-checkbox v-model:checked="item.enable">{{ index + 1 }}. {{ item.vul_name }}</a-checkbox>
            </a-col>
          </a-row>
        </a-collapse-panel>

        <a-collapse-panel key="5" header="弱口令爆破配置">
          <div style="display: flex; justify-content: space-between; margin-bottom: 16px; padding: 0 16px;">
            <a-checkbox :checked="isAllBruteSelected" @change="toggleAllBrute">全选</a-checkbox>
            <a-input v-model:value="bruteSearch" placeholder="请输入关键字进行查询" style="width: 250px;">
              <template #suffix><search-outlined style="color: rgba(0,0,0,0.25);" /></template>
            </a-input>
          </div>
          <a-row :gutter="[16, 16]" style="padding: 0 16px;">
            <a-col :span="12" v-for="(item, index) in filteredBruteList" :key="item._id">
              <a-checkbox v-model:checked="item.enable">{{ index + 1 }}. {{ item.vul_name }}</a-checkbox>
            </a-col>
          </a-row>
        </a-collapse-panel>

        <a-collapse-panel key="6" header="资产组配置">
          <a-form-item label="关联资产组">
            <a-select v-model:value="policyForm.scope_id" placeholder="请选择资产组" allowClear>
              <a-select-option v-for="scope in scopeList" :key="scope._id" :value="scope._id">{{ scope.name }}</a-select-option>
            </a-select>
          </a-form-item>
        </a-collapse-panel>

      </a-collapse>

      <div style="text-align: center; margin-bottom: 40px;">
        <a-button type="primary" style="background-color: #00bcd4; border-color: #00bcd4; margin-right: 16px; width: 100px;" @click="submitPolicy" :loading="submitLoading">确 定</a-button>
        <a-button style="width: 100px;" @click="goBack">取 消</a-button>
      </div>
    </a-form>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue';
import request from '../utils/request';
import { message } from 'ant-design-vue';
import { SearchOutlined } from '@ant-design/icons-vue';
import { useRouter, useRoute} from 'vue-router';

const router = useRouter();
const route = useRoute(); // 🚨 获取路由信息
const policyId = route.query._id;
const isEdit = !!policyId; // 🚨 判断当前是否为编辑模式

const goBack = () => router.push('/policy'); // 返回策略配置列表

const activePanels = ref([]);
const submitLoading = ref(false);

const initPolicyForm = () => ({
  name: '', desc: '',
  domain_config: { domain_brute: false, alt_dns: false, arl_search: false, dns_query_plugin: false, domain_brute_type: 'big' },
  ip_config: { port_scan: false, service_detection: false, os_detection:false, ssl_cert: false, skip_scan_cdn_ip: false, port_scan_type: 'top100', port_custom: '', host_timeout_type: 'default', host_timeout: 0, port_parallelism: 32, port_min_rate: 60, exclude_ports: '' },
  npoc_service_detection: false,
  site_config: { site_identify: false, search_engines: false, site_spider: false, site_capture: false, nuclei_scan: false, web_info_hunter: false },
  file_leak: false,
  scope_id: undefined
});

const policyForm = reactive(initPolicyForm());

const scopeList = ref([]);
const pocList = ref([]);
const bruteList = ref([]);

const pocSearch = ref('');
const bruteSearch = ref('');

// 🚨 强化版搜索引擎：自动转小写（忽略大小写差异），同时匹配中文名(vul_name)和英文插件名(plugin_name)！
const filteredPocList = computed(() => {
  const kw = (pocSearch.value || '').toLowerCase().trim();
  if (!kw) return pocList.value; // 为空时展示全部
  return pocList.value.filter(p =>
      (p.vul_name && p.vul_name.toLowerCase().includes(kw)) ||
      (p.plugin_name && p.plugin_name.toLowerCase().includes(kw))
  );
});

const filteredBruteList = computed(() => {
  const kw = (bruteSearch.value || '').toLowerCase().trim();
  if (!kw) return bruteList.value; // 为空时展示全部
  return bruteList.value.filter(p =>
      (p.vul_name && p.vul_name.toLowerCase().includes(kw)) ||
      (p.plugin_name && p.plugin_name.toLowerCase().includes(kw))
  );
});

const isAllPocSelected = computed(() => filteredPocList.value.length > 0 && filteredPocList.value.every(p => p.enable));
const isAllBruteSelected = computed(() => filteredBruteList.value.length > 0 && filteredBruteList.value.every(p => p.enable));

const toggleAllPoc = (e) => { const checked = e.target.checked; filteredPocList.value.forEach(p => p.enable = checked); };
const toggleAllBrute = (e) => { const checked = e.target.checked; filteredBruteList.value.forEach(p => p.enable = checked); };

// 🚨 新增：面板1和面板3的搜索关键词绑定
const domainSearch = ref('');
const siteSearch = ref('');


// 🚨 智能搜索辅助函数：忽略大小写进行比对
const matchSearch = (text, keyword) => {
  if (!keyword) return true; // 没输入关键字时，全部展示
  return text.toLowerCase().includes(keyword.toLowerCase());
};

// ================= 面板1：域名和IP 全选联动逻辑 =================
const isAllDomainSelected = computed(() => {
  const dc = policyForm.domain_config;
  const ic = policyForm.ip_config;
  return dc.domain_brute && dc.alt_dns && dc.arl_search && dc.dns_query_plugin &&
      ic.port_scan && ic.service_detection && ic.os_detection && ic.ssl_cert && ic.skip_scan_cdn_ip &&
      policyForm.npoc_service_detection;
});
const toggleAllDomain = (e) => {
  const val = e.target.checked;
  const dc = policyForm.domain_config;
  const ic = policyForm.ip_config;
  dc.domain_brute = dc.alt_dns = dc.arl_search = dc.dns_query_plugin = val;
  ic.port_scan = ic.service_detection = ic.os_detection = ic.ssl_cert = ic.skip_scan_cdn_ip = val;
  policyForm.npoc_service_detection = val;
};

// ================= 面板3：站点和风险 全选联动逻辑 =================
const isAllSiteSelected = computed(() => {
  const sc = policyForm.site_config;
  return sc.site_identify && sc.search_engines && sc.site_spider && sc.site_capture &&
      sc.nuclei_scan && sc.web_info_hunter && policyForm.file_leak;
});
const toggleAllSite = (e) => {
  const val = e.target.checked;
  const sc = policyForm.site_config;
  sc.site_identify = sc.search_engines = sc.site_spider = sc.site_capture = sc.nuclei_scan = sc.web_info_hunter = val;
  policyForm.file_leak = val;
};

// 组件挂载时并发请求弹药库
onMounted(async () => {
  try {
    // 1. 并发预加载弹药库
    const [scopeRes, pocRes, bruteRes] = await Promise.all([
      request.get('/asset_scope/', { params: { size: 100 } }),
      request.get('/poc/', { params: { plugin_type: 'poc', size: 10000 } }),
      request.get('/poc/', { params: { plugin_type: 'brute', size: 10000 } })
    ]);

    if (scopeRes.code === 200) scopeList.value = scopeRes.items || [];
    if (pocRes.code === 200) {
      const uniquePoc = new Map();
      (pocRes.items || []).forEach(p => {
        if (!uniquePoc.has(p.plugin_name)) uniquePoc.set(p.plugin_name, { ...p, enable: false });
      });
      pocList.value = Array.from(uniquePoc.values());
    }

    if (bruteRes.code === 200) {
      const uniqueBrute = new Map();
      (bruteRes.items || []).forEach(p => {
        if (!uniqueBrute.has(p.plugin_name)) uniqueBrute.set(p.plugin_name, { ...p, enable: false });
      });
      bruteList.value = Array.from(uniqueBrute.values());
    }

    // 🚨 2. 新增核心逻辑：如果是编辑模式，拉取详情并反向回填！
    if (isEdit) {
      const detailRes = await request.get('/policy/', { params: { _id: policyId } });
      if (detailRes.code === 200 && detailRes.items?.length > 0) {
        const data = detailRes.items[0];

        // 基础与常规配置回填
        policyForm.name = data.name;
        policyForm.desc = data.desc;
        Object.assign(policyForm.domain_config, data.policy.domain_config);
        Object.assign(policyForm.ip_config, data.policy.ip_config);
        Object.assign(policyForm.site_config, data.policy.site_config);
        policyForm.npoc_service_detection = data.policy.npoc_service_detection;
        policyForm.file_leak = data.policy.file_leak;
        policyForm.scope_id = data.policy.scope_config?.scope_id;

        // 插件状态精密回填：遍历后端返回的已开启插件，去长列表中打勾
        const pocMap = {};
        data.policy.poc_config?.forEach(p => pocMap[p.plugin_name] = p.enable);
        pocList.value.forEach(p => { if (pocMap[p.plugin_name] !== undefined) p.enable = pocMap[p.plugin_name]; });

        const bruteMap = {};
        data.policy.brute_config?.forEach(p => bruteMap[p.plugin_name] = p.enable);
        bruteList.value.forEach(p => { if (bruteMap[p.plugin_name] !== undefined) p.enable = bruteMap[p.plugin_name]; });
      }
    }
  } catch (e) {
    message.error('加载策略数据失败');
  }
});

// 提交组装
// 提交组装 (改名为 submitPolicy 即可)
const submitPolicy = async () => {
  if (!policyForm.name) return message.warning('策略名称不能为空！');

  submitLoading.value = true;
  try {
    const poc_config = pocList.value.map(p => ({ plugin_name: p.plugin_name, vul_name: p.vul_name, enable: p.enable }));
    const brute_config = bruteList.value.map(p => ({ plugin_name: p.plugin_name, vul_name: p.vul_name, enable: p.enable }));

    // 构建核心业务数据
    const policyData = {
      name: policyForm.name,
      desc: policyForm.desc,
      policy: {
        domain_config: { ...policyForm.domain_config },
        ip_config: { ...policyForm.ip_config },
        npoc_service_detection: policyForm.npoc_service_detection,
        site_config: { ...policyForm.site_config },
        file_leak: policyForm.file_leak,
        poc_config,
        brute_config,
        scope_config: policyForm.scope_id ? { scope_id: policyForm.scope_id } : {}
      }
    };

    // 🚨 根据模式切换发包 API 和 Payload 结构
    let res;
    if (isEdit) {
      res = await request.post('/policy/edit/', {
        policy_id: policyId,
        policy_data: policyData // 嵌套了一层 policy_data
      });
    } else {
      res = await request.post('/policy/add/', policyData); // 扁平结构
    }

    if (res.code === 200) {
      message.success(isEdit ? '修改策略成功！' : '创建策略成功！');
      router.push('/policy');
    } else {
      message.error((isEdit ? '修改' : '创建') + '失败: ' + res.message);
    }
  } catch (error) {
    message.error('请求异常');
  } finally {
    submitLoading.value = false;
  }
};
</script>

<style scoped>
:deep(.ant-collapse > .ant-collapse-item) { border-bottom: 1px solid #f0f0f0; }
:deep(.ant-collapse-header) { font-weight: 500; font-size: 15px; }
</style>