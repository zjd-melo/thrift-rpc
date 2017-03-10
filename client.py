# /usr/bin/env python
# -*- coding: utf-8 -*-

import thriftpy
import datetime
import json
import os
import xmlrpclib

from thriftpy.rpc import client_context

main_thrift = thriftpy.load("./conf/main.thrift", module_name="main_thrift")


def main():
    with client_context(main_thrift.OdooService, '127.0.0.1', 6000 ,timeout=0) as c:
        uid = c.isLoginSuccess('admin','admin')
        #print json.loads(c.getCollectData('1464758505','1464759000'))
        print json.loads(c.getFinishedRepairInfo(1,'admin','123'))


if __name__ == '__main__':
    main()

