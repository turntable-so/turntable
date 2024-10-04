#!/bin/bash
DEV=true rye run uvicorn server:app --reload-exclude /code/media/ws/