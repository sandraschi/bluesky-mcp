# Per-repo fleet start config for bluesky-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'bluesky-mcp'
    BackendPort  = 10760
    FrontendPort = 10761
    HealthPath   = '/api/health'
    WebRoot      = 'webapp'
    Backend = @{
        Kind          = 'uvicorn'
        UvicornTarget = 'bluesky_mcp.server:app'
        Env           = @{ WEB_PORT = '10760' }
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}
