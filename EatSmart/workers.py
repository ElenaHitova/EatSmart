from rq.timeouts import TimerDeathPenalty
from rq.worker import SimpleWorker


class WindowsSimpleWorker(SimpleWorker):

    death_penalty_class = TimerDeathPenalty