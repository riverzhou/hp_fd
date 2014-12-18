#!/usr/bin/env python3

group   = 1     # 1/2/3/5:  节点1/节点2/节点3/节点5

policy  = 1     # 1/2/3:    DLL 中性 / DLL 良好 / DLL 糟糕

#=============================================

ac_file = 'ac_file.txt'

db_file = ['db01.py','db02.py','db03.py','db04.py','db05.py','db06.py','db07.py','db08.py','db09.py']

g1_list = ['11','12','13','14','15','16','17','18','19']
g2_list = ['21','22','23','24','25','26','27','28','29']
g3_list = ['31','32','33','34','35','36','37','38','39']
g5_list = ['51','52','53','54','55','56','57','58','59']

group_list = [ None, g1_list, g2_list, g3_list, None, g5_list ]

p1_list = ['policy_a', 'policy_b','policy_c','policy_a','policy_b','policy_c','policy_a','policy_b','policy_c']
p2_list = ['policy_d', 'policy_e','policy_f','policy_d','policy_e','policy_f','policy_d','policy_e','policy_f']
p3_list = ['policy_g', 'policy_h','policy_h','policy_g','policy_h','policy_h','policy_g','policy_h','policy_h']

policy_list = [ None, p1_list, p2_list, p3_list ]

head_0 = '''\
#!/usr/bin/env python3

import common_policy
'''

head_1 = '''\
#=============================================

channel_trigger = common_policy.channel_trigger
channel_timeout = common_policy.channel_timeout
decode_deadline = common_policy.decode_deadline
htmludp_addr    = common_policy.htmludp_addr
bid0_maxretry   = common_policy.bid0_maxretry

image_trigger   = policy.image_trigger
decode_type     = policy.decode_type
decode_timeout  = policy.decode_timeout
image_timeout   = policy.image_timeout
price_timeout   = policy.price_timeout

#=============================================
'''

body_0 = '''\
account_list    = [
'''

body_1 = '''\
]
'''

#---------------------------------------------

dict_ac = {}

def read_ac(ac_file):
        global dict_ac
        f = open(ac_file,'r')
        while True:
                line = f.readline()
                if not line or line.strip() == '':
                        break
                data    = line.split()
                bidno   = data[0].strip()
                passwd  = data[1].strip()
                name    = data[2].strip()
                worker  = data[3].strip()
                if worker not in dict_ac:
                        dict_ac[worker] = []
                dict_ac[worker].append((bidno,passwd,name))
        f.close()
        return dict_ac

def make_ac(ac):
        return '''('%s', '%s', '%s'),''' % (ac[0],ac[1],ac[2])

def make_head(po):
        return '''import  %s as policy''' % po

def write_ac(f, ac_list, po):
        f.write(head_0)
        f.write('\n')
        f.write(make_head(po))
        f.write('\n')
        f.write('\n')
        f.write(head_1)
        f.write('\n')
        f.write(body_0)
        for ac in ac_list:
                f.write(make_ac(ac))
                f.write('\n')
        f.write(body_1)
        f.write('\n')

def write_db(dbid):
        global dict_ac, db_file, g1_list, g2_list
        global policy, p1_list, p1_list

        g_list = group_list[group]
        p_list = policy_list[policy]

        f   = open(db_file[dbid], 'w')
        acid  = g_list[dbid]
        if acid not in dict_ac:
                ac_list = []
        elif dict_ac[acid] == None:
                ac_list = []
        else:
                ac_list = dict_ac[acid]
        if dbid >= len(p_list):
                po = p_list[0]
        else:
                po = p_list[dbid]
        write_ac(f, ac_list, po)
        f.close()
        print('DBID %d : NUMBER %d' % (dbid+1, len(ac_list)))

def main():
        read_ac(ac_file)
        for dbid in range(9):
                write_db(dbid)

#=================================================

if __name__ == '__main__':
        main()

