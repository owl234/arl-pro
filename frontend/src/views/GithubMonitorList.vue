<template>
  <div style="background-color: #fff; padding: 24px; min-height: calc(100vh - 64px);">

    <div style="margin-bottom: 20px;">
      <a-button type="primary" style="background-color: #00bcd4; border-color: #00bcd4;" @click="openAddModal">添加任务</a-button>
    </div>

    <div class="search-row" style="margin-bottom: 16px; background-color: #f9f9f9; padding: 16px; border-radius: 4px;">
      <div class="search-item">
        <span class="label">任务名称：</span>
        <a-input v-model:value="searchForm.name" placeholder="请输入任务名称进行搜索" style="width: 180px;" allowClear @pressEnter="onSearch">
          <template #suffix><search-outlined @click="onSearch" style="cursor: pointer; color: rgba(0,0,0,0.25);" /></template>
        </a-input>
      </div>
      <div class="search-item">
        <span class="label">关键字：</span>
        <a-input v-model:value="searchForm.keyword" placeholder="请输入关键字进行搜索" style="width: 180px;" allowClear @pressEnter="onSearch">
          <template #suffix><search-outlined @click="onSearch" style="cursor: pointer; color: rgba(0,0,0,0.25);" /></template>
        </a-input>
      </div>
      <div class="search-item">
        <span class="label">状态：</span>
        <a-select v-model:value="searchForm.status" placeholder="请选择状态进行搜索" style="width: 180px;" allowClear @change="onSearch">
          <a-select-option value="running">running</a-select-option>
          <a-select-option value="stop">stop</a-select-option>
          <a-select-option value="error">error</a-select-option>
        </a-select>
      </div>
    </div>

    <div style="margin-bottom: 16px; display: flex; gap: 8px;">
      <a-popconfirm title="确认删除所选数据吗？" @confirm="handleBatchDelete">
        <a-button :disabled="!hasSelected">批量删除</a-button>
      </a-popconfirm>
      <a-popconfirm title="确认停止所选数据吗？" @confirm="handleBatchStop">
        <a-button :disabled="!hasSelected">批量停止</a-button>
      </a-popconfirm>
    </div>

    <a-table
        :row-selection="{ selectedRowKeys: selectedRowKeys, onChange: onSelectChange }"
        :loading="loading"
        :dataSource="dataSource"
        :columns="columns"
        :pagination="false"
        size="middle"
        :rowKey="(record) => record._id"
    >
      <template #emptyText>
        <div style="padding: 40px 0;">
          <inbox-outlined style="font-size: 48px; color: #d9d9d9;" />
          <div style="color: #999; margin-top: 8px;">暂无数据</div>
        </div>
      </template>

      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'name'">
          <a style="color: #00bcd4;" @click="goToDetail(record)">{{ record.name }}</a>
        </template>

        <template v-else-if="column.key === 'status'">
          <a-tag :color="record.status === 'running' ? 'blue' : record.status === 'stop' ? 'warning' : 'error'">
            {{ record.status }}
          </a-tag>
        </template>

        <template v-else-if="column.key === 'action'">
          <a-button
              size="small"
              style="margin-right: 8px;"
              :disabled="record.status !== 'running'"
              @click="handleSingleAction('stop', record._id)"
          >停止</a-button>

          <a-popconfirm title="确认删除？" @confirm="handleSingleAction('delete', record._id)">
            <a-button size="small" style="margin-right: 8px;">删除</a-button>
          </a-popconfirm>

          <a-button
              size="small"
              style="margin-right: 8px;"
              :disabled="record.status !== 'stop' && record.status !== 'error'"
              @click="handleSingleAction('recover', record._id)"
          >恢复</a-button>

          <a-button size="small" @click="openEditModal(record)">修改</a-button>
        </template>
      </template>
    </a-table>

    <div style="display: flex; justify-content: space-between; align-items: center; padding: 16px 0;">
      <div style="color: rgba(0,0,0,.65);">共 {{ Math.ceil(pagination.total / pagination.pageSize) || 1 }} 页 / {{ pagination.total }} 条数据</div>
      <a-pagination v-model:current="pagination.current" v-model:pageSize="pagination.pageSize" :total="pagination.total" show-size-changer @change="handleTableChange" />
    </div>

    <a-modal
        v-model:open="modalVisible"
        :title="isEdit ? '修改任务' : '添加任务'"
        @ok="submitModal"
        :confirmLoading="submitLoading"
        width="520px"
        okText="确定"
        cancelText="取消"
        destroyOnClose
    >
      <a-form :model="form" :label-col="{ span: 5 }" :wrapper-col="{ span: 18 }" style="margin-top: 20px;">
        <a-form-item label="任务名" required>
          <a-input v-model:value="form.name" placeholder="请输入任务名" />
        </a-form-item>

        <a-form-item label="关键字" required>
          <a-input v-model:value="form.keyword" placeholder="请输入关键字" />
        </a-form-item>

        <a-form-item label="cron表达式" required>
          <a-input v-model:value="form.cron" placeholder="请输入cron表达式" />
        </a-form-item>
      </a-form>
    </a-modal>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import request from '../utils/request';
import { message } from 'ant-design-vue';
import { SearchOutlined, InboxOutlined } from '@ant-design/icons-vue';

const router = useRouter();
const loading = ref(false);
const dataSource = ref([]);

// 搜索与分页
const searchForm = reactive({ name: '', keyword: '', status: undefined });
const pagination = reactive({ current: 1, pageSize: 10, total: 0 });

const selectedRowKeys = ref([]);
const hasSelected = computed(() => selectedRowKeys.value.length > 0);
const onSelectChange = (keys) => { selectedRowKeys.value = keys; };

const columns = [
  { title: '任务名', dataIndex: 'name', key: 'name', width: 150 },
  { title: '关键字', dataIndex: 'keyword', key: 'keyword', width: 150 },
  { title: 'cron表达式', dataIndex: 'cron', key: 'cron', width: 150 },
  { title: '状态', dataIndex: 'status', key: 'status', width: 100 },
  { title: '运行次数', dataIndex: 'run_number', key: 'run_number', width: 100 },
  { title: '上次运行时间', dataIndex: 'last_run_date', key: 'last_run_date', width: 180 },
  { title: '下次运行时间', dataIndex: 'next_run_date', key: 'next_run_date', width: 180 },
  { title: '操作', key: 'action', width: 280 }
];

// ================= 数据拉取 =================
const fetchData = async () => {
  loading.value = true;
  try {
    const params = { page: pagination.current, size: pagination.pageSize };
    if (searchForm.name) params.name = searchForm.name;
    if (searchForm.keyword) params.keyword = searchForm.keyword;
    if (searchForm.status) params.status = searchForm.status;

    const res = await request.get('/github_scheduler/', { params });
    if (res.code === 200) {
      dataSource.value = res.items || [];
      pagination.total = res.total || 0;
      selectedRowKeys.value = [];
    }
  } catch (error) {
    message.error('加载监控任务失败');
  } finally {
    loading.value = false;
  }
};

const onSearch = () => { pagination.current = 1; fetchData(); };
const handleTableChange = (page, pageSize) => { pagination.current = page; pagination.pageSize = pageSize; fetchData(); };

// ================= 详情跳转 =================
const goToDetail = (record) => {
  router.push({ path: '/GitHubMonitor/GitHubMonitorInfo', query: { _id: record._id } });
};

// ================= 操作按钮 =================
const performAction = async (actionType, idArray) => {
  try {
    const url = `/github_scheduler/${actionType}/`;
    const res = await request.post(url, { _id: idArray });
    if (res.code === 200) {
      message.success('操作成功！');
      fetchData(); // 接口自动触发列表刷新
    } else {
      message.error(res.message || '操作失败');
    }
  } catch (e) {
    message.error('请求异常');
  }
};

const handleSingleAction = (type, id) => performAction(type, [id]);
const handleBatchDelete = () => performAction('delete', selectedRowKeys.value);
const handleBatchStop = () => performAction('stop', selectedRowKeys.value);

// ================= 弹窗逻辑 (新增与修改复用) =================
const modalVisible = ref(false);
const submitLoading = ref(false);
const isEdit = ref(false);
const currentEditId = ref('');
const form = reactive({ name: '', keyword: '', cron: '' });

const openAddModal = () => {
  isEdit.value = false;
  currentEditId.value = '';
  Object.assign(form, { name: '', keyword: '', cron: '' });
  modalVisible.value = true;
};

const openEditModal = (record) => {
  isEdit.value = true;
  currentEditId.value = record._id;
  Object.assign(form, { name: record.name, keyword: record.keyword, cron: record.cron });
  modalVisible.value = true;
};

const submitModal = async () => {
  if (!form.name || !form.keyword || !form.cron) {
    return message.warning('请填写所有必填项！');
  }

  submitLoading.value = true;
  try {
    let res;
    if (isEdit.value) {
      const payload = { _id: currentEditId.value, ...form };
      res = await request.post('/github_scheduler/update/', payload);
    } else {
      res = await request.post('/github_scheduler/', form);
    }

    if (res.code === 200) {
      message.success(`${isEdit.value ? '修改' : '添加'}成功！`);
      modalVisible.value = false;
      onSearch(); // 刷新列表
    } else {
      message.error(res.message || '操作失败');
    }
  } catch (error) {
    message.error('请求异常');
  } finally {
    submitLoading.value = false;
  }
};

onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.search-row { display: flex; flex-wrap: wrap; gap: 16px 12px; align-items: center; }
.search-item { display: flex; align-items: center; }
.search-item .label { color: rgba(0,0,0,0.85); margin-right: 8px; min-width: 60px; text-align: right; white-space: nowrap; }
</style>