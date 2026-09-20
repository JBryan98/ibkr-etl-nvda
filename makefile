infra-up:
	docker compose up -d
	@echo ""
	@echo "  Infraestructura levantada. Accesos:"
	@echo "  ------------------------------------"
	@echo "  API IBKR live:        http://localhost:4001"
	@echo "  API IBKR paper:       http://localhost:4002"
	@echo "  IB Gateway vía VNC:   http://localhost:5900"
	@echo ""

infra-down:
	docker compose down

infra-clean:
	docker compose down -v
	@echo "Contenedores y volumenes eliminados. Usa make infra-up para empezar desde cero."