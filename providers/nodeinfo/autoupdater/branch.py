import providers

class Source(providers.DataSource):
    def call(self):
        return "stable"
