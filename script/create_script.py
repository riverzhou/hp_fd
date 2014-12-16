#!/usr/bin/env python3

from collections    import OrderedDict

#=============================================

map_worker_file     = 'map_worker.txt'
map_udp_file        = 'map_udp.txt'
map_ctrl_file       = 'map_ctrl.txt'

deploy_worker_file  = 'deploy_worker.sh'
deploy_udp_file     = 'deploy_udp.sh'
deploy_ctrl_file    = 'deploy_ctrl.sh'

start_worker_file   = 'start_worker.sh'
start_udp_file      = 'start_udp.sh'

stop_worker_file    = 'stop_worker.sh'
stop_udp_file       = 'stop_udp.sh'

check_worker_file   = 'check_worker.sh'
check_udp_file      = 'check_udp.sh'

#---------------------------------------------

list_node           = ['node1', 'node2', 'node3', 'node5']

list_wk_file        = ['/river/fd/fd_worker.tgz']
list_ct_file        = ['/river/fd/fd_control.tgz', '/river/fd/fd_log.tgz', '/river/fd/fd_udp.tgz']

PORT_SSH            = 9999
DIR_DEPOLY          = '/river/'
DIR_CONF            = 'conf/'
DIR_WORKER          = 'fd/fd_worker/'
LOCAL_CONF_WORKER   = 'fd_config.%s.py'
DST_CONF_WORKER     = 'fd_config.py'

#---------------------------------------------

cmd_worker_clean    = 'rm /river/fd -rf; mkdir -p /river/fd/fd_worker; ls -l /river '
cmd_worker_init     = 'cd /river/fd; tar -zxvf /river/fd_worker.tgz; cd /river/fd/fd_worker; cp /river/fd_config.py .; cat /river/fd_config.py; cat /etc/hosts.origin /river/hosts > /etc/hosts; cat /etc/hosts'
cmd_worker_start    = 'killall -9 python3; echo > /river/worker.log; nohup /river/fd/fd_worker/fd_worker.py > /dev/null 2>&1 &'
cmd_worker_stop     = 'killall -9 python3; echo killed'
cmd_worker_check    = 'cat /river/worker.log '

cmd_udp_clean       = 'rm /river/fd -rf; mkdir -p /river/fd/fd_udp; ls -l /river '
cmd_udp_init        = 'cd /river/fd; tar -zxvf /river/fd_udp.tgz; cat /etc/hosts.origin /river/hosts > /etc/hosts; cat /etc/hosts'
cmd_udp_start       = 'killall -9 python3; echo > /river/htmludp.log; nohup /river/fd/fd_udp/fd_udpserver.py > /dev/null 2>&1 &'
cmd_udp_stop        = 'killall -9 python3; echo killed'
cmd_udp_check       = 'cat /river/htmludp.log '

#---------------------------------------------

model_conf_worker   = '''\
#!/usr/bin/env python3

local_logfile   = '/river/worker.log'

redis_passwd    = 'river'
redis_port      = 6379
redis_ip        = '%s'
redis_dbid      = %d

'''

#=============================================

'''
scp -P 9999 -i /root/.ssh/id_rsa_121.41.72.124 /river/fd/*.tgz root@121.41.72.124:/river
ssh -p 9999 -i /root/.ssh/id_rsa_121.41.72.124 @121.41.72.124  "ls -al"
'''

#=============================================

def make_scp_hosts_cmd(ip, port):
        return 'scp -P %d -i /root/.ssh/id_rsa_%s conf/hosts root@%s:/river/hosts \n' %(port, ip.ljust(15), ip)

def make_scp_conf_cmd(ip, port, filename, confname):
        return 'scp -P %d -i /root/.ssh/id_rsa_%s %s root@%s:%s \n' %(port, ip.ljust(15), filename, ip, confname)

def make_scp_cmd(ip, port, filename, dirname):
        return 'scp -P %d -i /root/.ssh/id_rsa_%s %s root@%s:%s \n' %(port, ip.ljust(15), filename, ip, dirname)

def make_ssh_cmd(ip, port, cmd):
        return 'ssh -p %d -i /root/.ssh/id_rsa_%s root@%s "%s" \n' %(port, ip.ljust(15), ip, cmd)

def make_sh_head():
        return '#!/bin/sh\n\n'

#=============================================

def read_map(map_file):
        f = open(map_file,'r')
        dict_map = OrderedDict()
        while True:
                line = f.readline()
                if not line:
                        break
                if line.strip() == '':
                        continue
                data = line.split()
                node = data[0].strip()
                ip   = data[1].strip()
                name = data[2].strip()
                pip  = data[3].strip()
                if node not in dict_map:
                        dict_map[node]  = []
                dict_map[node].append({'ip':ip, 'name':name, 'pip':pip})
        f.close()
        return dict_map

def create_deploy_worker_clean(deply_file):
        global map_worker_file, PORT_SSH, DIR_DEPOLY
        dict_map = read_map(map_worker_file)
        f = open(deply_file, 'w')
        f.write(make_sh_head())
        for node in dict_map:
                for worker in dict_map[node]:
                        ip      = worker['ip']
                        port    = PORT_SSH
                        cmd     = make_ssh_cmd(ip, port, cmd_worker_clean)
                        f.write(cmd)
        f.close()
        return

def create_deploy_worker_init(deply_file):
        global map_worker_file, PORT_SSH, DIR_DEPOLY
        dict_map = read_map(map_worker_file)
        f = open(deply_file, 'a')
        for node in dict_map:
                for worker in dict_map[node]:
                        ip      = worker['ip']
                        port    = PORT_SSH
                        cmd     = make_ssh_cmd(ip, port, cmd_worker_init)
                        f.write(cmd)
        f.close()
        return

def create_deploy_worker_conf(deply_file):
        global map_worker_file, PORT_SSH, DIR_DEPOLY
        dict_map = read_map(map_worker_file)
        f = open(deply_file, 'a')
        for node in dict_map:
                for worker in dict_map[node]:
                        ip       = worker['ip']
                        name     = worker['name']
                        filename = DIR_CONF + LOCAL_CONF_WORKER % name
                        port     = PORT_SSH
                        confname = DIR_DEPOLY + DST_CONF_WORKER
                        cmd      = make_scp_conf_cmd(ip, port, filename, confname)
                        f.write(cmd)
                        f.write(make_scp_hosts_cmd(ip, port))
        f.close()
        return

def create_deploy_worker(deply_file):
        global map_worker_file, PORT_SSH, DIR_DEPOLY
        dict_map = read_map(map_worker_file)
        f = open(deply_file, 'a')
        for node in dict_map:
                for worker in dict_map[node]:
                        ip      = worker['ip']
                        port    = PORT_SSH
                        dirname = DIR_DEPOLY
                        for filename in list_wk_file:
                                cmd = make_scp_cmd(ip, port, filename, dirname)
                                f.write(cmd)
        f.close()
        return

def create_deploy_udp_clean(deply_file):
        global map_udp_file, PORT_SSH, DIR_DEPOLY
        dict_map = read_map(map_udp_file)
        f = open(deply_file, 'w')
        f.write(make_sh_head())
        for node in dict_map:
                for worker in dict_map[node]:
                        ip      = worker['ip']
                        port    = PORT_SSH
                        cmd     = make_ssh_cmd(ip, port, cmd_udp_clean)
                        f.write(cmd)
        f.close()
        return

def create_deploy_udp_init(deply_file):
        global map_udp_file, PORT_SSH, DIR_DEPOLY
        dict_map = read_map(map_udp_file)
        f = open(deply_file, 'a')
        for node in dict_map:
                for worker in dict_map[node]:
                        ip      = worker['ip']
                        port    = PORT_SSH
                        cmd     = make_ssh_cmd(ip, port, cmd_udp_init)
                        f.write(cmd)
        f.close()
        return

def create_deploy_udp(deply_file):
        global map_udp_file, PORT_SSH, DIR_DEPOLY
        dict_map = read_map(map_udp_file)
        f = open(deply_file, 'a')
        for node in dict_map:
                for worker in dict_map[node]:
                        ip      = worker['ip']
                        port    = PORT_SSH
                        dirname = DIR_DEPOLY
                        for filename in list_ct_file:
                                cmd = make_scp_cmd(ip, port, filename, dirname)
                                f.write(cmd)
                                f.write(make_scp_hosts_cmd(ip, port))
        f.close()
        return

def create_deploy_ctrl(deply_file):
        global map_ctrl_file, PORT_SSH, DIR_DEPOLY
        dict_map = read_map(map_ctrl_file)
        f = open(deply_file, 'w')
        f.write(make_sh_head())
        for node in dict_map:
                for worker in dict_map[node]:
                        ip      = worker['ip']
                        port    = PORT_SSH
                        dirname = DIR_DEPOLY
                        for filename in list_ct_file:
                                cmd = make_scp_cmd(ip, port, filename, dirname)
                                f.write(cmd)
        f.close()
        return

def create_start_worker(start_file):
        global map_worker_file, PORT_SSH
        dict_map = read_map(map_worker_file)
        f = open(start_file, 'w')
        f.write(make_sh_head())
        for node in dict_map:
                for worker in dict_map[node]:
                        ip      = worker['ip']
                        port    = PORT_SSH
                        cmd     = make_ssh_cmd(ip, port, cmd_worker_start)
                        f.write(cmd)
        f.close()
        return

def create_start_udp(start_file):
        global map_udp_file, PORT_SSH
        dict_map = read_map(map_udp_file)
        f = open(start_file, 'w')
        f.write(make_sh_head())
        for node in dict_map:
                for worker in dict_map[node]:
                        ip      = worker['ip']
                        port    = PORT_SSH
                        cmd     = make_ssh_cmd(ip, port, cmd_udp_start)
                        f.write(cmd)
        f.close()
        return

def create_stop_worker(stop_file):
        global map_worker_file, PORT_SSH
        dict_map = read_map(map_worker_file)
        f = open(stop_file, 'w')
        f.write(make_sh_head())
        for node in dict_map:
                for worker in dict_map[node]:
                        ip      = worker['ip']
                        port    = PORT_SSH
                        cmd     = make_ssh_cmd(ip, port, cmd_worker_stop)
                        f.write(cmd)
        f.close()
        return

def create_stop_udp(stop_file):
        global map_udp_file, PORT_SSH
        dict_map = read_map(map_udp_file)
        f = open(stop_file, 'w')
        f.write(make_sh_head())
        for node in dict_map:
                for worker in dict_map[node]:
                        ip      = worker['ip']
                        port    = PORT_SSH
                        cmd     = make_ssh_cmd(ip, port, cmd_udp_stop)
                        f.write(cmd)
        f.close()
        return

def create_check_worker(check_file):
        global map_worker_file, PORT_SSH
        dict_map = read_map(map_worker_file)
        f = open(check_file, 'w')
        f.write(make_sh_head())
        for node in dict_map:
                for worker in dict_map[node]:
                        ip      = worker['ip']
                        port    = PORT_SSH
                        cmd     = make_ssh_cmd(ip, port, cmd_worker_check)
                        f.write(cmd)
        f.close()
        return

def create_check_udp(check_file):
        global map_udp_file, PORT_SSH
        dict_map = read_map(map_udp_file)
        f = open(check_file, 'w')
        f.write(make_sh_head())
        for node in dict_map:
                for worker in dict_map[node]:
                        ip      = worker['ip']
                        port    = PORT_SSH
                        cmd     = make_ssh_cmd(ip, port, cmd_udp_check)
                        f.write(cmd)
        f.close()
        return

def make_conf_worker(node, name):
        dict_map = read_map(map_ctrl_file)
        ip_ctrl  = dict_map[node][0]['pip']
        id_db    = int(name[-1])
        #print(ip_ctrl, id_db)
        return model_conf_worker % (ip_ctrl, id_db)

def create_config_worker():
        global DIR_CONF
        dict_map = read_map(map_worker_file)
        for node in dict_map:
                for worker in dict_map[node]:
                        name = worker['name']
                        conf = DIR_CONF + LOCAL_CONF_WORKER % name
                        f = open(conf, 'w')
                        f.write(make_conf_worker(node, name))
                        #print(conf)
                        f.close()

def main():
        create_config_worker()
        create_deploy_worker_clean(deploy_worker_file)
        create_deploy_worker(deploy_worker_file)
        create_deploy_worker_conf(deploy_worker_file)
        create_deploy_worker_init(deploy_worker_file)

        create_deploy_udp_clean(deploy_udp_file)
        create_deploy_udp(deploy_udp_file)
        create_deploy_udp_init(deploy_udp_file)

        create_deploy_ctrl(deploy_ctrl_file)

        create_start_udp(start_udp_file)
        create_start_worker(start_worker_file)

        create_stop_udp(stop_udp_file)
        create_stop_worker(stop_worker_file)

        create_check_udp(check_udp_file)
        create_check_worker(check_worker_file)

#=================================================

if __name__ == '__main__':
        main()


