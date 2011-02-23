"""
Standard functions used by the init scripts
The original idea is of adulau: http://gitorious.org/forban/forban/blobs/master/bin/forbanctl

FIXME: More comments needed
"""

import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.optionxform = str
config_file = "/home/rvinot/bgp-ranking/etc/bgp-ranking.conf"
config.read(config_file)
root_dir = config.get('directories','root')
pid_path = os.path.join(root_dir,config.get('directories','pids'))

import subprocess

import syslog
syslog.openlog('BGP_Ranking', syslog.LOG_PID, syslog.LOG_USER)


def service_start_multiple(servicename, number, param = None):
    i = 0 
    #print('Starting ' + str(number) + ' times ' + servicename)
    syslog.syslog(syslog.LOG_INFO, 'Starting ' + str(number) + ' times ' + servicename)
    while i < number:
        proc = service_start(servicename, param)
        writepid(servicename, proc)
        i += 1 

def service_start_once(servicename = None, param = None, processname = None):
    processname = os.path.basename(processname)
    pidpath = os.path.join(pid_path,processname+".pid")
    if not os.path.exists(pidpath):
        proc = service_start(servicename, param)
        writepid(processname, proc)
    else:
        print(processname + ' already running on pid ' + str(pidof(processname)[0]))
        syslog.syslog(syslog.LOG_ERR, "%s already running with pid %s" % (param, pidof(processname)[0]))

def service_start(servicename = None, param = None):
    """
    Launch a Process
    """
    if servicename is not None :
        service = servicename+".py"
        if not param:
            proc =  subprocess.Popen(["python",service])
        else:
            proc =  subprocess.Popen(["python",service, param])
        return proc
    return False

def writepid (processname = None, proc = None):
    """
    Append the pid to the pids-list of this process
    """
    processname = os.path.basename(processname)
    pidpath = os.path.join(pid_path,processname+".pid")

    if processname is not None and proc is not None:
        f = open (pidpath,"a")
        f.write(str(proc.pid)+'\n')
        f.close()
        return True
    else:
        return False

def rmpid (processname = None):
    """
    Delete the pids-file
    """
    processname = os.path.basename(processname)
    pidpath = os.path.join(pid_path,processname+".pid")
    if os.path.exists(pidpath):
        os.unlink(pidpath)
        return True
    else:
        return False

def pidof(processname = None):
    """
    Get the pid of a process 
    """
    processname = os.path.basename(processname)
    pidpath = os.path.join(pid_path,processname+".pid")
    if processname is not None and os.path.exists(pidpath):
        f = open (pidpath)
        pids = f.readlines()
        f.close()
        return pids
    else:
        return False

def update_running_pids(old_procs):
    """
    Update the list of the running process
    """
    new_procs = []
    for proc in old_procs:
        if proc.poll() == None and check_pid(proc.pid):
#            syslog.syslog(syslog.LOG_DEBUG, str(proc.pid) + ' is alive')
            new_procs.append(proc)
        else:
            try:
#                syslog.syslog(syslog.LOG_DEBUG, str(proc.pid) + ' is gone')
                os.kill (proc.pid, signal.SIGKILL)
            except:
                # the process is just already gone
                pass
    return new_procs

def check_pid(pid):        
    """ Check For the existence of a unix pid. """
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True

    
def init_counter(total_ips):
    ip_counter = {}
    max_processes = int(config.get('whois_push','max_processes'))
    max_ips_by_process = int(config.get('whois_push','max_ips_by_process'))
    min_ips_by_process = int(config.get('whois_push','min_ips_by_process'))
    if total_ips > max_processes * max_ips_by_process:
        total_ips = max_processes * max_ips_by_process
    ip_counter['total_ips'] = total_ips
    ip_counter['interval'] = total_ips / max_processes + 1
    if ip_counter['interval'] < min_ips_by_process:
        ip_counter['interval'] = min_ips_by_process
    ip_counter['processes'] = 0
    while max_processes > 0 and total_ips > 0:
        total_ips -= ip_counter['interval']
        max_processes -= 1
        ip_counter['processes'] += 1
    return ip_counter
    

