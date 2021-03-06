service OdooService{
    string isLoginSuccess(1:string password,2:string username),
    string getAssets(1:i32 uid,2:string password),
    string getAttributes(1:i32 uid,2:string password),
    string getErrorAndEventByTime(1:i32 uid,2:string password,3:string starttime,4:string endtime),
    string getRepairInfoByTime(1:i32 uid,2:string password,3:string starttime,4:string endtime),
    string getAssetByOid(1:i32 oid,2:i32 uid,3:string password),
    string getCollectPointsByAssetId(1:i32 asset_id,2:i32 uid,3:string password),
    string getCollectPointsByOid(1:i32 oid,2:i32 uid,3:string password),
    string getControlPointByOid(1:i32 oid,2:i32 uid,3:string password),
    string packMessage(1:i32 oid,2:i32 uid,3:string password),
    string getSystemControlInfo(1:i32 uid, 2:string password),
    string getAsset2SystemControl(1:i32 uid, 2:string password, 3:i32 systemcontrol_id),

    string asset_repair(1:i32 uid,
    2:string password,
    3:string name,
    4:list <string> atta_name,
    5:list <string> atta_description,
    6:list <list<string>> file_list,
    7:string kind,
    8:bool flag,
    9:i32 repair_time,
    10:string fault_reason,
    11:string repair_method,
    12:string remark,
    13:list <list<string>> line,),
    
    string getCollectData(1:string starttime,2:string endtime),
    string getCollectDataByAssetAndAttr(1:string asset_id,2:string attribute,3:string starttime,4:string endtime),
    string getFinishedRepairInfo(1:i32 uid,2:string password,3:string name),
}

