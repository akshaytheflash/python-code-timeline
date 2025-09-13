from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
import sys
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


traceLog = []
startTime = None
lastVar = {}
lastRunTime = 0.0 

# f locals vars

def tracer(frame, event, arg):
    global traceLog, startTime, lastVar
    if event == "line":
        Time = time.perf_counter() - startTime
        local_vars = frame.f_locals.copy()

        if local_vars != lastVar:
            traceLog.append({"time": Time, "vars": local_vars.copy()})
            lastVar = local_vars.copy()

    return tracer


def run_code(code: str):
    global traceLog, startTime, lastVar, lastRunTime
    traceLog = []
    lastVar = {}
    startTime = time.perf_counter()

    sys.settrace(tracer)
    exec(code, {}, {})
    sys.settrace(None)

    endTime = time.perf_counter()
    lastRunTime = endTime - startTime
    return {"total_time": lastRunTime, "log": traceLog}





# FAST API








@app.post("/run")
def run_endpoint(code: str = Body(..., embed=True)):
    return run_code(code)


@app.get("/state")
def state_endpoint(t: float):
    closest = None
    for entry in traceLog:
        if entry["time"] <= t:
            closest = entry
        else:
            break
    return closest or {}


@app.get("/total_time")
def total_time_endpoint():
    return {"total_time": lastRunTime}
