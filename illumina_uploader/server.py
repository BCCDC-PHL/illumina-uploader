#!/usr/bin/env python

import argparse
import os

import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Session, create_engine

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--db', help="Database file (sqlite)")
parser.add_argument('-p', '--port', type=int, default=8080, help="Port to run server on")
args = parser.parse_args()

sqlite_file_name = os.path.abspath(args.db)

uvicorn.run("illumina_uploader.api:app", host="localhost", port=args.port)    
