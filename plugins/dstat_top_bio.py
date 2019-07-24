### Author: Dag Wieers <dag@wieers.com>

class dstat_plugin(dstat):
    """
    Top most expensive block I/O process.

    Displays the name of the most expensive block I/O process.
    """
    def __init__(self):
        self.name = 'most Block I/O expensive'
        self.vars = ('process','pid', 'read', 'write')
        self.types = ('s', 'd', 'd', 'd')
        self.scales = (0, 0, 1024, 1024)
        self.width = 8
        self.pidset1 = {}

    def check(self):
        if not os.access('/proc/self/io', os.R_OK):
            raise Exception('Kernel has no per-process I/O accounting [CONFIG_TASK_IO_ACCOUNTING], use at least 2.6.20')

    def extract(self):
        self.pidset2 = {}
        self.val['usage'] = 0.0
        for pid in proc_pidlist():
            try:
                ### Reset values
                if pid not in self.pidset2:
                    self.pidset2[pid] = {'read_bytes:': 0, 'write_bytes:': 0}
                if pid not in self.pidset1:
                    self.pidset1[pid] = {'read_bytes:': 0, 'write_bytes:': 0}

                ### Extract name
                name = proc_splitline('/proc/%s/stat' % pid)[1][1:-1]

                ### Extract counters
                for l in proc_splitlines('/proc/%s/io' % pid):
                    if len(l) != 2: continue
                    self.pidset2[pid][l[0]] = int(l[1])
            except IOError:
                continue
            except IndexError:
                continue

            read_usage = (self.pidset2[pid]['read_bytes:'] - self.pidset1[pid]['read_bytes:']) * 1.0 / elapsed
            write_usage = (self.pidset2[pid]['write_bytes:'] - self.pidset1[pid]['write_bytes:']) * 1.0 / elapsed
            usage = read_usage + write_usage

            ### Get the process that spends the most jiffies
            if usage > self.val['usage']:
                self.val['usage'] = usage
                self.val['read_usage'] = read_usage
                self.val['write_usage'] = write_usage
                self.val['pid'] = int(pid)
                self.val['name'] = getnamebypid(pid, name)

        if step == op.delay:
            self.pidset1 = self.pidset2

        self.val['process'] = self.val['name'][:self.width]
        self.val['read'] = self.val['read_usage']
        self.val['write'] = self.val['write_usage']

    def showcsv(self):
        return '%s,%d,%d,%d' % (self.val['name'], self.val['pid'], self.val['read_usage'], self.val['write_usage'])

# vim:ts=4:sw=4:et
