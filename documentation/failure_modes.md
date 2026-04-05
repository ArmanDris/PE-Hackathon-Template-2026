## Failing tests in CI pipeline:

When a pytest test fails or coverage drops below 70%, the integrate job in GitHub Actions will fail and stop the pipeline. Check the detailed logs in the Actions tab, fix the errors locally, and push a new commit to re-run CI.
## Failing deployment in CI pipeline:

The deploy job runs only on the main branch after tests pass. If SSH setup, git pull, or Docker commands fail, the deploy step will abort and show errors in the Actions tab. Fix the issue, then re-trigger the workflow by pushing a new commit or using the “Re-run jobs” option.
## Unhealthy container:

Docker Compose uses `restart: unless-stopped` for all services and a healthcheck for the database. If a service exits or fails its healthcheck, Docker will automatically restart it. Use `docker-compose ps` and `docker-compose logs` to inspect status and `docker-compose restart <service>` to recover manually.
