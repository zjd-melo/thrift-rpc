#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
write by zhujiadong 2016-04-12
"""

import thriftpy
from thriftpy.rpc import make_server
import xmlrpclib
import json
import datetime
from datetime import timedelta
import os
import redis

DB = 'db'
URL = "localhost"
ODOOPORT = "8069"
REDISHOST = '127.0.0.1'
REDISPORT = '6379'

class Dispatcher(object):
    # 登陆句柄
    @staticmethod
    def __loginSock():
        sock_common = xmlrpclib.ServerProxy('http://%s:%s/xmlrpc/common' % (URL, ODOOPORT), allow_none=True)
        return sock_common

    # 操作句柄
    @staticmethod
    def __optSock():
        sock = xmlrpclib.ServerProxy('http://%s:%s/xmlrpc/object' % (URL, ODOOPORT), allow_none=True)
        return sock

    # summary:移动登陆验证
    def isLoginSuccess(self, password, username):
        try:
            uid = Dispatcher().__loginSock().login(DB, username, password)
            if uid:
                return json.dumps({"uid": uid})
            else:
                return json.dumps({"faultcode": "Wrong username or password"})
        except Exception, e:
            if e.__dict__['faultCode'] == 'FATAL:  database ' + '"' + DB + '"' + ' does not exist\n':
                return json.dumps({"faultcode": "database " + DB + " does not exist"})
            elif str(e.__dict__['faultCode'].encode("utf-8")).find("AccessError"):
                return json.dumps({"faultcode": "AccessDenied"})

    # summary:获取设备信息
    def getAssets(self,uid, password):
        try:
            sock = Dispatcher().__optSock()
            ids = sock.execute_kw(DB, uid, password, "cmdb.asset", "search",
                                  [[['id', '>=', 1], ['is_data_collect', '=', 'true']]])
            assetsInfo = sock.execute_kw(DB, uid, password, "cmdb.asset", "search_read", [[['id', 'in', ids]]],
                                         {'fields': ['id', 'name', 'install_building_id']})
            return json.dumps(assetsInfo)
        except Exception, e:
            if e.__dict__['faultCode'] == 'FATAL:  database ' + '"' + DB + '"' + ' does not exist\n':
                return json.dumps({"faultcode": "database " + DB + " does not exist"})
            elif str(e.__dict__['faultCode'].encode("utf-8")).find("AccessError"):
                return json.dumps({"faultcode": "AccessDenied"})

    # summary:获取属性信息
    def getAttributes(self, uid, password):
        try:
            sock = Dispatcher().__optSock()
            ids = sock.execute_kw(DB, uid, password, "cmdb.asset.attribute", "search", [[]])
            attributeInfo = sock.execute_kw(DB, uid, password, "cmdb.asset.attribute", "search_read",
                                            [[['id', 'in', ids]]],
                                            {'fields': ["id", "name", "asset_id","high","low"]})
            return json.dumps(attributeInfo)
        except Exception, e:
            if e.__dict__['faultCode'] == 'FATAL:  database ' + '"' + DB + '"' + ' does not exist\n':
                return json.dumps({"faultcode": "database " + DB + " does not exist"})
            elif str(e.__dict__['faultCode'].encode("utf-8")).find("AccessError"):
                return json.dumps({"faultcode": "AccessDenied"})

    # summary:获取事件警告
    def getErrorAndEventByTime(self, uid, password, starttime, endtime):
        try:
            start_time = datetime.datetime.strptime(starttime, '%Y-%m-%d %H:%M:%S') + timedelta(hours=-8)
            end_time = datetime.datetime.strptime(endtime, '%Y-%m-%d %H:%M:%S') + timedelta(hours=-8, seconds=+1)

            if (end_time - start_time) < datetime.timedelta(seconds=0):
                return "time error"

            sock = Dispatcher().__optSock()
            ids = sock.execute_kw(DB, uid, password, "cmdb.asset.warning.error", "search",
                                  [[['id', '>=', 1], ['collect_time', '>=', start_time.strftime('%Y-%m-%d %H:%M:%S')],
                                    ['collect_time', '<=', end_time.strftime('%Y-%m-%d %H:%M:%S')]]])
            warreventInfo = sock.execute_kw(DB, uid, password, "cmdb.asset.warning.error", "search_read",
                                            [[['id', 'in', ids]]],
                                            {'fields': ["asset_id", "asset_attr_name", "excep_type", "collect_value",
                                                        "collect_time", "description","warning_state"]})
            if warreventInfo:
                return json.dumps(warreventInfo)
            else:
                return json.dumps({"faultcode": "Warning and Event does not exist"})
        except Exception, e:
            if e.__dict__['faultCode'] == 'FATAL:  database ' + '"' + DB + '"' + ' does not exist\n':
                return json.dumps({"faultcode": "database " + DB + " does not exist"})
            elif str(e.__dict__['faultCode'].encode("utf-8")).find("AccessError"):
                return json.dumps({"faultcode": "AccessDenied"})

    # summary:获取维修记录
    def getRepairInfoByTime(self, uid, password, starttime, endtime):
        start_time = datetime.datetime.strptime(starttime, '%Y-%m-%d %H:%M:%S') + timedelta(hours=-8)
        end_time = datetime.datetime.strptime(endtime, '%Y-%m-%d %H:%M:%S') + timedelta(hours=-8, seconds=+1)

        if (end_time - start_time) < datetime.timedelta(seconds=0):
            return "time error"

        sock = Dispatcher().__optSock()
        ids = sock.execute_kw(DB, uid, password, "cmdb.repair", "search",
                              [[['id', '>=', 1], ['create_date', '>=', start_time.strftime('%Y-%m-%d %H:%M:%S')],
                                ['create_date', '<=', end_time.strftime('%Y-%m-%d %H:%M:%S')]]])
        repairInfo = sock.execute_kw(DB, uid, password, "cmdb.repair", "search_read", [[['id', 'in', ids]]],
                                       {'fields': ["id", "name", "asset_id", "finished_time", "state","fault_reason","repair_man"]})
        if repairInfo:
            return json.dumps(repairInfo)
        else:
            return json.dumps({"faultcode": "Repair Info does not exist"})
    #获取维修完成的维修记录
    def getFinishedRepairInfo(self,uid,password,name):
        sock = Dispatcher().__optSock()
        try:
            ids = sock.execute_kw(DB,uid,password,"cmdb.repair","search",[[['name','=',name]]])
            repairInfo = sock.execute_kw(DB, uid, password, "cmdb.repair", "search_read", [[['id', 'in', ids],['state','=','finished']]],
                                       {'fields':['id','name','asset_id','finished_time','state','fault_reason','repair_man','repair_method']})
            res_id = ids and ids[0] or False
            repair=sock.execute_kw(DB, uid, password, 'ir.attachment', 'search_read',[[['res_model','=','cmdb.repair'],['res_id','=',res_id]]],
                                       {'fields':['name','datas','datas_fname']})
            repairInfo.append(repair)
            if repairInfo:
                return json.dumps(repairInfo)
            else:
                return json.dumps({"faultcode": "Repair Info does not exist"})
        except Exception,e:
            print e
        

    # 通过oid获取设备信息
    def getAssetByOid(self, oid, uid, password):
        try:
            sock = Dispatcher().__optSock()
            asset = sock.execute_kw(DB, uid, password, 'cmdb.asset', 'search_read', [[['oid', '=', oid]]],
                                    {'limit': 1,'fields': ['id', 'name', 'code', 'specification', 'brand', 'factory_number',
                                    'buying_price', 'attributes', 'control_points', 'oid', 'opc_server','opc_client']})
            if asset:
                asset_msg = asset[0]
                return json.dumps(asset_msg)
            else:
                return json.dumps({"faultcode": "Oid does not exist!"})
        except Exception, e:
            if e.__dict__['faultCode'] == 'FATAL:  database ' + '"' + DB + '"' + ' does not exist\n':
                return json.dumps({"faultcode": "database " + DB + " does not exist"})
            elif str(e.__dict__['faultCode'].encode("utf-8")).find("AccessError"):
                return json.dumps({"faultcode": "AccessDenied"})

    """
    # 获取设备全部信息
    def getAllAssets(self):
        sock = Dispatcher().__optSock()
        all_assets = sock.execute_kw(DB, SUPPER_USER_ID, USERPASS, 'cmdb.asset', 'search_read', [[]],
                                     {'fields': ['id', 'name', 'code', 'attributes', 'control_points']})

        all_assets_list = {
            "asset_info": all_assets,
        }

        return json.dumps(all_assets_list)
    """

    # 通过assetid获取采集点信息
    def getCollectPointsByAssetId(self, asset_id, uid, password):
        try:
            sock = Dispatcher().__optSock()

            collectpoints = sock.execute_kw(DB, uid, password, 'cmdb.asset.collectpoint',
                                            'search_read', [[['asset_id', '=', asset_id]]],
                                            {'fields': ['attribute_id', 'attribute_name', 'attribute_code']})
            if collectpoints:
                attribute_list = collectpoints
                for point in range(len(collectpoints)):
                    attribute_list[point]['attribute_id'] = collectpoints[point]['attribute_id'][0]
                    attribute_list[point].pop('id')

                collectpoints_msg = {
                    "asset_collectpoints": attribute_list,
                }
                return json.dumps(collectpoints_msg)
            else:
                return json.dumps({"faultcode": "Asset ID does not exist!"})
        except Exception, e:
            if e.__dict__['faultCode'] == 'FATAL:  database ' + '"' + DB + '"' + ' does not exist\n':
                return json.dumps({"faultcode": "database " + DB + " does not exist"})
            elif str(e.__dict__['faultCode'].encode("utf-8")).find("AccessError"):
                return json.dumps({"faultcode": "AccessDenied"})

    """
    # 通过设备id获取历史数据
    def getHistoryRecordsByAssetId(self, db, uid, password, attribute_id, start_time, end_time):

        sock = Dispatcher().__optSock()
        # 数据库中是GMT时间,所以拿过来的时间要进行时区换算
        start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S') + timedelta(hours=-8)
        end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S') + timedelta(hours=-8, seconds=+1)

        history_records = sock.execute_kw(db, uid, password, 'cmdb.asset.collect.record',
                                          'search_read', [[['asset_attr_id', '=', attribute_id], ['collect_time', '>=',
                                                                                                  start_time.strftime(
                                                                                                      '%Y-%m-%d %H:%M:%S')],
                                                           ['collect_time', '<=',
                                                            end_time.strftime('%Y-%m-%d %H:%M:%S')]]], {'fields': []})

        history_records_lists = history_records

        for point in range(len(history_records)):
            history_records_lists[point]['collect_point_id'] = history_records_lists[point]['collect_point_id'][1]
            history_records_lists[point]['collect_asset_id'] = history_records_lists[point]['collect_asset_id'][1]
            history_records_lists[point]['asset_attr_id'] = history_records_lists[point]['asset_attr_id'][1]
            history_records_lists[point]['asset_id'] = history_records_lists[point]['asset_id'][1]
            history_records_lists[point].pop('create_uid')
            history_records_lists[point].pop('__last_update')
            history_records_lists[point].pop('create_date')
            history_records_lists[point].pop('write_uid')
            history_records_lists[point].pop('write_date')
            history_records_lists[point].pop('display_name')
            history_records_lists[point].pop('id')

        history_records_msg = {
            "history_records": history_records_lists,
        }

        return json.dumps(history_records_msg)

    # 通过时间获取历史数据
    def getHistoryRecordsByTime(self, db, uid, password, start_time, end_time):

        sock = Dispatcher().__optSock()

        start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S') + timedelta(hours=-8)
        end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S') + timedelta(hours=-8, seconds=+1)

        history_records = sock.execute_kw(db, uid, password, 'cmdb.asset.collect.record',
                                          'search_read', [
                                              [['collect_time', '>=', start_time.strftime('%Y-%m-%d %H:%M:%S')],
                                               ['collect_time', '<=', end_time.strftime('%Y-%m-%d %H:%M:%S')]]],
                                          {'fields': []})

        history_records_lists = history_records

        for point in range(len(history_records)):
            history_records_lists[point]['collect_point_id'] = history_records_lists[point]['collect_point_id'][1]
            history_records_lists[point]['collect_asset_id'] = history_records_lists[point]['collect_asset_id'][1]
            history_records_lists[point]['asset_attr_id'] = history_records_lists[point]['asset_attr_id'][1]
            history_records_lists[point]['asset_id'] = history_records_lists[point]['asset_id'][1]
            history_records_lists[point].pop('create_uid')
            history_records_lists[point].pop('__last_update')
            history_records_lists[point].pop('create_date')
            history_records_lists[point].pop('write_uid')
            history_records_lists[point].pop('write_date')
            history_records_lists[point].pop('display_name')
            history_records_lists[point].pop('id')

        history_records_msg = {
            "history_records": history_records_lists,
        }

        return json.dumps(history_records_msg)
    """

    # 通过oid得到采集点信息
    def getCollectPointsByOid(self, oid, uid, password):
        try:
            sock = Dispatcher().__optSock()
            assets_info = self.getAssetByOid(oid, uid, password)

            if not json.loads(assets_info).has_key("faultcode"):
                asset_id, attributes = json.loads(assets_info)['id'], json.loads(assets_info)['attributes']
                collectpoints = sock.execute_kw(DB, uid, password, 'cmdb.asset.collectpoint','search_read', [[['asset_id', '=', asset_id]]],
                                                {'limit': len(attributes),'fields': ['name', 'attribute_id', 'attribute_name', 'attribute_code']})

                if collectpoints:
                    attribute_list = collectpoints
                    for point in range(len(collectpoints)):
                        attribute_list[point]['attribute_id'] = collectpoints[point]['attribute_id'][0]
                        attribute_list[point].pop('id')

                    collectpoints_msg = {
                        "asset_collectpoints": attribute_list,
                    }
                    return json.dumps(collectpoints_msg)
                else:
                    return json.dumps({"faultcode": "Collect Point does not exist!"})
            else:
                return json.dumps({"faultcode": "Oid or Attributes does not exist!"})
        except Exception, e:
            if e.__dict__['faultCode'] == 'FATAL:  database ' + '"' + DB + '"' + ' does not exist\n':
                return json.dumps({"faultcode": "database " + DB + " does not exist"})
            elif str(e.__dict__['faultCode'].encode("utf-8")).find("AccessError"):
                return json.dumps({"faultcode": "AccessDenied"})

    # 通过oid获取控制点信息
    def getControlPointByOid(self, oid, uid, password):
        try:
            sock = Dispatcher().__optSock()
            assets_info = self.getAssetByOid(oid, uid, password)

            if not json.loads(assets_info).has_key("faultcode"):
                control_points = json.loads(assets_info)['control_points']

                controlpoints = sock.execute_kw(DB, uid, password, 'cmdb.asset.controlpoint','search_read', [[['asset_id', '=', control_points]]],
                                                {'limit': len(control_points),'fields': ['action_id', 'name', 'asset_id', 'asset_id_2',
                                                'action_name', 'action_code', 'cmdcontent', 'item_id']})
                if controlpoints:
                    controlpoints_list = controlpoints
                    for point in range(len(controlpoints_list)):
                        controlpoints_list[point]['asset_id'] = controlpoints_list[point]['asset_id'][0]
                        controlpoints_list[point]['asset_id_2'] = controlpoints_list[point]['asset_id_2'][0]
                        controlpoints_list[point]['action_id'] = controlpoints_list[point]['action_id'][0]
                        controlpoints_list[point].pop('id')

                    controlpoints_msg = {
                        "asset_controlpoints": controlpoints_list,
                    }
                    return json.dumps(controlpoints_msg)
                else:
                    return json.dumps({"faultcode": "Control Point does not exist!"})
            else:
                return json.dumps({"faultcode": "Oid or Control Points does not exist!"})
        except Exception, e:
            if e.__dict__['faultCode'] == 'FATAL:  database ' + '"' + DB + '"' + ' does not exist\n':
                return json.dumps({"faultcode": "database " + DB + " does not exist"})
            elif str(e.__dict__['faultCode'].encode("utf-8")).find("AccessError"):
                return json.dumps({"faultcode": "AccessDenied"})

    # 提供给3D图形的接口，用于根据oid查询信息
    def packMessage(self, oid, uid, password):
        try:
            asset_msg = json.loads(self.getAssetByOid(oid, uid, password))
            collectpoints_msg = json.loads(self.getCollectPointsByOid(oid, uid, password))
            controlpoints_msg = json.loads(self.getControlPointByOid(oid, uid, password))

            if asset_msg.has_key("faultcode"):
                return json.dumps({"faultcode": "Oid does not exist!"})
            else:
                final_msg = {
                    "asset_name": asset_msg['name'],
                    "asset_code": asset_msg['code'],
                    "asset_specification": asset_msg['specification'],
                    "asset_brand": asset_msg['brand'],
                    "asset_factory_number": asset_msg['factory_number'],
                    "asset_buying_price": asset_msg['buying_price'],
                    "asset_oid": asset_msg['oid'],
                    "asset_opc_server": asset_msg['opc_server'],
                    "asset_opc_client": asset_msg['opc_client'],
                }
                final_msg = final_msg.copy()
                if collectpoints_msg.has_key("faultcode") and controlpoints_msg.has_key("faultcode"):
                    final_msg.update({"faultcode": "Collect Points and Control Points does not exist"})
                else:
                    final_msg.update(controlpoints_msg)
                    final_msg.update(collectpoints_msg)
                return json.dumps(final_msg)
        except Exception, e:
            if e.__dict__['faultCode'] == 'FATAL:  database ' + '"' + DB + '"' + ' does not exist\n':
                return json.dumps({"faultcode": "database " + DB + " does not exist"})
            elif str(e.__dict__['faultCode'].encode("utf-8")).find("AccessError"):
                return json.dumps({"faultcode": "AccessDenied"})

    # 获取全部控制系统
    def getSystemControlInfo(self, uid, password):
        try:
            sock = Dispatcher().__optSock()
            systemcontrolids = sock.execute_kw(DB, uid, password, 'cmdb.assetsystemcontrol',
                                               'search_read', [[]], {'fields': ['id', 'name', 'remark']})
            if systemcontrolids:
                systemcontrol_msg = {
                    "systemcontrol": systemcontrolids
                }
                return json.dumps(systemcontrol_msg)
            else:
                return json.dumps({"faultcode": "System Control does not exist"})
        except Exception, e:
            if e.__dict__['faultCode'] == 'FATAL:  database ' + '"' + DB + '"' + ' does not exist\n':
                return json.dumps({"faultcode": "database " + DB + " does not exist"})
            elif str(e.__dict__['faultCode'].encode("utf-8")).find("AccessError"):
                return json.dumps({"faultcode": "AccessDenied"})

    # 获取某个控制系统内的所有设备信息
    def getAsset2SystemControl(self, uid, password, systemcontrol_id):
        try:
            sock = Dispatcher().__optSock()
            asset2systems = sock.execute_kw(DB, uid, password, 'cmdb.asset','search_read', [[['system_control_id', '=', systemcontrol_id]]],
                                            {'fields': ['oid', 'system_control_id']})

            if asset2systems:
                asset2systems_list = asset2systems
                for point in range(len(asset2systems_list)):
                    asset2systems_list[point]['system_control_id'] = asset2systems_list[point]['system_control_id'][0]
                    asset2systems_list[point].pop('id')

                asset_systemcontrol_msg = {
                    "asset2system": asset2systems_list
                }
                return json.dumps(asset_systemcontrol_msg)
            else:
                return json.dumps({"faultcode": "System Asset does not exist"})
        except Exception, e:
            if e.__dict__['faultCode'] == 'FATAL:  database ' + '"' + DB + '"' + ' does not exist\n':
                return json.dumps({"faultcode": "database " + DB + " does not exist"})
            elif str(e.__dict__['faultCode'].encode("utf-8")).find("AccessError"):
                return json.dumps({"faultcode": "AccessDenied"})

    def insert_command_feedback(self, db, uid, password, action_id, asset_id, name, asset_id_2, action_code,action_name, item_id):

        sock = Dispatcher().__optSock()

        command_msg = {
            "cmd_action_id": action_id,
            "collect_assetId": asset_id,
            "control_name": name,
            "command_send_time": (datetime.datetime.now() + timedelta(hours=-8)).strftime("%Y-%m-%d %H:%M:%S"),
            "controlled_assetId": asset_id_2,
            "cmd_action_code": action_code,
            "is_success": u'\u5931\u8d25'.encode("utf8"),
            "cmd_action_name": action_name,
            "feedback_item_id": item_id,

            # 'cmd_content':control_asset[0]["cmdcontent"],
            # 'is_success':'false',
        }
        sock.execute(db, uid, password, "cmdb.asset.command.feedback", "create", command_msg)

    # 维修工作流的控制和附件的上传
    def asset_repair(self, uid, password, name, atta_name, atta_description,file_list, kind ,flag, repair_time, fault_reason, repair_method, remark,line):
        sock = Dispatcher.__optSock()
        ids = sock.execute_kw(DB, uid, password, 'cmdb.repair', 'search', [[['name', '=', name]]])
        res_id = ids and ids[0] or False
        atta_info = zip(atta_name, atta_description, file_list)

        # 上传附件
        def upload_attach():
            if kind == 'url':
                for item in atta_info:
                    data = {'name': item[0], 'type': 'url', 'url': item[2][0], 'res_model': 'cmdb.repair', 'res_id': res_id,
                            'description': item[1]}
                    sock.execute_kw(DB, uid, password, 'ir.attachment', 'create', [data])
            else:
                for item in atta_info:
                    data = {'name': item[0], 'type': 'binary', 'datas': item[2][1], 'res_model': 'cmdb.repair',
                            'res_id': res_id, 'description': item[1], 'datas_fname': item[2][0]}
                    sock.execute_kw(DB, uid, password, 'ir.attachment', 'create', [data])

        # 上传维修操作
        def upload_line():
            # 获取上一次维修时间
            repairing_time = sock.execute_kw(DB, uid, password, 'cmdb.repair',
                                        'search_read', [[['id', '=', res_id]]],
                                        {'fields': ['repairing_time']})[0]["repairing_time"]

            if not repairing_time:
                repairing_time = str(datetime.datetime.now() + timedelta(hours=-8))

            #print repairing_time

            if not line:
                val = {'state': 'repairing', 'repair_time': repair_time, 'repair_date': repairing_time,'fault_reason': fault_reason,
                    'repair_method': repair_method, 'remark': remark, 'repairing_time': repairing_time}
                sock.execute_kw(DB, uid, password, 'cmdb.repair', 'write', [[ids[0]], val])

                if atta_name:
                    # 上传附件
                    upload_attach()
            else:
                # 插入维修操作
                for i in line:
                    if i[2] == '服务'.decode('utf-8'):
                        record_id = [1]
                    else:
                        record_id = sock.execute_kw(DB, uid, password, 'product.template', 'search',
                                                [[['name', '=', i[2]]]])
                        val = {'state': 'repairing', 'repair_time': repair_time, 'repair_date': repairing_time,'fault_reason': fault_reason,
                                    'repair_method': repair_method, 'remark': remark,'repairing_time': repairing_time,
                                    "cmdb_repair_lines": [[0, 0, {'cmdb_repair_id': name, 'product_id': record_id[0],
                                    'product_qty': int(i[0]), 'operation_time': strtime, 'type':i[1],'name':i[3]}]]}
                        sock.execute_kw(DB, uid, password, 'cmdb.repair', 'write', [[ids[0]], val])
                if atta_name:
                    # 上传附件
                    upload_attach()
        # 是否完成维修
        if flag:
            finished_time = str(datetime.datetime.now() + timedelta(hours=-8))
            upload_line()

            # 更新维修单为完成状态
            sock.execute_kw(DB, uid, password, 'cmdb.repair', 'write', [[ids[0]],
                                {'finished_time': finished_time, 'state': 'finished'}])

            # 对维修申请单的状态进行修改
            repair_report_id = sock.execute_kw(DB, uid, password, 'cmdb.repair.report', 'search', [[['name', '=', name]]])
            if repair_report_id:
                sock.execute_kw(DB, uid, password, 'cmdb.repair.report', 'write',
                                [[repair_report_id[0]], {'state': 'finished','write_date': finished_time}])
            return json.dumps({"RepairStatus": "Finished"})
        else:
            upload_line()
            return json.dumps({"RepairStatus": "Repairing"})

    # 从redis获取历史数据    
    def getCollectData(self,starttime,endtime):
        if (int(endtime) - int(starttime)) <= 0:
            return json.dumps("time error")
        try:
            r = redis.StrictRedis(REDISHOST,REDISPORT)    
            result = r.zrangebyscore('test',starttime,endtime)
        except Exception,e:
            if e:
                return json.dumps({"faultcode": 'connect to redis error'})
        if result:
            return json.dumps(result)
        else:
            return json.dumps({'faultcode':'CollectData does not exist'})

    # 根据设备id，属性获取历史数据
    def getCollectDataByAssetAndAttr(self,asset_id,attribute,starttime,endtime):
        if (int(endtime) - int(starttime)) <= 0:
            return json.dumps("time error,check the start time and endtime!")
        item = self.getCollectData(starttime,endtime)
        if type(eval(item)) == dict:
           return json.dumps('Collect data does not exist!')
        result=[]
        item = json.loads(item)
        for i in item:
            t=i.encode('utf-8')
            d=eval(t)
            try:
                if d['asset_name'].decode('utf-8') == asset_id and d['attribute_name'].decode('utf-8') == attribute:
                    result.append(d)
            except Exception,e:
                print e
        if result:
            return json.dumps(result)
        return json.dumps('not found any data!')

def server_start(conf_path, thrift_ip, thrift_port):
    main_thrift = thriftpy.load(conf_path, module_name="main_thrift")
    server = make_server(main_thrift.OdooService, Dispatcher(),thrift_ip, thrift_port)
    print("Serving...")
    print "Listening on port " + str(thrift_port) + "..."
    server.serve()

if __name__ == "__main__":
    conf_path = os.path.abspath("./conf/main.thrift")
    server_start(conf_path,"127.0.0.1",6000)
