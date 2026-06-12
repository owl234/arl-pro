import re
from bson import ObjectId
from flask_restx import Resource, Api, reqparse, fields, Namespace
from app.utils import get_logger, auth
from app import utils
from . import base_query_fields, ARLResource, get_arl_parser
from app.utils import conn_db as conn
from app.modules import ErrorMsg, AssetScopeType

# 成立“资产组范围”部门，专门管理“地契”
ns = Namespace('asset_scope', description="资产组范围")

logger = get_logger()

# ==========================================
# 表单：新建和查询时用到的基础字段
# ==========================================
base_fields = {
    'name': fields.String(description="资产组名称"),
    'scope': fields.String(description="资产范围"),
    "black_scope": fields.String(description="资产黑名单"),
    "scope_type": fields.String(description="资产范围类别")
}


add_asset_scope_fields = ns.model('addAssetScope', base_fields)

# 查询时多加一个 _id 和 分页字段
base_fields.update({
    "_id": fields.String(description="资产范围 ID")
})

base_fields.update(base_query_fields)


@ns.route('/')
class ARLAssetScope(ARLResource):
    parser = get_arl_parser(base_fields, location='args')

    @auth
    @ns.expect(parser)
    def get(self):
        """
        资产组查看
        """
        args = self.parser.parse_args()
        data = self.build_data(args=args, collection='asset_scope')

        return data

    @auth
    @ns.expect(add_asset_scope_fields)
    def post(self):
        """
        资产组添加：创建一个新的地契
        """
        args = self.parse_args(add_asset_scope_fields)
        name = args.pop('name')
        scope = args.pop('scope')
        black_scope = args.pop('black_scope')
        scope_type = args.pop('scope_type')

        # 1. 强制规范类型：如果前端乱传，强制设为 DOMAIN (域名) 类型
        if scope_type not in [AssetScopeType.IP, AssetScopeType.DOMAIN]:
            scope_type = AssetScopeType.DOMAIN

        black_scope_array = []
        # 2. 正则切割黑名单：把前端传的用逗号或空格隔开的长字符串，切成列表
        if black_scope:
            black_scope_array = re.split(r",|\s", black_scope)

        # 3. 正则切割正常范围，并清理空字符 (比如用户多打了一个空格)
        scope_array = re.split(r",|\s", scope)
        scope_array = list(filter(None, scope_array))

        new_scope_array = []
        # 4. 【核心验证】：遍历用户填的每一个目标，验证是不是真的合法
        for x in scope_array:
            if scope_type == AssetScopeType.DOMAIN:
                # 借助内置工具校验是不是合法域名
                if not utils.is_valid_domain(x):
                    return utils.build_ret(ErrorMsg.DomainInvalid, {"scope": x})

                new_scope_array.append(x)

            if scope_type == AssetScopeType.IP:
                # 借助内置工具校验并转换 IP (支持 192.168.1.1 这种单IP，也支持 192.168.1.0/24 这种网段)
                transfer = utils.ip.transfer_ip_scope(x)
                if transfer is None:
                    return utils.build_ret(ErrorMsg.ScopeTypeIsNotIP, {"scope": x})

                new_scope_array.append(transfer)

        # 如果清洗完发现全是废数据，直接打回
        if not new_scope_array:
            return utils.build_ret(ErrorMsg.DomainInvalid, {"scope": ""})

        # 5. 组装数据并插入数据库
        scope_data = {
            "name": name,
            "scope_type": scope_type,
            "scope": ",".join(new_scope_array),        # 存一份字符串格式 (为了前端显示)
            "scope_array": new_scope_array,            # 存一份列表格式 (为了后端程序方便比对)
            "black_scope": black_scope,
            "black_scope_array": black_scope_array,
        }
        conn('asset_scope').insert(scope_data)

        # 补全返回数据
        scope_id = str(scope_data.pop("_id"))
        scope_data["scope_id"] = scope_id

        return utils.build_ret(ErrorMsg.Success, scope_data)

# ==========================================
# 接口模块：删除相关 (包含部分删除 和 整体销毁)
# ==========================================
delete_task_get_fields = ns.model('DeleteScopeByID',  {
    'scope': fields.String(description="删除资产范围", required=True),
    'scope_id': fields.String(description="资产范围id", required=True)
})


delete_task_post_fields = ns.model('DeleteScope',  {
    'scope_id': fields.List(fields.String(description="删除资产范围", required=True), required=True)
})


@ns.route('/delete/')
class DeleteARLAssetScope(ARLResource):
    parser = get_arl_parser(delete_task_get_fields, location='args')

    _table = 'asset_scope'

    # 接口 A：局部删除 (GET) - 从某个资产组里，剔除一个具体的域名
    @auth
    @ns.expect(parser)
    def get(self):
        """
        针对资产组删除范围
        """
        args = self.parser.parse_args()
        scope = str(args.pop('scope', "")).lower()  # 比如要删 "baidu.com"
        scope_id = str(args.pop('scope_id', "")).lower()# 在 "资产组A" 里面

        scope_data = self.get_scope_data(scope_id)
        if not scope_data:
            return utils.build_ret(ErrorMsg.NotFoundScopeID, {"scope_id": scope_id})

        query = {'_id': ObjectId(scope_id)}

        # 防御：要删的东西根本不在这里面
        if scope not in scope_data.get("scope_array", []):
            return utils.build_ret(ErrorMsg.NotFoundScope, {"scope_id": scope_id, "scope":scope})

        # 核心：操作 Python 列表剔除元素，再更新成字符串，最后整条替换数据库里的旧数据
        scope_data["scope_array"].remove(scope)
        scope_data["scope"] = ",".join(scope_data["scope_array"])
        utils.conn_db(self._table).find_one_and_replace(query, scope_data)

        return utils.build_ret(ErrorMsg.Success, {"scope_id": scope_id, "scope":scope})

    def get_scope_data(self, scope_id):
        query = {'_id': ObjectId(scope_id)}
        scope_data = utils.conn_db(self._table).find_one(query)
        return scope_data

    # 接口 B：整体销毁 (POST) - 连锅端！
    @auth
    @ns.expect(delete_task_post_fields)
    def post(self):
        """
        删除资产组和资产组中的资产 (极其危险的操作)
        """
        args = self.parse_args(delete_task_post_fields)
        scope_id_list = args.pop('scope_id')

        # 1. 第一轮循环：纯校验
        for scope_id in scope_id_list:
            if not self.get_scope_data(scope_id):
                return utils.build_ret(ErrorMsg.NotFoundScopeID, {"scope_id": scope_id})

        # 2. 定义受牵连的表（因为你把地契烧了，那这块地上的所有财产全得清空）
        table_list = ["asset_domain", "asset_site", "asset_ip", "scheduler", "asset_wih"]

        # 3. 第二轮循环：大清洗 (级联删除)
        for scope_id in scope_id_list:
            # 删地契本身
            utils.conn_db(self._table).delete_many({'_id': ObjectId(scope_id)})

            # 删牵连的战利品
            for name in table_list:
                utils.conn_db(name).delete_many({'scope_id': scope_id})

        return utils.build_ret(ErrorMsg.Success, {"scope_id": scope_id_list})


# ==========================================
# 接口：向现有资产组追加新域名 (POST /add/)
# ==========================================
add_scope_fields = ns.model('AddScope',  {
    'scope': fields.String(description="添加资产范围"),
    "scope_id": fields.String(description="添加资产范围")
})


@ns.route('/add/')
class AddARLAssetScope(ARLResource):
    @auth
    @ns.expect(add_scope_fields)
    def post(self):
        """
        添加资产范围(局部追加)
        """
        args = self.parse_args(add_scope_fields)
        scope = str(args.pop('scope', "")).lower()

        scope_id = args.pop('scope_id', "")

        table = 'asset_scope'
        query = {'_id': ObjectId(scope_id)}
        scope_data = utils.conn_db(table).find_one(query)
        if not scope_data:
            return utils.build_ret(ErrorMsg.NotFoundScopeID, {"scope_id": scope_id, "scope": scope})

        scope_type = scope_data.get("scope_type")
        if scope_type not in [AssetScopeType.IP, AssetScopeType.DOMAIN]:
            scope_type = AssetScopeType.DOMAIN

        scope_array = re.split(r",|\s", scope)
        # 清除空白符
        scope_array = list(filter(None, scope_array))
        if not scope_array:
            return utils.build_ret(ErrorMsg.DomainInvalid, {"scope": ""})

        for x in scope_array:
            new_scope = x
            if scope_type == AssetScopeType.DOMAIN:
                if not utils.is_valid_domain(x):
                    return utils.build_ret(ErrorMsg.DomainInvalid, {"scope": x})

            if scope_type == AssetScopeType.IP:
                transfer = utils.ip.transfer_ip_scope(x)
                if transfer is None:
                    return utils.build_ret(ErrorMsg.ScopeTypeIsNotIP, {"scope": x})
                new_scope = transfer

            if new_scope in scope_data.get("scope_array", []):
                return utils.build_ret(ErrorMsg.ExistScope, {"scope_id": scope_id, "scope": x})

            scope_data["scope_array"].append(new_scope)

        scope_data["scope"] = ",".join(scope_data["scope_array"])
        utils.conn_db(table).find_one_and_replace(query, scope_data)

        return utils.build_ret(ErrorMsg.Success, {"scope_id": scope_id, "scope": scope})