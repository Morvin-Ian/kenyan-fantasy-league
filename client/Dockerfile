FROM node:20
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install
COPY . .
RUN npm run build

# FROM node:20 AS build-stage

# WORKDIR /app

# COPY package.json package-lock.json ./

# RUN npm ci

# COPY . .

# RUN npm run build

# FROM nginx:alpine AS production-stage

# RUN rm /etc/nginx/conf.d/default.conf

# COPY --from=build-stage /app/dist /usr/share/nginx/html

# EXPOSE 80

# CMD ["nginx", "-g", "daemon off;"]