#!/bin/bash
# Development helper script

set -e

echo "🚀 Structured Prompt Service - Development Script"
echo ""

case "$1" in
  start)
    echo "Starting all services..."
    docker compose up -d
    echo "✅ Services started!"
    echo ""
    echo "Available at:"
    echo "  - API:       http://localhost:8000"
    echo "  - API Docs:  http://localhost:8000/docs"
    echo "  - Prometheus: http://localhost:9090"
    echo "  - Grafana:   http://localhost:3000 (admin/admin)"
    echo "  - RabbitMQ:  http://localhost:15672 (guest/guest)"
    ;;

  stop)
    echo "Stopping all services..."
    docker compose down
    echo "✅ Services stopped!"
    ;;

  restart)
    echo "Restarting all services..."
    docker compose restart
    echo "✅ Services restarted!"
    ;;

  logs)
    docker compose logs -f ${2:-api}
    ;;

  db:migrate)
    echo "Running database migrations..."
    docker compose exec api alembic upgrade head
    echo "✅ Migrations applied!"
    ;;

  db:create-migration)
    if [ -z "$2" ]; then
      echo "❌ Please provide a migration message"
      echo "Usage: ./scripts/dev.sh db:create-migration 'your message'"
      exit 1
    fi
    echo "Creating new migration: $2"
    docker compose exec api alembic revision --autogenerate -m "$2"
    echo "✅ Migration created!"
    ;;

  db:reset)
    echo "⚠️  Resetting database (all data will be lost)..."
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      docker compose down -v
      docker compose up -d postgres
      sleep 5
      docker compose exec api alembic upgrade head
      echo "✅ Database reset complete!"
    fi
    ;;

  test)
    echo "Running tests..."
    docker compose exec api pytest ${@:2}
    ;;

  shell)
    echo "Opening shell in API container..."
    docker compose exec api /bin/bash
    ;;

  format)
    echo "Formatting code with black..."
    black src/ tests/
    echo "✅ Code formatted!"
    ;;

  lint)
    echo "Running linters..."
    flake8 src/ tests/
    mypy src/
    echo "✅ Linting complete!"
    ;;

  clean)
    echo "Cleaning up..."
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete
    find . -type f -name "*.pyo" -delete
    echo "✅ Cleanup complete!"
    ;;

  *)
    echo "Usage: $0 {command}"
    echo ""
    echo "Commands:"
    echo "  start              - Start all services"
    echo "  stop               - Stop all services"
    echo "  restart            - Restart all services"
    echo "  logs [service]     - View logs (default: api)"
    echo "  db:migrate         - Run database migrations"
    echo "  db:create-migration 'message' - Create new migration"
    echo "  db:reset           - Reset database (destructive!)"
    echo "  test [args]        - Run tests"
    echo "  shell              - Open bash shell in API container"
    echo "  format             - Format code with black"
    echo "  lint               - Run linters"
    echo "  clean              - Remove Python cache files"
    exit 1
    ;;
esac
