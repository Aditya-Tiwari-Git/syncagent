FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

ARG VITE_BACKEND_URL=https://syncagent-toqlcshkma-uc.a.run.app
ENV VITE_BACKEND_URL=${VITE_BACKEND_URL}

RUN echo "Building with backend URL: ${VITE_BACKEND_URL}"
RUN npm run build


FROM nginx:alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
