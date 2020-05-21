import csv
import mysql.connector


def update_csv():
    cnx = mysql.connector.connect(user='ibosmaster',
                                  password='150Progress',
                                  host='ibostestrds.c9silei7qcpu.us-east-1.rds.amazonaws.com',
                                  database='ibostestdb')

    cursor = cnx.cursor()
    query = ('SELECT * FROM ibostestdb.april2020packetsQuickSight')
    cursor.execute(query)
    data = cursor.fetchall()

    with open('data.csv', 'w+') as out:
        csv_out = csv.writer(out)
        csv_out.writerow(['dbId', 'ChargersParentId', 'CycleId', 'EventCodeId', 'EventTypeID', 'PoolId', 'SiteId',
                          'ChargerDurationBucket', 'ChargerAlias', 'ConnectVPCBucket', 'CooldownDurationBucket', 'DateLocal', 'Duration',
                          'EventStartTimeLocal', 'EventTime', 'EventTimeLocal', 'EventVPC', 'HourLocal', 'IsChargeComplete',
                          'IsChargerMissedSwitch', 'IsChargerNoStart', 'IsChargerSwitch', 'IsChargeStart',
                          'IsConnectNormal', 'IsConnectSameBattery', 'IsSelectBad', 'IsSelectFalsePick', 'IsSelectGood',
                          'IsSelectMaint', 'IsSelectMispick', 'IsSelectAll', 'QCountAvailable', 'QCountChargersOn',
                          'QCountConnected', 'QCountCooledBatteries', 'QCountNoBattery', 'QCountQuarantine',
                          'QCountUnknown', 'UseForAvailability', 'SiteName', 'EnterpriseName', 'PoolName', 'PoolBatCount',
                          'PoolTruckCount', 'PoolChargerCount'])
        csv_out.writerows(data)

    cnx.close()


if __name__ == '__main__':
    update_csv()
