FROM node:20-alpine AS build
WORKDIR /app

ARG VITE_API_URL=http://localhost:8011
ARG VITE_TENANT_ID=
ARG VITE_CSRF_COOKIE_NAME=rupmes_csrf
ARG VITE_DEFAULT_LANG=es

ENV VITE_API_URL=$VITE_API_URL
ENV VITE_TENANT_ID=$VITE_TENANT_ID
ENV VITE_CSRF_COOKIE_NAME=$VITE_CSRF_COOKIE_NAME
ENV VITE_DEFAULT_LANG=$VITE_DEFAULT_LANG

COPY package.json package-lock.json* ./
RUN npm install
COPY . ./
RUN npm run build

FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
COPY app-config.template.js /usr/share/nginx/html/app-config.template.js
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
EXPOSE 80
CMD ["/docker-entrypoint.sh"]
