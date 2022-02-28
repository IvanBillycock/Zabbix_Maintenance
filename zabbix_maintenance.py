from pyzabbix import ZabbixAPI
import datetime
import json
import time
import random
import argparse
import sys

#parser = argparse.ArgumentParser(description='Enable maintenance mode in Zabbix')
#parser.add_argument('-h', '--host', help='Input a host name. Example eb-arp-demo-ufos')
#parser.add_argument('-p', '--period', help='Input a period. 1800 = 30 minutes ')
#args = parser.parse_args()

eb_host = "eb-arp-demo-ufos.pds.otr.ru"
period = 60

zapi = ZabbixAPI('http://web.zabbix.pds.otr.ru', user='eb.service.acc', password='LockAndLoad123')


def get_host_id(host):
    host_id = zapi.do_request('host.get', {
                             'filter': {
                                 "host": host
                                 },
                             'output': ['hostid']
                            })
    return json.dumps(host_id['result']).split(":")[-1].replace("}","").replace("]","").replace('"',"").replace(' ',"")

def create_maintenance(host_id, period):
    host_id = [host_id]
    today = datetime.datetime.today()
    date = today.strftime("%d/%m/%Y/%H")
    next_day = datetime.datetime.today() + datetime.timedelta(1)
    date_next_day = next_day.strftime("%d/%m/%Y/%H")
    stamp = datetime.datetime.strptime(date, "%d/%m/%Y/%H").timestamp()
    stamp_next_day = datetime.datetime.strptime(date_next_day, "%d/%m/%Y/%H").timestamp()
    stamp = int(stamp)
    stamp_next_day = int(stamp_next_day)
    maintenance_name = str(random.randint(100,999))
    
    maintenance = zapi.do_request('maintenance.create',
                         {
                             "name": "Ufos update" +maintenance_name, 
                             "active_since": stamp,
                             "active_till": stamp_next_day,
                             "tags_evaltype": 0, 
                             "hostids": host_id, 
                             "timeperiods":[{
                                 "timeperiod_type":0,
                                 "every":1, 
                                 "dayofweek":64, 
                                 "start_time":64800, 
                                 "period": period
                              }]
                         })
    return json.dumps(maintenance['result']['maintenanceids']).replace("[","").replace("]","").replace('"',"")

def delete_maintenance(maintenance_id, period):
    time.sleep(period)
    zapi.do_request('maintenance.delete', 
                         [
                             maintenance_id,                             
                         ])



host_id = get_host_id(eb_host)
maintenance_id = create_maintenance(host_id, period)
delete_maintenance(maintenance_id, period)

zapi.user.logout()
