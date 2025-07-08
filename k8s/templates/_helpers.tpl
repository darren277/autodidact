{{- define "flask.sharedEnv" }}
- name: APP_SECRET_KEY
  valueFrom:
    secretKeyRef:
      name: flask-secret
      key: flaskAppSecret
- name: USER_POOL_ID
  value: "{{ .Values.auth.cognito.userPoolId }}"
- name: USER_POOL_CLIENT_ID
  value: "{{ .Values.auth.cognito.userPoolClientId }}"
- name: USER_POOL_CLIENT_SECRET
  valueFrom:
    secretKeyRef:
      name: cognito-secret
      key: userPoolClientSecret
- name: COGNITO_DOMAIN
  value: "{{ .Values.auth.cognito.cognitoDomain }}"
- name: GOOGLE_REDIRECT_URI
  value: "{{ .Values.auth.googleRedirectUri }}"
- name: REDIS_HOST
  value: "{{ .Values.redis.host }}"
- name: REDIS_PORT
  value: "{{ .Values.redis.port }}"
- name: POSTGRES_HOST
  value: "{{ .Values.postgres.host }}"
- name: POSTGRES_PORT
  value: "{{ .Values.postgres.port }}"
- name: POSTGRES_DB
  value: "{{ .Values.postgres.db }}"
- name: POSTGRES_USER
  valueFrom:
    secretKeyRef:
      name: postgres-secret
      key: user
- name: POSTGRES_PASSWORD
  valueFrom:
    secretKeyRef:
      name: postgres-secret
      key: pass
- name: OPENAI_API_KEY
  valueFrom:
    secretKeyRef:
      name: openai-secret-api-key
      key: apiKey
{{- end }}
