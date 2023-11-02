FROM node:latest
WORKDIR /app/frontend
COPY ./frontend/package.json ./frontend/package-lock.json /app/frontend/
RUN npm install
COPY ./frontend /app/frontend
RUN npm run build
