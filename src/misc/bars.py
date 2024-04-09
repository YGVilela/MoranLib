from multiprocessing import Queue, Process
from tqdm import tqdm, trange
from time import sleep

class SimpleBar:
    def __init__(self, total):
        self.total = total
        self.bar = tqdm(total=total)

    def tick(self, ticks=1):
        self.bar.update(ticks)

class ParallelBar:
    def __init__(self, total):
        self.total = total
        self.queue = Queue(maxsize=total)
        self.consumer = Process(target=self.__consume, args=[self.queue, self.total])

        self.consumer.start()

    def tick(self, ticks=1):
        self.queue.put(ticks)

    def wait(self):
        self.consumer.join()

    @staticmethod
    def __consume(queue: Queue, total: int):
        bar = tqdm(total=total)
        currentProgress = 0

        while True:
            progress = queue.get()
            currentProgress += progress

            bar.update(progress)

            if currentProgress >= total:
                break

        bar.close()

class CountdownBar:
    def __init__(self, timeInSeconds):
        self.total = timeInSeconds

    def start(self):
        for i in trange(self.total):
            sleep(1)
