# frontend/Dockerfile
FROM node:18-alpine

# Set work directory
WORKDIR /app

# Install dependencies
COPY package.json .
RUN npm install

# Copy project
COPY . .

# Build the app
RUN npm run build

# Install serve
RUN npm install -g serve

# Expose port
EXPOSE 3000

# Serve the build
CMD ["serve", "-s", "dist", "-l", "3000"]