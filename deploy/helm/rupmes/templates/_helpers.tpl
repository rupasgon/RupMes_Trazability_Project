{{- define "rupmes.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "rupmes.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name (include "rupmes.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{- define "rupmes.labels" -}}
app.kubernetes.io/name: {{ include "rupmes.name" . }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{- define "rupmes.selectorLabels" -}}
app.kubernetes.io/name: {{ include "rupmes.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "rupmes.databaseUrl" -}}
{{- if .Values.database.external.enabled -}}
{{- .Values.database.external.url -}}
{{- else -}}
{{- printf "postgresql+psycopg2://%s:%s@%s-postgres:%v/%s" .Values.database.internal.user .Values.database.internal.password (include "rupmes.fullname" .) .Values.database.internal.service.port .Values.database.internal.db -}}
{{- end -}}
{{- end -}}
