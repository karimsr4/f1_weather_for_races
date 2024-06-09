# Use the official Node.js image as base
FROM node:14 AS build

# Set environment variables
ENV APP_HOME /app

# Create and set the working directory
WORKDIR $APP_HOME

# Copy the frontend code into the container
COPY . .

ENV REACT_APP_API_URL="https://f1backend-y66wotluqa-uc.a.run.app"

# Install dependencies and build the app
RUN npm install
RUN npm run build

# Use Nginx to serve the built static files
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
