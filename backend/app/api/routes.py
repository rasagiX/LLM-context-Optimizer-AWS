"""Aggregates all sub-routers under /api/v1."""

from fastapi import APIRouter

from app.api import benchmarks, evaluation, optimize, runs

router = APIRouter()

router.include_router(runs.router, tags=["runs"])
router.include_router(optimize.router, tags=["optimize"])
router.include_router(evaluation.router, tags=["evaluate"])
router.include_router(benchmarks.router, tags=["benchmarks"])
