#<center>OdooRPC数据封装调用文档</center>
###<center>Made by Imperio Dec 2015</center>
>## 一、移动(Mobile)RPC调用总览


### 

| 方法名 | 作用 |
|:----:|:----:|
| isLoginSuccess() | 验证用户登录 |
| getAssetsAttrRealTimeByMobile() | 查询设备、属性信息、实时数据 |
| getInfoFromTimeByMobile()    | 获取事件警告、历史数据、维修信息 |
~~~
INTERFACEPORT = 7777
URL = IP
server = xmlrpclib.ServerProxy("http://%s:%s" % (URL,INTERFACEPORT))
~~~
### 1. isLoginSuccess(self, db, password, username)
~~~
/**
 *@params db,password,username
 *@return  1.uid(成功)
 *         2.false(失败)
 *         3.{"faultcode": "database dbname does not exist"}(数据库错误)
 **/
 
 //登录调用实例(python)
 server = xmlrpclib.ServerProxy("http://%s:%s" % (URL,INTERFACEPORT))
 isLogin = server.isLoginSuccess('db', 'admin', 'admin')
 print isLogin
 
 //结果
 1
~~~
###2. getAssetsAttrRealTimeByMobile(self,db,uid,password,tablename)
~~~
/**
 *@params db,uid,password,tablename
 *@return  1.[[{……}]](成功)
 *         2.{"faultcode": "AccessDenied"}(没有权限)
 *         3.{"faultcode": "database dbname does not exist"}(数据库错误)
 **/
 
 //1.获取设备信息调用实例(python)
 server = xmlrpclib.ServerProxy("http://%s:%s" % (URL,INTERFACEPORT))
 getAssetsByMobile = server.getAssetsAttrRealTimeByMobile('db', isLogin, 'admin', 'cmdb.asset')
 print getAssetsByMobile
 
 //结果(由于我是整个对象的输出，所以是打印的是Unicode编码，JS直接获取JSON数据应该能获取到utf-8)
 [[
    {
        "id": 1, 
        "name": "\u6c28\u6c34\u8f93\u9001\u6cf5A", 
        "install_building_id": [1, "\u4e09\u53f7\u9505\u7089\u623f\u533a\u95f4"]
    }, 
    {…}
 ]]
 
 
 //2.获取设备属性调用实例(python)
 server = xmlrpclib.ServerProxy("http://%s:%s" % (URL,INTERFACEPORT))
 getAttributeByMobile = server.getAssetsAttrRealTimeByMobile('db',isLogin,'admin','cmdb.asset.attribute')
 print getAttributeByMobile

 //结果
 [[
    {
        "asset_id": [7, "\u6c28\u6c34\u7ba1\u9053\u538b\u529b\u8868"], 
        "id": 53, 
        "name": "\u7ba1\u9053\u538b\u529b\u53cd\u9988"
    }, 
    {…}
 ]]
 
 //3.获取实时数据调用实例(python)
 server = xmlrpclib.ServerProxy("http://%s:%s" % (URL,INTERFACEPORT))
 getRealTimeByMobile = server.getAssetsAttrRealTimeByMobile('db',isLogin,'admin','cmdb.asset.collect.finalrecord')
 print getRealTimeByMobile
 
 //结果
 [[ 
    {
        "collect_value": "0.9004", 
        "id": 57, 
        "collect_time": "2015-12-29 21:03:53"
    },
    {…}
 ]]    

~~~

###3. getInfoFromTimeByMobile(self,db,uid,password,starttime,endtime,tablename)
~~~
/**
 *@params db,uid,password,starttime,endtime,tablename
 *@return  1.[[{……}]](成功)
 *         2.{"faultcode": "AccessDenied"}(没有权限)
 *         3.{"faultcode": "database dbname does not exist"}(数据库错误)
 **/
 
 //1.获取事件警告调用实例(python)
 server = xmlrpclib.ServerProxy("http://%s:%s" % (URL,INTERFACEPORT))
 getWarrEventByMobile = server.getInfoFromTimeByMobile('db',isLogin,'admin',
                            '2015-12-17 22:55:00','2015-12-17 22:56:00','cmdb.asset.warning.error')
 print getWarrEventByMobile
 
 //结果(由于我是整个对象的输出，所以是打印的是Unicode编码，JS直接获取JSON数据应该能获取到utf-8)
 [[
    {
        "asset_id": [5, "\u7a00\u91ca\u6c34\u8f93\u9001\u6cf5A"], 
        "description": false, 
        "collect_value": "45.4149", 
        "asset_attr_name": "\u8f93\u9001\u6cf5\u53d8\u9891\u8d8b\u52bf", 
        "collect_time": "2015-12-17 14:55:11", 
        "excep_type": "\u53d8\u9891\u8d8b\u52bf\u5f02\u5e38", 
        "id": 3389006
    },
    {…}
 ]]
 
 //2.获取历史报表调用实例(python)
 getHisByMobile = server.getInfoFromTimeByMobile('db',isLogin,'admin',
                        '2015-12-17 22:55:00','2015-12-17 22:56:00','cmdb.asset.collect.record')
 print getHisByMobile

 //结果
 [[
    {
        "asset_id": [1, "\u6c28\u6c34\u8f93\u9001\u6cf5A"], 
        "collect_value": "0.9362", 
        "asset_attr_name": "\u8f93\u9001\u6cf5\u53d8\u9891\u53cd\u9988", 
        "id": 46015564, 
        "collect_time": "2015-12-17 14:55:10"
    },
    {…}
 ]]
 
 //3.获取维修记录调用实例(python)
 getRepairByMobile = server.getInfoFromTimeByMobile('db',isLogin,'admin',
                        '2015-10-12 14:38:19','2015-10-13 01:17:02','cmdb.repair')
 print getRepairByMobile

 //结果
 [[
    {
        "asset_id": [2, "\u6c28\u6c34\u8f93\u9001\u6cf5B"], 
        "state": "finished", 
        "finished_time": "2015-10-12 14:44:19", 
        "id": 3, 
        "name": "001"
    },
    {…}
 ]]
~~~
###4.测试角色分组
~~~
三个测试登录用户

1. 管理员（cmdb.asset、cmdb.asset.attribute、cmdb.asset.warning.error、
         cmdb.asset.collect.record、cmdb.asset.collect.finalrecord、cmdb.repair）
username: manager
password: manager

2. 监控员（cmdb.asset.warning.error、cmdb.asset.collect.record、cmdb.asset.collect.finalrecord）
username:monitor
password:monitor

3. 维修员（cmdb.repair）
username:repairman
password:repairman

~~~
<p style="color:red">(PS：关于权限的设定——若调用方法时返回json {"faultcode": "AccessDenied"}表示没有权限，则这张表用户没有权限查询，数据无法获取)</p>

###5.设备维修操作接口
~~~
asset_repair(self, uid, password, name, atta_name, kind, url,flag, repair_time, fault_reason, repair_method,  
 remark,atta_description,line)  
/*  
  参数说明：  
  1.uid是isLogin接口返回的结果  
  2.password是密码，name是维修单号  
  3.atta_name是附件的名称  
  4.kind是附件的种类（url，binary），kind从这2者中取值，url根据kind的取值而不同，如果是kind=url，则url是一个链接,若kind=binary，url是一个  
    绝对路径，'/'作区分  
  5.atta_description是附件的描述  
  6.flag是一个bool值，为True时表示开始维修，False表示完成维修  
  7.repair_time是维修次数  
  8.fault_reason、repair_method和remark是故障原因、维修方法和备注  
  9.line是一个list [[]]也是一个list，[[product_qty,select,record_name,descripe]，]类似于这种，添加维修操作的，product_qty，是产品数量，  
  这里传一个字符,比如：‘10’，select是‘add’和‘remove’中的一个，record_name是产品，descripe是描述,传参顺序不能乱，line如果没有请传一个[]列表  
  example：   
*/ 
  server.asset_repair(uid,'admin','123','附件','url','www.baidu.com',False,0,'设备陈旧','换新设备','该设备需定期保养','附件描述',  
  [['1','remove','Service','22']])    
//这是模拟的完成维修的操作，调用完成后维修单状态变成完成，附件也上传成功。  

~~~
<p style="color:red">(PS：目前是这么做的，参数是强制传入的，对调用者来说，传参要格外注意)</p>
             