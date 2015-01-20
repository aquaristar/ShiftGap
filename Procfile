web: newrelic-admin run-program  waitress-serve --port=$PORT shiftgap.wsgi:application
#scheduler: newrelic-admin run-program celery -A shiftgap.celery worker -B -E --loglevel=info
#worker: newrelic-admin run-program celery worker --app=shiftgap.celery
console: bash