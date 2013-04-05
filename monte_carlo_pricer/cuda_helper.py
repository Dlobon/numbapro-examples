from collections import deque
from numbapro import cuda

class MM(object):
    """Memory Manager
    
    Maintain a freelist of device memory for reuse.
    """
    def __init__(self, shape, dtype, prealloc):
        self.device = cuda.get_current_device()
        self.freelist = deque()
        self.events = {}
        for i in range(prealloc):
            gpumem = cuda.device_array(shape=shape, dtype=dtype)
            self.freelist.append(gpumem)
            self.events[gpumem] = cuda.event(timing=False)

    def get(self):
        assert self.freelist
        gpumem = self.freelist.popleft()
        evnt = self.events[gpumem]
        if not evnt.query(): # not ready?
            # querying is faster then waiting
            evnt.wait() # future works must wait
        return gpumem

    def free(self, gpumem, stream=0):
        evnt = self.events[gpumem]
        evnt.record()
        self.freelist.append(gpumem)

