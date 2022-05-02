#import things
from datetime import timedelta
from multiprocessing.dummy import connection
import pymysql as sql
import time

def get_database(TableName):
    cmd = "SELECT * FROM %s;" %(TableName)
    cursor.execute(cmd)
    return cursor.fetchall()

def get_comparing(farmname):
    cmd = "SELECT * FROM farm_controller where iot_farmname = '%s';" %(farmname)
    #print(cmd)
    cursor.execute(cmd)
    return cursor.fetchone()

def fetch_devices(farmname,devices):
    cmd = "SELECT * FROM %s WHERE iot_farmname = '%s' ORDER BY iot_datetime DESC LIMIT 1;" % (devices,farmname)
    cursor.execute(cmd)
    return cursor.fetchall()

def update_devices(TableName,controller_statuses,farmname):
    commands = (TableName,) + ('iot_datetime', 'CURRENT_TIMESTAMP',) + controller_statuses + (farmname,)
    cmd = "UPDATE %s SET %s = %s, %s = %d, %s = %d, %s = %d, %s = %d, %s = %d, %s = %d WHERE iot_farmname = '%s' " %commands
    #print(cmd)
    cursor.execute(cmd)
    #return cursor.fetchall()

def light_controlling(light_controller,current_time,opentime,closetime, mc):
    if(mc == 1):
        if    (current_time < closetime) & (current_time > opentime): return 1
        elif  (current_time > opentime) & (current_time < closetime): return 1
        else: return 0
    else: return light_controller

def physical_device_controlling(floor_controller,ceiling_controller,sensor_reading,ceiling_sensor,floor_sensor,mc):
    if(mc == 1):
        if    ceiling_sensor < sensor_reading < floor_sensor: return [0,0]
        elif  sensor_reading < ceiling_sensor: return [0,1]
        elif  sensor_reading > floor_sensor  : return [1,0]
    else: return [floor_controller, ceiling_controller]
    #case humid : floor control is foggy, ceiling control is fan
    #case ph    : floor control is base,  ceiling control is acid
    #case temp  : floor control is heatlight,   ceiling control is fan
    #floor control means if the sensor goes down the floor value, that controller will help bring value up
    #ceiling control means the same but in vice versa
    
def controller_log_save(farmname,controllers_name,controls_status):
    cmd = "INSERT INTO %s_controller_log (%s) VALUES (%s)" %(farmname,','.join(controllers_name),','.join(str(stat) for stat in controls_status))
    print(cmd)
    cursor.execute(cmd)

#database connection
connection = sql.connect(host = 'localhost', user = 'root',database = 'smartfarm')
#connection = sql.connect(host = '139.162.39.94', user = 'root',password = 'root' ,database = 'smartfarm')
cursor = connection.cursor()

#new code


farms = get_database("farm")
farms_param = get_database("plants_parameters")

while True:
    for farm in farms:
        farm_name = farm[1]; farm_plant = farm[4]; farm_stage = farm[5]
        try:
            sensors_val = fetch_devices(farm_name,"farm_iot")
            sensor_time = timedelta(hours = sensors_val[0][1].hour, minutes = sensors_val[0][1].minute, seconds = sensors_val[0][1].second)
            (iot_temp,iot_humid,iot_ph,heat_index) = sensors_val[0][3:6] + (sensors_val[0][7],)

            controllers_val = fetch_devices(farm_name,"farm_controller")
            (light_MC, temp_MC, humid_MC, pH_MC, light, fan, heatlight, fog, phhigh, phlow) = controllers_val[0][2:-1]

            for farm_param in farms_param:
                if (farm_param[1],farm_param[2]) == (farm_plant,farm_stage):
                    (opentime, closetime, ceiling_temp, floor_temp, ceiling_humid, floor_humid, ceiling_ph, floor_ph) = farm_param[3:-1]
                    break
            (fog_control, fan_control) = physical_device_controlling(fog,fan,iot_humid,ceiling_humid,floor_humid,humid_MC)
            (base_control, acid_control) = physical_device_controlling(phhigh,phlow,iot_ph,ceiling_ph,floor_ph,pH_MC)
            (heatlight_control, temp_fan_control) = physical_device_controlling(heatlight,fan,iot_temp,ceiling_temp,floor_temp,temp_MC)
            light_control = light_controlling(light,sensor_time,opentime,closetime,light_MC)
            controller_statuses = ('fog',fog_control,'phhigh',base_control,'phlow', acid_control,'heatlight', heatlight_control,'fan', temp_fan_control,'light', light_control)
            # controller_name = [i for i in controller_statuses if controller_statuses.index(i)%2 == 0]
            # controls_status = [i for i in controller_statuses if controller_statuses.index(i)%2 == 1]
            # controller_log_save(farm_name,controller_name,controls_status)
            prev_stat = get_comparing(farm_name)[6:-1]
            curr_stat = (light_control,fan_control,heatlight_control,fog_control,base_control,acid_control)
            print(prev_stat, curr_stat, sep=' -> ', end=' ')
            if prev_stat != curr_stat:
                update_devices("farm_controller",controller_statuses,farm_name)
                print("Controller got update!!")
            else: print(" ")
        except (IndexError, sql.err.OperationalError): break
    
    time_now = time.asctime( time.localtime(time.time()) )
    #print("Controller script execution complete, timestamp : %s" %(time_now))
    

    connection.commit()
    time.sleep(2)
    
#close connection
connection.close()