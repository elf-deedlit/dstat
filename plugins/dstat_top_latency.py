### Authority: Dag Wieers <dag$wieers,com>

class dstat_plugin(dstat):
    """
    Top process with highest total latency.

    Displays name and total amount of CPU time waited in milliseconds of
    the process that has the highest total amount waited for the measured
    timeframe.

    For more information see:

        http://eaglet.rain.com/rick/linux/schedstat/
    """

    def __init__(self):
        self.name = 'highest total'
        self.vars = ('process', 'pid', 'latency',)
        self.types = ('s', 'd', 'f',)
        self.scales = (0, 0, 34,)
        self.width = 8
        self.pidset1 = {}

    def check(self):
        if not os.access('/proc/self/schedstat', os.R_OK):
            raise Exception('Kernel has no scheduler statistics [CONFIG_SCHEDSTATS], use at least 2.6.12')

    def extract(self):
        self.pidset2 = {}
        self.val['result'] = 0
        for pid in proc_pidlist():
            try:
                ### Reset values
                if pid not in self.pidset1:
                    self.pidset1[pid] = {'wait_ticks': 0}

                ### Extract name
                name = proc_splitline('/proc/%s/stat' % pid)[1][1:-1]

                ### Extract counters
                l = proc_splitline('/proc/%s/schedstat' % pid)
            except IOError:
                continue
            except IndexError:
                continue

            if len(l) != 3: continue

            self.pidset2[pid] = {'wait_ticks': int(l[1])}

            totwait = (self.pidset2[pid]['wait_ticks'] - self.pidset1[pid]['wait_ticks']) * 1.0 / elapsed

            ### Get the process that spends the most jiffies
            if totwait > self.val['result']:
                self.val['result'] = totwait
                self.val['pid'] = int(pid)
                self.val['name'] = getnamebypid(pid, name)

        if step == op.delay:
            self.pidset1 = self.pidset2

        self.val['process'] = self.val['name'][:self.width]
        self.val['latency'] = self.val['result']

    def showcsv(self):
        return '%s,%d,%f' % (self.val['name'], self.val['pid'], self.val['result'])

# vim:ts=4:sw=4:et
