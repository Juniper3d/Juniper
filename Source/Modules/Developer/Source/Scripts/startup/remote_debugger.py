"""
:type script
:callbacks [startup]
:desc Attaches a PTVSD remote debugger to the port 7720
"""
import ptvsd

import juniper


if(juniper.program_context != "python"):
    initialized = False

    for i in range(16):
        if(not initialized):
            try:
                ptvsd.enable_attach(address=('127.0.0.1', 7720 + i))
                juniper.log.info(f"Attached PTVSD remote debugger to port {7720 + i}", silent=True)
                initialized = True
            except Exception:
                pass

    if(not initialized):
        juniper.log.warning("Failed to initialize PTVSD remote debugger.", traceback=False)
