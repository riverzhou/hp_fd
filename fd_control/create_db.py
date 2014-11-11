#!/usr/bin/env python3

group   = 1     # 1/2:  节点1/节点2

policy  = 1     # 1/2:  DLL OK / DLL 不OK

#=============================================

ac_file = 'ac_file.txt'

db_file = ['db01.py','db02.py','db03.py','db04.py','db05.py','db06.py','db07.py','db08.py','db09.py','db10.py','db11.py']

g2_list = ['2A01','2A02','2A03','2A04','2A05','2B06','2B07','2B08','2B09','2B10','2B11']

g1_list = ['1A01','1A02','1A03','1A04','1A05','1B06','1B07','1B08','1B09','1B10','1B11']

p1_list = ['policy_a', 'policy_b','policy_c','policy_d','policy_e','policy_a','policy_b','policy_c','policy_d','policy_e','policy_a']

p2_list = ['policy_f', 'policy_f','policy_f','policy_g','policy_g','policy_f','policy_f','policy_f','policy_g','policy_g','policy_g']

head_0 = '''\
#!/usr/bin/env python3
'''


head_1 = '''\
#=============================================

channel_trigger = policy.channel_trigger
channel_timeout = policy.channel_timeout
image_trigger   = policy.image_trigger
decode_type     = policy.decode_type
decode_timeout  = policy.decode_timeout
decode_deadline = policy.decode_deadline
bid0_maxretry   = policy.bid0_maxretry

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
        if group == 1:
                g_list = g1_list
        else:
                g_list = g2_list
        if policy == 1:
                p_list = p1_list
        else:
                p_list = p2_list
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

def main():
        read_ac(ac_file)
        for dbid in range(11):
                write_db(dbid)

#=================================================

if __name__ == '__main__':
        main()

