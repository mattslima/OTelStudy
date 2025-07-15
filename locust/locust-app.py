from locust import HttpUser, task, between

class FastAPIUser(HttpUser):
    wait_time = between(1, 2)  # tempo entre requisições

    @task
    def get_home(self):
        self.client.get("/")

    @task
    def get_metrics(self):
        self.client.get("/metrics")

    @task
    def get_random_status(self):
        self.client.get("/random-status")

    @task
    def get_slow_endpoint(self):
        self.client.get("/slow-endpoint")

    @task
    def get_health(self):
        self.client.get("/health")

    @task
    def get_simulate_error(self):
        self.client.get("/simulate-error")
