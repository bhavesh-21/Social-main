# Define the commands to run
$commands = @(
    { celery -A app:celery worker --loglevel=info --concurrency=1 },
    { gunicorn app:app }
)

# Run the commands in parallel
$jobs = foreach ($command in $commands) {
    Start-Job -ScriptBlock $command
}

# Wait for any job to complete (or fail)
$completedJob = Wait-Job -Job $jobs -Any

# Check if the completed job failed
if ($completedJob.State -eq 'Failed') {
    # If any job failed, stop all jobs
    foreach ($job in $jobs) {
        Stop-Job -Job $job
    }
    Write-Host "One of the commands failed. Stopped all jobs."
    exit 1
}

# Retrieve the results of the jobs (this will block until all are complete)
$results = $jobs | Receive-Job

# Clean up
$jobs | Remove-Job

# Output the results
$results
Write-Host "All commands completed successfully."
