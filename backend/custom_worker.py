from gunicorn.workers.ggevent import GeventWorker


class CustomWorker(GeventWorker):
    def handle_request(self, listener_name, req, client, addr):
        self.log.info("Worker %s: Handling request", self.pid)
        super().handle_request(listener_name, req, client, addr)
        self.log.info("Worker %s: Finished request", self.pid)
