import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Optional

from app.models import ProcessingJob


class ProcessingStatusManager:
    """
    Manages processing job status, creation, updates, and cleanup.
    Handles all database operations related to job tracking.
    """

    def __init__(self, db_session: Any, logger: Optional[logging.Logger] = None):
        self.db_session = db_session
        self.logger = logger or logging.getLogger(__name__)

    def generate_job_id(self) -> str:
        """Generate a unique job ID."""
        return str(uuid.uuid4())

    def create_job(self, post_guid: str, job_id: str) -> ProcessingJob:
        """Create new job, cleaning up old jobs."""
        # Clean up old jobs (older than 1 day)
        cutoff_date = datetime.utcnow() - timedelta(days=1)
        old_jobs = ProcessingJob.query.filter(
            ProcessingJob.created_at < cutoff_date
        ).all()

        for old_job in old_jobs:
            self.db_session.delete(old_job)

        self.db_session.commit()

        # Create new job
        job = ProcessingJob(
            id=job_id,
            post_guid=post_guid,
            status="pending",
            current_step=0,
            total_steps=4,
            progress_percentage=0.0,
            created_at=datetime.utcnow(),
        )
        self.db_session.add(job)
        self.db_session.commit()
        return job

    def cancel_existing_jobs(self, post_guid: str, current_job_id: str) -> None:
        """Delete any existing active jobs for this post (called when we acquire the lock)."""
        existing_jobs = (
            ProcessingJob.query.filter_by(post_guid=post_guid)
            .filter(
                ProcessingJob.status.in_(["pending", "running"]),
                ProcessingJob.id != current_job_id,
            )
            .all()
        )

        for existing_job in existing_jobs:
            self.db_session.delete(existing_job)

        self.db_session.commit()

    def update_job_status(
        self,
        job: ProcessingJob,
        status: str,
        step: int,
        step_name: str,
        progress: Optional[float] = None,
    ) -> None:
        """Update job status in database."""
        job.status = status
        job.current_step = step
        job.step_name = step_name

        if progress is not None:
            job.progress_percentage = progress
        else:
            # Calculate progress based on step
            job.progress_percentage = (step / job.total_steps) * 100.0

        if status == "running" and not job.started_at:
            job.started_at = datetime.utcnow()
        elif status in ["completed", "failed"]:
            job.completed_at = datetime.utcnow()

        self.db_session.commit()
