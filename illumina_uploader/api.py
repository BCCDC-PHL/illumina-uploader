#!/usr/bin/env python

import argparse
import os

from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, create_engine, select

from .server import sqlite_file_name
from .model import *

sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}

engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)

def get_session():
    with Session(engine) as session:
        yield session

app = FastAPI()
api = FastAPI(openapi_prefix="/api")
app.mount("/api", api)

static_directory_path = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'resources', 'public',
)
app.mount("/", StaticFiles(directory=static_directory_path, html=True), name="static")


@api.on_event("startup")
def on_startup():
    pass

@api.get("/runs/")
def get_runs(*, session: Session = Depends(get_session)):
    folderinfos = session.exec(select(FolderInfo)).all()
    runs = []
    for f in folderinfos:
        run = {
            'run_id': f.folder,
            'upload_timestamp': f.querylastrun,
            'upload_status': f.status,
        }
        runs.append(run)
    if not runs:
        raise HTTPException(status_code=404, detail="Run data not found")
    return runs

@api.get("/runs/{run_id}")
def get_run(*, session: Session = Depends(get_session), run_id: str):
    folderinfo = session.get(FolderInfo, run_id)
    run = {
        'run_id': folderinfo.folder,
        'upload_timestamp': folderinfo.querylastrun,
        'upload_status': folderinfo.status,
    }
    if not folderinfo:
        raise HTTPException(status_code=404, detail="Run data not found")
    return run
