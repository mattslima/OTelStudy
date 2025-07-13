from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
import random
import os
import time
import logging
from prometheus_client import Counter, Gauge, Histogram, make_asgi_app

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

os.environ["OTEL_SERVICE_NAME"] = "fastapi-app"
os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "http://otel-collector:4317"

def setup_telemetry():
    """Configure OpenTelemetry tracing"""
    resource = Resource(attributes={
        SERVICE_NAME: "fastapi-app"
    })
    
    trace.set_tracer_provider(TracerProvider(resource=resource))
    
    try:
        otlp_exporter = OTLPSpanExporter(
            endpoint="http://otel-collector:4317",
            insecure=True,
            timeout=5
        )
        
        span_processor = BatchSpanProcessor(otlp_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        print("OpenTelemetry configurado com sucesso!")
        
    except Exception as e:
        print(f" Warning: não foi possível configurar o exportador do OpenTelemetry: {e}")
        print(f"Os traces serão gerados, mas não serão exportados para o collector.")

setup_telemetry()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="FastAPI com OpenTelemetry", version="1.0.0")

FastAPIInstrumentor.instrument_app(app)

metrics_app = make_asgi_app()
app.mount("/metrics/", metrics_app)

# MÉTRICAS PROMETHEUS

REQUEST_COUNTER = Counter(
    "app_requests_total",
    "Total number of requests to the app",
    ["endpoint", "method"],
)

HTTP_STATUS_COUNTER = Counter(
    "app_http_responses_total",
    "Total HTTP responses by status code",
    ["status_code", "endpoint", "method"],
)

REQUEST_DURATION = Histogram(
    "app_request_duration_seconds",
    "Request duration in seconds",
    ["endpoint", "method"],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

RANDOM_NUMBER_GAUGE = Gauge(
    "app_random_number",
    "Current value of the random number",
)

ERROR_COUNTER = Counter(
    "app_errors_total",
    "Total number of errors",
    ["error_type", "endpoint"],
)

tracer = trace.get_tracer(__name__)

# MIDDLEWARE PARA CAPTURAR MÉTRICAS AUTOMATICAMENTE

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Middleware para capturar métricas de todas as requisições"""
    start_time = time.time()
    
    endpoint = request.url.path
    method = request.method
    
    REQUEST_COUNTER.labels(endpoint=endpoint, method=method).inc()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    
    status_code = str(response.status_code)
    REQUEST_DURATION.labels(endpoint=endpoint, method=method).observe(duration)
    HTTP_STATUS_COUNTER.labels(
        status_code=status_code, 
        endpoint=endpoint, 
        method=method
    ).inc()
    
    return response

# ENDPOINTS

@app.get("/", response_class=JSONResponse)
def get_homepage():
    """Endpoint raiz para geração de um número aleatorio"""
    with tracer.start_as_current_span("generate_random_number") as span:
        random_number = random.randint(0, 100)
        
        span.set_attribute("random_number", random_number)
        span.set_attribute("endpoint", "/")
        
        RANDOM_NUMBER_GAUGE.set(random_number)
        
        span.set_attribute("operation", "generate_random")
        span.set_attribute("random_range", "0-100")

    return {"status": "ok", "random_number": random_number}

@app.get("/health")
def health_check():
    """Endpoint de HealthCheck"""
    with tracer.start_as_current_span("health_check") as span:
        span.set_attribute("endpoint", "/health")
        span.set_attribute("check_type", "basic")
        
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/simulate-error")
def simulate_error():
    """Endpoint para simulação de erros com tratamento adequado"""
    
    with tracer.start_as_current_span("simulate_error") as span:
        try:
            # Simula algum processamento
            time.sleep(0.1)
            
            # Configura atributos do span ANTES do erro
            span.set_attribute("endpoint", "/simulate-error")
            span.set_attribute("operation", "error_simulation")
            
            # Incrementa counter de erro
            ERROR_COUNTER.labels(
                error_type="simulated_error",
                endpoint="/simulate-error"
            ).inc()
            
            # Registra o erro no span
            span.set_attribute("error", True)
            span.set_attribute("error_message", "Erro simulado para testes")
            span.record_exception(Exception("Erro simulado para testes"))
            span.set_status(trace.Status(trace.StatusCode.ERROR, "Erro simulado"))
            
            # Log do erro
            logger.error("Erro simulado executado no endpoint /simulate-error")
            
            # Opção 1: Retornar erro HTTP controlado
            raise HTTPException(
                status_code=500,
                detail="Erro simulado para testes de monitoramento"
            )
            
        except HTTPException:
            # Re-raise HTTPException para que seja tratada pelo FastAPI
            raise
        except Exception as e:
            # Captura qualquer outro erro não esperado
            span.set_attribute("error", True)
            span.set_attribute("error_message", str(e))
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            
            logger.error(f"Erro inesperado em /simulate-error: {str(e)}")
            
            raise HTTPException(
                status_code=500,
                detail="Erro interno do servidor"
            )

@app.get("/slow-endpoint")
def slow_endpoint():
    """Endpoint para verificar rotas lentas"""
    with tracer.start_as_current_span("slow_processing") as span:
        sleep_time = random.uniform(1, 3)
        time.sleep(sleep_time)
        
        span.set_attribute("processing_time", sleep_time)
        span.set_attribute("endpoint", "/slow-endpoint")
        
    return {"status": "completed", "processing_time": sleep_time}

@app.get("/random-status")
def random_status():
    """Endpoint que retorna diferentes status codes aleatoriamente"""
    with tracer.start_as_current_span("random_status") as span:
        possible_statuses = [200, 201, 400, 404, 500, 503]
        status_code = random.choice(possible_statuses)
        
        span.set_attribute("returned_status_code", status_code)
        span.set_attribute("endpoint", "/random-status")
        
        if status_code >= 400:
            ERROR_COUNTER.labels(
                error_type=f"http_{status_code}", 
                endpoint="/random-status"
            ).inc()
        
        return JSONResponse(
            content={"status": "random", "code": status_code},
            status_code=status_code
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)