### Authority: Dag Wieers <dag@wieers.com>

class dstat_plugin(dstat):
    """
    Most expensive CPU process.

    Displays the process that uses the CPU the most during the monitored
    interval. The value displayed is the percentage of CPU time for the total
    amount of CPU processing power. Based on per process CPU information.
    """
    def __init__(self):
        self.name = 'most CPU expensive'
        self.vars = ('process','pid', 'usage')
        self.types = ('s', 'd', 'f')
        self.scales = (0, 0, 34)
        self.width = 8
        self.pidset1 = {}

    def extract(self):
        self.pidset2 = {}
        self.val['max'] = 0.0
        for pid in proc_pidlist():
            try:
                ### Using dopen() will cause too many open files
                l = proc_splitline('/proc/%s/stat' % pid)
            except IOError:
                continue

            if len(l) < 15: continue

            ### Reset previous value if it doesn't exist
            if pid not in self.pidset1:
                self.pidset1[pid] = 0

            self.pidset2[pid] = int(l[13]) + int(l[14])
            usage = (self.pidset2[pid] - self.pidset1[pid]) * 1.0 / elapsed / cpunr

            ### Is it a new topper ?
            if usage < self.val['max']: continue

            name = l[1][1:-1]

            self.val['max'] = usage
            self.val['pid'] = int(pid)
            self.val['name'] = getnamebypid(pid, name)

        self.val['process'] = self.val['name'][:self.width]
        self.val['usage'] = self.val['max']

        if step == op.delay:
            self.pidset1 = self.pidset2

    def showcsv(self):
        return '%s,%s,%s' % (self.val['name'], self.val['pid'], self.val['max'])

# vim:ts=4:sw=4:et
