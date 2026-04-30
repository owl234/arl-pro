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
        <a-input v-model:value="searchForm.status" placeholder="请输入状态进行搜索" style="width: 180px;" allowClear @pressEnter="onSearch">
          <template #suffix><search-outlined @click="onSearch" style="cursor: pointer; color: rgba(0,0,0,0.25);" /></template>
        </a-input>
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
          <a-tag
              :color="
              record.status === 'running' || record.status === 'waiting' ? 'blue' :
              record.status === 'error' ? 'error' :
              'success'
            "
          >
            {{ record.status }}
          </a-tag>
        </template>

        <template v-else-if="column.key === 'action'">
          <a-button
              size="small"
              style="margin-right: 8px;"
              :disabled="record.status === 'done' || record.status === 'error'"
              @click="handleSingleAction('stop', record._id)"
          >停止</a-button>

          <a-popconfirm title="确认删除？" @confirm="handleSingleAction('delete', record._id)">
            <a-button size="small">删除</a-button>
          </a-popconfirm>
        </template>
      </template>
    </a-table>

    <div style="display: flex; justify-content: space-between; align-items: center; padding: 16px 0;">
      <div style="color: rgba(0,0,0,.65);">共 {{ Math.ceil(pagination.total / pagination.pageSize) || 1 }} 页 / {{ pagination.total }} 条数据</div>
      <a-pagination v-model:current="pagination.current" v-model:pageSize="pagination.pageSize" :total="pagination.total" show-size-changer @change="handleTableChange" />
    </div>

    <a-modal
        v-model:open="addModalVisible"
        title="添加任务"
        @ok="submitAdd"
        :confirmLoading="addLoading"
        width="520px"
        okText="确定"
        cancelText="取消"
        destroyOnClose
    >
      <a-form :model="addForm" :label-col="{ span: 4 }" :wrapper-col="{ span: 18 }" style="margin-top: 20px;">
        <a-form-item label="任务名" required>
          <a-input v-model:value="addForm.name" placeholder="请输入任务名" />
        </a-form-item>

        <a-form-item label="关键字" required>
          <a-input v-model:value="addForm.keyword" placeholder="请输入关键字" />
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

// 表格多选
const selectedRowKeys = ref([]);
const hasSelected = computed(() => selectedRowKeys.value.length > 0);
const onSelectChange = (keys) => { selectedRowKeys.value = keys; };

// 表头完全匹配截图
const columns = [
  { title: '任务名', dataIndex: 'name', key: 'name', width: 150 },
  { title: '关键字', dataIndex: 'keyword', key: 'keyword', width: 150 },
  { title: '结果数目', dataIndex: 'result_count', key: 'result_count', width: 100 }, // 盲猜名称
  { title: '状态', dataIndex: 'status', key: 'status', width: 100 },
  { title: '开始时间', dataIndex: 'start_time', key: 'start_time', width: 180 },
  { title: '结束时间', dataIndex: 'end_time', key: 'end_time', width: 180 },
  { title: '任务id', dataIndex: '_id', key: '_id', width: 200 },
  { title: '操作', key: 'action', width: 150 }
];

// ================= 数据拉取 =================
const fetchData = async () => {
  loading.value = true;
  try {
    const params = { page: pagination.current, size: pagination.pageSize };
    if (searchForm.name) params.name = searchForm.name;
    if (searchForm.keyword) params.keyword = searchForm.keyword;
    if (searchForm.status) params.status = searchForm.status;

    const res = await request.get('/github_task/', { params });
    if (res.code === 200) {
      dataSource.value = res.items || [];
      pagination.total = res.total || 0;
      selectedRowKeys.value = [];
    }
  } catch (error) {
    message.error('加载任务失败');
  } finally {
    loading.value = false;
  }
};

const onSearch = () => { pagination.current = 1; fetchData(); };
const handleTableChange = (page, pageSize) => { pagination.current = page; pagination.pageSize = pageSize; fetchData(); };

// ================= 占位交互函数 (等情报) =================
// ================= 弹窗交互与发包 =================
const addModalVisible = ref(false);
const addLoading = ref(false);
const addForm = reactive({ name: '', keyword: '' });

const openAddModal = () => {
  addForm.name = '';
  addForm.keyword = '';
  addModalVisible.value = true;
};

const submitAdd = async () => {
  if (!addForm.name || !addForm.keyword) {
    return message.warning('请填写任务名和关键字！');
  }

  addLoading.value = true;
  try {
    const payload = {
      name: addForm.name,
      keyword: addForm.keyword
    };

    const res = await request.post('/github_task/', payload);

    if (res.code === 200) {
      message.success('添加任务成功！');
      addModalVisible.value = false;
      onSearch(); // 刷新列表
    } else {
      message.error('添加失败: ' + res.message);
    }
  } catch (error) {
    message.error('请求异常，添加失败');
  } finally {
    addLoading.value = false;
  }
};

// ================= 行操作与批量操作 =================
// 🚨 跳转到详情页，携带着 _id 过去
const goToDetail = (record) => {
  router.push({ path: '/GitHubTasks/GitHubTasksInfo', query: { _id: record._id } });
};

const performAction = async (actionType, idArray) => {
  try {
    const url = `/github_task/${actionType}/`;
    const res = await request.post(url, { _id: idArray });
    if (res.code === 200) {
      message.success('操作成功！');
      fetchData();
    } else {
      message.error(res.message || '操作失败');
    }
  } catch (e) {
    message.error('请求异常');
  }
};

const handleSingleAction = (type, id) => performAction(type, [id]);
const handleBatchStop = () => performAction('stop', selectedRowKeys.value);
const handleBatchDelete = () => performAction('delete', selectedRowKeys.value);

onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.search-row { display: flex; flex-wrap: wrap; gap: 16px 12px; align-items: center; }
.search-item { display: flex; align-items: center; }
.search-item .label { color: rgba(0,0,0,0.85); margin-right: 8px; min-width: 60px; text-align: right; white-space: nowrap; }
</style>