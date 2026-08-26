from .contracts import Candidate, ImageResult, RouterResult
from .schemas.registry import SchemaRegistry

class RegistrySchemaAdapter:
    def __init__(self, registry=None):
        self.registry = registry or SchemaRegistry()
    def as_graph_schemas(self):
        from .workflow.schema import SchemaField, ServiceSchema
        result = {}
        for sid, raw in self.registry.all().items():
            result[sid] = ServiceSchema(sid, raw["service_name"], raw["description"], raw["department"], tuple(raw["keywords"]), tuple(SchemaField(f["id"], f["type"], f["required"], tuple(f.get("options", [])), f.get("image_derivable", False)) for f in raw["fields"]), raw["schema_version"], raw["submission"]["endpoint"], raw["submission"]["id_prefix"])
        return result

class SchemaRouterAdapter:
    def __init__(self, schemas): self.router = __import__("app.services.router", fromlist=["ServiceRouter"]).ServiceRouter({k:{"keywords":v.keywords} for k,v in schemas.items()})
    def classify(self, message, schemas): return self.router.route(message)

class SchemaCollectorAdapter:
    def __init__(self): self.engine = __import__("app.collection.engine", fromlist=["CollectionEngine"]).CollectionEngine()
    def collect(self, field, message):
        schema = {"fields":[{"id":field.id,"type":field.field_type,"required":field.required,"options":list(field.options)}]}
        candidates = self.engine.collect(message, schema)
        return candidates[0] if candidates else None

class ImageAnalyzerAdapter:
    def __init__(self): self.analyzer = __import__("app.tools.image", fromlist=["ImageAnalyzer"]).ImageAnalyzer()
    def analyze(self, schema, *, filename, content_type, content): return self.analyzer.analyze(filename, content)
