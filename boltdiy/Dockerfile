# Bolt.DIY Docker Container
FROM node:20-alpine

WORKDIR /app

# Install git for cloning the repository
RUN apk add --no-cache git

# Clone Bolt.DIY repository
RUN git clone https://github.com/stackblitz/bolt.new.git . || \
    git clone https://github.com/stackblitz/bolt.git . || \
    echo "Note: Bolt.DIY repo URL may have changed"

# Install dependencies
RUN npm install || yarn install

# Expose the default Vite port
EXPOSE 5173

# Start the development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]