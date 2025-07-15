from locust import HttpUser, task, between

class FastAPIUser(HttpUser):
    wait_time = between(1, 2)  # tempo entre requisições

    @task
    def get_home(self):
        self.client.get("/")

    @task
    def get_health(self):
        self.client.get("/health")

