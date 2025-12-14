import uvicorn.workers


class Worker(uvicorn.workers.UvicornWorker):
    CONFIG_KWARGS = {"loop": "npps4.evloop:new_event_loop"}
