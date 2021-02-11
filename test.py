import asyncio
import threading

from asyncio.locks import Event

class EventWithErr(Event):
    def __init__(self, loop):
        super().__init__(loop=loop)

    def set(self, e=None):
        self.e = e
        return super().set()
    

async def fire():
    raise BaseException("ERR")

async def fire_and_forget():
    async def fire_and_catch_err():
        try:
            await fire()
        except BaseException as e:
            stop_event.set(e)            
    f = asyncio.ensure_future(fire_and_catch_err())

loop = asyncio.new_event_loop()
loop.set_debug(True)
stop_event = EventWithErr(loop)

async def main_loop():
    """非同期スレッドの本体
    エラーが起きるまで動かし続ける。"""
    print("Start Loop")
    await stop_event.wait()
    if stop_event.e:
        raise stop_event.e
    
def start_loop():
    try:
        loop.run_until_complete(main_loop())
    except:
        print("Catch Thread", loop.is_running())        
        loop.close()
        raise


thread = threading.Thread(target=start_loop, name="Test", daemon=True)
thread.start()
asyncio.run_coroutine_threadsafe(fire_and_forget(), loop)
print("wait...")
from time import sleep
sleep(10)

print(thread.is_alive())
asyncio.run_coroutine_threadsafe(fire_and_forget(), loop)
print("bye")
