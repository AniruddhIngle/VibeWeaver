from locust import HttpUser, task, constant_pacing

class MyUser(HttpUser):
    wait_time = constant_pacing(1) 
    host = "http://127.0.0.1:8000"  

    @task
    def query_api(self):
        query_text = "Your query text here"
        n_results = 10
        response = self.client.get(f"/query?query_text={query_text}&n_results={n_results}")
