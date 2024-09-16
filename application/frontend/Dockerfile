# Use a lightweight NGINX image to serve the HTML file
FROM nginx:alpine

# Copy the HTML file(s) and other static assets to the NGINX web root
COPY . /usr/share/nginx/html

# Expose port 80 to serve the frontend
EXPOSE 80

# Start the NGINX server
CMD ["nginx", "-g", "daemon off;"]