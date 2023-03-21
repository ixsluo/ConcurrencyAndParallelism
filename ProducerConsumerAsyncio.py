import asyncio
import random
from typing import Any


class Factory:
    def __init__(self, *args, **kwargs):
        self.n_produce = 0
        self.n_recycle = 0

    async def produce(self) -> Any:
        """Produce one production.

        Returns
        -------
        Any
            production
        """
        self.n_produce += 1
        # --- simulate producing ---
        await asyncio.sleep(random.randrange(1) / 5)
        print("produce: ", self.n_produce)
        # --------------------------
        return self.n_produce

    async def recycle(self, production, *args, **kwargs) -> None:
        self.n_recycle += 1
        # --- simulate recycling ---
        await asyncio.sleep(random.randrange(10) / 5)
        print("recycle: ", production)
        # --------------------------
        return None


async def consume(product: Any) -> Any:
    """Consume a product and return something to be recycled.

    Parameters
    ----------
    product : Any
        product to use

    Returns
    -------
    Any
        anything to be recycled
    """
    # --- simulate consuming ---
    recycling = product
    await asyncio.sleep(random.randrange(20) / 5)
    print("Comsuming", product)
    # --------------------------
    return recycling


async def producer(
    p_queue: asyncio.Queue,
    r_queue: asyncio.Queue,
    factory: Factory,
    nmax: int,
):
    """Producer to produce products and recycle them after consumed.

    Parameters
    ----------
    p_queue : asyncio.Queue
        products Queue
    r_queue : asyncio.Queue
        recycling Queue
    factory : Factory
        factory with `produce` and `recycle` attribute.
    nmax : int
        max number of products, stop when `factory.n_recycle` reaches this number.
    """
    while factory.n_recycle < nmax:
        # recycle
        if not r_queue.empty():
            await factory.recycle(r_queue.get_nowait())
            r_queue.task_done()
        # produce
        if factory.n_produce < nmax:
            product = await factory.produce()
            await p_queue.put(product)
        await asyncio.sleep(random.randrange(5) / 5)  # ! release


async def consumer(
    p_queue: asyncio.Queue,
    r_queue: asyncio.Queue,
    factory: Factory,
    nmax: int,
):
    """Consumer to consume products.

    Parameters
    ----------
    p_queue : asyncio.Queue
        products Queue
    r_queue : asyncio.Queue
        recycling Queue
    factory : Factory
        factory with `produce` and `recycle` attribute.
    nmax : int
        max number of products, stop when `factory.n_recycle` reaches this number.
    """
    while factory.n_recycle < nmax:
        if not p_queue.empty():
            product = p_queue.get_nowait()
            p_queue.task_done()
            recycling = await consume(product)
            r_queue.put_nowait(recycling)
        await asyncio.sleep(random.randrange(5) / 5)  # ! release


def main():
    MAX_PRODUCER = 1
    MAX_CONSUMER = 3
    MAX_PRODUCT = 4

    p = asyncio.Queue()  # product queue, no need to be MAX_JOB
    r = asyncio.Queue()  # recycling queue
    factory = Factory()

    loop = asyncio.get_event_loop()
    # create producers
    pros = [
        loop.create_task(producer(p, r, factory, MAX_PRODUCT))
        for _ in range(MAX_PRODUCER)
    ]
    # create consumers
    cons = [
        loop.create_task(consumer(p, r, factory, MAX_PRODUCT))
        for _ in range(MAX_CONSUMER)
    ]
    tasks = pros + cons
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()


if __name__ == '__main__':
    main()
