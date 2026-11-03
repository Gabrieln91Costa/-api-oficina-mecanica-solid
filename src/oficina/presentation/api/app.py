from fastapi import FastAPI
from oficina.config import get_settings
from oficina.infrastructure.persistence.database import create_schema, engine
from oficina.presentation.api.v1.router import router

def create_app(database_engine=None, initialize_schema=True):
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version=settings.app_version,
        description='API de gestão de oficina mecânica — Clean Architecture e SOLID.')
    if initialize_schema:
        create_schema(database_engine or engine)
    app.include_router(router, prefix='/api/v1')
    @app.get('/health', tags=['Infraestrutura'])
    def health(): return {'status': 'ok', 'service': settings.app_name}
    @app.get('/', tags=['Infraestrutura'])
    def root(): return {'message': settings.app_name, 'version': settings.app_version, 'docs': '/docs'}
    return app

app = create_app()
