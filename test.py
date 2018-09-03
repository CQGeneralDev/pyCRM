from pyCRM.TimingTask import scheduler


@scheduler.scheduled_job('interval', seconds=3)
def ping():
    print('aaaaaaaaaaaaaaaaaaaaa')
    return 'pong'


if __name__ == '__main__':
    import time

    time.sleep(61)
