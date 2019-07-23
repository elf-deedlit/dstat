### Dstat all I/O process plugin
### Displays all processes' I/O read/write stats and CPU usage
###
### Authority: Guillermo Cantu Luna

class dstat_plugin(dstat):
    def __init__(self):
        self.name = 'most expensive cpu process'
        self.vars = ('process', 'pid', 'cpu', 'read', 'write')
        self.types = ('s', 's', 'f', 'd', 'd')
        self.scales = (0, 0, 34, 1024, 1024)
        self.width = 8
        self.pidset1 = {}

    def check(self):
        if not os.access('/proc/self/io', os.R_OK):
            raise Exception('Kernel has no per-process I/O accounting [CONFIG_TASK_IO_ACCOUNTING], use at least 2.6.20')
        return True

    def extract(self):
        self.pidset2 = {}
        self.val['cpu_usage'] = 0
        for pid in proc_pidlist():
            try:
                ### Reset values
                if pid not in self.pidset2:
                    self.pidset2[pid] = {'rchar:': 0, 'wchar:': 0, 'cputime:': 0, 'cpuper:': 0}
                if pid not in self.pidset1:
                    self.pidset1[pid] = {'rchar:': 0, 'wchar:': 0, 'cputime:': 0, 'cpuper:': 0}

                ### Extract name
                name = proc_splitline('/proc/%s/stat' % pid)[1][1:-1]

                ### Extract counters
                for l in proc_splitlines('/proc/%s/io' % pid):
                    if len(l) != 2: continue
                    self.pidset2[pid][l[0]] = int(l[1])

                ### Get CPU usage
                l = proc_splitline('/proc/%s/stat' % pid)
                if len(l) < 15:
                    cpu_usage = 0.0
                else:
                    self.pidset2[pid]['cputime:'] = int(l[13]) + int(l[14])
                    cpu_usage = (self.pidset2[pid]['cputime:'] - self.pidset1[pid]['cputime:']) * 1.0 / elapsed / cpunr

            except ValueError:
                continue
            except IOError:
                continue
            except IndexError:
                continue

            read_usage = (self.pidset2[pid]['rchar:'] - self.pidset1[pid]['rchar:']) * 1.0 / elapsed
            write_usage = (self.pidset2[pid]['wchar:'] - self.pidset1[pid]['wchar:']) * 1.0 / elapsed

            ### Get the process that spends the most jiffies
            if cpu_usage > self.val['cpu_usage']:
                self.val['read_usage'] = read_usage
                self.val['write_usage'] = write_usage
                self.val['pid'] = pid
                self.val['name'] = getnamebypid(pid, name)
                self.val['cpu_usage'] = cpu_usage

        if step == op.delay:
            self.pidset1 = self.pidset2

        if self.val['cpu_usage'] != 0.0:
            self.val['process'] = self.val['name'][:self.width]
            self.val['cpu'] = self.val['cpu_usage']
            self.val['read'] = self.val['read_usage']
            self.val['write'] = self.val['write_usage']

    def showcsv(self):
        return '%s,%s,%s,%s,%s' % (self.val['name'], self.val['pid'], self.val['cpu_usage'], self.val['read_usage'], self.val['write_usage'])
