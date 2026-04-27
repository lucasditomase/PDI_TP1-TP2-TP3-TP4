## Componentes del modelo OAuth

- Resource Owner (Usuario).
   - Quien posee los datos y recursos.
- Cliente (Aplicación).Flujo básico de OAuth 2.0
  - Aplicación que quiere acceder (ej: app Flask)
- Servidor de autorizaciones. 
  - Emite los tokens (ej: Google Auth)
- Servidor de recursos. 
  - Donde están los datos (API protegida)

## Flujo (Authorization Code)

- La Aplicación solicita permiso al usuario
  - Redirige Servidor de autorizaciones.
- El usuario acepta
  - Login + consentimiento
- El servidor devuelve un código (authorization code)
  - La aplicación intercambia el código por un token
- Access Token (y opcionalmente Refresh Token)
  - La apliación accede a la API con el token

En cada request HTTP:      

GET /api/v1/alumnos HTTP/1.1   
Host: api.uca.edu   
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... (Header Authorization (RFC 6750))      
Content-Type: application/json   

- Authorization: encabezado HTTP estándar
- Bearer: tipo de token (portador)
- <access_token>: credencial
- “quien posee el token, tiene acceso”

- {   
  "access_token": "eyJhbGciOiJIUzI1NiIs...",   
  "token_type": "Bearer",   
  "expires_in": 3600,    
  "scope": "read write"   
}   

La seguridad depende de:

- HTTPS
- expiración del token
- scopes
 


